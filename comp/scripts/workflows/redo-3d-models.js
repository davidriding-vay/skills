export const meta = {
  name: 'redo-3d-models',
  description: 'Per-footprint agents read datasheets and return CadQuery solid lists for lib_create_3d_model (no Altium writes)',
  phases: [{ title: 'Design', detail: 'one agent per footprint family returns solids JSON' }],
}

const ROOT = '/mnt/c/Users/Public/Documents/Altium/rearguard/Rearguard/scratch/'
const WROOT = 'C:\\Users\\Public\\Documents\\Altium\\rearguard\\Rearguard\\scratch\\'

const SPEC = `
You design the parameters for ONE 3D model of an Altium footprint. Do NOT call any Altium write tool and do NOT call lib_create_3d_model, app_set_active_document or anything that changes focus or edits: read-only only. The lead agent will build the model from your result.

How to read pads (read-only): load the MCP tool mcp__altium__lib_get_pad_geometry via ToolSearch (select:mcp__altium__lib_get_pad_geometry) and call it with footprint_name. Its replies are in mm (session unit mm). Pad positions are in footprint coordinates (origin as is, +x right, +y up). The 3D model must be drawn in the SAME coordinates so every lead/terminal lands on its pad with the right pin number. Pin 1 = pad named "1". Do not guess orientation: derive it from the pads.

Datasheets are local PDFs (WSL paths below). Read the page with the package outline drawing: use python3 with PyMuPDF (fitz) from the user site (run "python3 -c 'import fitz'"; plain python3, not -I) to render pages to PNG and read them with the Read tool, and/or extract text. Do not fetch from the web unless the local PDF lacks the drawing; if you must, use curl (never sub-agents). Use nominal dims (mid of min/max), cite page. If a dim is not in the datasheet, state it as an ASSUMPTION (typical value) in assumptions.

The solids list goes to lib_create_3d_model (CadQuery). All numbers in mm, footprint origin, Z up from the board (z=0 board surface). Each solid: {kind, name, role, ...}. Kinds:
- box: x0 y0 z0 x1 y1 z1 (optional corner_r, edge_r (top edges), taper deg)
- extrude: outline [[x,y],...] z0 z1 (plan-view polygon; optional corner_r, edge_r, taper)
- cylinder: r cx cy z0 z1 (axis "x": cy cz x0 x1)
- sphere: cx cy cz r
- prism: axis ("x" or "y", ALWAYS give it) profile [[u,z],...] ; axis "y": profile is (x,z) extruded over y0..y1 ; axis "x": profile is (y,z) extruded over x0..x1. Use for gull-wing leads, chamfered/sloped bodies.
- text / dot marks: dot cx cy r z1 (cut flush into the top face at z1 inside its edges); role ink or laser. A dot marks pin 1.
- instance: {kind:"instance", group, rot, dx, dy, dz} places a group (groups: name -> solids list) so repeated leads need only be defined once; rot is degrees about z.
- cut: role "cut" with "cut_from": [names] and same geometry kinds.
Roles: body (plastic/ceramic body), metal, nickel, tin (leads/terminations), gold, ceramic, ceramic_ivory, white, lens, pin1, seal_ring, silicon, backside_coat, substrate, pcb_green, lcp_white, cut; marks: ink, laser.
Model EVERY visible detail from the drawing, not a plain box: gull-wing/J-leads with shoulder and foot, terminal end bands on chips, exposed pad/heat slug, tab and holes, chamfered or sloped body, pin-1 mark. Leads must reach the pads (foot on z 0..lead thickness) and enter the body.

The tool also checks the model against a "drawing" object: body_x (extent along X of role-body solids, nominal number or [min,max]), body_y, height (overall max: [0,max]), span_x / span_y (lead tip to tip, where the drawing prints it). Fill drawing with the printed values (min/max) so the built extents fall inside. Only report values the datasheet prints.

Return the structured result. "solids" must be directly pasteable. Also give "pad_check": one sentence confirming pin 1 location and that leads sit on the pad coordinates you read (list the pad coordinates you used).`

