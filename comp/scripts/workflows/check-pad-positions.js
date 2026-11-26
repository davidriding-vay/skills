export const meta = {
  name: 'check-pad-positions',
  description: 'One read-only agent per footprint compares library pads with the datasheet land pattern',
  phases: [{ title: 'Check', detail: 'pads vs datasheet land pattern, one agent per footprint' }],
}

const ROOT = '/mnt/c/Users/Public/Documents/Altium/rearguard/Rearguard/scratch/'
const WROOT = 'C:\\Users\\Public\\Documents\\Altium\\rearguard\\Rearguard\\scratch\\'

const SPEC = `
You verify the PAD POSITIONS of ONE footprint in an Altium PcbLib against the manufacturer's datasheet. Read-only: do NOT call any Altium tool that writes or changes focus (no lib_create_*, lib_set_*, lib_add_*, app_set_active_document, obj_modify, etc.). Report only.

Step 1: read the library pads: load the MCP tool via ToolSearch (select:mcp__altium__lib_get_pad_geometry) and call it with footprint_name. Replies are in mm; coordinates are footprint coordinates (origin as is, +x right, +y up). Record every pad: name, x, y, width (w_mm), height (h_mm).

Step 2: find the datasheet's RECOMMENDED LAND PATTERN / suggested pad layout / soldering footprint page (page hint below). Render it at high dpi with python3 + PyMuPDF (fitz): e.g. python3 -c "import fitz; d=fitz.open(PDF); p=d[PAGE-1]; p.get_pixmap(dpi=300, clip=...).save('/tmp/x.png')" and view the PNG with the Read tool; crop to the land drawing and zoom if numbers are small. Also extract text with page.get_text() for printed numbers.

BE CAREFUL ABOUT WHAT EACH DIMENSION SPANS (a previous mistake: a "7.2" dimension was read as the pad centre distance but it was the GAP between the two pads, so the real centres were 9.0 apart). For every printed dimension decide from its extension lines/arrows whether it is centre-to-centre, edge-to-edge (gap), outer-to-outer, or pad size, and check the numbers add up (e.g. gap + 2*pad length = outer span). Derive each pad's centre, width and height from the drawing, in the library's coordinate frame (work out the frame mapping from pad 1's position / the pin-1 location and the drawing orientation; the drawing may be rotated or mirrored vs the footprint).

Step 3: compare pad by pad. A difference below 0.02 mm is OK. Report any pad whose centre differs by >=0.02 mm or whose size differs by >=0.05 mm. If the datasheet has NO land pattern, say so, and instead check the library pads against the package outline using the IPC-7351B nominal logic (state the IPC toe/heel/side goals you used) and mark verdict "no_land_pattern" with your opinion on whether the pads are plausible (within ~0.1 mm of IPC nominal) or off.

Return the structured result. "differences" lists concrete numbers (pad, library value, datasheet value). "recommended_pads" lists the corrected pad set (name, x, y, w, h) ONLY for pads that should change (empty if verdict is ok). Say how sure you are and what is ambiguous.`

