import json
L=[("7","NRST","io"),("44","BOOT0","input"),None,("5","PD0-OSC_IN","input"),("6","PD1-OSC_OUT","output"),None,("2","PC13-TAMPER-RTC","io"),("3","PC14-OSC32_IN","io"),("4","PC15-OSC32_OUT","io"),None,
("10","PA0-WKUP","io"),("11","PA1","io"),("12","PA2","io"),("13","PA3","io"),("14","PA4","io"),("15","PA5","io"),("16","PA6","io"),("17","PA7","io"),("29","PA8","io"),("30","PA9","io"),("31","PA10","io"),("32","PA11","io"),("33","PA12","io"),("34","PA13-SWDIO","io"),("37","PA14-SWCLK","io"),("38","PA15","io")]
R=[("18","PB0"),("19","PB1"),("20","PB2-BOOT1"),("39","PB3"),("40","PB4"),("41","PB5"),("42","PB6"),("43","PB7"),("45","PB8"),("46","PB9"),("21","PB10"),("22","PB11"),("25","PB12"),("26","PB13"),("27","PB14"),("28","PB15")]
PL=[("1","VBAT"),None,("24","VDD_1"),("36","VDD_2"),("48","VDD_3"),None,("9","VDDA")]
PR=[("23","VSS_1"),("35","VSS_2"),("47","VSS_3"),None,("8","VSSA")]
p1=[];p2=[]
for i,r in enumerate(L):
    if r: p1.append({"designator":r[0],"name":r[1],"x":0,"y":-100*i,"length":300,"rotation":180,"electrical_type":r[2],"owner_part_id":1})
for i,r in enumerate(R):
    p1.append({"designator":r[0],"name":r[1],"x":1500,"y":-100*i,"length":300,"rotation":0,"electrical_type":"io","owner_part_id":1})
for i,r in enumerate(PL):
    if r: p2.append({"designator":r[0],"name":r[1],"x":0,"y":-100*i,"length":300,"rotation":180,"electrical_type":"power","owner_part_id":2})
for i,r in enumerate(PR):
    if r: p2.append({"designator":r[0],"name":r[1],"x":1500,"y":-100*i,"length":300,"rotation":0,"electrical_type":"power","owner_part_id":2})
import sys
out = sys.argv[1] if len(sys.argv) > 1 else "pins.json"
print(len(p1),len(p2))
with open(out, "w", encoding="utf-8") as f:
    json.dump(p1+p2,f,separators=(",",":"))
print(json.dumps(p1+p2,separators=(",",":")))
