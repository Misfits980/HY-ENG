/* (v694) 🐾 움직이는 동물 — Quaternius Ultimate Animated Animal Pack (CC0, quaternius.com)
   tools/kk/anipack.py 가 만든 assets/town/ani/<key>.json · .bin 을 읽어 SkinnedMesh 로 (three r128 에는 GLTFLoader 가 없어서 직접)
   ANI.load(k) → Promise · ANI.make(k, {h: 키(m), lift: 색 밝게}) → {g, mesh, play(name, fade), tick(dt), dispose()} */
const ANI=(()=>{
  const P={}, R={}; const X={B:"../assets/town/ani/"};
  function load(k){ if(P[k]) return P[k];
    return P[k]=Promise.all([fetch(X.B+k+".json").then(r=>{ if(!r.ok) throw new Error(r.status); return r.json(); }), fetch(X.B+k+".bin").then(r=>{ if(!r.ok) throw new Error(r.status); return r.arrayBuffer(); })]).then(([h,buf])=>{
      const nv=h.nv, o=h.off, q=new Int16Array(buf, o.p, nv*3), pos=new Float32Array(nv*3);
      for(let i=0;i<nv;i++) for(let a=0;a<3;a++) pos[i*3+a]=h.mn[a]+(q[i*3+a]+32768)/65535*(h.mx[a]-h.mn[a]);
      const g=new THREE.BufferGeometry();
      g.setAttribute("position", new THREE.BufferAttribute(pos,3));
      g.setAttribute("normal", new THREE.BufferAttribute(new Int8Array(buf, o.n, nv*3),3,true));
      g.setAttribute("skinIndex", new THREE.BufferAttribute(new Uint8Array(buf, o.j, nv*4),4));
      g.setAttribute("skinWeight", new THREE.BufferAttribute(new Uint8Array(buf, o.w, nv*4),4,true));
      const mi=new Uint8Array(buf, o.m, nv), col=new Float32Array(nv*3);
      /* 원본 색이 어두움(선형 0.03~0.5) → 마을 툰 그림과 맞게 밝게 · 눈(검정)은 그대로 */
      const pal=h.pal.map(c=>{ const m=Math.max(c[0],c[1],c[2]); if(m<.06) return c; const k=Math.min(1.9, .62/Math.max(m,.2)); return c.map(x=>Math.min(1, Math.pow(x*k, .9))); });
      for(let i=0;i<nv;i++){ const c=pal[mi[i]]||[1,1,1]; col[i*3]=c[0]; col[i*3+1]=c[1]; col[i*3+2]=c[2]; }
      g.setAttribute("color", new THREE.BufferAttribute(col,3));
      g.setIndex(new THREE.BufferAttribute(new Uint16Array(buf, o.x, h.ni),1));
      g.computeBoundingBox(); g.computeBoundingSphere();
      const ib=new Float32Array(buf, o.ib, h.joints.length*16), inv=h.joints.map((_,i)=>new THREE.Matrix4().fromArray(ib, i*16));
      const mat=new THREE.MeshStandardMaterial({vertexColors:true, skinning:true, roughness:.8, metalness:0});
      const clips={}; Object.keys(h.anims).forEach(nm=>{ const A=h.anims[nm], T=new Float32Array(A.t), n=T.length, tr=[];
        A.tr.forEach(([b, p, off, v])=>{ const prop=p==="r"?"quaternion":p==="t"?"position":"scale", w=p==="r"?4:3, name="b"+b+"."+prop;
          let vals; if(off<0){ vals=new Float32Array(w*2); for(let k=0;k<2;k++) vals.set(v, k*w); tr.push(p==="r" ? new THREE.QuaternionKeyframeTrack(name, [0, A.d], vals) : new THREE.VectorKeyframeTrack(name, [0, A.d], vals)); return; }
          if(p==="r"){ const s=new Int16Array(buf, off, n*4); vals=new Float32Array(n*4); for(let k=0;k<n;k++){ let x=s[k*4]/32767, y=s[k*4+1]/32767, z=s[k*4+2]/32767, ww=s[k*4+3]/32767; const l=Math.hypot(x,y,z,ww)||1; vals[k*4]=x/l; vals[k*4+1]=y/l; vals[k*4+2]=z/l; vals[k*4+3]=ww/l; } tr.push(new THREE.QuaternionKeyframeTrack(name, T, vals)); }
          else { vals=new Float32Array(buf.slice(off, off+n*12)); tr.push(new THREE.VectorKeyframeTrack(name, T, vals)); } });
        clips[nm]=new THREE.AnimationClip(nm, A.d, tr); });
      return (R[k]={h, geo:g, mat, inv, clips, H:h.mx[1]-Math.min(0,h.mn[1])}); }).catch(e=>{ console.warn("ANI", k, e); P[k]=null; return null; }); }
  function ready(k){ return R[k]||null; }
  /* 한 마리 — 뼈는 마리마다 새로 · 도형·재료·애니는 같이 씀 */
  function make(k, o){ const r=R[k]; if(!r) return null; o=o||{}; const h=r.h, root=new THREE.Group(), body=new THREE.Group(); root.add(body);
    const nodes=h.bones.map((b,i)=>{ const n=new THREE.Bone(); n.name="b"+i; n.position.fromArray(b[1]); n.quaternion.fromArray(b[2]); n.scale.fromArray(b[3]); return n; });
    h.bones.forEach((b,i)=>{ (b[0]<0 ? body : nodes[b[0]]).add(nodes[i]); });
    const mesh=new THREE.SkinnedMesh(r.geo, r.mat); mesh.castShadow=true; mesh.receiveShadow=false; mesh.frustumCulled=false; (h.mesh<0 ? body : nodes[h.mesh]).add(mesh);
    body.updateMatrixWorld(true); mesh.bind(new THREE.Skeleton(h.joints.map(i=>nodes[i]), r.inv.map(m=>m.clone())), mesh.matrixWorld);
    const s=(o.h||1)/Math.max(.1, r.H); body.scale.setScalar(s);
    const mixer=new THREE.AnimationMixer(body); let cur=null, curN="";
    function play(nm, fade, once){ const c=r.clips[nm] || r.clips.Idle; if(!c) return; if(curN===nm && cur && !once) return; const a=mixer.clipAction(c); a.reset(); a.enabled=true; a.setEffectiveWeight(1); a.setEffectiveTimeScale(1);
      if(once){ a.setLoop(THREE.LoopOnce, 1); a.clampWhenFinished=true; } else a.setLoop(THREE.LoopRepeat, Infinity);
      if(cur && cur!==a && fade>0){ a.play(); cur.crossFadeTo(a, fade, false); } else { if(cur && cur!==a) cur.stop(); a.play(); } cur=a; curN=nm; }
    function has(nm){ return !!r.clips[nm]; }
    function done(){ return !cur || (cur.loop===THREE.LoopOnce && !cur.isRunning()); }
    play("Idle", 0);
    mixer.update(Math.random()*2);
    return {g:root, body, mesh, mixer, play, has, done, cur:()=>curN, tick(dt){ mixer.update(dt); }, dispose(){ try{ mixer.stopAllAction(); mixer.uncacheRoot(body); }catch(e){} try{ mesh.skeleton.dispose && mesh.skeleton.dispose(); }catch(e){} } }; }
  return Object.assign(X, {load, ready, make, R});
})();
window.ANI=ANI;
