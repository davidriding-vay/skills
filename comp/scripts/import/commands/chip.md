Generate an ASCII-format `.txt` component file for an STM32 (or compatible) microcontroller and commit it.

Arguments: $ARGUMENTS
Expected format: `<MPN> <package> <datasheet_url>`
Example: `STM32WB55CGU5 UFBGA129 https://www.st.com/resource/en/datasheet/stm32wb55rg.pdf`

If no datasheet URL is given, construct it from ST's standard pattern:
`https://www.st.com/resource/en/datasheet/<lowercase-base-mpn>.pdf`

Note: the file format requires coordinates in mils. Convert: mil = mm × 39.3701.

---

## What to do

1. Parse MPN, package, and datasheet URL from arguments.
2. Fetch pin data from ST's open_pin_data GitHub repo using curl (see below).
3. Parse the XML to extract pin number, name, type, and signal.
4. Classify pins into Part A (GPIO/Logic) and Part B (Power).
5. Compute layout geometry using the formulas below.
6. Write the `.txt` file to `Components/<MPN>.txt`.
7. Commit and push.

---

## Fetching pin data

Use curl to fetch the XML directly — do NOT use Agent tool for web fetching:

```bash
curl -s "https://raw.githubusercontent.com/STMicroelectronics/STM32_open_pin_data/master/mcu/<MPN>.xml" -o /tmp/<MPN>.xml
```

If that returns a 404, try with the family prefix directory, e.g.:
```
https://raw.githubusercontent.com/STMicroelectronics/STM32_open_pin_data/master/mcu/STM32WB/STM32WB55CGU5.xml
```

Parse with Python `xml.etree.ElementTree`. Each pin is a `<Pin>` element with attributes:
- `Position` — pin number / ball reference (use as Designator)
- `Name` — pin name (use as Name)
- `Type` — pin electrical type
- `Signal` — primary signal name (optional, not used in output)

### Pin type mapping

| XML Type | PinType |
|---|---|
| I/O | IO |
| Power | Power |
| Reset | Input |
| MonoIO | IO |
| NC | Passive |
| Input | Input |
| Output | Output |
| (anything else) | IO |

---

## Pin classification

### Part A — GPIO / Logic (left and right sides)

| Side | Ports / names |
|---|---|
| LEFT | PA*, PC*, PD*, PE*, PH* |
| RIGHT | PB*, NRST*, OSC_IN, OSC_OUT, RF*, AT*, SWDIO, SWDCLK, SWO, TRACESWO, JTCK, JTDI, JTDO, JTMS, JTRST |

Sort left side: PA0–PA15, PC0–PC15 (etc.), in port+number order.
Sort right side: PB0–PB15 first (port+number order), then special pins alphabetically.

### Part B — Power

| Side | Names (prefix match) |
|---|---|
| LEFT | VBAT, VDD, VDDA, VDDRF, VDDSMPS, VDDUSB, VDDIO2 |
| RIGHT | VSS, VSSRF, VSSSMPS, VFBSMPS, VLXSMPS, VCAP |

Sort each side alphabetically by name, then by pin number for duplicates (multiple VDD pins etc.).

### Unclassified pins
Any pin not matching the above: add to Part A RIGHT as IO type.

---

## Layout geometry

Grid: 1 mm. Pin pitch: 3 mm. Pin length: 5 mm.

### Body widths (half, each side)
- Part A body: ±10 mm
- Part B body: ±8 mm

### Pin tip X positions
- Part A pins: ±15 mm  (body edge ±10 mm + pin length 5 mm)
- Part B pins: ±13 mm  (body edge ±8 mm + pin length 5 mm)

Left-side pins use Rotation 180 (tip at negative X).
Right-side pins use Rotation 0 (tip at positive X).

### Vertical layout formula

For each part (A and B separately):
```
N_max   = max(count_left, count_right)
body_hH = (N_max // 2 + 1) × 3 mm     # half-height
y_top   = body_hH - 3 mm               # topmost pin Y
```

