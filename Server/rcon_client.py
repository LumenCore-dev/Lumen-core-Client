"""Dependency-free Source RCON client for the Halo 4 dedicated operator API."""
import argparse
import getpass
from pathlib import Path
import socket
import struct


def packet(request_id, kind, body=b""):
    if isinstance(body, str):
        body = body.encode("utf-8")
    if len(body) > 4086 or b"\0" in body:
        raise ValueError("RCON request exceeds packet limit or contains NUL")
    return struct.pack("<iii", len(body) + 10, request_id, kind) + body + b"\0\0"


def read_exact(stream, size):
    data = bytearray()
    while len(data) < size:
        chunk = stream.recv(size - len(data))
        if not chunk:
            raise ConnectionError("RCON connection closed")
        data.extend(chunk)
    return bytes(data)


def receive(stream):
    size, = struct.unpack("<i", read_exact(stream, 4))
    if not 10 <= size <= 4096:
        raise ValueError("Invalid RCON packet length")
    data = read_exact(stream, size)
    if data[-2:] != b"\0\0":
        raise ValueError("Invalid RCON packet terminator")
    request_id, kind = struct.unpack("<ii", data[:8])
    return request_id, kind, data[8:-2]


class Client:
    def __init__(self, host, port, password, timeout=5):
        self.stream = socket.create_connection((host, port), timeout)
        self.next_id = 10
        try:
            self.stream.sendall(packet(1, 3, password))
            for _ in range(4):
                request_id, kind, _ = receive(self.stream)
                if kind == 2:
                    if request_id == -1:
                        raise PermissionError("RCON: falsches Passwort")
                    if request_id != 1:
                        raise ValueError("RCON authentication ID mismatch")
                    break
            else:
                raise ValueError("RCON authentication response missing")
        except BaseException:
            self.stream.close()
            raise

    def run(self, command):
        if not 1 <= len(command.encode("utf-8")) <= 1024:
            raise ValueError("Command needs 1..1024 UTF-8 bytes")
        request_id = self.next_id
        self.next_id += 2
        probe_id = request_id + 1
        self.stream.sendall(packet(request_id, 2, command) + packet(probe_id, 0))
        chunks = []
        for _ in range(128):
            response_id, kind, body = receive(self.stream)
            if kind != 0:
                raise ValueError("Unexpected RCON response type")
            if response_id == request_id:
                chunks.append(body)
            elif response_id == probe_id and not body:
                if receive(self.stream) != (probe_id, 0, b"\0\1\0\0"):
                    raise ValueError("RCON response terminator missing")
                return b"".join(chunks).decode("utf-8")
            else:
                raise ValueError("RCON response ID mismatch")
        raise ValueError("RCON response exceeds limit")

    def close(self):
        self.stream.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def main():
    parser = argparse.ArgumentParser(description="Halo 4 Source RCON")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=50682)
    parser.add_argument("--password-file", type=Path)
    parser.add_argument("command", nargs="*", help="Without a command, open an interactive RCON shell")
    args = parser.parse_args()
    try:
        password = args.password_file.read_text(encoding="utf-8").strip() if args.password_file else getpass.getpass("RCON-Passwort: ")
        with Client(args.host, args.port, password) as client:
            if args.command:
                print(client.run(" ".join(args.command)), end="")
            else:
                while True:
                    try:
                        command = input("rcon> ").strip()
                    except (EOFError, KeyboardInterrupt):
                        break
                    if not command:
                        continue
                    print(client.run(command), end="")
                    if command.lower() in ("stop", "quit", "exit"):
                        break
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
