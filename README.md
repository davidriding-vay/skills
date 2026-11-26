# skills

Claude Code skills used by the Vay hardware team.

## comp

Creates, fixes and restyles Altium components to the Rearguard house standard: a schematic symbol (SchLib), a PCB footprint (PcbLib) with a 3D STEP model, parameters, and, when Altium 365 is set up, an automatic upload of the finished part as a managed component.

It works live through the [eda-agent](https://github.com/salitronic/eda-agent) MCP tools. The datasheet comes first: every pin, dimension and land pattern is read from the manufacturer PDF and cited.

Ask Claude Code, for example:

    /comp ZXMP3A13F

### Layout

| Path | Content |
|---|---|
| `comp/SKILL.md` | The skill: non-negotiables, route, the 8 steps, datasheet fetch routes, tool notes |
| `comp/reference/house-standard.md` | The full standard: colours, symbols, parameters, mechanical layers, naming |
| `comp/reference/mcp-workflow.md` | Tool recipes, order of operations, gotchas and faults |
| `comp/reference/altium365-upload.md` | Automatic upload to Altium 365 through Nexar, folder choice table, pitfalls |
| `comp/reference/readme-textbox.txt` | Text for the project-template README text frame (setup, standard, Nexar) |
| `comp/scripts/tools/` | Helpers: `extract.py` (PDF to text), `fp_house.py` (house layers for chip footprints), `symp.py` (example) |
| `comp/scripts/import/`, `comp/reference/ascii-format.md` | Retired Import.pas route, kept for history only |

### Install

Copy the `comp` folder to `~/.claude/skills/comp` (Windows: `%USERPROFILE%\.claude\skills\comp`) and restart Claude Code. `/comp` should then appear in the skill list.

### Requirements

- Altium Designer with the eda-agent MCP server connected (`/mcp`), see the eda-agent README.
- Python 3 with PyMuPDF (`pip install pymupdf`) for the helper scripts.
- CadQuery in the eda-agent environment (`pip install -e ".[models3d]"`) for the 3D models.
- Optional, for the Altium 365 upload: a Nexar app and `eda-agent altium365-login` (steps in `comp/reference/readme-textbox.txt`, section 15). The upload relies on the footprint fix reported upstream for `altium365_publish_library_file`; until it is released, patch `publish_operation` to select `footprintId` for footprints.

### Keeping it current

When the standard changes, update `house-standard.md`, the project `HOUSE_STANDARD.md` and `readme-textbox.txt` together, then commit here.
