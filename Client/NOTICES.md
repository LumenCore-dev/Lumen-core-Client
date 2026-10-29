# Third-party notices



## HaloCheckpointManager



Pointer definitions in `native/game.hpp` are adapted from HaloCheckpointManager by Maurice Dix (Burnt-o), commit `c5f4069a9e79060d0eeb85105636fe17b6b77563`.



MIT License



Copyright (c) 2025 Maurice Dix



Permission is hereby granted, free of charge, to any person obtaining a copy

of this software and associated documentation files (the "Software"), to deal

in the Software without restriction, including without limitation the rights

to use, copy, modify, merge, publish, distribute, sublicense, and/or sell

copies of the Software, and to permit persons to whom the Software is

furnished to do so, subject to the following conditions:



The above copyright notice and this permission notice shall be included in all

copies or substantial portions of the Software.



THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR

IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,

FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE

AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER

LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,

OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE

SOFTWARE.



## Dear ImGui / MinHook



These libraries are compiled from the included source trees. Full licenses:



- `licenses/imgui-LICENSE.txt` (MIT, Omar Cornut; source: `third_party/imgui/LICENSE.txt`).

- `licenses/minhook-LICENSE.txt` (BSD-style licenses, Tsuda Kageyu and contributors; source: `third_party/minhook/LICENSE.txt`).



## libmcc



The public libmcc headers were consulted for numeric layout information about

MCC game options and Halo 3 static TLS, data arrays, player configuration and observer layouts. No libmcc implementation or compiled library is included in

the application. The research checkout is retained for traceability.



## Assembly schema reference



The Halo3MCC weapon and biped plugins from XboxChaos/Assembly were consulted

for numeric field offsets, model-reference layout, bounding metadata and field

meaning. No Assembly executable, implementation, or

XML plugin is shipped in the binary package. Runtime tag pointers also use

the HCM reference identified above.



## MCCVR-Halo-Build collision and node-bank reference



The Halo 3 collision-vector signature, eight-argument ABI and scheduling reference in `native/visibility.hpp` were consulted/adapted from `src/dll/game.cpp` and `halo3_collision_dispatch.inl` in moistman42069/MCCVR-Halo-Build, commit `b243af2256a1a3b424cbccd940f8e8a674cef608`. The exact signature and numeric output/flags layout were independently checked against the pinned local retail Halo 3 image. The numeric object-node-bank layout (signed byte size at 0x136, signed relative offset at 0x138, 0x34-byte world-space matrices) was also consulted in that reference and independently confirmed by read-only live object samples. No VR runtime, game binaries or editing-kit assets are included.



MIT License, Copyright (c) 2026 pancreations. Full license: `licenses/MCCVR-LICENSE.txt`.



## Halo 3 firing-data reference



The seven-argument firing-data ABI (RVA 0x3524B0), pinned entry bytes and native weapon-barrel call edge (0x368B92 / return 0x368B97) in `native/shot.hpp` were consulted in the local MCCVR-Halo-Build `halo3_dual_wield_runtime.inl`, `halo3_dual_lifecycle.inl` and `DUAL-WIELD-REFINEMENT-2026-09-09.md`. This build implements its own target selection and shot-origin collision check. The reference license is `licenses/MCCVR-LICENSE.txt` (MIT). No game binaries or VR runtime are distributed.



## Team/allegiance layout research



The ManagedDonkey unit and game-allegiance headers were consulted as general structure references: https://github.com/twist84/ManagedDonkey/blob/main/game/source/units/units.hpp and https://github.com/twist84/ManagedDonkey/blob/main/game/source/game/game_allegiance.hpp. No implementation from that project is distributed. Retail x64 unit fields (+0x174, +0x178), player team (+0xF0), TLS allegiance (+0x180), row strides and offsets (+0x144/+0x184), active engine dispatch and Infection mask were independently established from the pinned local retail image. `test-team-binding.py` records the exact code/data-flow checks. The application reads the verified data; it does not call the native team functions from its worker thread.


## Object placement research

The public ManagedDonkey object-placement and game-simulation headers were consulted as a cross-check. No implementation or compiled library is included. All MCC offsets and ABI bindings used by the new features were independently verified against the local retail Halo 3 binary. Reference: https://github.com/theTwist84/ManagedDonkey/blob/main/game/source/objects/objects.hpp


## Vehicle-control and projectile damage-owner research

ManagedDonkey vehicle/unit, seat and damage-owner headers were consulted for field names. Retail MCC driver/seat, tag-seat stride, control-throttle, primary-action flags and the generic velocity setter were independently verified from the pinned local image; see test-vehicle-binding.py. No reference implementation or game binary is distributed. References: https://github.com/theTwist84/ManagedDonkey/blob/main/game/source/units/units.hpp and https://github.com/theTwist84/ManagedDonkey/blob/main/game/source/objects/damage_owner.hpp
