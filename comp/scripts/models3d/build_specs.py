"""Rebuilds the lib_create_3d_model parameter sets (mm, footprint origin, Z up) used for the Rearguard footprints.

Usage: python3 build_specs.py [out_dir]   writes one <footprint>.json per model.
Each file is {footprint, source, drawing, solids, groups?} and goes straight into
lib_create_3d_model (always give prism `axis`; lead groups are placed with `instance`).
"""
import json, os, sys

def lead(profile, x0, x1, name):
    return {"kind": "prism", "name": name, "role": "tin", "axis": "x", "x0": x0, "x1": x1, "profile": profile}

def inst_ring(vals, group="lead"):
    out = []
    for rot, key in ((0, "dy"), (180, "dy"), (90, "dx"), (270, "dx")):
        for v in vals:
            d = {"kind": "instance", "group": group, "rot": rot, "dx": 0, "dy": 0, "dz": 0}
            d[key] = v
            out.append(d)
    return out

def chip(name, L, W, H, T, kind):
    if kind == "res":
        body = {"kind": "box", "name": "body", "role": "body", "x0": -L/2, "y0": -W/2, "z0": 0, "x1": L/2, "y1": W/2, "z1": round(H-0.05, 3)}
        ty, tz = round(W/2+0.01, 3), H
        drawing = {"body_x": [round(L-.1, 3), round(L+.1, 3)], "body_y": [round(W-.1, 3), round(W+.1, 3)], "height": [0, round(H+.05, 3)]}
        src = "Yageo AC/RC series typical dims (not fetched; Vishay CRCW p.11 cross-check)"
    else:
        body = {"kind": "box", "name": "body", "role": "ceramic_ivory", "x0": -L/2, "y0": -W/2, "z0": 0, "x1": L/2, "y1": W/2, "z1": H}
        ty, tz = round(W/2, 3), H
        drawing = {"body_x": [round(L-.1, 3), round(L+.1, 3)], "body_y": [round(W-.1, 3), round(W+.1, 3)], "height": [0, round(H+.1, 3)]}
        src = "KEMET C-series typical dims (not fetched; Murata GRM31 p.5 and TDK CGA5L3 p.1 for 1206)"
    t1 = {"kind": "box", "name": "t1", "role": "tin", "x0": -L/2, "y0": -ty, "z0": 0, "x1": round(-L/2+T, 3), "y1": ty, "z1": tz}
    t2 = {"kind": "box", "name": "t2", "role": "tin", "x0": round(L/2-T, 3), "y0": -ty, "z0": 0, "x1": L/2, "y1": ty, "z1": tz}
    return {"footprint": name, "source": src, "drawing": drawing, "solids": [body, t1, t2]}

P_SOT = [[-1.2,0],[-0.85,0],[-0.65,0.3],[-0.45,0.3],[-0.45,0.41],[-0.68,0.41],[-0.88,0.11],[-1.2,0.11]]
P_SOT_M = [[1.2,0],[0.85,0],[0.65,0.3],[0.45,0.3],[0.45,0.41],[0.68,0.41],[0.88,0.11],[1.2,0.11]]
P_323 = [[-1.05,0],[-0.68,0],[-0.6,0.37],[-0.4,0.37],[-0.4,0.55],[-0.66,0.55],[-0.78,0.18],[-1.05,0.18]]

