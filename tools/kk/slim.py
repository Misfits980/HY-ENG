import json, glob, os, shutil, sys
from PIL import Image
src, dst, maxpx = sys.argv[1], sys.argv[2], int(sys.argv[3])
os.makedirs(dst, exist_ok=True)
used=set(); conv={}
def webp(name):
    if name in conv: return conv[name]
    b=os.path.splitext(name)[0]+'.webp'
    im=Image.open(os.path.join(src,name)); im.load()
    if max(im.size)>maxpx: im.thumbnail((maxpx,maxpx), Image.LANCZOS)
    mode='RGBA' if (im.mode in ('RGBA','LA') or 'transparency' in im.info) else 'RGB'
    im.convert(mode).save(os.path.join(dst,b),'WEBP',quality=86,method=6)
    conv[name]=b; return b
for f in sorted(glob.glob(os.path.join(glob.escape(src),'*.gltf'))):
    j=json.load(open(f))
    for m in j.get('materials',[]):
        for k in ('normalTexture','occlusionTexture','emissiveTexture'): m.pop(k,None)
        p=m.get('pbrMetallicRoughness',{}); p.pop('metallicRoughnessTexture',None)
    # keep only textures referenced by baseColorTexture
    keepT=[]; 
    for m in j.get('materials',[]):
        bt=m.get('pbrMetallicRoughness',{}).get('baseColorTexture')
        if bt is not None and bt['index'] not in keepT: keepT.append(bt['index'])
    texs=j.get('textures',[]); imgs=j.get('images',[])
    newT=[]; newI=[]; tmap={}; imap={}
    for ti in keepT:
        t=dict(texs[ti]); si=t.get('source')
        if si is not None:
            if si not in imap:
                im=dict(imgs[si]); im['uri']=webp(im['uri']); im['mimeType']='image/webp'; imap[si]=len(newI); newI.append(im)
            t['source']=imap[si]
        tmap[ti]=len(newT); newT.append(t)
    for m in j.get('materials',[]):
        bt=m.get('pbrMetallicRoughness',{}).get('baseColorTexture')
        if bt is not None: bt['index']=tmap[bt['index']]
    if newT: j['textures']=newT
    else: j.pop('textures',None)
    if newI: j['images']=newI
    else: j.pop('images',None)
    if 'samplers' in j and not newT: j.pop('samplers')
    json.dump(j, open(os.path.join(dst,os.path.basename(f)),'w'), separators=(',',':'))
    for b in j.get('buffers',[]):
        shutil.copy(os.path.join(src,b['uri']), os.path.join(dst,b['uri']))
for t in glob.glob(os.path.join(glob.escape(src),'*.txt')): shutil.copy(t, dst)
print(len(glob.glob(os.path.join(dst,'*.gltf'))), 'gltf', len(conv), 'textures')
