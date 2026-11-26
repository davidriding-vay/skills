Generate an ASCII-format `.txt` component file for a chip capacitor and commit it.

Arguments: $ARGUMENTS
Expected format: `<MPN> <capacitance> <voltage> <tolerance> <dielectric> <package>`
Example: `C0603C104K5RACTU 100nF 50V 10% X7R 0603`

Note: the file format requires coordinates in mils. Convert: mil = mm × 39.3701.

---

## What to do

1. Parse the arguments to extract MPN, capacitance, voltage, tolerance, dielectric, and package size.
2. Look up PCB footprint dimensions from the package table below.
3. Write the `.txt` file to the `Components/` folder using the MPN as the filename (e.g. `Components/C0603C104K5RACTU.txt`).
4. The DES value must follow the format: `CAP - <capacitance> <voltage> <tolerance> <dielectric> - <package>`
   Example: `CAP - 100nF 50V 10% X7R - 0603`
5. Commit and push.

---

## SCH Symbol spec  (IEC parallel-plate capacitor symbol)

Grid: 1 mm.

| Element | Value (mm) |
|---|---|
| Pin 1 Location | -3.50, 0 |
| Pin 2 Location | +3.50, 0 |
| Pin Rotation 1 | 0 |
| Pin Rotation 2 | 180 |
| Pin Length | 3.00 |
| Pin Type | Passive |
| Pin Designator | Hidden |
| Pin Name | Hidden, value `~` |
| Plate 1 Line | Start -0.50, -1.50  End -0.50, +1.50  (Width 5) |
| Plate 2 Line | Start +0.50, -1.50  End +0.50, +1.50  (Width 5) |

Note: pin inner end = 3.50 − 3.00 = 0.50 mm, which is exactly at the plate line. No gap.

### Parameters

| Name | Location (mm) | Justification | Visible | Font | Bold | Italic | Underline |
|---|---|---|---|---|---|---|---|
| MPN | 0, -2.00 | TopCenter | True | Arial | True | False | False |
| DES | 0, -3.50 | TopCenter | True | Arial | True | False | False |
| Manufacturer | 0, 0 | Center | False | Arial | False | False | False |
| Datasheet | 0, 0 | Center | False | Arial | False | False | False |

All parameter Height: 60. All parameter Rotation: 0. All Part: 1.

### Component header
```
Component (Name "<MPN>") (PartCount 1) (DesPrefix "C?")
Description (Value "<DES>")
Comment (Value "<capacitance>")
```

---

## PCB Footprint spec

Grid: 1 mm.

### Layers used
| Layer keyword | Purpose |
|---|---|
| Top | SMD pads |
| TopOverlay | Silkscreen tick marks |
| Mechanical13 | Assembly outline |
| Mechanical15 | Courtyard + centre marker |

### Centre marker (Mechanical15, all packages)
```
Line (Width 2) (Start -19.69, 0) (End 19.69, 0) (Layer Mechanical15)
Line (Width 2) (Start 0, -19.69) (End 0, 19.69) (Layer Mechanical15)
Arc (Location 0, 0) (Radius 9.84) (Width 2) (StartAngle 0) (EndAngle 360) (Layer Mechanical15)
```

### Package dimensions

#### 0402 (1005M)
| Parameter | mm |
|---|---|
| Pad location X | ±0.52 |
| Pad size X | 0.54 |
| Pad size Y | 0.64 |
| Silkscreen X | ±0.15 |
| Silkscreen Y | ±0.40 |
| Courtyard X | ±0.97 |
| Courtyard Y | ±0.52 |
| Assembly X | ±0.50 |
| Assembly Y | ±0.25 |

#### 0603 (1608M)
| Parameter | mm |
|---|---|
| Pad location X | ±0.75 |
| Pad size X | 0.75 |
| Pad size Y | 1.00 |
| Silkscreen X | ±0.30 |
| Silkscreen Y | ±0.60 |
| Courtyard X | ±1.40 |
| Courtyard Y | ±0.75 |
| Assembly X | ±0.80 |
| Assembly Y | ±0.45 |

#### 0805 (2012M)
| Parameter | mm |
|---|---|
| Pad location X | ±1.00 |
| Pad size X | 0.90 |
| Pad size Y | 1.45 |
| Silkscreen X | ±0.40 |
| Silkscreen Y | ±0.85 |
| Courtyard X | ±1.75 |
| Courtyard Y | ±0.95 |
| Assembly X | ±1.00 |
| Assembly Y | ±0.60 |

#### 1206 (3216M)
| Parameter | mm |
|---|---|
| Pad location X | ±1.50 |
| Pad size X | 1.00 |
| Pad size Y | 1.80 |
| Silkscreen X | ±0.65 |
| Silkscreen Y | ±1.05 |
| Courtyard X | ±2.35 |
| Courtyard Y | ±1.15 |
| Assembly X | ±1.60 |
| Assembly Y | ±0.80 |

