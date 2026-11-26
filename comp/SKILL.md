---
name: comp
description: Create, regenerate or fix a component for the Rearguard house libraries - a schematic symbol (SchLib) and a PCB footprint (PcbLib) built to the house standard (colours, 100/300 mil pins, parameters, mechanical layers M5-M38, overlay and line widths, IPC-7351 lands, naming), live through the eda-agent MCP tools (the only method; Import.pas is retired). Use when the user gives an MPN or datasheet and asks for a symbol, footprint or "component", asks to check or restyle an existing library part against the house standard, or asks about the project-template README text. Read reference/house-standard.md first; reference/mcp-workflow.md for the workflow.
user-invocable: true
---

# comp - house-standard components

Goal: every symbol and footprint that leaves this workflow looks and behaves the same, comes from the
manufacturer datasheet, and imports into Altium without hand fixing.

## Non-negotiables
- **Datasheet first.** Fetch the manufacturer PDF (plain `curl`; if blocked, ask the user to drop it in
  `scratch/ds*/`), read the pin table, package dimensions and land-pattern page, and cite page numbers.
  Library Comment/Description/Value, distributor pages and memory are only hints to find the datasheet.
- **House standard is the spec.** `reference/house-standard.md`. Where an older note disagrees (1 mm grid,
  5 mm pins, 3 mm pitch, `#073763`, light-grey resistor fill) the house standard wins.
- **Chips 300 mil pins; everything else (R, C, L, diodes, transistors, connectors) 100 mil.**
- **Work in scratch libraries.** Never write into `libs/` (or any production library) until the user approves.
- **Release file names carry a timestamp**: `sch-dd-mm-yy-HH-MM.SchLib` and `pcb-dd-mm-yy-HH-MM.PcbLib` (24 h local time, get it with `date +%d-%m-%y-%H-%M`); each release is a NEW file, never an overwrite. Scratch work files keep fixed names. The same names are used in every project.
- **Footprint name = package name only** (`SMB`, `SOT26`, `D0008A`, `CP-32-12`, `T3255Y-8`, `IND1028`, `RES0603`); never add the MPN.
- **Capacitor symbols copy the user's reference layout** (`C0603C104K5RACTU`, see house-standard.md); copy it with `lib_copy_component` in the same library, then set MPN/Comment/DES/description/footprint.
- **Never bypass a tool check** (pin table, footprint vs drawing). If a check blocks you, say what differs and
  let the user decide; only the user switches checks off.
- **Verify by reading back.** Colours, positions and font ids written with `obj_modify` must be queried back.
- **Be honest about unverified items** (values taken from a part-number code, assumed 3D standoff, etc.).

## Choose the route
| Situation | Route |
|---|---|
| One part, a fix, or a restyle of an existing symbol/footprint | MCP tools: `reference/mcp-workflow.md` |
| A batch of parts, any size | The same MCP route, one part at a time (copy a template symbol for similar passives). Import.pas / ASCII files are NOT used (user decision 2026-11-24) |
| Package family supported by the footprint tool (2-pin chip, QFP, SOIC, QFN, ...) | `lib_create_footprint_from_package`, then house fixes |
| Datasheet draws its own land pattern | custom pads + `footprint_compare_drawing` (see workflow) |

## Steps
1. Identify the part: MPN exact (orderable), package, datasheet URL/PDF. Ask if the MPN is ambiguous.
2. Download and read the datasheet. Record: pin table (per package column), package dims `[min, nom, max]`,
   land-pattern page or "none".
3. Decide the symbol type: IC (300 mil pins, 1500 mil body, `#CFE5F3`) or other (100 mil pins, existing glyph style).
   Group IC pins by function, Part A signals / Part B power.
