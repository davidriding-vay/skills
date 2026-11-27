# Rearguard house standard (components)

Current as of 2026-11-21. Source of truth in the project: `HOUSE_STANDARD.md` (also holds the dated log).
Font sizes are px, line widths mm, schematic lengths mil. Colours are Altium integers (BGR).

## Colours
| Name | Hex | Altium int | Use |
|---|---|---|---|
| Dark blue | `#344062` | 6438964 | text, borders, pins, leads, parameters |
| Light blue | `#90D5FF` | 16766352 | sheet symbols, IO ports (fill) |
| Symbol body | `#CFE5F3` = RGB 207,229,243 | 15983311 | IC / connector symbol body fill |
| White | `#FFFFFF` | 16777215 | passive symbol body fill |

The old README listed light blue as `#663350`, which is a dark maroon; the user supplied the corrected values above.

## Schematic sheet
Grid 100 mil (2.54 mm), snap 50 mil. Arial Bold. Sizes: page titles 12-24, general 8, sheet entries 8, harness entries 8, component parameters 6, power ports 8, ref designators 8, sheet name 12 UPPERCASE, sheet filename 6 lower-case-with-hyphens. Sheet symbols and IO ports: fill light blue, border dark blue, medium. No repeating sheets.

## Pin length rule
Chips (ICs): 300 mil. Every other component (R, C, L, diodes, transistors, connectors, etc.): 100 mil.

