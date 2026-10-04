# Vision enclosure models

Self-contained, editable OpenSCAD code for all seven designs in the supplied
`ENCLOSURE_PROMPTS.md`. The reference is at `../../ENCLOSURE_PROMPTS.md` relative
to this folder. No libraries are required. All dimensions are millimetres.

## Use

1. Open `vision_enclosures.scad` in OpenSCAD, or paste its entire contents into
   the playground, replacing the example code.
2. Change `part = "layout";` to a selection from the table below.
3. Replace the typical component sizes and the explicitly marked position
   placeholders near the top of the file with measurements.
4. Preview, render, then export one selected part as STL. In desktop OpenSCAD,
   use F5 for preview and F6 for render, then File > Export > Export as STL.
5. Use `camera_assembly` and `preview_tilt` to inspect the camera arrangement.
   This view omits purchased servos, horns, screws, boards and cables. It is
   not an STL to print and does not constitute a collision or load test.

| Selection | Result |
| --- | --- |
| `layout` | Eight separate pieces laid out for viewing, using horizontal C1 |
| `camera_assembly` | Assembled camera enclosure preview |
| `C1` | Pan pod with horizontal-axis tube clamp and tripod nut pocket |
| `C1_vertical` | Alternative with vertical-axis tube clamp behind the pod |
| `C2` | Pan yoke, tilt-servo window and pivot spacer |
| `C3` | Camera front shell, PCB ledges and hinge mounting plates |
| `C4` | Camera rear bay, perfboard rails, vents and strain-relief bridge |
| `P5` | Voice enclosure with breadboard locator, spare bay and strap ears |
| `P6` | Matching voice lid |
| `P7_front` | Mic pod half containing the angled NeoPixel diffuser |
| `P7_back` | Other mic pod half |

Example:

```scad
part = "C3";
```

The nine default STL exports and two previews are in `validation/`. They are
prototype exports using typical sizes, not measurement-approved production files.
Regenerate them after changing parameters. Never export the layout as one part.

## Deliberate corrections and prototype limitations

The reference contains conflicting dimensions and printing constraints. These
models resolve some geometrically and make the remaining limits explicit:

- Camera outer body: **40.8 x 76.8 x 39.6 mm**. Its larger footprint allows for
  the 30 mm perfboard and corner fasteners, beyond the 28 mm camera PCB.
- Rear depth: **25.6 mm**, derived from 10 mm header separation + 1.6 mm perfboard
  + 12 mm component space + 2 mm rear wall. The original 20 mm cannot hold that
  stack. Actual pin lengths and capacitor clearance still need checking.
- Hinge plates extend rearward from C3 to put the tilt axis at assembled
  mid-depth. The original 10 mm circular boss cannot contain a 20 mm horn.
  The enlarged horn pocket takes a conservative 20 mm hub-to-tip length.
- Yoke inner gap: **69.8 mm**, allowing 11.5 mm per side beyond the case bosses.
  This includes the provisional 8.5 mm servo projection and 2 mm horn thickness.
  A matching spacer on the pivot arm fills its extra distance. The base is
  **76.4 x 44.8 mm**, expanded to contain both the arms and the horn pocket.
  Measure the servo tab-to-output-face distance before selecting final spacing.
- The tilt axis remains 48 mm above the plate top. Its height also increases
  automatically if the case diagonal grows. This gives a conservative body-to-
  plate envelope, but does not check ribs, cables, screws or the actual servo.
- C1's bearing ring is approximately **37.77 mm inside diameter, 9 mm tall**:
  its diameter clears the off-centre servo body and its height follows the
  assumed servo/horn stack. A 30 mm ring only 1 mm above the mounting tabs would
  collide with that body or fail to reach the yoke. The bearing surface is not
  a load-rated bearing. The pod is intentionally thick around the mount.
- The vertical clamp is offset behind the pod to keep its tube bore open.
  C1's origin is the pan shaft axis at bed height, rather than the centre of
  its asymmetric tripod flange footprint. The horizontal clamp has a 90-degree
  mouth (270-degree wrap). Interference is diametral and requires a fit coupon.
- The camera USB cut-outs continue into the rear rim where needed. The cable
  notch opens to that rim for assembly and avoids tiny detached tabs.
- C3's optional outward lens hood defaults to **off** (`camera_hood = 0`) so
  its front lies flat on the bed. Set it to 1.5 for a hood and revise supports
  or print orientation. Labels are 0.6 mm engravings, rather than raised text
  underneath the print. They are optional.
- Voice interior: **96.8 x 49.6 x 30 mm**. Space is reserved for the breadboard
  and optional battery/charger, but the spare bay has no battery-specific clips
  or charger standoffs. Secure and insulate those components separately. USB
  positions are placeholders. Strap slots are external ears to isolate straps
  from the electronics.
- P7 uses a **30 mm nominal diameter x 52 mm nominal length** capsule to make
  room for the mic, header space, LED and 12 mm arm socket. Its ports remove
  the extreme tips; the angled diffuser also projects above the capsule.
  Both halves print with their split planes on the bed. Front screw seats use
  counterbores, not conical countersinks. The diffuser is a 1 mm solid window
  angled 30 degrees; use translucent/natural material. Transmission is untested.
- `mic_sound_x` and `mic_sound_z` must match the actual acoustic port, and the
  module's acoustic side must face the tip. The two clamped halves capture it;
  the 0.8 mm retaining rim is a local exception to the 1.2 mm minimum feature.
- Curved clamp bores, horizontal pivot/horn pockets, rear guides, the offset
  vertical clamp platform and pod roofs may need supports or reorientation.
  **Support-free printing, uniform 3 mm fillets, all overhangs below 45 degrees,
  and bridges below 20 mm have not been achieved or certified.** Rounded planar
  footprints use chamfers; curved clamps/pods do not have universal bottom chamfers.
- Camera rear fasteners pass through the deep bay, so the reference's M2 x 6 mm
  screws are too short. Allow roughly 30-32 mm screw length (verify head seating
  and engagement). The enlarged pivot spacer also needs a longer pivot screw.
  Select actual screw and clamp-bolt lengths after the fit test.

## Validation performed on 2026-10-04

Rendered with the official portable OpenSCAD 2021.01 Windows build from the
[OpenSCAD download page](https://openscad.org/downloads.html), without installing
it system-wide. Each of the nine part exports reported `Simple: yes`.

`python enclosure/check_meshes.py` checks the exported ASCII STLs using the
Python standard library. All nine default exports passed: one connected mesh,
every edge shared by two faces, consistent edge winding, no zero-area triangles
and positive signed volume. See `validation/mesh_report.json` and individual
render logs. Layout and camera assembly previews were visually inspected.

These checks establish default-export geometry only. They do not establish
component fit, arbitrary parameter combinations, slicer support requirements,
clamp holding force, servo torque, thermal performance, acoustics, or full
pan/tilt motion. No hardware or software-phase acceptance is inferred.

Before printing the full set, measure the components, make a clamp/horn/lip fit
coupon, inspect each sliced layer, and assemble and sweep the mechanism on a
bench. Confirm sound-port alignment and secure mounting before use near a person.
