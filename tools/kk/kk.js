/* (v434) KayKit(CC0, Kay Lousberg) 모델 묶음 읽기 — tools/kk/pack.py 로 만든 assets/town/kk/<묶음>.json·.bin·.webp
   KK.load("nature").then(P=>P.mesh("tree_single_A")) · 같은 묶음은 텍스처·재료 하나 */
const KK={ P:{}, base:"",
  load(name){ if(this.P[name]) return this.P[name]; const b=this.base+"assets/town/kk/"+name;
    return this.P[name]=Promise.all([fetch(b+".json").then(r=>r.json()), fetch(b+".bin").then(r=>r.arrayBuffer())]).then(([j,buf])=>{
      const tex=new THREE.TextureLoader().load(this.base+"assets/town/kk/"+j.tex); if(THREE.sRGBEncoding) tex.encoding=THREE.sRGBEncoding; tex.flipY=false; tex.anisotropy=4;
      const mat=new THREE.MeshStandardMaterial({map:tex, roughness:.85, metalness:0}), G={};
      Object.keys(j.m).forEach(k=>{ const m=j.m[k], q=new Int16Array(buf, m.p, m.v*3), pos=new Float32Array(m.v*3);
        for(let i=0;i<m.v;i++) for(let a=0;a<3;a++) pos[i*3+a]=m.mn[a]+(q[i*3+a]+32768)/65535*(m.mx[a]-m.mn[a]);
        const g=new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(pos,3)); g.setAttribute("normal", new THREE.BufferAttribute(new Int8Array(buf, m.n, m.v*3),3,true));
        g.setAttribute("uv", new THREE.BufferAttribute(new Uint16Array(buf, m.u, m.v*2),2,true)); g.setIndex(new THREE.BufferAttribute(new Uint16Array(buf, m.x, m.i),1)); g.computeBoundingBox(); g.computeBoundingSphere(); G[k]=g; });
      return {G, mat, tex, names:Object.keys(G),
        mesh(k, o){ o=o||{}; const g=G[k]; if(!g) return null; const m=new THREE.Mesh(g, o.mat||mat); m.castShadow=o.cast!==false; m.receiveShadow=true; m.name="kk:"+k; return m; } }; }); }
};
