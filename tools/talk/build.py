import json, os
out={}
for g in ['g12','g34','g56']:
    f=g+'.txt'
    if not os.path.exists(f): continue
    for ln in open(f,encoding='utf8'):
        ln=ln.rstrip('\n')
        if not ln or ln.startswith('#'): continue
        en,a,b,ko=ln.split('|')
        L=out.setdefault(en,[])
        if len(L)<4 and not any(x[0]==a for x in L): L.append([a,b,ko])
json.dump(out, open('/home/claude/hy-eng/data/talk.json','w',encoding='utf8'), ensure_ascii=False, separators=(',',':'))
print('words', len(out), 'dialogues', sum(len(v) for v in out.values()))