Both left and right sides start at `y_top` and step down by 3 mm per pin.
If one side has fewer pins than the other, start from the same `y_top` (top-aligned).

This formula guarantees all Y values land on the 1 mm metric grid for any even or odd N.

### MPN / DES parameter positions (Part 1 only)
```
y_MPN = -(body_hH_A + 3 mm)    # one pitch below body A bottom
y_DES = -(body_hH_A + 6 mm)    # two pitches below body A bottom
```

### Rectangle dimensions
```
Rectangle (Width 5) (Start -393.70, -<body_hH_A_mil>) (End 393.70, <body_hH_A_mil>) (Part 1)
Rectangle (Width 5) (Start -314.96, -<body_hH_B_mil>) (End 314.96, <body_hH_B_mil>) (Part 2)
```
body_hH_A_mil = body_hH_A × 39.3701, body_hH_B_mil = body_hH_B × 39.3701.

---

## File format

No footprint geometry — leave StartFootprints/EndFootprints empty.
The footprint name at the end of the component references the package name directly.

```
# STMicroelectronics <MPN>
# Package  : <package> (<package>)
# Datasheet: <datasheet_url>
#
# SCH Symbol - 1mm metric grid, 3mm pin pitch, 5mm pin length
# Body A: 20mm W x <2×body_hH_A>mm H  |  Body B: 16mm W x <2×body_hH_B>mm H
# Part A = GPIO / Logic (left: PortA/C/E/H  |  right: PortB + special)
# Part B = Power (left: VDD supply  |  right: VSS/SMPS return)

StartFootprints

EndFootprints

StartComponents

Component (Name "<MPN>") (PartCount 2) (DesPrefix "U?")
Description (Value "<description>")
Comment (Value "<MPN>")
Parameter (Name "MPN") (Location 0, <y_MPN_mil>) (Height 60) (Rotation 0) (Justification TopCenter) (Visible True) (Font "Arial") (Bold True) (Italic False) (Underline False) (Value "<MPN>") (Part 1)
Parameter (Name "DES") (Location 0, <y_DES_mil>) (Height 60) (Rotation 0) (Justification TopCenter) (Visible True) (Font "Arial") (Bold True) (Italic False) (Underline False) (Value "<description>") (Part 1)
Parameter (Name "Manufacturer") (Location 0, 0) (Height 60) (Rotation 0) (Justification Center) (Font "Arial") (Bold False) (Italic False) (Underline False) (Value "STMicroelectronics") (Part 1)
Parameter (Name "Datasheet") (Location 0, 0) (Height 60) (Rotation 0) (Justification Center) (Font "Arial") (Bold False) (Italic False) (Underline False) (Value "<datasheet_url>") (Part 1)
<Part 1 pins — left side Rotation 180, right side Rotation 0>
Rectangle (Width 5) (Start -393.70, -<body_hH_A_mil>) (End 393.70, <body_hH_A_mil>) (Part 1)
<Part 2 pins — left side Rotation 180, right side Rotation 0>
Rectangle (Width 5) (Start -314.96, -<body_hH_B_mil>) (End 314.96, <body_hH_B_mil>) (Part 2)
Footprint (Name "<package>")
EndComponent

EndComponents
```

### Pin line format
```
Pin (Location <x_mil>, <y_mil>) (Rotation <r>) (PinType <type>) (Length 196.85) (Width 0) (Designator Visible "<pos>") (Name Visible "<name>") (PinSwap 0) (PartSwap 0) (PinSeq <seq>) (Part <1|2>)
```

PinSeq is a global counter starting at 1, incrementing across all pins in order (Part 1 left, Part 1 right, Part 2 left, Part 2 right).

---

## Description string format

`MCU <core> <features> - <package>`

Examples:
- `MCU ARM Cortex-M4/M0+ BLE5.0 - UFQFPN48`
- `MCU ARM Cortex-M33/M0+ BLE5.3 - UFBGA129`
