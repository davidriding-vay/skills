# ASCII component file and the Import.pas importer

Derived from reading `scripts/import/Import.pas` (1168 lines), `ImportForm.pas/.dfm`, `Import.PrjScr` and sample
files in `altium-script-test/Components/`. Nothing here was run in Altium during this write-up; items marked
**unverified** need a one-part test import first.

## What the importer does
The copy in `scripts/import/` is PATCHED (layers 17-32, house dark blue, line-width fix); the unpatched file is `Import.pas.orig` and the diff is `Import.patch`. Line numbers below refer to the original and shift by up to about 16 after line 107 in the patched copy.
- Reads one or many `.txt` files and builds a new integrated-library set: `<Libs>\<name>.LibPkg`, `.PcbLib`,
  `.SchLib` (`InitLibDocs`, lines 900-965). `<Libs>` is a folder named `Libs` next to the folder that holds
  the `.txt` files (`Components\` -> `..\Libs\`).
- `ImportAscIIData(file)` (line 967): one file, library named after the file. `ImportAllAscIIData(files, libname)`
  (line 1084): many files into one library; this is what `ImportForm` calls (file picker + library-name box + Import button).
- It creates a brand-new library each run (delete old outputs in `Libs\` first). It deletes the blank default footprint;
  the blank default symbol deletion is marked "looks broken" in the code, so check for a stray `Component_1`.
- It only adds; it never updates an existing library part.
- Altium 19 has a broken schematic FontManager: all texts then use `ForceSchFontID` (line 2) instead of the file's font.
- Launching: **no launch procedure exists in this folder.** `ImportForm.pas` only has `BtnFileClick` and `BtnImportClick`;
  `ImportAscIIData` / `ImportAllAscIIData` take parameters, so Run Script cannot list them. A comment at line 1074 mentions an
  AutoIt routine, so something outside this folder drove the old workflow. Before relying on the importer, add a parameterless
  procedure that shows the form (for example `Procedure RunImport; Begin ImportForm.ShowModal; End;`). `Import.PrjScr` lists
  `Import.pas`, `ImportForm.pas` and a stray `DAC11001APFBR.txt`, but not `ImportForm.dfm`. **Unverified in Altium.**
- The form's library-name box defaults to `Resistors`; an empty name is not validated. `Libs\` is derived from the FIRST
  selected file's folder only (`GetFileLocation`, lines 90-102, uses a first-occurrence text search, so a parent folder whose
  name contains the last folder's name misplaces it).

## File layout
```
# comment lines start with # (inside a footprint block only)
StartFootprints
Footprint (Name "RES0603") (Height 20)
  Pad ... / PadShape ... / EndPad
  Line ... / Arc ... / Polygon ... Point ... EndPolygon / Text ... / Step (Name file.step)
EndFootprint
EndFootprints

StartComponents
Component (Name "<MPN>") (PartCount 1) (DesPrefix "R?")
  Description (Value "...")
  Comment (Value "...")
  Parameter ... / Pin ... / Line ... / Rectangle ... / Arc ... / Polygon ... / Text ... / Footprint (Name "RES0603") (Map "...")
EndComponent
EndComponents
```
Each line is `<Keyword> (Field value) (Field value) ...`. Fields are found by text search, so order does not matter;
spaces inside parentheses matter: `(Location -29.53, 0)`.
**Start every line in column 0 inside a `Component` block**: the symbol loop does not trim, so a leading space makes an empty tag and the
line is silently skipped (lines 801-828, 874); the footprint loops do trim. The indentation in the layout sketch above is for reading only.
`#` comment lines are accepted only inside a footprint block (line 446). In a `Component` block a `#` line raises "Keyword Error", breaks
out, and the component is never added (lines 875-878, 868). Between footprints a `#` line also breaks out (489-492).
Unknown keywords show a "Keyword Error" box; inside `PadShape` and polygon loops the loop continues, inside the footprint and component loops it
stops the block, and at the top level unknown tags are silently ignored (no `Else`). Modal boxes block unattended batches.
All lengths are **mils** (1 mm = 39.3701 mil), decimals allowed. Angles in degrees.

## Footprint keywords (`FP_*`, lines 200-497)
| Keyword | Fields |
|---|---|
| `Footprint` | `(Name "x")`, optional `(Height mils)` |
| `Pad` | `(Name "1") (Location x, y) (Rotation deg) (Surface True|False) (HoleSize mils) (Plated True|False) (ExpandPaste mils) (ExpandMask mils)` then one or more `PadShape` lines, then `EndPad`. `Surface True` = simple SMD pad on TopLayer; otherwise a local stack (through-hole). Paste/mask expansion become manual values when present |
| `PadShape` | `(Size x, y) (Shape NoShape|Rounded|Rectangular|Octagonal|CircleShape|ArcShape|Terminator|RoundedRectangle|RotatedRectangle) (Layer Top|Mid|Bot...)` - the first 3 letters of the layer choose Top/Mid/Bottom |
| `Line` | `(Width mils) (Start x, y) (End x, y) (Layer <name>)` -> track |
| `Arc` | `(Location x, y) (Radius) (Width) (StartAngle) (EndAngle) (Layer)`; 0..360 is a circle |
| `Polygon` | `(Layer) (PointCount n) (Type KeepOut)` then `Point (x, y)` lines then `EndPolygon` -> region |
| `Text` | `(Location x, y) (Layer) (Height mils) (Width mils) (Rotation) (Mirrored True) (Value "text")` (justification is a TODO in the code) |
| `Step` | `(Name file.step)` - STEP file looked up in the same folder as the `.txt`; added as a component body |
Layer names accepted (`LayerFromString`, lines 108-197): TopLayer, BottomLayer, MidLayer1-30, TopOverlay, BottomOverlay,
TopPaste, BottomPaste, TopSolder, BottomSolder, InternalPlane1-16, KeepOutLayer, **Mechanical1-Mechanical32** (17-32 added by the patch),
MultiLayer and a few system layers. Any other name silently becomes NoLayer.

## Symbol keywords (`SY_*`, lines 502-894)
| Keyword | Fields |
|---|---|
| `Component` | `(Name "<LibRef>") (PartCount n) (DesPrefix "R?")`; description defaults to "Imported" |
| `Description` | `(Value "text")` |
| `Comment` | `(Value "text")` (sets the Comment text; the richer `SY_AddComment` is disabled because it crashes Altium 16) |
| `Parameter` | `(Name "MPN") (Location x, y) (Height 60) (Rotation 0|90|180|270) (Justification TopCenter...) (Visible True) (Font "Arial") (Bold True) (Italic False) (Underline False) (Value "...") (Part n)`; hidden unless `Visible True`. `Height 60` means font size 6 (height x 0.1) |
| `Pin` | `(Location x, y) (Rotation 0|90|180|270) (PinType IO|Input|Output|Passive|Power|OpenCollector|OpenEmitter|HiZ) (Length mils) (Designator Visible|Hidden "1") (Name Visible|Hidden "NRST") (PinSwap) (PartSwap) (PinSeq) (Part n)`. **`Bidirectional` is unknown and becomes Passive; use `IO`** |
| `Line` | `(Width n) (Start x, y) (End x, y) (Part n)` |
| `Rectangle` | `(Start x, y) (End x, y) (Width n) (FillColor BBGGRR hex) (Part n)`; with FillColor the rectangle is solid, without it is transparent. FillColor is parsed with `StrToInt('$' + value)` so it is Altium BGR: house body 204,204,255 -> `FFCCCC` |
| `Arc` | `(Location x, y) (Radius) (Width) (StartAngle) (EndAngle) (Part n)` |
| `Polygon` | `(PointCount n) (Part n)` then `Point (x, y)` lines then `EndPolygon` (solid, zero-size border) |
| `Text` | like Parameter but a label |
| `Footprint` | `(Name "RES0603") (Map "...")` - adds a PcbLib footprint link by name |
Line widths: `Width` < 10 -> Small, > 10 -> Medium, > 12 -> Large; exactly 10 leaves Altium's default. The compare is string against number
(**unverified** in DelphiScript), and `SY_AddLine` used to discard the width it read (fixed in the patched copy: it now reads the width and compares it as a number). Use `Width 5` for Small as
the samples do and read `LineWidth` back after import. Multi-part: set `PartCount` and tag each item `(Part n)`; shared part-0 pins are not implemented.
Symbol `Polygon` has no colour field: it sets `Color := $000000` (line 666) and `IsSolid := True`, so expect a black fill; avoid it, or recolour after import.
`Mirrored` is supported on Parameter and Text (and footprint Text). `Height` is searched without a leading `(`, so the first occurrence on the line wins.
The Pin `(Width 0)` field is never read. A pin `Designator` or `Name` containing `")` breaks the parse (lines 781-786).

## Worked examples (syntax from the working sample files)
2-pin chip footprint and the symbol that links to it (old-style values, only to show the syntax):
```
StartFootprints
Footprint (Name "C0603")
Pad (Name "1") (Location -29.53, 0) (Surface True) (Rotation 0) (ExpandMask 0) (ExpandPaste 0)
PadShape (Size 29.53, 39.37) (Shape Rectangular) (Layer Top)
EndPad
Pad (Name "2") (Location 29.53, 0) (Surface True) (Rotation 0) (ExpandMask 0) (ExpandPaste 0)
PadShape (Size 29.53, 39.37) (Shape Rectangular) (Layer Top)
EndPad
Line (Width 5) (Start -11.81, 23.62) (End 11.81, 23.62) (Layer TopOverlay)
Arc (Location 0, 0) (Radius 9.84) (Width 2) (StartAngle 0) (EndAngle 360) (Layer Mechanical15)
EndFootprint
EndFootprints
StartComponents
Component (Name "C0603C101F5GACTU") (PartCount 1) (DesPrefix "C?")
Description (Value "CAP - 100pF 50V 1% C0G - 0603")
Comment (Value "100pF")
Parameter (Name "MPN") (Location 0, -78.74) (Height 60) (Rotation 0) (Justification TopCenter) (Visible True) (Font "Arial") (Bold True) (Italic False) (Underline False) (Value "C0603C101F5GACTU") (Part 1)
Pin (Location -137.80, 0) (Rotation 0) (PinType Passive) (Length 118.11) (Width 0) (Designator Hidden "1") (Name Hidden "~") (PinSwap 0) (PartSwap 0) (PinSeq 1) (Part 1)
Pin (Location 137.80, 0) (Rotation 180) (PinType Passive) (Length 118.11) (Width 0) (Designator Hidden "2") (Name Hidden "~") (PinSwap 0) (PartSwap 0) (PinSeq 2) (Part 1)
Line (Width 5) (Start -19.69, -59.06) (End -19.69, 59.06) (Part 1)
Line (Width 5) (Start 19.69, -59.06) (End 19.69, 59.06) (Part 1)
Footprint (Name "C0603")
EndComponent
EndComponents
```
IC body and pins (grammar-derived with house values; no sample file contains a Rectangle or an IC, so this is **untested**), for a body spanning x 0..1500, using the
importer's convention seen in the samples (Location = OUTER end, Rotation points toward the body):
```
Rectangle (Start 0, -2700) (End 1500, 600) (Width 5) (FillColor FFCCCC) (Part 1)
Pin (Location -300, 300) (Rotation 0) (PinType IO) (Length 300) (Width 0) (Designator Visible "7") (Name Visible "NRST") (PinSwap 0) (PartSwap 0) (PinSeq 7) (Part 1)
Pin (Location 1800, 0) (Rotation 180) (PinType IO) (Length 300) (Width 0) (Designator Visible "18") (Name Visible "PB0") (PinSwap 0) (PartSwap 0) (PinSeq 18) (Part 1)
```
**Pin location caution (unverified):** in the working samples a left pin has `Location` at the OUTER end (-137.80) with `Rotation 0` and length 118.11, ending at the
plate (-19.69); the right pin is at 137.80 with `Rotation 180`. The eda-agent MCP tools use the opposite convention (Location at the body end, rotation pointing away
from the body). Import one test part and read the pin back (`obj_query ePin ... ConnectionX`) before bulk generation.

## Other importer behaviour to know
- SMD pads (`Surface True`) are always TopLayer (line 348); there are no bottom-side SMD pads. The hole is always round; `HoleSize` is evaluated even for SMD pads. `Plated` is set only when present.
- Any non-empty `ExpandPaste` / `ExpandMask` (even 0) switches that expansion to a manual value, overriding the design rule.
- `Step (Name file.step)`: write the name unquoted. The file is looked up beside the `.txt` (line 206 adds a doubled backslash). It is most likely linked, not embedded (second argument of `ModelFactory_FromFilename`, **unconfirmed**).
- Many files that each define the same footprint name (all the sample capacitors define `C0603`) register it again with no de-duplication; behaviour in Altium is unknown. Prefer one shared footprint block per library.
- `Comment` sets only the text; visibility and position are untouched. `BrokenSCHFontManager` is never reset between runs.
- Not determined: whether `Evaluate('')` is harmless for omitted fields, whether layer names are case-sensitive, what happens when output files already exist.

## Gaps against the Rearguard house standard
| House rule | Importer today | Fix |
|---|---|---|
| Mechanical layers M5, M19, M25, M27, M33, M35, M37 (and M17+) | **Patched** in `scripts/import/Import.pas`: `LayerFromString` now parses `MechanicalNN` for NN 17-32 via `LayerUtils.MechanicalLayer(NN)` (see `Import.patch`; untested in Altium). Mechanical1-16 behave as before | in the new PcbLib enable and name the layers with `lib_set_mech_layers` so they are visible |
| Layer names, kinds, top/bottom pairs | not set (the new PcbLib has defaults) | run `lib_set_mech_layers` once on the output library (see mcp-workflow) |
| Pad shape roundrect with 10% corners | `RoundedRectangle` is accepted but no corner radius is set (`FP_AddPad` 367-396) | `lib_set_pad_properties corner_radius_pct 10` after import, or add the property in `FP_AddPad` |
| 3D body on M13 | `Step` adds the body but sets no layer (`FP_AddStep` 200-214) | `lib_move_bodies_to_layer Mechanical13` after import |
| Dark blue `#344062` on lines, rectangle border, arcs, text, parameters, pins, polygons | **Patched**: the nine hard-coded `$000000` assignments now use `HouseBlue = $624034` (BGR of #344062 = 6438964). `Import.patch` shows each line. Untested in Altium | read colours back after the first import |
| Body border line width Small (1) | rectangle width bands as above | use `Width 5`; read back `LineWidth` |
| Body fill 204,204,255 | supported via `(FillColor FFCCCC)` | none |
| Parameter font Arial Bold 6 | supported: `(Height 60) (Font "Arial") (Bold True)`; colour black (above) | colour fix |
| Hidden `Comment` = MPN and only DES, MPN visible | `Comment` supported; extra `Parameter`s are written as given | write only `MPN` and `DES` visible, no Manufacturer/Datasheet parameters |
| Designator Arial Bold 8, `#344062`, position | only `Designator.Text` (the prefix) is set | restyle after import with `obj_modify eDesignator` |
| Pin colour, pin name/designator font and offsets (120/50 mil) | not settable (`ISch_Pin` has no font property); library defaults apply | check after import; set pin colour with `obj_modify ePin Color=6438964` |
| Footprint overlay 0.2 mm, mechanical lines 0.1 mm | widths are taken from `(Width n)` in mils: exact values 0.2 mm = 7.874, 0.1 mm = 3.937 (decimals are accepted) | write those widths in the file |
| Chips 300 mil pins, other parts 100 mil | `Length` is free | write 300 / 100 |
| Naming, uppercase DES | free text | generator must follow `house-standard.md` |

## Superseded by the Rearguard standard (old project notes)
- 1 mm metric grid, 5 mm (196.85 mil) pins, 3 mm (118.11 mil) pin pitch, body +/-10 mm and +/-8 mm, pin tips +/-15 mm: replaced by
  100 mil grid, 300 mil chip pins (100 mil others), 100 mil pitch, 1500 mil body.
- `RESISTOR_SPEC.md`: black lines, light-grey `#D3D3D3` body, 3 mm pins, DES format `RES - 100R 0.25W 1% - 0603`,
  courtyard on Mechanical15, assembly on Mechanical13: replaced by white body, 100 mil pins, uppercase hyphenated DES,
  courtyard M27, assembly M35, 3D body M13.
- Old DES format `CAP - 100pF 50V 1% C0G - 0603`: replaced by `CAP-100PF-50V-1%-C0G-0603`.
- Old generator prompts live in `scripts/import/commands/` (capacitor, resistor, chip) and still describe the old geometry; do not reuse their numbers.
