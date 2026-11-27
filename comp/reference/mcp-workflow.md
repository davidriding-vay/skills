# Building components through the eda-agent MCP tools

Use this route for one-off parts or fixes. For batches from datasheet data, the ASCII importer
(`reference/ascii-format.md`, `scripts/import/`) is the alternative. Either way the result must
match `reference/house-standard.md`.

## Before touching Altium
1. Datasheet first. Download the manufacturer PDF into `<project>/scratch/ds*/` with plain `curl`
   (no spoofed user agent; if a site returns 403, ask the user to drop the PDF there). Extract text with
   `python3 ~/.claude/skills/comp/scripts/tools/extract.py <pdf> <out.txt>` run from outside the download folder
   (PyMuPDF; run without `-I`). WSL has no `pdftotext` or `jq`, and `/tmp` is wiped when WSL restarts.
2. Read the pin table, package drawing and land-pattern figure. Cite page numbers. Never use
   Comment/Description/Value from a library, distributor pages or memory as a source.
3. Work in a fresh scratch pair of libraries in `scratch/` (created with `app_create_document`). The workspace is the source of truth; there are no project libraries (`libs/`) to write to.
4. Check what is in front: `app_get_active_document`. A tool given a `library_path` of a file that is not
   open can silently act on whatever library is in front (it once ran on a project library instead, read-only).
   Open files with `app_set_active_document`.
5. Length units: `length_units` is per session and defaults to mil. A length with no unit in its name is read in the
   session unit, whatever the tool description says (1.6 became 0.04064 mm in a mil session). Set mm for footprint
   work and mil for schematic work, and after ANY switch read one coordinate back to confirm. The
   `lib_add_footprint_*` writers default to mil: pass `units: "mm"`.

## New library files
`app_create_document` kind `SCHLIB` / `PCBLIB`, `add_to_project: false` (keeps the project file clean).
Delete the default `Component_1` / `PCBComponent_1` it ships with. Set the mechanical layer scheme
once with `lib_set_mech_layers` (names, kinds, pairs; see the layer table in the standard).

## Footprint recipe (2-pin chip passives and other packages)
1. `footprint_check_package` with the PackageSpec (family chip, qfp, soic, ...; dims as `[min, nom, max]`;
   `source` {document, revision, page, ref, path}). Chip fields: `body_x`, `body_y`, `lead_span_x` (L),
   `lead_length` (B), `lead_width` (W), `height` (T). QFP adds `pins`, `pitch`, `lead_span_y`, and `vendor`
   {pad_length, pad_width, pitch, span, span_y, cite}. `span` is pad centre to pad centre
   (outer extent - pad length). If the datasheet has a land page, `source.page` must be that page;
   if it has none (or only refers elsewhere) say "no land pattern for this package" in `source.ref`.
2. Datasheet drawn land pattern: render it (`datasheet_view_page`; needs `pypdfium2` in the eda-agent
   Python), build `family: custom` with `custom_pads` plus `drawing_numbers` and `drawing_dims`, run
   `footprint_compare_drawing`, read the picture, pass its `compared` id to the create call. The custom family
   builds no 3D model: link an existing STEP with `lib_link_3d_model`.
3. `lib_create_footprint_from_package` with `assembly_layer` Mechanical35, `courtyard_layer` Mechanical27,
   `drafting {"silk_width": 0.2}`, `model_3d: auto`. Four resistor footprints went through in one `items` call, but
   a five-capacitor call and then a single capacitor both crashed Altium at the pad step (access violation in
   `ScriptingSystem.DLL`). Build ONE footprint per call, and after a crash restart Altium before retrying.
4. House fixes after creation (all verified with `lib_get_footprint_primitives`):
   - `lib_move_bodies_to_layer` Mechanical13 (the STEP lands on Mechanical1).
   - `lib_delete_footprint_primitives` (always give `object_type` AND `layer`, `confirm: true`): tracks on
     Mechanical27 (0.05 mm default), text on Mechanical35 (designator belongs on M33), TopOverlay tracks on
     0805 and bigger (the tool draws two silk lines that clash with the house box).
   - Draw the house layers: `scripts/tools/fp_house.py` prints track and text items for chips from a size
     list (`fps_res.json` shows the format). `lib_add_footprint_tracks` takes ONE footprint per call (no
     `items`); arc, text, delete and pad tools do take `items`.
   - Pad corners 10%: `lib_set_pad_properties` with `footprint_name` + `pad_name`, `shape roundrect`,
     `corner_radius_pct 10`.
   - Text boxes: Altium anchors text with ~0.54 mm below and ~1.2 mm above the anchor for 1 mm text, so
     dimension text needs anchor y = line y + 0.8 or more. Check boxes in `lib_get_footprint_primitives`.
5. `lib_check_pcblib`, `lib_render_footprint` (look at the PNG; its text rotation is not reliable), then
   `app_save_document <path>`.

