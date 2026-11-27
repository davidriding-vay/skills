# comp skill: session summary and decisions (2026-11-22 to 2026-11-26)

Curated from the working session that built the SNVA717 parts and the `comp` skill. No secrets and no Nexar API data are included. The rules themselves live in `comp/reference/house-standard.md`; this file records what was done, why, and what is still open.

## What was built
- All 24 BOM lines of TI SNVA717 (Sept 2014, "Automotive Line Transient Protection Circuit"): symbols (SchLib), footprints with CadQuery 3D models (PcbLib), uploaded to Altium 365 as components `CMP-00475` to `CMP-00498` (parameters MPN and DES only, Name = MPN).
- The page 5 schematic, drawn horizontally (TI figure rotated 90 degrees clockwise) as `power-filter.SchDoc` in the Rearguard project, using only workspace components, with plain `C? R? D? Q? L?` reference designators.
- This repo: the skill, build scripts, 3D parameter sets, workflow scripts and the eda-agent footprint-publish patch.

## Decisions (user)
- Datasheet first. Never bypass a tool check; only the user switches checks off (Config tab, `preferences.json` `checks_off`).
- House colours: dark blue `#344062` on all symbol graphics, IC body fill light blue `#CFE5F3`; MPN/DES visible (FontId 3), designator FontId 4; Comment hidden.
- Chips 300 mil pins, everything else 100 mil. **Every pin hotspot (wire end, ConnectionX/Y) on the 100 mil grid**; the body end may be off grid (BJT/MOSFET C/E/S/D pins: 80 mil, roots +-120, hotspots +-200).
- Pin numbers visible and upright on transistors, FETs and 3-pin diodes.
- **Every MOSFET symbol (N or P) draws the body diode** between drain and source; reference ZXMP3A13F rev 4 / CMP-00475-4.
- Footprint name = package name only. Chip RES/CAP pads at IPC-7351B nominal. Footprint heights stay 0 (do not run `lib_update_footprint_heights_from_3d`).
- Altium 365 upload: no component templates; Name field = release `componentComment` = the MPN (symbols too: set the component Comment to the MPN before upload); nothing can be deleted through the tools, so duplicate checks come first.
- **Sources of truth:** parts in the Altium 365 workspace; skill, scripts, README and house-style md in this git repo; the project template is updated by hand.
- On schematics always link parts to the workspace components (`sch_place_vault_components`), never to scratch libraries.

## Nexar setup (no secrets)
Create a Nexar account, create an app with the authorization-code grant, redirect URL `http://localhost:3000/login` and the design scopes, set `EDA_AGENT_NEXAR_APP_ID` and `EDA_AGENT_NEXAR_CLIENT_SECRET` with `setx` (and `WSLENV` if run from WSL), sign in once with `eda-agent altium365-login` (valid 24 hours). Full steps in `README.md`. Nexar data may not be kept longer than 24 hours.

## Lessons learned
- Altium bridge drops often: `app_recover_script`. Dialogs (for example "Update From Library") block it: read them with `app_list_open_dialogs`.
- `obj_delete` of all schematic components needed an allow rule (`/permissions`, `mcp__altium__obj_delete`).
- Managed parts keep a visible Comment parameter; hide it on the instance.
- The template tool (`sch_draw_template`) cannot place managed parts: place them with `sch_place_vault_components`, read pin hotspots with `obj_query` ePin `ConnectionX/Y`, and draw wires from those coordinates.
- Rev 3 of the SUP53P06-20 symbol moved pin roots onto the grid but left the hotspots off it; the hotspot is what counts (rev 4 is correct).

## Open items
- SUP53P06-20 symbol (rev 4) has no body diode yet; confirm the N-channel layout on the first N-FET.
- ZXMP3A13F on the sheet still uses `CMP-00475-2`; update to `-4` via Update From Library.
- MMBT3904 symbol Name is still blank in Altium 365 (component Name is set).
- Switch-off checks: `symbol_pins` was switched back on in `preferences.json`.
- Annotate the sheet (`C?`, `R?` etc. are unnumbered).
- ROVS2 (27.4 k) uses the 27 k part; EEE-FC1H101P lands are IPC-derived; confirm the 575-4 banana jack hole/pad/body.
- The project template files (`HOUSE_STANDARD.md`, `README_TEXTBOX.txt`, `skills.zip`) need a manual update after repo changes.

- 2026-11-27: FAKRA 3D model alignment. Pin positions must be read from the STEP vertices (lib_link_3d_model does not centre the model); tab pad must sit under the housing plate; MB_281 `3.3` dimension runs from the hole-row centre to the tab top (tab y 4.34..5.84). Recorded as SKILL.md notes 4c/4d.

- 2026-11-27: Rule: every symbol is created with its Comment parameter hidden and every placed Comment is hidden on the sheets. Swapping placed managed parts for new components is done by place new + delete old (see reference/mcp-workflow.md). 21 components CMP-00499..00519 released with the 13 new footprints and swapped on the sheets.

- 2026-11-27: CPH3225A (SII chip EDLC) built and released as CMP-00521 (footprint EDLC3225, symbol CPH3225A-S). First upload (CMP-00520) was unusable: the files were published as work.SchLib / work.PcbLib; the file name must equal the item name. Deleted/draft items keep their names forever (AddALU_ItemsDuplicate), so a broken upload costs new names. See reference/altium365-upload.md. Also: 21 components CMP-00499..00519 swapped on the sheets, FAKRA model orientation lessons (SKILL.md 4c/4d).

- 2026-11-27: Telematic project rebuild. A 49-agent parallel run built 48 footprints (with 3D models) but crashed Altium (ADVPCB.DLL access violation) so no component was released. Rules recorded: never run Altium calls from parallel agents, throttle with pace.py (4 s), restart Altium regularly (restart_altium.sh), the user allows pressing "Send and Close" and restarting Altium after a crash. A serial, throttled build of the remaining 114 parts followed.

- 2026-11-27: Decision: publish symbols/footprints and release components from the MAIN session only; workflow workers build and verify files (their publish/release calls are refused). Restart Altium only after a real crash (no scheduled restarts).
