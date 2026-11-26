# Upload a finished part to Altium 365 (Nexar route)

Runs as the LAST step of /comp, by itself, when `altium365_check_setup` returns ok. If it does not, say so
in one line and skip (the part stays in the scratch libraries). Setup: README text box section 15.
Needs the eda-agent footprint fix (`desCreateFootprint` returns `footprintId`; reported upstream, patch in the
user's clone until released).

## Preconditions (check every time)
1. The part passed `lib_check_schlib` / `lib_check_pcblib`, the symbol links to the footprint, pin/pad parity ok.
2. `altium365_check_setup` ok. Workspace URL from `altium365_list_workspaces` (one workspace: use it).
3. Parameters: ONLY `MPN` and `DES` (user decision 2026-11-25, no Manufacturer or others). Do not pass `type`.
   Description = the symbol description. Leave `componentComment` out (see the notes at the end).
4. Never upload a whole library: one SchLib and one PcbLib per part, written to `scratch/upload/`
   (footprint: `lib_save_footprint_library`; symbol: `app_create_document` SCHLIB with add_to_project false,
   `lib_copy_component`, `lib_delete_component` Component_1, save).

## Duplicate checks (read-only, before anything is sent)
- Component: `desLibrary{components(first:2300){nodes{name}}}` via `altium365_run_query`. If a component with the
  same MPN parameter already exists, STOP and ask (updating = new revision, `altium365_set_component_parameters`).
- Footprint: if a footprint item with the same name (package name, e.g. `SOT23`) already exists
  (`desLibrary{footprints(first:2000, where:{...})}`), REUSE its revision id instead of publishing again.
  Item names are unique across symbols, footprints and components, so never publish a second one.
- Symbol item name = the MPN. The component can NOT also be named the MPN (HRID clash): components are named
  `CMP-NNNNN`.

## Order
1. Folder ids: `altium365_list_library_folders`, match by PATH (never hard-code ids). Symbol folder
   `Components/Models/Symbols`, footprint folder `Components/Models/Footprints`, component folder from the table below.
2. `altium365_publish_library_file` kind symbol (folder Symbols, name = MPN) and kind footprint (folder Footprints,
   name = footprint name): preview, then `confirm=true`. Keep the returned ids (revision ids).
3. Next component number: take the highest `CMP-NNNNN` (five digits) from the names query, +1 (on 2026-11-25 the
   last was CMP-00474, ZXMP3A13F became CMP-00475). If the release answers `AddALU_ItemsDuplicate`, add 1 and retry.
4. `altium365_release_component` with workspaceUrl, componentParentFolderId, componentItemName `CMP-NNNNN`,
   componentDescription, parameters [{name:"MPN"},{name:"DES"}], symbol {id}, footprints [{id}].
   Preview, then `confirm=true`.
5. Verify: `altium365_get_component` (name `CMP-NNNNN-1`, only MPN and DES), and offer the Explorer check.
6. Log in the project `HOUSE_STANDARD.md`: item names, folders, date. Report in two lines.

## Choosing the component folder (best match, decide from the part, never ask unless truly ambiguous)
Workspace paths under `Components/`; choose by the part's function (datasheet), most specific first:

| Part | Folder |
|---|---|
| BJT, MOSFET, JFET, IGBT, digital transistor | `Transistors` |
| Diode, Zener, TVS, Schottky, rectifier | `Diodes` (LED: `Diodes/LED`; vehicle ECU diodes: `Diodes/Diodes_vay_ecu` only if the user says so) |
| LED, photodiode, optocoupler, display | `Optoelectronics` |
| Resistor, thermistor, varistor | `Resistors` |
| Capacitor (ceramic, electrolytic, tantalum) | `Capacitors` |
| Inductor, ferrite bead, choke | `Inductors` |
| Filter, EMI filter, common-mode choke | `Filters` |
| Fuse, PTC fuse | `Fuses` |
| Crystal, oscillator, resonator | `Crystals&Oscillators` |
| Relay | `Relays` |
| Switch, button | `Switches` |
| Transformer | `Transformers` |
| Battery, holder | `Batteries` |
| Audio parts | `Audio` |
| RF parts, antennas, RF connectors, baluns | `Radio&RF` |
| Connector, header, jack, socket | `Connectors` (harness connectors/terminals: `Harness components/...`) |
| Regulator, buck/boost, LDO, PMIC, converter modules | `Integrated Circuits/Power Supply` |
| Op amp, comparator, instrumentation amp | `Integrated Circuits/Amplifiers` |
| Microcontroller, SoC, FPGA, processor | `Integrated Circuits/Processors` |
| Memory (flash, SRAM, DRAM, EEPROM) | `Integrated Circuits/Memory` |
| Interface/transceiver (CAN, LIN, UART, SerDes, USB, Ethernet PHY, video decoder/serializer) | `Integrated Circuits/Interface` |
| Logic gates, level shifters, buffers | `Integrated Circuits/Logic` |
| Gate/motor/LED drivers, load switches | `Integrated Circuits/Drivers` |
| Clock generators, PLL, timers, RTC | `Integrated Circuits/Clock&Timing` |
| Sensors (temperature, IMU, current, pressure) | `Integrated Circuits/Sensors` |
| Wi-Fi, BLE, cellular, GNSS modules/ICs | `Integrated Circuits/Wireless` |
| Mechanical parts, hardware | `Mechanical` |
| Test points, jumpers, misc hardware | `Miscellaneous` |
| Anything else or unclear | `Uncategorized` |
Say which folder was chosen and why in the report (one line). The folder list can change: always confirm the path
exists in `altium365_list_library_folders` and fall back to `Components/Uncategorized` if it does not.

## Pitfalls (all met on 2026-11-25)
- No tool and no API call deletes or renames a symbol, footprint or component. A wrong upload has to be removed
  by hand in Explorer, so run the duplicate checks and use the right names the first time.
- `altium365_list_components` shows only 10 components; read names with `altium365_run_query` as above.
- Nexar data may not be kept more than 24 h: large replies are saved in the session's tool-results folder; tell
  the user to delete them (they cannot be deleted from the session).
- Explorer's list does not refresh by itself after an upload: press its refresh button before checking.

## Duplicate check detail (learned with MMBT3904, 2026-11-25)
`desLibrary{components(first:5, where:{name:{eq:"<MPN>"}}){nodes{id name}}}` also matches components whose MPN/name field
is the MPN, even when their item name is CMP-xxx (MMBT3904 was already CMP-014-00026 in the workspace, from a vendor
library). If it returns anything, read it with `altium365_get_component` and STOP: report it to the user and ask
(reuse, update as a new revision, or upload anyway under a new CMP number). Do not upload a second component silently.
The footprint/symbol `eq` filter did not find items that exist (names carry a revision suffix), so for those compare with
the folder contents in Explorer or use a `name` containing search through the library query before publishing.

## User decisions (2026-11-25)
- An existing component with the same MPN in the workspace (older parts made by colleagues without the house style) does
  NOT block the upload: publish ours as a new `CMP-NNNNN` (next number) and mention the old one in the report. Never
  overwrite or change another person's component.
- Footprint height fields stay 0 (the user relies on the 3D STEP model): never run `lib_update_footprint_heights_from_3d`.
- Parameters MPN and DES only.
- First proven end to end with MMBT3904 -> CMP-00476 (Components/Transistors); symbol item MMBT3904, footprint item TO-236.
- Component templates (`componentTemplateId`, Managed Content/Templates/Component Templates) are NOT used and not edited:
  the user finds them buggy, slow and complicated (2026-11-25). Release without a template, as done so far.
- Placed Altium 365 components showed their Comment (Times New Roman 10) although the symbol's Comment is hidden
  (seen on CMP-00476-1 in main.SchDoc; fixed on the instance with `obj_modify` eParameter Name=Comment IsHidden true).
  Suspected cause: `componentComment` in the release. From the next upload on, leave `componentComment` OUT, then place
  the part and read `eSchComponent` Comment.IsHidden. If it is hidden, keep it out for good; if not, note the result here
  and hide the Comment on each placed instance on request.

## Batch upload (done for the SNVA717 BOM, 22 parts)
- Per part: one-symbol SchLib (`app_create_document` has no items, so call it once per file; then `lib_copy_component` and
  `lib_delete_component` Component_1 with `items`, then `app_save_document` per file; do NOT use `app_save_all`, it would save
  the user's unsaved sheets), one PcbLib per unique footprint (`lib_save_footprint_library` with `items`).
- Publish every unique footprint once and reuse its revision id in all components that use it (RES1206, CAP1206, TP-TH).
- Numbers: next free CMP-NNNNN in sequence; a release the classifier refuses is left out (note the gap).
