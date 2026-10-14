import json, re, sys
grade=sys.argv[1]; setk={'g12':'basic','g34':'elem','g56':'g56'}[grade]
W=json.load(open('words.json'))[setk]; need=[]
for n,ws in W:
    for x in ws:
        en=x.split('=')[0]
        if en not in need: need.append(en)
prev={'g12':[],'g34':['g12'],'g56':['g12','g34']}[grade]; have=set()
import os
for g in prev:
    for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)),g+'.txt'),encoding='utf8'):
        if l.strip() and not l.startswith('#'): have.add(l.split('|')[0])
need=[e for e in need if e not in have]
D={}; bad=[]
for ln in open(os.path.join(os.path.dirname(os.path.abspath(__file__)),grade+'.txt'),encoding='utf8'):
    ln=ln.rstrip('\n')
    if not ln or ln.startswith('#'): continue
    p=ln.split('|')
    if len(p)!=4: bad.append(('fields',ln)); continue
    en,a,b,ko=p
    re_=re.compile(r'(?<![A-Za-z\-])'+re.escape(en)+r'(?![A-Za-z\-])', re.I)
    ca,cb=len(re_.findall(a)),len(re_.findall(b))
    if ca+cb!=1: bad.append(('count %d/%d'%(ca,cb),ln))
    if ' / ' not in ko: bad.append(('ko',ln))
    D.setdefault(en,[]).append([a,b,ko])
miss=[e for e in need if e not in D]; print('missing count',len(miss)); extra=[e for e in D if e not in need]
cnt=[(e,len(v)) for e,v in D.items() if len(v)!=2]
print(grade,'words',len(need),'have',len(D),'missing',miss,'extra',extra,'not2',cnt)
for b in bad: print(' BAD',b[0],'|',b[1][:150])