const TASKS = [
  { fp: 'SMA', pdf: 'ds-diodes/diodes_B340A.pdf', note: 'SMA (DO-214AC) diode, 2 J-bend/flat terminations, cathode band marking on the body. Footprint pad 1 = cathode.' },
  { fp: 'SMB', pdf: 'ds-diodes/onsemi_SZ1SMB.pdf', note: 'SMB case 403A TVS diode, 2 terminations, cathode band marking. Pad 1 = cathode.' },
  { fp: 'D0008A', pdf: 'ds-ics/lmh6643.pdf', note: 'TI D0008A = SOIC-8 (3.9 mm body, 1.27 pitch), gull-wing leads, outline drawing in the package section near the end.' },
  { fp: 'SOT26', pdf: 'ds-ics/ap5100.pdf', note: 'Diodes SOT26 (SOT-23-6), gull-wing leads, 0.95 pitch; outline drawing and table in the package section.' },
  { fp: 'LQFP48', pdf: '', note: 'LQFP48 7x7 mm, 0.5 pitch, gull-wing leads, 48 pins. Find the STM32F103C8T6 datasheet PDF locally first (find /mnt/c/Users/Public/Documents/Altium /mnt/c/Users/david -iname "*stm32f103*" -o -iname "*DS5319*" 2>/dev/null | head); if none, use curl to fetch DS5319 from st.com with --http1.1 and a browser UA into /tmp/stm32/; otherwise use the JEDEC MS-026 LQFP48 7x7 package dims (state as assumption). Use instance groups for the 12 leads per side.' },
  { fp: 'CP-32-12', pdf: 'ds-ics/adv7280.pdf', note: 'ADI CP-32-12 = 32-lead LFCSP 5x5 mm QFN, 0.5 pitch, exposed pad; 33 pads (pad 33 = exposed paddle). Outline dimensions in the outline dimensions section near the end.' },
  { fp: 'T3255Y-8', pdf: 'ds-ics/tqfn_21-100156.pdf', note: 'Maxim/ADI T3255Y-8 TQFN-SW 32L 5x5 mm. Outline drawing 21-100156 (this PDF); land pattern in ds-ics/tqfn_90-100067.pdf. 33 pads (33 = exposed pad). Side-wettable terminals.' },
  { fp: 'IND1028', pdf: 'ds-ics/we_7440650033.pdf', note: 'Wurth WE-TPC 1028 shielded inductor, ~10x10x2.78 mm, 2 terminals (metal tabs wrapping the body). 3D height 2.78.' },
  { fp: 'IND7040', pdf: 'ds-power/we_744311470.pdf', note: 'Wurth WE-HCI 7040 inductor, 7.0x6.9x3.8 mm, 2 flat terminals under/at the sides.' },
  { fp: 'SOT23', pdf: 'ds-power/zxmp3a13f.pdf', note: 'Diodes ZXMP3A13F SOT23 (3 pins: 1 gate, 2 source at the bottom side, 3 drain on the opposite side). Gull-wing leads.' },
  { fp: 'TO-236', pdf: 'ds-power/mmbt3906.pdf', note: 'onsemi case 318 SOT-23 (TO-236) 3 pins. Gull-wing leads. Package outline on the case 318 page.' },
  { fp: 'SOD-123', pdf: 'ds-power/cmhz4705.pdf', note: 'Central Semiconductor SOD-123 zener, 2 flat gull-wing terminals, cathode band. Pad 1 = cathode. Outline on the case mechanical outline page (p.2).' },
  { fp: 'PowerDI5', pdf: 'ds-power/pdu540.pdf', note: 'Diodes PowerDI5: molded body with a large exposed heat-sink pad (pad 1 cathode) on the bottom and two anode pads (pad 2 x2). Outline drawing and land pattern near p.5.' },
  { fp: 'RES0201 RES0402 RES0603 RES0805 RES1206', pdf: 'ds-power/crcw.pdf', note: 'Five chip resistors (footprints RES0201, RES0402, RES0603, RES0805, RES1206; Yageo AC / RC series, body L x W: 0.6x0.3, 1.0x0.5, 1.6x0.8, 2.0x1.25, 3.1x1.6). Return one result object PER footprint inside "variants" is NOT available: instead return ONE solids list for the first size (RES0603) and in "assumptions" give a table of L, W, H, termination band length and thickness for all five sizes with sources (Yageo datasheet via curl if reachable, else Vishay CRCW PDF ds-power/crcw.pdf, else typical). The lead agent will scale the generic model: body ceramic/dark box between two end terminations (tin) wrapping 5 faces, resistive layer top face (dark) typical.' },
  { fp: 'CAP0201 CAP0402 CAP0603 CAP0805 CAP1206', pdf: 'ds-power/murata_grm31.pdf', note: 'Five MLCC chip capacitors (footprints CAP0201, CAP0402, CAP0603, CAP0805, CAP1206; KEMET C-series, body L x W: 0.6x0.3, 1.0x0.5, 1.6x0.8, 2.0x1.25, 3.2x1.6). Return ONE solids list for CAP0603 and in "assumptions" a table of L, W, T (height), termination band length for all five sizes with sources (KEMET datasheet via curl if reachable; Murata ds-power/murata_grm31.pdf for 1206; TDK ds-power/tdk_CGA5L3.pdf; else typical). Generic model: ceramic body box + two terminations (tin/metal) wrapping 5 faces.' },
]

const SCHEMA = {
  type: 'object',
  properties: {
    footprint: { type: 'string' },
    source: { type: 'string' },
    drawing: { type: 'object' },
    solids: { type: 'array', items: { type: 'object' } },
    groups: { type: 'object' },
    assumptions: { type: 'array', items: { type: 'string' } },
    pad_check: { type: 'string' },
  },
  required: ['footprint', 'source', 'drawing', 'solids', 'assumptions', 'pad_check'],
}

phase('Design')
const results = await parallel(TASKS.map(t => () => agent(
  SPEC + `\n\nYOUR FOOTPRINT: ${t.fp}\nDatasheet: ${t.pdf ? ROOT + t.pdf : '(see note)'}\nNotes: ${t.note}\nLibrary: ${WROOT}trial1.PcbLib`,
  { label: t.fp.split(' ')[0], phase: 'Design', schema: SCHEMA }
)))
return results.filter(Boolean)
