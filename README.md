# skills

Claude Code skills used by the Vay hardware team.

## comp

Creates, fixes and restyles Altium components to the Rearguard house standard: a schematic symbol (SchLib), a PCB footprint (PcbLib) with a 3D STEP model, parameters, and, when Altium 365 is set up, an automatic upload of the finished part as a managed component.

It works live through the [eda-agent](https://github.com/salitronic/eda-agent) MCP tools. The datasheet comes first: every pin, dimension and land pattern is read from the manufacturer PDF and cited.

Ask Claude Code, for example:

    /comp ZXMP3A13F

### What it does

1. Reads the manufacturer datasheet (PDF) and cites page numbers; pin tables and package drawings are never taken from memory.
2. Builds the footprint (pads, house mechanical layers M5-M38, courtyard, designator) and a detailed 3D STEP model with CadQuery.
3. Builds the symbol (house colours, fonts, 100 mil pins, 300 mil on ICs, parameters `MPN` and `DES`, component Comment = MPN, which fills the Name field in Altium 365).
4. Checks pins against the datasheet table, pads against the drawing, symbol against footprint.
5. Builds in a throwaway pair of scratch libraries (`scratch/`), never in a project library. The Altium 365 workspace is the source of truth: existing parts are read from it and finished parts go back to it.
6. Optionally uploads the part to Altium 365 through Nexar, as the next free `CMP-NNNNN` in the best-matching `Components/...` folder.
7. Logs what was built and what is still unverified in the project's `HOUSE_STANDARD.md`.

Built-in safeguards: the tool checks (pin table, footprint vs drawing) are never bypassed by the agent, only the user can switch them off in the eda-agent Config tab; every write is read back; assumptions are listed in the report.

### Layout

| Path | Content |
|---|---|
| `comp/SKILL.md` | The skill: non-negotiables, route, the 8 steps, datasheet fetch routes, tool notes |
| `comp/reference/house-standard.md` | The full standard: colours, symbols, parameters, mechanical layers, naming |
| `comp/reference/mcp-workflow.md` | Tool recipes, order of operations, gotchas and faults |
| `comp/reference/altium365-upload.md` | Automatic upload to Altium 365 through Nexar, folder choice table, pitfalls |
| `comp/reference/readme-textbox.txt` | Text for the project-template README text frame (setup, standard, Nexar) |
| `comp/scripts/tools/` | Helpers: `extract.py` (PDF to text), `fp_house.py` (house layers for chip footprints), `symp.py` (example) |
| `comp/scripts/models3d/` | `build_specs.py` rebuilds the `lib_create_3d_model` parameter sets for every footprint built so far (SMD packages, QFP/QFN, inductors, TO-220AB, electrolytic can, test point, banana jack, chips); `specs/*.json` are its output. Reconstructed from the build session, so they match what was built |
| `comp/scripts/workflows/` | The two Claude Code workflow scripts used for the bulk jobs: `redo-3d-models.js` (agents read datasheets and return the 3D parameters) and `check-pad-positions.js` (agents compare library pads with datasheet land patterns). Read-only fan-outs; the Altium writes stay in the main session |
| `comp/scripts/patches/eda-agent-publish-footprint-fix.patch` | Local fix for eda-agent: `desCreateFootprint` returns `footprintId`, not `id`. Apply with `git apply` in the eda-agent clone until the upstream fix is released |
| `comp/scripts/import/`, `comp/reference/ascii-format.md` | Retired Import.pas route, kept for history only |

### Install

Copy the `comp` folder to `~/.claude/skills/comp` (Windows: `%USERPROFILE%\.claude\skills\comp`) and restart Claude Code. `/comp` should then appear in the skill list.

### Requirements

- Altium Designer with the eda-agent MCP server connected (`/mcp` shows "altium"), see the eda-agent README. Windows; Claude Code may run in Windows or WSL.
- Python 3 with PyMuPDF (`pip install pymupdf`) for the helper scripts.
- CadQuery in the eda-agent environment (`pip install -e ".[models3d]"`) for the 3D models.
- For bulk jobs (all 3D models, pad audits) the Claude Code Workflow tool; single parts do not need it.
- Optional, for the Altium 365 upload: a Nexar account and app (below). The upload relies on the footprint fix reported upstream for `altium365_publish_library_file`; until it is released, apply `comp/scripts/patches/eda-agent-publish-footprint-fix.patch` in the eda-agent clone (`git apply`).

### Altium 365 upload: one-time setup (per person)

1. Register at https://nexar.com (confirm the e-mail) and open https://nexar.com/api, Apps.
2. Create an app: Authorization code grant on, redirect URL exactly `http://localhost:3000/login`, design scopes enabled (`design.domain`, `user.access`). Note the Client ID and Client secret. The secret is a password: never paste it into the chat or commit it.
3. In PowerShell, with the real values (not the placeholders):

        setx EDA_AGENT_NEXAR_APP_ID "your client id"
        setx EDA_AGENT_NEXAR_CLIENT_SECRET "your client secret"

4. If eda-agent is started from WSL, also let the variables through, then restart WSL:

        setx WSLENV "EDA_AGENT_NEXAR_APP_ID:EDA_AGENT_NEXAR_CLIENT_SECRET"
        wsl --shutdown

5. Open a new terminal and check `echo $env:EDA_AGENT_NEXAR_APP_ID` prints the id.
6. Sign in once: `eda-agent altium365-login` (browser opens, use the Altium 365 account). The login lasts 24 hours; repeat when it expires. `eda-agent altium365-logout` forgets it.
7. Reconnect the MCP server (`/mcp`) and ask the agent to run `altium365_check_setup`: it must report route `nexar` and offer publish symbol, publish footprint, release component and set parameters.

Alternative to Nexar: a workspace API token (Admin, Developer) in `EDA_AGENT_ALTIUM365_TOKEN` with the workspace domain in `EDA_AGENT_ALTIUM365_DOMAIN`.

### Altium 365 upload: how it behaves

- Checks the workspace for an existing component first; if found it stops and asks.
- Symbol goes to `Components/Models/Symbols`, footprint to `Components/Models/Footprints`, component to the best-matching `Components/...` folder (Transistors, Diodes, Capacitors, Resistors, Inductors, Connectors, Miscellaneous, IC subfolders).
- Parameters are only `MPN` and `DES`; the component Name (release `componentComment`) is the MPN. The Name of a symbol is its Comment: set it to the MPN before uploading, neither can be edited afterwards through the API tools.
- Previews first and sends only after the user confirms. One part per upload file (`scratch/upload/`). No component templates.
- Nothing can be deleted or renamed through the tools: check the part before approving. Footprints are named after the package only (`SOT23`, `RES1206`) and shared between parts.
- Nexar terms: data the API returns may not be kept more than 24 hours. Large replies are saved in the Claude Code session's tool-results folder; delete them.

### Troubleshooting

| Symptom | Fix |
|---|---|
| `altium365_check_setup` says not signed in / expired | `eda-agent altium365-login` again |
| Variable prints nothing | Placeholders typed instead of values, or an old terminal; repeat step 3 and open a new one (WSL: step 4) |
| "No response ... polling loop" from an Altium tool | Dismiss any open Altium dialog, then ask the agent to run `app_recover_script` |
| Two Altium instances running | Screenshots and some tools refuse; close one |
| Footprint upload fails with a missing id | The eda-agent footprint patch is not applied |
| A pin-table or drawing check blocks the build | Read what differs; only the user may switch the check off (eda-agent Config tab) |

### Keeping it current

When the standard changes, update `house-standard.md`, the project `HOUSE_STANDARD.md` and `readme-textbox.txt` together, then commit here.