def specs():
    S = []
    S.append({"footprint": "SOT23", "source": "Diodes ZXMP3A13F DS33573 Rev 2-2, SOT23 package outline p.7; nominal dims; bend shape assumed",
        "drawing": {"body_x": [2.8, 3], "body_y": [1.2, 1.4], "height": [0, 1.1], "span_y": [2.3, 2.5]},
        "solids": [{"kind": "box", "name": "body", "role": "body", "x0": -1.45, "y0": -0.65, "z0": 0.05, "x1": 1.45, "y1": 0.65, "z1": 0.975, "edge_r": 0.05},
                   {"kind": "dot", "name": "pin1_mark", "role": "laser", "cx": -1.1, "cy": -0.4, "r": 0.12, "z1": 0.975},
                   lead(P_SOT, -1.15, -0.75, "lead1"), lead(P_SOT, 0.75, 1.15, "lead2"), lead(P_SOT_M, -0.2, 0.2, "lead3")]})
    S.append({"footprint": "TO-236", "source": "onsemi MMBT3906L/MMBT3904L, case 318 SOT-23 (TO-236) issue AU; nominal dims; bend shape assumed",
        "drawing": {"body_x": [2.8, 3.04], "body_y": [1.2, 1.4], "height": [0, 1.11], "span_y": [2.1, 2.64]},
        "groups": {"lead": [lead([[1.2,0],[0.8,0],[0.66,0.3],[0.4,0.3],[0.4,0.44],[0.8,0.44],[0.94,0.14],[1.2,0.14]], -0.22, 0.22, "lead_gw")]},
        "solids": [{"kind": "box", "name": "body", "role": "body", "x0": -1.45, "y0": -0.65, "z0": 0.06, "x1": 1.45, "y1": 0.65, "z1": 1, "edge_r": 0.08},
                   {"kind": "dot", "name": "pin1_mark", "role": "laser", "cx": -1.05, "cy": -0.3, "r": 0.12, "z1": 1},
                   {"kind": "instance", "name": "lead3", "group": "lead", "rot": 0, "dx": 0, "dy": 0, "dz": 0},
                   {"kind": "instance", "name": "lead1", "group": "lead", "rot": 180, "dx": -0.95, "dy": 0, "dz": 0},
                   {"kind": "instance", "name": "lead2", "group": "lead", "rot": 180, "dx": 0.95, "dy": 0, "dz": 0}]})
    S.append({"footprint": "SOT-323", "source": "onsemi BAV99WT1G, SC-70 (SOT-323) case 419 issue R, p.4; nominal dims; gull-wing bend estimated from the end view",
        "drawing": {"body_x": [1.8, 2.2], "body_y": [1.15, 1.35], "height": [0, 1], "span_y": [2, 2.4]},
        "solids": [{"kind": "box", "name": "body", "role": "body", "x0": -1, "y0": -0.62, "z0": 0.2, "x1": 1, "y1": 0.62, "z1": 0.9},
                   lead(P_323, -0.825, -0.475, "lead1"), lead(P_323, 0.475, 0.825, "lead2"),
                   lead([[-y, z] for y, z in P_323], -0.175, 0.175, "lead3"),
                   {"kind": "dot", "name": "pin1", "role": "ink", "cx": -0.7, "cy": -0.3, "r": 0.1, "z1": 0.9}]})
    S.append({"footprint": "SOD-123", "source": "Central Semiconductor CMHZ4678-4717 R7, SOD-123 case mechanical outline p.2; nominal dims; bend shape assumed",
        "drawing": {"body_x": [2.5, 2.8], "body_y": [1.4, 1.8], "height": [0, 1.35], "span_x": [3.6, 3.9]},
        "solids": [{"kind": "box", "name": "body", "role": "body", "x0": -1.325, "y0": -0.8, "z0": 0.05, "x1": 1.325, "y1": 0.8, "z1": 1.2},
                   {"kind": "box", "name": "cathode_band", "role": "white", "x0": -0.925, "y0": -0.8, "z0": 1.2, "x1": -0.525, "y1": 0.8, "z1": 1.21},
                   {"kind": "prism", "name": "lead_pin1_cathode", "role": "tin", "axis": "y", "y0": -0.3, "y1": 0.3, "profile": [[-1.875,0],[-1.52,0],[-1.3,0.35],[-1,0.35],[-1,0.5],[-1.38,0.5],[-1.62,0.15],[-1.875,0.15]]},
                   {"kind": "prism", "name": "lead_pin2_anode", "role": "tin", "axis": "y", "y0": -0.3, "y1": 0.3, "profile": [[1.875,0],[1.875,0.15],[1.62,0.15],[1.38,0.5],[1,0.5],[1,0.35],[1.3,0.35],[1.52,0]]}]})
    S.append({"footprint": "SMA", "source": "Diodes B320A-B360A DS30891 Rev 20-2, p.6 package outline; nominal dims; lead bend and band assumed",
        "drawing": {"body_x": [4, 4.6], "body_y": [2.29, 2.92], "height": [0, 1.63], "span_x": [4.8, 5.59]},
        "groups": {"lead": [{"kind": "prism", "name": "lead_a", "role": "tin", "axis": "y", "y0": -1.09, "y1": 1.09, "profile": [[1.46,0],[2.6,0],[2.6,0.73],[2,0.73],[2,0.5],[2.37,0.5],[2.37,0.23],[1.46,0.23]]}]},
        "solids": [{"kind": "box", "name": "body", "role": "body", "x0": -2.15, "y0": -1.3, "z0": 0.125, "x1": 2.15, "y1": 1.3, "z1": 1.45, "edge_r": 0.1},
                   {"kind": "box", "name": "cathode_band", "role": "white", "x0": -1.85, "y0": -1.3, "z0": 1.4, "x1": -1.45, "y1": 1.3, "z1": 1.45},
                   {"kind": "instance", "name": "lead_anode", "group": "lead", "rot": 0, "dx": 0, "dy": 0, "dz": 0},
                   {"kind": "instance", "name": "lead_cathode", "group": "lead", "rot": 180, "dx": 0, "dy": 0, "dz": 0}]})
    S.append({"footprint": "SMB", "source": "onsemi 1SMB5.0AT3G series case 403A-03 Issue H p.7; nominal dims; J-lead shape assumed",
        "drawing": {"body_x": [4.06, 4.6], "body_y": [3.3, 3.95], "height": [0, 2.28], "span_x": [5.21, 5.6]},
        "groups": {"lead_px": [{"kind": "box", "name": "leg", "role": "tin", "x0": 2.49, "y0": -1.015, "z0": 0, "x1": 2.72, "y1": 1.015, "z1": 1.23},
                               {"kind": "box", "name": "arm", "role": "tin", "x0": 2, "y0": -1.015, "z0": 1, "x1": 2.72, "y1": 1.015, "z1": 1.23},
                               {"kind": "box", "name": "foot", "role": "tin", "x0": 1.7, "y0": -1.015, "z0": 0, "x1": 2.72, "y1": 1.015, "z1": 0.23}]},
        "solids": [{"kind": "box", "name": "body", "role": "body", "x0": -2.16, "y0": -1.78, "z0": 0.1, "x1": 2.16, "y1": 1.78, "z1": 2.2, "edge_r": 0.1},
                   {"kind": "box", "name": "cathode_band", "role": "white", "x0": -1.95, "y0": -1.78, "z0": 2.2, "x1": -1.45, "y1": 1.78, "z1": 2.21},
                   {"kind": "instance", "name": "lead_pin2", "group": "lead_px", "rot": 0, "dx": 0, "dy": 0, "dz": 0},
                   {"kind": "instance", "name": "lead_pin1", "group": "lead_px", "rot": 180, "dx": 0, "dy": 0, "dz": 0}]})
    S.append({"footprint": "D0008A", "source": "TI LMH6642/6643/6644 SNOS966Q, D0008A package outline p.31; nominal dims; bend shape assumed",
        "drawing": {"body_x": [3.81, 3.98], "body_y": [4.81, 5], "height": [0, 1.75], "span_x": [5.8, 6.19]},
        "groups": {"leadR": [{"kind": "prism", "name": "lead", "role": "tin", "axis": "y", "y0": -0.205, "y1": 0.205, "profile": [[3,0],[2.4,0],[2.1,0.55],[1.7,0.55],[1.7,0.74],[2.25,0.74],[2.55,0.19],[3,0.19]]}]},
        "solids": [{"kind": "box", "name": "body", "role": "body", "x0": -1.95, "y0": -2.45, "z0": 0.15, "x1": 1.95, "y1": 2.45, "z1": 1.65, "edge_r": 0.1, "taper": 5},
                   {"kind": "dot", "name": "pin1", "role": "laser", "cx": -1.3, "cy": 1.9, "r": 0.3, "z1": 1.65}] +
                  [{"kind": "instance", "group": "leadR", "name": f"p{n}", "rot": r, "dx": 0, "dy": y, "dz": 0}
                   for n, r, y in [(8,0,1.905),(7,0,0.635),(6,0,-0.635),(5,0,-1.905),(4,180,-1.905),(3,180,-0.635),(2,180,0.635),(1,180,1.905)]]})
    S.append({"footprint": "SOT26", "source": "Diodes AP5100 DS32130 Rev 3-2, package outline p.11; nominal dims; bend shape assumed",
        "drawing": {"body_x": [2.9, 3.1], "body_y": [1.5, 1.7], "height": [0, 1.3], "span_y": [2.7, 3]},
        "groups": {"lead": [lead([[1.4,0],[1,0],[0.85,0.4],[0.6,0.4],[0.6,0.55],[0.95,0.55],[1.15,0.15],[1.4,0.15]], -0.19, 0.19, "lead_top")]},
        "solids": [{"kind": "box", "name": "body", "role": "body", "x0": -1.5, "y0": -0.8, "z0": 0.05, "x1": 1.5, "y1": 0.8, "z1": 1.1},
                   {"kind": "dot", "name": "pin1_mark", "role": "laser", "cx": -1.05, "cy": -0.5, "r": 0.15, "z1": 1.1}] +
                  [{"kind": "instance", "group": "lead", "name": f"l{i+1}", "rot": r, "dx": x, "dy": 0, "dz": 0}
                   for i, (r, x) in enumerate([(0,-0.95),(0,0),(0,0.95),(180,-0.95),(180,0),(180,0.95)])]})
    ring12 = [round(-2.75 + 0.5*i, 2) for i in range(12)]
    ring8 = [round(-1.75 + 0.5*i, 2) for i in range(8)]
    S.append({"footprint": "LQFP48", "source": "STM32F103x8/xB DS5319 Rev 20, Table 62 LQFP48 mechanical data p.99; nominal dims; gull-wing bend shape assumed",
        "drawing": {"body_x": [6.9, 7.1], "body_y": [6.9, 7.1], "height": [0, 1.6], "span_x": [8.9, 9.1], "span_y": [8.9, 9.1]},
        "groups": {"lead": [{"kind": "prism", "name": "lead_gull", "role": "tin", "axis": "y", "y0": -0.11, "y1": 0.11, "profile": [[4.5,0],[3.9,0],[3.62,0.7],[3.4,0.7],[3.4,0.85],[3.74,0.85],[4.05,0.15],[4.5,0.15]]}]},
        "solids": [{"kind": "box", "name": "body", "role": "body", "x0": -3.5, "y0": -3.5, "z0": 0.1, "x1": 3.5, "y1": 3.5, "z1": 1.5, "edge_r": 0.1},
                   {"kind": "dot", "name": "pin1_mark", "role": "laser", "cx": -2.7, "cy": 2.7, "r": 0.4, "z1": 1.5}] + inst_ring(ring12)})
    S.append({"footprint": "CP-32-12", "source": "ADV7280 data sheet Rev A, Figure 18 CP-32-12 outline dimensions p.28; nominal dims",
        "drawing": {"body_x": [4.9, 5.1], "body_y": [4.9, 5.1], "height": [0, 0.8]},
        "groups": {"lead": [{"kind": "box", "name": "lead", "role": "tin", "x0": -2.5, "y0": -0.125, "z0": 0, "x1": -2.1, "y1": 0.125, "z1": 0.2}]},
        "solids": [{"kind": "box", "name": "body", "role": "body", "x0": -2.5, "y0": -2.5, "z0": 0.02, "x1": 2.5, "y1": 2.5, "z1": 0.75},
                   {"kind": "box", "name": "ep", "role": "metal", "x0": -1.8, "y0": -1.8, "z0": 0, "x1": 1.8, "y1": 1.8, "z1": 0.2},
                   {"kind": "dot", "name": "pin1_dot", "role": "laser", "cx": -1.9, "cy": 1.9, "r": 0.2, "z1": 0.75}] + inst_ring(ring8)})
    S.append({"footprint": "T3255Y-8", "source": "ADI/Maxim 21-100156 rev F p.1 (32L TQFN 5x5x0.75 side-wettable); nominal dims; pin-1 chamfer on pad assumed",
        "drawing": {"body_x": 5, "body_y": 5, "height": [0, 0.8]},
        "groups": {"lead": [{"kind": "box", "name": "lead", "role": "tin", "x0": -2.5, "y0": -0.125, "z0": 0, "x1": -2.1, "y1": 0.125, "z1": 0.203}]},
        "solids": [{"kind": "box", "name": "body", "role": "body", "x0": -2.5, "y0": -2.5, "z0": 0.02, "x1": 2.5, "y1": 2.5, "z1": 0.75},
                   {"kind": "extrude", "name": "epad", "role": "metal", "outline": [[-1.2,1.55],[1.55,1.55],[1.55,-1.55],[-1.55,-1.55],[-1.55,1.2]], "z0": 0, "z1": 0.203},
                   {"kind": "dot", "name": "pin1", "role": "laser", "cx": -2, "cy": 2, "r": 0.15, "z1": 0.75}] + inst_ring(ring8)})
    S.append({"footprint": "IND1028", "source": "Wurth WE-TPC 7440650033 rev 003.007 p.1: body 10x10 octagon, height 2.78, terminals 4.2 wide at the +-y flats; land pattern 4.6 x 1.8 pads, 7.2 gap; chamfer and terminal details assumed",
        "drawing": {"body_x": [9.7, 10.3], "body_y": [9.7, 10.3], "height": [0, 3.08]},
        "solids": [{"kind": "extrude", "name": "body_oct", "role": "body", "outline": [[-2.2,5],[2.2,5],[5,2.2],[5,-2.2],[2.2,-5],[-2.2,-5],[-5,-2.2],[-5,2.2]], "z0": 0.15, "z1": 2.58},
                   {"kind": "cylinder", "name": "core_cap", "role": "ceramic", "r": 3.7, "cx": 0, "cy": 0, "z0": 2.58, "z1": 2.78},
                   {"kind": "box", "name": "foot1", "role": "tin", "x0": -2.1, "y0": 3.6, "z0": 0, "x1": 2.1, "y1": 5, "z1": 0.15},
                   {"kind": "box", "name": "wall1", "role": "tin", "x0": -2.1, "y0": 4.8, "z0": 0, "x1": 2.1, "y1": 5, "z1": 1.3},
                   {"kind": "box", "name": "foot2", "role": "tin", "x0": -2.1, "y0": -5, "z0": 0, "x1": 2.1, "y1": -3.6, "z1": 0.15},
                   {"kind": "box", "name": "wall2", "role": "tin", "x0": -2.1, "y0": -5, "z0": 0, "x1": 2.1, "y1": -4.8, "z1": 1.3},
                   {"kind": "dot", "name": "pin1_dot", "role": "ink", "cx": 0, "cy": 3.1, "r": 0.25, "z1": 2.78}]})
    S.append({"footprint": "IND7040", "source": "Wurth WE-HCI 744311470 rev 005.000; nominal dims (terminal 1.2 wide x 1.8 long); standoff assumed",
        "drawing": {"body_x": [6.6, 7.2], "body_y": [6.7, 7.3], "height": [0, 4], "span_y": [6.7, 7.3]},
        "solids": [{"kind": "box", "name": "body", "role": "body", "x0": -3.45, "y0": -3.4, "z0": 0.25, "x1": 3.45, "y1": 3.4, "z1": 3.8, "edge_r": 0.3},
                   {"kind": "box", "name": "t1_foot", "role": "tin", "x0": -0.6, "y0": 1.7, "z0": 0, "x1": 0.6, "y1": 3.5, "z1": 0.25},
                   {"kind": "box", "name": "t1_side", "role": "tin", "x0": -0.6, "y0": 3.3, "z0": 0, "x1": 0.6, "y1": 3.5, "z1": 3},
                   {"kind": "box", "name": "t2_foot", "role": "tin", "x0": -0.6, "y0": -3.5, "z0": 0, "x1": 0.6, "y1": -1.7, "z1": 0.25},
                   {"kind": "box", "name": "t2_side", "role": "tin", "x0": -0.6, "y0": -3.5, "z0": 0, "x1": 0.6, "y1": -3.3, "z1": 3},
                   {"kind": "dot", "name": "pin1_mark", "role": "ink", "cx": -2.5, "cy": 2.5, "r": 0.4, "z1": 3.8}]})
    S.append({"footprint": "PowerDI5", "source": "Diodes PDU540 DS30759 Rev 4-2, PowerDI5 package outline p.5; nominal dims; slug extent estimated",
        "drawing": {"body_x": [3.9, 4.05], "body_y": [5.3, 5.45], "height": [0, 1.15], "span_y": [6.4, 6.6]},
        "solids": [{"kind": "box", "name": "body", "role": "body", "x0": -1.983, "y0": -2.685, "z0": 0.025, "x1": 1.983, "y1": 2.685, "z1": 1.1, "taper": 5},
                   {"kind": "box", "name": "anode_lead_a", "role": "tin", "x0": -1.365, "y0": -3.252, "z0": 0, "x1": -0.475, "y1": -2.405, "z1": 0.381},
                   {"kind": "box", "name": "anode_lead_b", "role": "tin", "x0": 0.475, "y0": -3.252, "z0": 0, "x1": 1.365, "y1": -2.405, "z1": 0.381},
                   {"kind": "box", "name": "heat_slug", "role": "tin", "x0": -1.527, "y0": -1.049, "z0": 0, "x1": 1.527, "y1": 2.5, "z1": 0.381},
                   {"kind": "box", "name": "cathode_tab", "role": "tin", "x0": -0.89, "y0": 2.4, "z0": 0, "x1": 0.89, "y1": 3.252, "z1": 0.381},
                   {"kind": "dot", "name": "pin1_mark", "role": "laser", "cx": -1.2, "cy": 2, "r": 0.25, "z1": 1.1}]})
    circle = lambda cx, cz, r, n=16: [[round(cx + r*__import__("math").cos(2*__import__("math").pi*k/n), 3), round(cz + r*__import__("math").sin(2*__import__("math").pi*k/n), 3)] for k in range(n)]
    S.append({"footprint": "TO-220AB", "source": "Vishay SUP53P06-20 doc 68633 / package drawing 71195 (DWG 5471) TO-220AB, p.6; nominal dims; plastic width 9.6 mm and top chamfer scaled from the drawing figure",
        "drawing": {"body_x": [10.04, 10.51], "body_y": [4.25, 4.65], "height": [0, 19.31]},
        "solids": [{"kind": "prism", "name": "plastic", "role": "body", "axis": "x", "x0": -4.8, "x1": 4.8, "profile": [[-1.54,3.57],[1.64,3.57],[1.64,12.47],[0,12.47],[-1.54,11.17]]},
                   {"kind": "prism", "name": "tab", "role": "nickel", "axis": "y", "y0": 1.64, "y1": 2.91, "profile": [[-5.14,3.57],[5.14,3.57],[5.14,17.94],[4.34,18.74],[-4.34,18.74],[-5.14,17.94]]},
                   {"kind": "prism", "name": "tabhole", "role": "cut", "axis": "y", "cut_from": ["tab"], "y0": 1.4, "y1": 3.1, "profile": circle(0, 15.94, 1.87)},
                   {"kind": "box", "name": "s1", "role": "tin", "x0": -3.275, "y0": -0.2425, "z0": 0, "x1": -1.805, "y1": 0.2425, "z1": 3.57},
                   {"kind": "box", "name": "s2", "role": "tin", "x0": -0.735, "y0": -0.2425, "z0": 0, "x1": 0.735, "y1": 0.2425, "z1": 3.57},
                   {"kind": "box", "name": "s3", "role": "tin", "x0": 1.805, "y0": -0.2425, "z0": 0, "x1": 3.275, "y1": 0.2425, "z1": 3.57},
                   {"kind": "box", "name": "l1", "role": "tin", "x0": -2.965, "y0": -0.2425, "z0": -10.12, "x1": -2.115, "y1": 0.2425, "z1": 0},
                   {"kind": "box", "name": "l2", "role": "tin", "x0": -0.425, "y0": -0.2425, "z0": -10.12, "x1": 0.425, "y1": 0.2425, "z1": 0},
                   {"kind": "box", "name": "l3", "role": "tin", "x0": 2.115, "y0": -0.2425, "z0": -10.12, "x1": 2.965, "y1": 0.2425, "z1": 0},
                   {"kind": "dot", "name": "pin1_dot", "role": "ink", "cx": -3.5, "cy": 0.8, "r": 0.5, "z1": 12.47}]})
    S.append({"footprint": "CAPAE-10X10.2", "source": "Panasonic FC series (type V) size code G, p.1 dimension table: D 10.0, L 10.2, A/B 10.3, H 12.0 max, I 3.5, W 0.9, P 4.6, K 0.7; seat height H-L, terminal foot thickness and riser assumed",
        "drawing": {"body_x": [10.1, 10.5], "body_y": [10.1, 10.5], "height": [0, 12]},
        "solids": [{"kind": "box", "name": "seat", "role": "body", "x0": -5.15, "y0": -5.15, "z0": 0.05, "x1": 5.15, "y1": 5.15, "z1": 1.8, "edge_r": 0.3},
                   {"kind": "cylinder", "name": "can", "role": "metal", "r": 5, "cx": 0, "cy": 0, "z0": 1.8, "z1": 12},
                   {"kind": "dot", "name": "polarity", "role": "ink", "cx": -3.4, "cy": 0, "r": 0.5, "z1": 12},
                   {"kind": "box", "name": "foot1", "role": "tin", "x0": -5.85, "y0": -0.45, "z0": 0, "x1": -2.3, "y1": 0.45, "z1": 0.2},
                   {"kind": "box", "name": "riser1", "role": "tin", "x0": -5.85, "y0": -0.45, "z0": 0, "x1": -5.6, "y1": 0.45, "z1": 1.2},
                   {"kind": "box", "name": "foot2", "role": "tin", "x0": 2.3, "y0": -0.45, "z0": 0, "x1": 5.85, "y1": 0.45, "z1": 0.2},
                   {"kind": "box", "name": "riser2", "role": "tin", "x0": 5.6, "y0": -0.45, "z0": 0, "x1": 5.85, "y1": 0.45, "z1": 1.2}]})
    S.append({"footprint": "TP-TH", "source": "Keystone THM test points catalog p.56, multipurpose: base 3.0 dia, loop 3.2 OD / 1.8 ID, 8.1 above board, 11.3 overall, mounting hole 1.6, terminal .38 x .81; base height and loop shape assumed",
        "drawing": {"body_x": [2.9, 3.1], "body_y": [2.9, 3.1], "height": [0, 8.2]},
        "solids": [{"kind": "cylinder", "name": "base", "role": "body", "r": 1.5, "cx": 0, "cy": 0, "z0": 0, "z1": 3},
                   {"kind": "box", "name": "post", "role": "metal", "x0": -0.405, "y0": -0.19, "z0": 3, "x1": 0.405, "y1": 0.19, "z1": 5},
                   {"kind": "prism", "name": "ring", "role": "metal", "axis": "y", "y0": -0.19, "y1": 0.19, "profile": circle(0, 6.5, 1.6)},
                   {"kind": "prism", "name": "ringhole", "role": "cut", "cut_from": ["ring"], "axis": "y", "y0": -0.3, "y1": 0.3, "profile": circle(0, 6.5, 0.9)},
                   {"kind": "box", "name": "pin", "role": "metal", "x0": -0.405, "y0": -0.19, "z0": -3.2, "x1": 0.405, "y1": 0.19, "z1": 0}]})
    S.append({"footprint": "BANANA-5.5", "source": "Keystone catalog p.111, 575-4 non-insulated standard banana jack: L 5.5, accepts 4.5 plug, panel hole 4.2; flange, shank and socket depth assumed",
        "drawing": {"body_x": [6.3, 6.5], "body_y": [6.3, 6.5], "height": [0, 5.6]},
        "solids": [{"kind": "cylinder", "name": "barrel", "role": "metal", "r": 3.2, "cx": 0, "cy": 0, "z0": 0, "z1": 5.5},
                   {"kind": "cylinder", "name": "socket", "role": "cut", "cut_from": ["barrel"], "r": 2.25, "cx": 0, "cy": 0, "z0": 1, "z1": 5.6},
                   {"kind": "cylinder", "name": "shank", "role": "metal", "r": 2.1, "cx": 0, "cy": 0, "z0": -1.6, "z1": 0}]})
    for n, L, W, H, T in [("0201",.6,.3,.23,.12),("0402",1.0,.5,.35,.25),("0603",1.6,.8,.45,.30),("0805",2.0,1.25,.5,.4),("1206",3.1,1.6,.55,.45)]:
        S.append(chip("RES"+n, L, W, H, T, "res"))
    for n, L, W, H, T in [("0201",.6,.3,.3,.15),("0402",1.0,.5,.5,.25),("0603",1.6,.8,.8,.35),("0805",2.0,1.25,1.25,.5),("1206",3.2,1.6,1.6,.5)]:
        S.append(chip("CAP"+n, L, W, H, T, "cap"))
    return S

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "specs")
    os.makedirs(out, exist_ok=True)
    for s in specs():
        json.dump(s, open(os.path.join(out, s["footprint"] + ".json"), "w"), indent=1)
    print(len(specs()), "specs ->", out)