const TASKS = [
  { fp: 'SMA', pdf: 'ds-diodes/diodes_B340A.pdf', page: 6, note: 'Suggested pad layout (C G X X1 Y) on p.6.' },
  { fp: 'SMB', pdf: 'ds-diodes/onsemi_SZ1SMB.pdf', page: 7, note: 'SMB case 403A-03 soldering footprint, p.7.' },
  { fp: 'D0008A', pdf: 'ds-ics/lmh6643.pdf', page: 33, note: 'D0008A land pattern example, p.33 (TI, may be in the last pages).' },
  { fp: 'SOT26', pdf: 'ds-ics/ap5100.pdf', page: 11, note: 'SOT26 suggested pad layout, p.11.' },
  { fp: 'LQFP48', pdf: '', page: 99, note: 'STM32F103x8/xB datasheet DS5319 Rev 20: LQFP48 footprint example Figure 56 (p.99-100). Find the local PDF first: find /mnt/c/Users/Public/Documents/Altium /mnt/c/Users/david -iname "*stm32f103*" -o -iname "*DS5319*" 2>/dev/null | head ; or /tmp/stm32 ; else curl from st.com (--http1.1, browser UA) into /tmp/chk_stm32/. The footprint has 48 pads: check every pad row, pitch, pad length/width, the row-to-row span and pad 1 location.' },
  { fp: 'CP-32-12', pdf: 'ds-ics/adv7280.pdf', page: 28, note: 'ADI CP-32-12 (LFCSP 32, 5x5, 0.5 pitch) outline p.28; the datasheet may have no land pattern: then verdict no_land_pattern, check against IPC QFN logic. 33 pads (33 = exposed pad).' },
  { fp: 'T3255Y-8', pdf: 'ds-ics/tqfn_90-100067.pdf', page: 1, note: 'ADI/Maxim land pattern drawing 90-100067 rev C (this PDF), outline in ds-ics/tqfn_21-100156.pdf. 33 pads.' },
  { fp: 'IND1028', pdf: 'ds-ics/we_7440650033.pdf', page: 1, note: 'Wurth WE-TPC 1028 land pattern p.1. Corrected earlier to pads 4.6 x 1.8 at y=+-4.5 (gap 7.2); verify independently.' },
  { fp: 'IND7040', pdf: 'ds-power/we_744311470.pdf', page: 1, note: 'Wurth WE-HCI 7040 land pattern p.1 (labels 2.2, 2.7, 2.4: work out which is pad width, pad height, and gap).' },
  { fp: 'SOT23', pdf: 'ds-power/zxmp3a13f.pdf', page: 7, note: 'Diodes SOT23 suggested pad layout p.7 (X, Y, C, E dims).' },
  { fp: 'TO-236', pdf: 'ds-power/mmbt3906.pdf', page: 9, note: 'onsemi case 318 SOT-23 recommended mounting footprint p.9 (may be page 8-10).' },
  { fp: 'SOD-123', pdf: 'ds-power/cmhz4705.pdf', page: 2, note: 'Central SOD-123: probably no land pattern (verdict no_land_pattern, check vs IPC).' },
  { fp: 'SOT-323', pdf: 'ds-power/bav99wt1.pdf', page: 4, note: 'onsemi case 419 SC-70 soldering footprint p.4: 0.65 / 0.65 / 1.90 / 0.90 / 0.70.' },
  { fp: 'PowerDI5', pdf: 'ds-power/pdu540.pdf', page: 5, note: 'Diodes PowerDI5 suggested pad layout p.5. Pad "1" = large cathode pad; pads "2" x2 = anode pads.' },
  { fp: 'TO-220AB', pdf: 'ds-power/sup53p06.pdf', page: 6, note: 'Vishay TO-220AB: the datasheet has no land pattern; check hole/pad vs IPC-2222 from the lead dims on p.6 (lead b 0.69-1.01, c 0.36-0.61, e 2.41-2.67), verdict no_land_pattern.' },
  { fp: 'RES0201 RES0402 RES0603 RES0805 RES1206', pdf: 'ds-power/crcw.pdf', page: 11, note: 'Five chip resistor footprints (pads at +-x). Vishay CRCW PDF p.11 has body dims, maybe a land pattern (mounting pad dims) for each size: compare with the library pads of each of the five footprints (call lib_get_pad_geometry five times). Else IPC-7351B nominal (density N). Report per footprint inside the differences list.' },
  { fp: 'CAP0201 CAP0402 CAP0603 CAP0805 CAP1206', pdf: 'ds-power/murata_grm31.pdf', page: 1, note: 'Five MLCC chip capacitor footprints (pads at +-x). Murata GRM31 PDF has the 1206 recommended land pattern (check which page); TDK ds-power/tdk_CGA5L3.pdf also. For other sizes use IPC-7351B nominal. Call lib_get_pad_geometry five times. Report per footprint inside the differences list.' },
]

const SCHEMA = {
  type: 'object',
  properties: {
    footprint: { type: 'string' },
    verdict: { type: 'string', enum: ['ok', 'mismatch', 'no_land_pattern', 'unclear'] },
    library_pads: { type: 'string' },
    datasheet_land: { type: 'string' },
    differences: { type: 'array', items: { type: 'string' } },
    recommended_pads: { type: 'array', items: { type: 'object' } },
    confidence: { type: 'string' },
    notes: { type: 'string' },
  },
  required: ['footprint', 'verdict', 'library_pads', 'datasheet_land', 'differences', 'recommended_pads', 'confidence'],
}

phase('Check')
const results = await parallel(TASKS.map(t => () => agent(
  SPEC + `\n\nFOOTPRINT(S): ${t.fp}\nDatasheet: ${t.pdf ? ROOT + t.pdf : '(see note)'}  page hint: ${t.page}\nNotes: ${t.note}\nLibrary: ${WROOT}trial1.PcbLib`,
  { label: t.fp.split(' ')[0], phase: 'Check', schema: SCHEMA }
)))
return results.filter(Boolean)