## Symbol recipe
- ICs: `lib_create_symbol` (parts), `lib_add_symbol_rectangle` (body BEFORE pins; fill 15983311,
  border 6438964, `line_width 1`), `lib_add_pins` (left x=0 rotation 180, right x=width rotation 0, length 300,
  type `io`/`input`/`output`/`power`, `owner_part_id`). `lib_add_pins` is refused unless the pin table check
  passes against the datasheet page (it cannot parse some tables such as ST's multi-line Table 5); only the user
  can switch that check off. Alternative the user may approve: `lib_copy_component` from a symbol already in
  their library, then restyle.
- Other parts: `lib_create_passive_symbol` (resistor, capacitor, inductor, diode, ...), then conform to the
  100 mil style with `obj_modify` (rectangle, polylines via `obj_create`, pin colour, designator position and
  font). Make one finished template and `lib_copy_component` it for siblings; only parameters change.
- Parameters: `lib_batch_set_params` sets the component fields `Designator` and `Description`, the `Comment`, and
  creates the hidden parameters `MPN` and `DES`; then `obj_modify` eParameter
  `IsHidden=false|FontId=3|Color=6438964|Location.X|Location.Y` for MPN and DES only (Comment stays hidden). Only
  DES, MPN and Comment may exist as parameters.
- Link: `lib_link_footprint` binds by NAME and checks pin/pad parity against whichever open PcbLib has that
  name first. Keep names unambiguous or close the other library.
- ALWAYS read colours and positions back (`obj_query`): `obj_modify` once reported `matched 1` and did not
  write the body fill.
- `lib_check_schlib`, then `app_save_document`.

## Faults and what to do
| Symptom | Cause / action |
|---|---|
| `ALTIUM_TIMEOUT`, "polling loop not running" | `app_recover_script` restarts the bridge; then retry |
| Modal "Information ... Send and Close" (access violation in ScriptingSystem.DLL) | Altium bug; do NOT press "Send and Close" (sends a report). Close with the X / "Close"; restart Altium if it repeats; save nothing partial |
| "Trying to Reconnect to Notification Service" toast | harmless |
| `lib_add_pins`: "give datasheet" or "no column headed ..." | pin-table check; see above, never bypass. The user can switch it off themselves (Config tab of the "EDA Agent MCP" window, or by creating `workspace/preferences.json` with `{"checks_off": "symbol_pins"}`); the agent never writes that file |
| Footprint created but "incomplete" (pads missing after a crash) | restart Altium, delete the incomplete footprint with `lib_delete_footprint`, never save that library first, rebuild one footprint alone |
| Parallel calls | one Altium: keep writes to one library serial (each footprint tool switches the current footprint) |

## Finish
Update the project's `HOUSE_STANDARD.md` progress log (what was built, values verified, open points), and
tell the user what was changed and what is still unverified. Do not commit scratch libraries or PDFs unless asked.

## Quirks learned 2026-11-24
- `lib_add_footprint_tracks` takes ONE footprint per call (`footprint_name`, `tracks`, `units`); `lib_add_footprint_text` takes `component_name`, `library_path`, `items`, `units`. `length_units` takes `to`, `datasheet_view_page` takes `path` (Windows path), `app_set_active_document` takes `file_path`.
- `lib_link_footprint` needs the SchLib focused (`app_set_active_document` first); `lib_add_footprint_tracks`/text need the PcbLib focused or `library_path`.
- `obj_modify` pin property `Designator_CustomPosition_Margin` only accepts a string ("250000").
- A footprint family without a model (to220) builds no STEP; use `lib_create_3d_model`, which needs CadQuery installed in the eda-agent environment (`pip install -e ".[models3d]"`, then `/mcp` reconnect).
- Tab/metal solids do not count towards the `drawing` body_x/body_y check; only role `body` does.
- `lib_create_3d_model` prisms: always give `axis` explicitly ("y": profile (x,z) over y0..y1; "x": profile (y,z) over x0..x1); without it CadQuery fails with `BRepSweep_Translation`. A `cut` solid needs `cut_from` and the same axis. The PcbLib must be the focused document. TO-220AB built this way (plastic, tab with hole, stepped leads, pin-1 dot); then `lib_move_bodies_to_layer` Mechanical13 and `lib_update_footprint_heights_from_3d`.
- 3D model builds with many leads: define one lead in `groups` and place it with `instance` {group, rot (about z, 0/90/180/270), dx, dy}; `ink`/`laser` roles are for `dot`/`text` marks only (use `white` for a cathode band box); a dot must sit >= 0.02 mm inside the face it marks. `lib_update_footprint_heights_from_3d` takes mode `raise` or `match`.
- Adding graphics to one part of a multi-part symbol: `lib_set_current_component(component_name, part=N)` first, then `lib_add_symbol_lines` (line items accept color, width). Check each part against the others (LMH6643MA part B once missed the V+/V- stubs).
- Recolouring symbols to the house colour: `obj_modify` takes ONE object_type per item (no lists); use `filter` "Color!=6438964" with `set` {"Color":6438964}, scope `lib_component:NAME` (and `NAME@2` for part 2), over eLine, ePolyline, sch_polygon, sch_arc, eRectangle, ePin; fills (AreaColor) are separate.
- Verify pad positions against land patterns by checking what each printed dimension spans (centre-to-centre, gap or outer): IND1028 was once built with the 7.2 gap read as a centre distance.

## Altium 365 (Nexar route), learned 2026-11-25 with ZXMP3A13F
- Flow that worked: one-part SchLib and PcbLib files (never upload a whole library: `lib_save_footprint_library` for the footprint; for the symbol `app_create_document` SCHLIB with add_to_project false, `lib_copy_component`, `lib_delete_component` the default Component_1, save) -> `altium365_publish_library_file` kind symbol / footprint into Components/Models/Symbols and /Footprints (preview first, then confirm) -> `altium365_release_component` with componentParentFolderId (folder id from `altium365_list_library_folders`, e.g. Components/Transistors), componentItemName, componentComment/Description, parameters [{name,value}] (do NOT pass `type`: it is an unquoted enum and the tool quotes it), symbol {id}, footprints [{id}] (revision ids returned by the publish).
- Item names are unique across symbols, footprints and components (HRID): a component named like its symbol fails with AddALU_ItemsDuplicate. Components are named CMP-NNNNN (the number is the item name, the component reads back as CMP-NNNNN-1). To find the next number, read all component names with `altium365_run_query` `desLibrary(workspaceUrl:..){components(first:2300){nodes{name}}}` and take max+1 (CMP-00474 was the last on 2026-11-25; the plain list_components tool shows only 10).
- No tool or API call deletes a symbol, footprint or component: delete by hand in Explorer. A published item cannot be renamed by the tools.
- eda-agent bug fixed locally (2026-11-25, uncommitted in the clone): `desCreateFootprint` returns `footprintId`, not `id`; patched in `altium365.py` (`publish_operation`) and `tools/altium365.py`.
- Nexar terms: data returned by the API may not be kept more than 24 h; large replies are saved by the harness under the session's tool-results folder, delete them afterwards.
- NEVER run `lib_update_footprint_heights_from_3d` (it acts on every footprint in the library; the user keeps all Height fields at 0 and relies on the STEP model). Save single documents with `app_save_document`, not `app_save_all`, when an unwanted change sits in memory.

## Swapping a placed managed part for another component (2026-11-27)
The API cannot rewrite ItemGUID/RevisionGUID and Update From Libraries only moves to the latest revision of the SAME item (and runs project-wide). To point a sheet at a new CMP-NNNNN: rename the old designator (`OLD_R1`), `sch_place_vault_components` the new part at the same x/y/rotation with the real designator (`part_id` for multipart), `sch_mirror_component` if the old one was mirrored, compare pin ConnectionX/Y old vs new, `obj_delete` filter `Designator~OLD_*`, hide Comment, save each sheet with `app_save_document`. `sch_reload_document` saves before reloading: it is not an undo.

## Never fan out Altium work (2026-11-27)
One Altium instance serves every MCP call. Running ~15 sub-agents against it at once crashed it (modal "Access violation in ADVPCB.DLL", only button "Send and Close"), made calls act on another worker's focused library, and left the bridge dead for hours. Fan out only the research (datasheet download, reading pin tables and land patterns into a JSON spec per part, curl and Python only); build, upload and release serially in ONE agent or in the main session. Reserve CMP numbers up front only if nothing else is releasing in parallel.

## Throttling and crash policy for Altium (2026-11-27, user instruction)
Altium is unstable under load, so drive it slowly and one user at a time:
- `python3 scripts/tools/pace.py 4` before every Altium MCP call sleeps until 4 s have passed since the last one (shared stamp file `~/.last_altium_call`). Use `items` to batch edits into fewer calls.
- Restart Altium ONLY after a real crash (a modal error dialog that stays, or a dead bridge): user rule 2026-11-27, no scheduled restarts. Pace the calls instead.
- No renders, 3D views or screenshots unless debugging; close finished documents, keep at most 2 open.
- Crash dialogs: the user allows pressing any button including "Send and Close" (`app_list_open_dialogs`, `app_press_dialog_button`). If the bridge stays dead: kill X2.exe, start `C:\Program Files\Altium\AD26\X2.EXE`, wait for `app_ping`, `app_recover_script`, then check which files and workspace items already exist before redoing anything.
- Research (datasheets, dimensions, pin tables as JSON specs) may fan out to many agents; every Altium call stays serial (see "Never fan out Altium work").

Sub-agents cannot publish or release to Altium 365: the Claude Code permission classifier refuses `altium365_publish_library_file` / `altium365_release_component` confirm=true from workers. Workers build and verify the SchLib/PcbLib files; the main session publishes and releases (or the user adds permission rules).