4. Build the footprint, apply the house layer rules, check and render it (`scripts/tools/fp_house.py` for 2-pin chip passives).
5. Build the symbol, set `MPN` and uppercase `DES`, the component Comment (`obj_modify` eSchComponent `Comment.Text`) = the MPN, kept hidden (it fills the symbol's Name field in Altium 365 and cannot be changed after upload), description; link the footprint.
6. Run `lib_check_schlib` / `lib_check_pcblib`, read back styles, save only the scratch files.
7. Log the work in the project's `HOUSE_STANDARD.md` (built, verified values with sources, open points).
8. Upload to Altium 365 through Nexar, automatically, when `altium365_check_setup` is ok: publish the symbol and footprint into `Components/Models/Symbols` / `Footprints` and release the component as the next `CMP-NNNNN` in the best-matching `Components/...` folder (e.g. a MOSFET goes to `Transistors`), parameters MPN and DES only. Follow `reference/altium365-upload.md` exactly (duplicate checks first; nothing can be deleted afterwards).

## Files
- `reference/house-standard.md` - the full standard (colours, symbols, parameters, layers, rules, naming).
- `reference/mcp-workflow.md` - tool recipes, order of operations, gotchas and faults.
- `reference/altium365-upload.md` - the automatic Altium 365 upload (Nexar): checks, order, folder choice table, pitfalls.
- `reference/ascii-format.md` - RETIRED: Import.pas and the ASCII format are not used (kept for history only).
- `reference/readme-textbox.txt` - current text for the project-template README text frame (edit it when the standard changes, and keep blank lines between groups so it reads in an Altium text box).
- `scripts/import/` - RETIRED, do not run. Contents: `Import.pas` (PATCHED: layers Mechanical17-32, house dark blue `$624034` on all schematic objects, line-width fix; original kept as `Import.pas.orig`, diff in `Import.patch`; untested in Altium), `ImportForm.*`, `Import.PrjScr`, and the old generator prompts in `commands/` (they still describe the superseded mm geometry). Write ASCII files in mils using `reference/house-standard.md`, section "Values in mils".
- `scripts/tools/` (run with plain `python3`, not `-I`; PyMuPDF is in the user site packages):
  - `extract.py <pdf> <out.txt>` - PDF to text with `=====PAGE n=====` markers.
  - `fp_house.py <sizes.json> <out.json>` - house-layer primitives for 2-pad chip footprints. Input is a JSON ARRAY of
    `{"name","px","pl","ph","cx","cy","bl","bw"}` in mm: px = pad centre x, pl = pad length, ph = pad height,
    cx/cy = IPC courtyard half-sizes, bl/bw = body length and width (see `fps_res.json`). Output is a list of
    `{name, cx, cy, tracks[{x1,y1,x2,y2,width,layer}], texts[{text,x,y,size,layer[,rotation]}]}` in mm, ready to paste
    into `lib_add_footprint_tracks` / `lib_add_footprint_text` (pass `units: "mm"`). It reproduces the house 0603.
  - `symp.py [out.json]` - EXAMPLE ONLY: pin-item list for one 48-pin STM32 (shape of `lib_add_pins` items: mil,
    length 300, pitch 100, x 0/1500, rotations 180/0, types io/input/output/power). It is not a generic generator and
    its layout is not the final STM32 symbol.

## When the standard changes
Update `reference/house-standard.md`, the project `HOUSE_STANDARD.md` and `reference/readme-textbox.txt`
together, and say so in the log. Existing parts are not silently changed.

## Getting blocked datasheets (curl; no sub-agents for web fetching)
Many vendor sites time out or 403 from WSL. Try in this order, and check `head -c4` is `%PDF`:
1. Plain `curl -sL --http1.1 -A "<browser UA>"`; analog.com times out entirely.
2. LCSC: fetch `https://www.lcsc.com/product-detail/<Cxxxx>.html` (find the C-number with WebSearch), grep it for `datasheet.lcsc.com/datasheet/pdf/<hash>.pdf`, then curl that with `-e https://www.lcsc.com/` (this gave MAX96717 and ADV7280).
3. ADI/Maxim package outline and land pattern drawings: `https://mds.analog.com/api/public/content/tqfn_<doc-number>.pdf` (e.g. 21-100156 outline, 90-100067 land pattern); pick the package-family prefix that matches.
4. Mirrors found by WebSearch (ariat-tech.com/datasheet/..., oemstron, pneda). we-online.com returns 403; the WE-TPC catalogue on media.digikey.com has no land pattern, the single-part PDF does.
5. mouser.com / octopart / digikey / alldatasheet return bot pages (13 KB HTML or 403): do not bother.
Save into the project's `scratch/ds-*/` folder, then ask the user only if all of these fail.

## Route notes learned 2026-11-22
- `lib_create_ic_symbol` / `lib_create_symbol_in_parts` check pins against the datasheet text; a pin table that groups pins ("23, 24, 25 AIN4 to AIN8") fails the check. Do not bypass: copy the user's own symbol with `lib_copy_component` (user chose this route), verify pin numbers/names against the datasheet table, then restyle (rectangle 0..1500, fill 15983311, line/pins/params 6438964, pin types per datasheet, DES uppercase).
- Custom footprint: `footprint_compare_drawing` (package with `custom_pads`, `drawing_numbers`, `drawing_dims`, region) returns `compared`; put `"compared"` INSIDE the `package` dict in `lib_create_footprint_from_package` together with the same `drawing_dims`. Custom family (and families the tool does not model, e.g. to220) builds no 3D model: build it with `lib_create_3d_model` (CadQuery is installed; this is THE route, no more throwaway TMP footprints). Focus the PcbLib first. Give `footprint_name`, `source`, `drawing` {body_x, body_y, height as printed, [min,max] or [0,max]} and `solids` read off the datasheet drawing: boxes, extrudes, prisms (ALWAYS set `axis` "x" or "y"), cylinders, `cut` solids with `cut_from`, `dot`/`text` marks, roles body/metal/nickel/tin/ink. Model every visible detail (leads with shoulders, tab and hole, chamfers, pin-1 mark), not a box. Read the `review` PNG, then `lib_move_bodies_to_layer ["<fp>"] Mechanical13` (leave the Height field at 0; do not run `lib_update_footprint_heights_from_3d`). Fall back to the TMP-footprint + `lib_link_3d_model` trick only if CadQuery fails.
- After a tool-built footprint: delete M27 tracks (0.05 wide) and the M35 `.Designator` text with `lib_delete_footprint_primitives` (object_type track/text, layer, confirm), re-add M27 at 0.1 mm, M19 body outline, M37 centre cross, M5 dimensions, `.Designator` on M33, set every pad to 10% corners (`lib_set_pad_properties` with `footprint_name`, `corner_radius_pct` and `items:[{pad_name}]`; the reply is long for QFNs).
- Tool signatures: `lib_add_footprint_tracks(footprint_name, tracks, units)`; `lib_add_footprint_text(component_name, library_path, items, units)`; `lib_link_footprint(component_name, footprint_name, footprint_library)`; `lib_link_3d_model(component_name, model_path, rotation_z)`; `lib_move_bodies_to_layer(footprint_names, layer)`; `lib_rename_footprint`; `obj_modify` items use `set` (not properties) with `scope: "lib_component:<name>"`, pin type via `Electrical` (`io`, `power`, `output`, `input`, `passive`); `obj_delete` of library parameters fails.
- Pin 1 orientation for datasheet pad layouts that do not number pins: use the datasheet's top-view pin diagram and state the assumption.
- Fonts: a symbol made with `lib_create_symbol` + `lib_batch_set_params` gets the default font for new MPN/DES parameters, not the house one. Always set `FontId` through `obj_modify`: MPN and DES `FontId 3` (Arial Bold 6, check with `obj_get_font_spec`), designator `FontId 4` (Arial Bold 8), colour 6438964, then read back with `obj_query ... properties [FontId, Color]`.
