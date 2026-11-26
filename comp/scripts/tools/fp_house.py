import json, math, sys
def up05(v): return round(math.ceil(round(v/0.05,6))*0.05,3)
def gen(fp):
    n=fp["name"]; px=fp["px"]; pl=fp["pl"]; ph=fp["ph"]; bl=fp["bl"]; bw=fp["bw"]
    ox=round(px+pl/2+0.15,3); oy=round(ph/2+0.15,3)
    cx=max(fp["cx"],up05(ox+0.1)); cy=max(fp["cy"],up05(oy+0.1))
    T=[]
    def box(x,y,w,layer):
        for a in [(-x,y,x,y),(x,y,x,-y),(x,-y,-x,-y),(-x,-y,-x,y)]:
            T.append({"x1":a[0],"y1":a[1],"x2":a[2],"y2":a[3],"width":w,"layer":layer})
    def ln(x1,y1,x2,y2,layer="Mechanical5",w=0.1):
        T.append({"x1":round(x1,3),"y1":round(y1,3),"x2":round(x2,3),"y2":round(y2,3),"width":w,"layer":layer})
    box(ox,oy,0.2,"TopOverlay"); box(cx,cy,0.1,"Mechanical27"); box(round(bl/2,3),round(bw/2,3),0.1,"Mechanical19")
    ln(-0.3,0,0.3,0,"Mechanical37"); ln(0,-0.3,0,0.3,"Mechanical37")
    bx=round(bl/2,3); by=round(bw/2,3)
    yd=cy+0.85; al=min(0.5,bx)
    ln(-bx,by,-bx,yd+0.1); ln(bx,by,bx,yd+0.1); ln(-bx,yd,bx,yd)
    for s in (-1,1):
        ln(s*bx,yd,s*(bx-al),yd+0.15); ln(s*bx,yd,s*(bx-al),yd-0.15)
    xd=-(cx+0.75); av=min(0.4,by)
    ln(-bx,by,xd-0.1,by); ln(-bx,-by,xd-0.1,-by); ln(xd,-by,xd,by)
    for s in (-1,1):
        ln(xd,s*by,xd-0.15,s*(by-av)); ln(xd,s*by,xd+0.15,s*(by-av))
    texts=[{"text":".Designator","x":round(xd,3),"y":round(-(cy+1.15),3),"size":1,"layer":"Mechanical33"},
           {"text":"%.2fmm"%bl,"x":-1.6,"y":round(yd+0.8,3),"size":1,"layer":"Mechanical5"},
           {"text":"%.2fmm"%bw,"x":round(xd-0.4,3),"y":-1.6,"size":1,"layer":"Mechanical5","rotation":90}]
    return {"name":n,"cx":cx,"cy":cy,"tracks":T,"texts":texts}
if __name__=="__main__":
    fps=json.load(open(sys.argv[1]))
    out=[gen(f) for f in fps]
    json.dump(out,open(sys.argv[2],"w"))
    for o in out: print(o["name"],"courtyard",o["cx"],o["cy"],"tracks",len(o["tracks"]))
