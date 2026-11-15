/* (v684) 🪙 새 이모지 대신 그림 — 사용자: 「마이타운 버그 찾아봐」 + 「크롬으로도 확인」
   학원 PC(Windows 10 크롬)·옛 패드(iOS 14.1 이하)는 2020년 뒤에 나온 이모지(🪙 코인 · 🪱 미끼 · 🪜 계단 · 🪵 나무 …)를
   빈 네모(⊠)로 그림 → My Town 은 코인이 거의 모든 창에 있어서 은행·가게·놀이 공원 값이 다 ⊠ 로 보였음.
   → 이 기기가 못 그리는 것만 골라(캔버스로 한 번 그려 봄) 그 글자를 투명하게 두고, 같은 자리에 그림(assets/emoji/*.svg · Twemoji CC-BY)을 깔아 줌.
   글자는 지우지 않음 → textContent 를 읽고 비교하는 코드·시험은 그대로. 잘 그리는 기기(요즘 패드·폰)는 아무것도 안 함. */
(function(){
  const CODES = "1f43b-200d-2744-fe0f 1f6d6 1f6dd 1f6df 1f7e5 1f7e6 1f7e8 1f7e9 1f7ea 1f7eb 1f93f 1f96c 1f975 1f976 1f978 1f97e 1f998 1f99b 1f99c 1f9aa 1f9ad 1f9b4 1f9b5 1f9b6 1f9b7 1f9b8 1f9ba 1f9c2 1f9c3 1f9c5 1f9c8 1f9ca 1f9cd 1f9d1-200d-1f680 1f9d1-200d-1f692 1f9d1-200d-1f91d-200d-1f9d1 1f9e9 1f9ea 1f9f1 1f9f3 1f9f5 1f9f6 1f9f8 1f9f9 1f9fa 1f9fb 1f9fc 1f9fd 1f9fe 1fa70 1fa75 1fa80 1fa81 1fa84 1fa86 1fa88 1fa90 1fa91 1fa99 1fa9a 1fa9c 1fa9e 1fa9f 1faa1 1faa2 1faa3 1faa4 1faa5 1faa7 1faa8 1fab1 1fab4 1fab5 1fab6 1fabd 1fad2 1fad8 1fad9 1fae7".split(" ");
  let base, ctx, ref;
  try{ base = new URL("assets/emoji/", document.currentScript.src).href; }catch(e){ return; }
  try{ const cv = document.createElement("canvas"); cv.width = cv.height = 44; ctx = cv.getContext("2d", {willReadFrequently:true}); if(!ctx) return;
    ctx.font = '32px "Segoe UI Emoji","Apple Color Emoji","Noto Color Emoji",sans-serif'; ctx.textBaseline = "top"; ref = ctx.measureText("\u{1F600}").width || 32; }catch(e){ return; }
  /* 검은색이 아닌 점이 하나라도 나오면 = 그릴 줄 앎 (빈 네모·흑백 글자는 칠한 색(검정) 그대로 · 회색 돌 🪨 같은 그림 글자는 밝은 점이 있음) · 붙은 이모지가 둘로 갈라지면(너비 1.45배) = 못 그림 */
  function ok(ch){ try{ if(ctx.measureText(ch).width > ref*1.45) return false; ctx.clearRect(0,0,44,44); ctx.fillStyle = "#000"; ctx.fillText(ch, 4, 4);
      const d = ctx.getImageData(0,0,44,44).data; for(let i=0;i<d.length;i+=4){ if(d[i+3]>60 && Math.max(d[i],d[i+1],d[i+2])>70) return true; } return false; }catch(e){ return true; } }
  const M = {}; let forced = false; try{ forced = /[?&]emjfix=1/.test(location.search) || localStorage.getItem("hyeng_emjfix")==="1"; }catch(e){}   /* 시험·확인용: 잘 그리는 기기에서도 그림으로 */
  CODES.forEach(c=>{ let ch; try{ ch = String.fromCodePoint(...c.split("-").map(h=>parseInt(h,16))); }catch(e){ return; } if(forced || !ok(ch)) M[ch] = c; });
  const K = Object.keys(M).sort((a,b)=>b.length-a.length);
  window.EMOJI_DOM = {n:K.length, M, ok};
  if(!K.length) return;
  const esc = s=>s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const RE = new RegExp("(?:"+K.map(esc).join("|")+")\\uFE0F?", "gu");
  const st = document.createElement("style");
  st.textContent = ".emjF{display:inline-block;width:1.15em;height:1.15em;line-height:1.15em;vertical-align:-.2em;overflow:hidden;white-space:nowrap;text-align:center;color:transparent!important;-webkit-text-fill-color:transparent!important;text-shadow:none!important;background:center/contain no-repeat!important;-webkit-background-clip:border-box!important;background-clip:border-box!important}";
  (document.head || document.documentElement).appendChild(st);
  const SKIP = /^(SCRIPT|STYLE|TEXTAREA|INPUT|OPTION|SELECT|TITLE|NOSCRIPT|CANVAS)$/;
  function fixText(n){ const p = n.parentNode; if(!p || p.nodeType!==1 || SKIP.test(p.nodeName) || p.namespaceURI==="http://www.w3.org/2000/svg" || (p.classList && p.classList.contains("emjF"))) return;
    const s = n.data; RE.lastIndex = 0; if(!s || !RE.test(s)) return; RE.lastIndex = 0;
    const f = document.createDocumentFragment(); let last = 0, m;
    while((m = RE.exec(s))){ if(m.index>last) f.appendChild(document.createTextNode(s.slice(last, m.index)));
      const c = M[m[0]] || M[m[0].replace(/\uFE0F$/, "")]; const sp = document.createElement("span"); sp.className = "emjF"; if(c) sp.style.backgroundImage = 'url("'+base+c+'.svg")'; sp.textContent = m[0]; f.appendChild(sp); last = m.index + m[0].length; }
    if(last<s.length) f.appendChild(document.createTextNode(s.slice(last)));
    p.replaceChild(f, n); }
  function walk(r){ if(r.nodeType===3){ fixText(r); return; } if(r.nodeType!==1 || SKIP.test(r.nodeName) || (r.classList && r.classList.contains("emjF"))) return;
    const tw = document.createTreeWalker(r, NodeFilter.SHOW_TEXT), L = []; while(tw.nextNode()){ RE.lastIndex = 0; if(RE.test(tw.currentNode.data)) L.push(tw.currentNode); } L.forEach(fixText); }
  const mo = new MutationObserver(R=>{ for(const r of R){ if(r.type==="characterData") fixText(r.target); else r.addedNodes.forEach(walk); } });
  const start = ()=>{ walk(document.body); mo.observe(document.body, {childList:true, subtree:true, characterData:true}); };
  if(document.body) start(); else document.addEventListener("DOMContentLoaded", start);
})();
