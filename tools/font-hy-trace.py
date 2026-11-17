"""HY Trace: Edu (AU School Handwriting, OFL) → 정해진 굵기 · 똑바로 세움(기울기 풀기) · 이름 바꿈 · 라틴 기본만"""
import sys, math
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools import subset
src, out, deg, wght = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
f=TTFont(src)
f=instancer.instantiateVariableFont(f, {"wght": wght})
gs=f.getGlyphSet(); glyf=f['glyf']; k=math.tan(math.radians(deg))
order=f.getGlyphOrder()
new={}
for g in order:
    if glyf[g].isComposite() or glyf[g].numberOfContours==0: continue
    p=TTGlyphPen(gs); gs[g].draw(TransformPen(p, (1,0,-k,1,0,0))); new[g]=p.glyph()
for g,v in new.items(): glyf[g]=v
for g in order:
    gl=glyf[g]; gl.recalcBounds(glyf)
    adv,lsb=f['hmtx'][g]; f['hmtx'][g]=(adv, getattr(gl,'xMin',0) if gl.numberOfContours!=0 else lsb)
f['post'].italicAngle=0
# 이름
nm=f['name']
for r in list(nm.names):
    if r.nameID in (1,4,16,21): r.string="HY Trace"
    elif r.nameID==6: r.string="HYTrace-Regular"
    elif r.nameID in (2,17,22): r.string="Regular"
    elif r.nameID==3: r.string="HY Trace; derived from AU School Handwriting Fonts (OFL)"
# 라틴 기본만
opt=subset.Options(); opt.layout_features=['kern','liga','calt','ccmp','locl','mark','mkmk']; opt.flavor=None; opt.name_IDs=['*']; opt.notdef_outline=True
s=subset.Subsetter(opt); s.populate(unicodes=list(range(0x20,0x7F))+[0xA0,0x2019,0x2018,0x201C,0x201D,0x2026,0x2013,0x2014]); s.subset(f)
f.save(out); print(out, __import__('os').path.getsize(out))