## Chip (IC) symbols
- LibRef name = the MPN. Ref designator single `?`: `U?`, `J?`, `R?`, `C?`, `L?`, `D?`.
- Body 1500 mil wide, fill 15983311, border 6438964, line width 1 (Small; 0 is Smallest, do not use 0).
- PIN GRID (user rule 2026-11-26): the HOTSPOT of every pin, i.e. its wire end (ConnectionX/Y, the electrical end a wire touches), sits on the 100 mil grid. The pin root (Location, body end) and the length do not have to: 80 mil pins with roots at +-120 are right for BJT/MOSFET leads inside the circle. Check with `obj_query` ePin `Location.X,Location.Y,ConnectionX,ConnectionY,PinLength`; do not move roots onto the grid if that pushes the hotspot off it (SUP53P06-20 rev 3 did: roots +-100, length 80, hotspots +-180; rev 4 is correct, hotspots +-200).
- Pins 300 mil (chips only), dark blue, pitch 100 mil, pin designator offset (120, 0) mil, pin name offset (50, 0) mil, pin font Arial Bold 8 dark blue.
- Pin types allowed: Input, Output, IO, Power. Write `io` (tools) or `IO` (ASCII importer); never "Bidirectional". Open question: the user's STM32 keeps all GPIO and OSC pins as IO and BOOT0 as input; datasheet types (OSC_IN input, OSC_OUT output) were not applied.
- Multi-part: Part A = signals (GPIO, logic, SWD, RF), Part B = power (VDD/VSS). Pins grouped by function, not package order, with empty rows between groups (the tools' guidance puts pins on the left and right only).
- Pin 1 top-left with counter-clockwise numbering is how the LQFP48 footprint was built; apply it to ICs unless the datasheet land drawing says otherwise.
- Left pin: Location x=0, rotation 180. Right pin: Location x=body width, rotation 0. Pin Location is where the pin meets the body.
- Designator: Arial Bold 8 (font id 4), `#344062`, near the body top-left. MPN and DES parameters below the body.

## All other symbols (R, C, L, diodes, transistors, connectors, ...) - 100 mil pins, NOT the chip rules
Geometry below is the existing R / C style; diodes, transistors and connectors follow the same 100 mil pin length and dark-blue style. Their glyph sizes are not yet written down.
- Pins 100 mil long, connection points x=0 and x=400, pin 1 left, pin 2 right. Pins, leads and body border `#344062`, line width 1.
- Designators on R and C: Arial Bold 8 (font id 4), `#344062`.
- Resistor: body rectangle x 130..270, y -25..25, white fill, 30 mil lead polylines (100-130, 270-300). Designator `R?` at (120, 70). MPN at (0,-130), DES at (0,-200).
- Capacitor (user layout, reference part `C0603C104K5RACTU`, adopted 2026-11-22; the scratch library that held it is deleted, the workspace symbol of `GRM31CR72A105KA01L` / CMP-00477 carries the same layout): IEC parallel plates, plate lines x=140 and x=170 (30 mil gap), y -50..50; lead polylines y=0 from x=50 to 140 and 170 to 250. Pins length 100, pin 1 body-end at x=100 rotation 180, pin 2 body-end at x=200 rotation 0 (wire ends at x=0 and x=300); pin name and designator hidden. Designator `C?` at (70, 90). MPN at (0,-180), DES at (0,-250), hidden Comment at (-50,-150). All lines width 1 `#344062`. The old layout (plates x=190/220, pins at x=0 and 400) is superseded; the plate centre (155) is 5 mil right of the pin centre (150) in the reference, copy it exactly.
- Inductor: same pin geometry; keep the existing library glyph.

## Parameters
- Only `DES` and `MPN` are visible. A hidden `Comment` mirrors the MPN. No other parameters (the project standard says "no other parameters"; the old library carried `Available Preview Images` and a hash). `Designator` and `Description` are component fields, not parameters.
- Arial Bold 6 (font id 3), `#344062`, no auto-arrange.
- `DES` is ALL UPPERCASE including units, no spaces, hyphen-separated: `IC-DUAL-OPAMP-LOW-POWER-130MHZ-75MA-RAIL-TO-RAIL-SOIC8`, `RES-24R-1%-100MW-100PPM-0603`, `CAP-0.1UF-50V-10%-X7R-0603`, `IC-MCU-32B-CORTEX-M3-64KB-FLASH-20KB-RAM-48-LQFP`.
- `MPN` is the exact orderable part number from the datasheet (no truncation, no letter O for zero).
- Description: one clear line from the datasheet.

## Footprints
Mechanical layer pairs (top/bottom). Names are "Top <purpose>" / "Bottom <purpose>"; kinds set except M15/16 and M25/26. The kind names below are the ones `lib_set_mech_layers` accepted and read back for the project libraries.

| Pair | Purpose | Kind |
|---|---|---|
| M5/M6 | Dimensions | Dimensions |
| M9/M10 | Glue points | Glue Points |
| M13/M14 | 3D body | 3D Body |
| M15/M16 | Mechanical info | not set |
| M19/M20 | Component outline | Component Outline |
| M25/M26 | Keepout | not set |
| M27/M28 | Courtyard | Courtyard |
| M33/M34 | Designator | Designator |
| M35/M36 | Assembly | Assembly |
| M37/M38 | Component centre | Component Center |
Plus Overlay, Paste, Solder.

Drawing rules (every generated footprint):
- Lands: the manufacturer's recommended land pattern when the datasheet draws one (custom pads, compared against the drawing); otherwise IPC-7351B nominal. Pad shape roundrect, 10% corners. Mask and paste by rule. Pin 1 top-left, pins counter-clockwise for ICs.
- Overlay (TopOverlay) 0.2 mm line, box with its centre-line 0.15 mm outside the pad bounding box (for chips), never over copper.
- Every mechanical-layer line is 0.1 mm.
- Courtyard (M27) rectangle, = max(IPC courtyard, overlay outer edge rounded up to 0.05 mm).
- Component outline (M19) = body outline, nominal L x W.
- Component centre (M37): cross with 0.3 mm arms plus circle radius 0.15 mm.
- Designator (M33): text `.Designator`, 1 mm, below-left of the courtyard.
- Dimensions (M5), rule changed 2026-11-24: the BODY X size above the part and the BODY Y size to the left, 1 mm text (`%.2fmm`), 0.1 mm lines. The extension lines start exactly on the M19 (Top Component Outline) edges, so the dimension is true to M19. Horizontal dimension line at y = cy+0.85, vertical at x = -(cx+0.75); arrow length min(0.5, half body X) / min(0.4, half body Y). Pad dimensions are retired. For a body not centred on the origin (e.g. TO-220AB) draw the extension lines at the real M19 edges.
- Assembly (M35): outline as generated by the tool, 0.1 mm.
- 3D body (M13): STEP model; M9, M15, M25 left empty.
- 2-pin chip passive rule that reproduces the 0603 reference (cx, cy = courtyard half-extents, 0603: 1.45, 0.75; px = pad centre x): overlay centre-line = pad bounding box + 0.15 mm in x and y; designator at (-(cx+0.75), -(cy+1.15)) = (-2.2, -1.9) for the 0603; horizontal dimension line at y = cy+0.85; vertical dimension line at x = -(cx+0.75); dimensions follow the M19 body (see Dimensions (M5)). Implemented in `scripts/tools/fp_house.py`. For ICs use the tool's overlay (0.2 mm corner marks, as on LQFP48) unless the user says otherwise; the 0.15 mm box rule has only been applied to chip passives.
- Vocabulary: "IC" means a chip symbol with 300 mil pins; "2-pin chip passive" means R, C, L in 0201-1206. The word "chip" alone is avoided here.

## Naming
- 2-pin chip passives 0201, 0402, 0603, 0805, 1206: `<TYPE><SIZE>`: `RES0603`, `CAP0402`, `IND0805`. 2512 is still an open question (not a standard MLCC or chip inductor size; the project standard lists it, the README text does not).
- Everything else: package name from the datasheet, e.g. `LQFP48`, `DO-214AA`, `SOT-23-6`.
- Symbol LibRef = MPN.

## Reference values already agreed
| Item | Value |
|---|---|
| 0603 chip pads | 0.80 x 0.95 mm at +/-0.80 mm (1.60 centre span, 0.95 pad height, matches the reference image) |
| LQFP48 lands (ST Figure 56) | 1.2 x 0.3 mm, pitch 0.5, centres +/-4.25 mm |
| STM32F103C8T6 symbol (copied from the user's library, restyled) | part A body (0,-2700)-(1500,600), part B (0,-1000)-(1500,0), read back with `obj_query`; the project log's "2700 / 800" refers to a discarded shell |

## Rules the tools enforce (do not fight them)
- Build from the datasheet: every package needs a source page; use the datasheet's land drawing when it has one.
- Symbol pins are checked against the datasheet pin table. Only the user can switch that check off (Config tab, or `preferences.json` key `checks_off`). Never bypass it.

## Values in mils (for ASCII component files and the importer)
1 mm = 39.3701 mil. File coordinates may carry decimals; give values to 2 decimals unless exact (3 decimals for widths).

| Item | mm | mil |
|---|---|---|
| Overlay line width | 0.2 | 7.874 |
| Mechanical-layer line width | 0.1 | 3.937 |
| Centre-mark cross arm | 0.3 | 11.81 |
| Centre-mark circle radius | 0.15 | 5.91 |
| Designator / dimension text height | 1 | 39.37 |
| Overlay offset from pad bounding box | 0.15 | 5.91 |
| Courtyard rounding step | 0.05 | 1.97 |
| Pad corner radius | 10 % | 10 % (unchanged) |
| 0603 pad size (w x h) | 0.80 x 0.95 | 31.50 x 37.40 |
| 0603 pad centres x | +/-0.80 | +/-31.50 |
| 0603 courtyard | +/-1.45 x +/-0.75 | +/-57.09 x +/-29.53 |
| 0603 overlay centre-line | +/-1.35 x +/-0.625 | +/-53.15 x +/-24.61 |
| 0603 body | 1.6 x 0.8 | 62.99 x 31.50 |
| 0603 M19 outline | +/-0.8 x +/-0.4 | +/-31.50 x +/-15.75 |
| 0603 designator (x, y) | (-2.2, -1.9) | (-86.61, -74.80) |
| 0603 dimension line y | 1.6 | 62.99 |
| LQFP48 pad size (l x w) | 1.2 x 0.3 | 47.24 x 11.81 |
| LQFP48 pad centres | +/-4.25 | +/-167.32 |
| LQFP48 pitch | 0.5 | 19.69 |

Schematic (already mils, no conversion): chip pin length 300, other pin length 100, pin pitch 100, chip body width 1500, pin designator offset 120, pin name offset 50, passive geometry as in "All other symbols" (R body x 130..270, y -25..25; C: see Capacitor above, pins at x=100 and 200 body ends; R pins at x=0 and 400), grid 100, snap 50.

Widths in ASCII files: schematic line width is the Small index `Width 5` (an Altium size code, not mils of drawing width). Footprint line widths are real mils: 7.874 (overlay) and 3.937 (mechanical).

## Footprint names (2026-11-22)
Footprint name = the package name only, never the MPN: `RES0603`, `CAP0603`, `SMB`, `SMA`, `D0008A`, `SOT26`, `LQFP48`. A rename `<package>-<MPN>` was tried and withdrawn by the user.

## Part split rule (2026-11-24)
Part split rule (decided 2026-11-24): split into Part A signals / Part B power ONLY for microcontrollers and microprocessors (many pins, few special-function pins). Analog and interface ICs with several power domains and special-function pins (video decoders, serializers, converters) stay as ONE single-part symbol for clarity. Op-amp triangles stay in the user's library style.

## Diode symbols (2026-11-24)
Diode glyphs (user reference `scratch/Diodes.SchLib`, adopted 2026-11-24; B340A-13-F is the reference): pins 100 mil, pin 2 = anode on the LEFT (body end x=100), pin 1 = cathode on the RIGHT (body end x=400), wire ends x=0 and x=500. Lead lines (100,0)-(200,0) and (300,0)-(400,0). Triangle polygon (200,-50)(300,0)(200,50), SOLID, area colour 15983311 (#CFE5F3), line `#344062` width 1. Cathode bar (300,50)-(300,-50). Variants: generic = bar only; Zener = bar plus hooks (300,50)-(280,70) and (300,-50)-(320,-70); Schottky = bar with square hooks (300,50)-(320,50)-(320,40) and (300,-50)-(280,-50)-(280,-40) (see the library); LED = generic plus two arrows; TVS = two opposed triangles with Zener hooks, pins 1 at x=500. Designator `D?`. Cathode pad is pad 1 on the footprint. The symbol is a polygon (`eSchPolygon`) plus lines: `obj_delete` of old glyphs needs eSchPolygon AND eLine AND ePolyline.

## BJT symbols (2026-11-24, corrected)
General style (reference: the user's `MMBT3906`):
1. A circle around the whole transistor: arc centre (250,0), radius 130, 0-360, width 1.
2. Base pin: body end (100,0) pointing left, length 100 (wire end x=0). Collector and emitter pins: length 80, body ends (roots) at (300,+-120), so the wire ends (hotspots) are at (300,+-200) ON the 100 mil grid (confirmed by the user 2026-11-26 on SUP53P06-20 rev 4; the root being off grid is fine). Base lead (100,0)-(200,0), base bar (200,100)-(200,-100), diagonals (200,20)-(300,120) and (200,-20)-(300,-120), all width 1.
3. PNP: emitter on TOP; arrow on the emitter diagonal pointing DOWN towards the junction (solid triangle (225,45)(235.6,76.8)(256.8,55.6)). NPN: collector on TOP, emitter at the BOTTOM, arrow pointing AWAY from the junction (solid triangle (275,-95)(264.4,-63.2)(243.2,-84.4)).
4. Pins 1 base, 2 emitter, 3 collector (SOT-23 onsemi style 6). Designator `Q?` at (350,80); MPN (350,-300) and DES (350,-370) VISIBLE; Comment hidden.
5. ALL colours are the house `#344062` (6438964): lines, arc, arrow, pins, text.

## MOSFET symbols (2026-11-24, proposed, same style as the BJT)
RULE (user, 2026-11-26): EVERY MOSFET symbol, N-channel or P-channel, draws the body diode between drain and source. P-channel: anode at the drain, cathode at the source. N-channel (mirror of the P-channel drawing): anode at the source, cathode at the drain; keep the channel arrow, pins and hotspots on the 100 mil grid as below, and confirm the N-channel pin positions with the user on the first N-FET. JFETs have no body diode.

P-channel enhancement, drawn inside the BJT circle (arc centre (250,0), r 130). Gate pin 100 mil, body end (100,0) pointing left, lead (100,0)-(150,0), gate plate (150,60)-(150,-60); three channel segments at x=175: (75..45), (15..-15), (-45..-75); source (top) and drain (bottom) pins 80 mil with body ends (roots) at (300,+-120) so the wire ends (hotspots) at (300,+-200) are on the 100 mil grid (SUP53P06-20 rev 4 is the reference); connections (175,+-60)-(300,+-60) and (300,+-60)-(300,+-120); body tie (175,0)-(300,0) and (300,0)-(300,60) with a solid arrow (240,0)(215,12)(215,-12) pointing away from the channel (P-channel; mirror it for N-channel). Source on top, drain at the bottom. BODY DIODE (user edit 2026-11-26, ZXMP3A13F symbol rev 4 / CMP-00475-4 is the reference, picture in the log): a small diode glyph between source and drain on the right of the channel, anode at the drain (bottom), cathode at the source (top), arrow pointing up; pin hotspots unchanged: G (0,0), S (300,+200), D (300,-200) relative to the placed part (read back from the workspace part). Designator `Q?` (350,80), MPN (350,-300), DES (350,-370), house colour, FontId 3 / 4. Pinouts: ZXMP3A13F 1 G, 2 S, 3 D (SOT23); SUP53P06-20 1 G, 2 D, 3 S (TO-220AB). Both built with the "Symbol vs pin table" check OFF (the datasheets print no pin numbers).

Pin numbers on transistors, FETs and 3-pin diodes (user, 2026-11-24; reference CMHZ4705): pin designators VISIBLE (`ShowDesignator` true), `Designator_PositionMode` 1, `Designator_FontMode` 1, `Designator_CustomFontID` 3 (Arial Bold 6), `Designator_CustomPosition_Margin` "250000" (pass it as a STRING; a number fails), `Designator_CustomPosition_RotationAnchor` 0, `Designator_CustomColor` 0. Numbers must read upright: `Designator_CustomPosition_RotationRelative` 1 on vertical pins (Orientation 1 and 3), 0 on horizontal pins (0 and 2). Pin names stay hidden. Set with `obj_modify` (object_type ePin, scope `lib_component:NAME`, `filter` "Orientation=1"). MPN and DES visible (FontId 3, `#344062`), the hidden Comment carries the MPN text; a duplicated `Comment` parameter ("*") may exist on 3-pin parts: set both to the MPN and hide them.

TO-220AB (Vishay 71195 p.6, built 2026-11-24): vertical mount, origin pad 2, pads 2.0 mm / holes 1.4 mm at 2.54 pitch, body 10.28 x 4.45 mm with the leads 0.69 mm towards the front face, M19 box y -1.54..2.91. The tab (drain) has no copper. Tool family `to220` has no 3D model: `lib_create_3d_model` (needs CadQuery, extra `models3d`) with prisms for plastic/tab, cut for the tab hole, `drawing` must give body_x, body_y and height (overall height includes the 3.57 mm shoulder standoff) and only `body`-role solids count towards body_x/body_y.

Chip passive lands (user decision 2026-11-25): RES/CAP 0201-1206 pads are IPC-7351B nominal (density N), never a vendor-specific land pattern, because one footprint serves several vendors.

Three-pin dual series diode (BAV99WT1G, user edit 2026-11-25): two generic diode glyphs in series (pin 1 anode left at body end x=100, pin 2 cathode right at x=600), the common pin 3 on the 100 mil grid at (400,-200) pointing down. The connection is a vertical line from the junction at x=350 (graphically centred between the two glyphs, 50 mil off the grid on purpose) down to y=-200, then a short horizontal line (350,-200)-(400,-200) to the pin root. Wire end of pin 3 is (400,-300).

## Default passive selection (user guideline, 2026-11-27)
When a passive is needed and no MPN is given, pick from these and build/release it in the house style (0603 footprints RES0603 / CAP0603):
- Capacitors: MLCC, 0 to 10 uF, tolerance 1-10 %, 10-50 V, X7R, 0603. (X7R is not made for small values: below about 100 pF use C0G/NP0; above 10 uF in 0603 only X5R exists; flag such exceptions in the description and the log.)
- Resistors: 0 to 1 GOhm, 1 %, 0.1 W to 0.5 W, 100 ppm/degC, 0603.
- Only components built in the house style count as "exists" when checking the workspace: parts released by this skill (CMP-00475 and later, DES parameter in house format, house symbol and footprint). Older colleague parts (CMP-001-..., CMP-009-..., CAP-/RES-/IND-00xxx) are not house style even when the footprint is 0603.
- The old colleague components are to be deleted one day and completely re-modelled by Claude: when a part is needed always create a new house-style component, never reuse an old one (user, 2026-11-27).
