import json, os
out={}; v6w=set()
for g in ['v6','g12','g34','g56']:   # (v278) v6 = 노션 v6 대화(상황 칸) — 먼저 넣어 단어마다 앞자리
    f=os.path.join(os.path.dirname(os.path.abspath(__file__)), g+'.txt')
    if not os.path.exists(f): continue
    for ln in open(f,encoding='utf8'):
        ln=ln.rstrip('\n')
        if not ln or ln.startswith('#'): continue
        p=ln.split('|'); en,a,b,ko=p[:4]; sit=p[4] if len(p)>4 else ''
        if g!='v6' and en in v6w: continue   # (v281) 노션 v6 대화가 있는 단어는 옛 대화를 섞지 않음 (옛 대화엔 숫자·색처럼 답이 여럿인 것이 있음)
        if g=='v6': v6w.add(en)
        L=out.setdefault(en,[])
        if len(L)<4 and not any(x[0]==a for x in L): L.append([a,b,ko,sit] if sit else [a,b,ko])
json.dump(out, open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),'data','talk.json'),'w',encoding='utf8'), ensure_ascii=False, separators=(',',':'))
print('words', len(out), 'dialogues', sum(len(v) for v in out.values()))