### Footprint block template
```
Footprint (Name "<footprint_name>")
Pad (Name "1") (Location -<pad_x>, 0) (Surface True) (Rotation 0) (ExpandMask 0) (ExpandPaste 0)
PadShape (Size <pad_sx>, <pad_sy>) (Shape Rectangular) (Layer Top)
EndPad
Pad (Name "2") (Location <pad_x>, 0) (Surface True) (Rotation 0) (ExpandMask 0) (ExpandPaste 0)
PadShape (Size <pad_sx>, <pad_sy>) (Shape Rectangular) (Layer Top)
EndPad
Line (Width 5) (Start -<silk_x>, <silk_y>) (End <silk_x>, <silk_y>) (Layer TopOverlay)
Line (Width 5) (Start -<silk_x>, -<silk_y>) (End <silk_x>, -<silk_y>) (Layer TopOverlay)
Line (Width 2) (Start -<cyard_x>, -<cyard_y>) (End <cyard_x>, -<cyard_y>) (Layer Mechanical15)
Line (Width 2) (Start <cyard_x>, -<cyard_y>) (End <cyard_x>, <cyard_y>) (Layer Mechanical15)
Line (Width 2) (Start <cyard_x>, <cyard_y>) (End -<cyard_x>, <cyard_y>) (Layer Mechanical15)
Line (Width 2) (Start -<cyard_x>, <cyard_y>) (End -<cyard_x>, -<cyard_y>) (Layer Mechanical15)
Line (Width 2) (Start -19.69, 0) (End 19.69, 0) (Layer Mechanical15)
Line (Width 2) (Start 0, -19.69) (End 0, 19.69) (Layer Mechanical15)
Arc (Location 0, 0) (Radius 9.84) (Width 2) (StartAngle 0) (EndAngle 360) (Layer Mechanical15)
Line (Width 2) (Start -<assy_x>, -<assy_y>) (End <assy_x>, -<assy_y>) (Layer Mechanical13)
Line (Width 2) (Start <assy_x>, -<assy_y>) (End <assy_x>, <assy_y>) (Layer Mechanical13)
Line (Width 2) (Start <assy_x>, <assy_y>) (End -<assy_x>, <assy_y>) (Layer Mechanical13)
Line (Width 2) (Start -<assy_x>, <assy_y>) (End -<assy_x>, -<assy_y>) (Layer Mechanical13)
EndFootprint
```

---

## Complete file template

```
# <Manufacturer> <series> - <capacitance> <voltage> <tolerance> <dielectric> SMD Ceramic Capacitor
# MPN      : <MPN>
# Package  : <package> (<metric_code>)
# Datasheet: <datasheet_url>
#
# PCB Footprint - IPC-7351 Nominal, reflow soldering
# SCH Symbol - IEC parallel-plate, 3mm pins, 1mm metric grid, Arial Bold 6

StartFootprints

<footprint block from above>

EndFootprints

StartComponents

Component (Name "<MPN>") (PartCount 1) (DesPrefix "C?")
Description (Value "<DES>")
Comment (Value "<capacitance>")
Parameter (Name "MPN") (Location 0, -78.74) (Height 60) (Rotation 0) (Justification TopCenter) (Visible True) (Font "Arial") (Bold True) (Italic False) (Underline False) (Value "<MPN>") (Part 1)
Parameter (Name "DES") (Location 0, -137.80) (Height 60) (Rotation 0) (Justification TopCenter) (Visible True) (Font "Arial") (Bold True) (Italic False) (Underline False) (Value "<DES>") (Part 1)
Parameter (Name "Manufacturer") (Location 0, 0) (Height 60) (Rotation 0) (Justification Center) (Font "Arial") (Bold False) (Italic False) (Underline False) (Value "<manufacturer>") (Part 1)
Parameter (Name "Datasheet") (Location 0, 0) (Height 60) (Rotation 0) (Justification Center) (Font "Arial") (Bold False) (Italic False) (Underline False) (Value "<datasheet_url>") (Part 1)
Pin (Location -137.80, 0) (Rotation 0) (PinType Passive) (Length 118.11) (Width 0) (Designator Hidden "1") (Name Hidden "~") (PinSwap 0) (PartSwap 0) (PinSeq 1) (Part 1)
Pin (Location 137.80, 0) (Rotation 180) (PinType Passive) (Length 118.11) (Width 0) (Designator Hidden "2") (Name Hidden "~") (PinSwap 0) (PartSwap 0) (PinSeq 2) (Part 1)
Line (Width 5) (Start -19.69, -59.06) (End -19.69, 59.06) (Part 1)
Line (Width 5) (Start 19.69, -59.06) (End 19.69, 59.06) (Part 1)
Footprint (Name "<footprint_name>")
EndComponent

EndComponents
```
