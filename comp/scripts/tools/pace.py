import time,os,sys
f=os.path.join(os.path.expanduser("~"),".last_altium_call")
gap=float(sys.argv[1]) if len(sys.argv)>1 else 4.0
try: last=float(open(f).read())
except Exception: last=0
w=last+gap-time.time()
if w>0: time.sleep(w)
open(f,"w").write(str(time.time()))
