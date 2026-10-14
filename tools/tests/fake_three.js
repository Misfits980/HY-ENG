/* 테스트용 가짜 THREE — 그림은 안 그리지만 게임 로직은 그대로 돈다 */
(function(){
const T={};
class V3{constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z;}
 set(x,y,z){this.x=x;this.y=y;this.z=z;return this;} setScalar(s){this.x=this.y=this.z=s;return this;}
 copy(v){this.x=v.x;this.y=v.y;this.z=v.z;return this;} clone(){return new V3(this.x,this.y,this.z);}
 add(v){this.x+=v.x;this.y+=v.y;this.z+=v.z;return this;} sub(v){this.x-=v.x;this.y-=v.y;this.z-=v.z;return this;}
 addScaledVector(v,s){this.x+=v.x*s;this.y+=v.y*s;this.z+=v.z*s;return this;}
 multiplyScalar(s){this.x*=s;this.y*=s;this.z*=s;return this;} length(){return Math.hypot(this.x,this.y,this.z);}
 normalize(){const l=this.length()||1;return this.multiplyScalar(1/l);} distanceTo(v){return Math.hypot(this.x-v.x,this.y-v.y,this.z-v.z);}
 lerp(v,a){this.x+=(v.x-this.x)*a;this.y+=(v.y-this.y)*a;this.z+=(v.z-this.z)*a;return this;}
 setX(x){this.x=x;return this;} setY(y){this.y=y;return this;} setZ(z){this.z=z;return this;}
 applyMatrix4(){return this;} project(){return this;} unproject(){return this;} applyQuaternion(){return this;} applyEuler(){return this;}
 dot(v){return this.x*v.x+this.y*v.y+this.z*v.z;} negate(){this.x=-this.x;this.y=-this.y;this.z=-this.z;return this;}
 equals(v){return v.x===this.x&&v.y===this.y&&v.z===this.z;} }
class V2{constructor(x=0,y=0){this.x=x;this.y=y;} set(x,y){this.x=x;this.y=y;return this;} copy(v){this.x=v.x;this.y=v.y;return this;} clone(){return new V2(this.x,this.y);}}
class Eu extends V3{constructor(){super();this.order="XYZ";}}
class Col{constructor(r){this.r=1;this.g=1;this.b=1; if(r!==undefined) this.set(r);}
 set(v){ if(typeof v==="number") this.setHex(v); else if(v&&v.r!==undefined) this.copy(v); else if(typeof v==="string"&&v[0]==="#") this.setHex(parseInt(v.slice(1),16)); return this;}
 setHex(h){h=Math.floor(h);this.r=(h>>16&255)/255;this.g=(h>>8&255)/255;this.b=(h&255)/255;return this;}
 getHex(){return (Math.round(this.r*255)<<16)|(Math.round(this.g*255)<<8)|Math.round(this.b*255);} getHexString(){return this.getHex().toString(16).padStart(6,"0");}
 setRGB(r,g,b){this.r=r;this.g=g;this.b=b;return this;} setHSL(){return this;} getHSL(t){t=t||{};t.h=0;t.s=0;t.l=0.5;return t;} offsetHSL(){return this;}
 copy(c){this.r=c.r;this.g=c.g;this.b=c.b;return this;} clone(){return new Col().copy(this);}
 lerp(c,a){this.r+=(c.r-this.r)*a;this.g+=(c.g-this.g)*a;this.b+=(c.b-this.b)*a;return this;}
 lerpColors(a,b,t){this.copy(a);return this.lerp(b,t);} multiplyScalar(s){this.r*=s;this.g*=s;this.b*=s;return this;}
 multiply(c){this.r*=c.r;this.g*=c.g;this.b*=c.b;return this;} add(c){this.r+=c.r;this.g+=c.g;this.b+=c.b;return this;} convertSRGBToLinear(){return this;} convertLinearToSRGB(){return this;}}
let OID=0;
class O3{constructor(){this.id=++OID;this.uuid="u"+this.id;this.position=new V3();this.rotation=new Eu();this.scale=new V3(1,1,1);this.quaternion={set(){},copy(){},setFromEuler(){}};
 this.children=[];this.parent=null;this.visible=true;this.userData={};this.renderOrder=0;this.matrixWorld={elements:new Array(16).fill(0)};
 this.layers={set(){},enable(){},disable(){}};this.up=new V3(0,1,0);this.matrixAutoUpdate=true;}
 add(...o){o.forEach(c=>{if(!c)return; if(c.parent) c.parent.remove(c); c.parent=this; this.children.push(c);}); T.__count=(T.__count||0)+o.length; return this;}
 remove(...o){o.forEach(c=>{const i=this.children.indexOf(c); if(i>=0){this.children.splice(i,1); c.parent=null;}}); return this;}
 removeFromParent(){if(this.parent)this.parent.remove(this);return this;}
 traverse(f){f(this);this.children.slice().forEach(c=>c.traverse(f));} traverseVisible(f){if(!this.visible)return;f(this);this.children.forEach(c=>c.traverseVisible(f));}
 lookAt(){} updateMatrixWorld(){} updateMatrix(){} getWorldPosition(v){v=v||new V3(); let o=this,x=0,y=0,z=0; while(o){x+=o.position.x;y+=o.position.y;z+=o.position.z;o=o.parent;} return v.set(x,y,z);}
 clone(){const c=new this.constructor(this.geometry,this.material); c.position.copy(this.position); c.rotation.copy(this.rotation); c.scale.copy(this.scale); c.visible=this.visible; this.children.forEach(k=>c.add(k.clone())); return c;}
 getObjectByName(n){let r=null;this.traverse(o=>{if(!r&&o.name===n)r=o;});return r;} attach(o){return this.add(o);} }
class Geo{constructor(...a){this.parameters={};const n=["width","height","depth"];a.forEach((v,i)=>this.parameters[n[i]||("p"+i)]=v);this.args=a;
 this.attributes={position:new BA(new Float32Array(72),3),uv:new BA(new Float32Array(48),2),normal:new BA(new Float32Array(72),3)};this.boundingBox=null;this.groups=[];this.tr=[0,0,0];}
 translate(x,y,z){this.tr[0]+=x;this.tr[1]+=y;this.tr[2]+=z;return this;} rotateX(){return this;} rotateY(){return this;} rotateZ(){return this;} scale(){return this;} center(){return this;}
 setAttribute(k,v){this.attributes[k]=v;return this;} getAttribute(k){return this.attributes[k];} setIndex(){return this;} computeVertexNormals(){} computeBoundingBox(){this.boundingBox={min:new V3(),max:new V3()};} computeBoundingSphere(){}
 dispose(){T.__geoDisposed=(T.__geoDisposed||0)+1;} clone(){const g=new this.constructor(...this.args); g.tr=this.tr.slice(); return g;} setFromPoints(){return this;} applyMatrix4(){return this;}}
class BA{constructor(arr,n){this.array=arr;this.itemSize=n;this.count=arr.length/n;this.needsUpdate=false;}
 getX(i){return this.array[i*this.itemSize]} getY(i){return this.array[i*this.itemSize+1]} getZ(i){return this.array[i*this.itemSize+2]}
 setX(i,v){this.array[i*this.itemSize]=v} setY(i,v){this.array[i*this.itemSize+1]=v} setZ(i,v){this.array[i*this.itemSize+2]=v} setXYZ(i,a,b,c){this.setX(i,a);this.setY(i,b);this.setZ(i,c);} setXY(i,a,b){this.setX(i,a);this.setY(i,b);} setUsage(){return this;}}
class Mat{constructor(o){this.opacity=1;this.transparent=false;this.visible=true;this.side=0;this.color=new Col();this.emissive=new Col(0);this.uniforms={};this.defines={};
 if(o) for(const k in o){ if(k==="color"||k==="emissive") this[k]=new Col(o[k]); else this[k]=o[k]; } T.__mats=(T.__mats||0)+1;}
 dispose(){T.__matDisposed=(T.__matDisposed||0)+1;} clone(){const m=new this.constructor(); Object.assign(m,this); m.color=this.color.clone(); m.emissive=this.emissive.clone(); return m;} setValues(o){Object.assign(this,o);} onBeforeCompile(){} }
class Tex{constructor(img){this.image=img||null;this.wrapS=0;this.wrapT=0;this.repeat=new V2(1,1);this.offset=new V2();this.center=new V2();this.rotation=0;this.needsUpdate=false;T.__tex=(T.__tex||0)+1;}
 dispose(){T.__texDisposed=(T.__texDisposed||0)+1;} clone(){const t=new Tex(this.image);Object.assign(t,this);t.repeat=this.repeat.clone();t.offset=this.offset.clone();return t;}}
class Loader{constructor(){} setCrossOrigin(){return this;} setPath(){return this;}
 load(url,ok,prog,err){const t=new Tex(); const im=new Image(); im.onload=()=>{t.image=im;t.needsUpdate=true; T.__loaded=(T.__loaded||[]); T.__loaded.push(url); ok&&ok(t);}; im.onerror=e=>{err&&err(e);}; im.src=url; return t;}}
class Cam extends O3{constructor(f,a,n,fr){super();this.fov=f;this.aspect=a;this.near=n;this.far=fr;this.projectionMatrix={elements:[]};this.matrixWorldInverse={};} updateProjectionMatrix(){} }
class Rend{constructor(o){this.domElement=(o&&o.canvas)||document.createElement("canvas");this.shadowMap={enabled:false,type:0};this.capabilities={maxTextureSize:4096,isWebGL2:true,getMaxAnisotropy(){return 4}};
 this.info={render:{calls:0,triangles:0},memory:{geometries:0,textures:0},programs:[]};this.outputEncoding=0;this.toneMapping=0;this.toneMappingExposure=1;this.renders=0;}
 setAnimationLoop(f){const run=this._f==null; this._f=f; if(f&&run){const t=(ts)=>{ if(this._f){ try{this._f(ts);}catch(e){console.error('LOOP '+e.message+' '+(e.stack||'').split('\n')[1]);} requestAnimationFrame(t);} }; requestAnimationFrame(t);} }
 setSize(w,h){this.domElement.width=w;this.domElement.height=h;} setPixelRatio(){} getPixelRatio(){return 1;} render(){this.renders++; T.__renders=this.renders;} setClearColor(){} setClearAlpha(){} getSize(v){return (v||new V2()).set(this.domElement.width,this.domElement.height);}
 dispose(){} getContext(){return {getExtension(){return null},getParameter(){return 0}};} compile(){} clear(){} setRenderTarget(){} getClearColor(c){return c||new Col();} getClearAlpha(){return 1;} setScissorTest(){} setViewport(){} }
Object.assign(T,{Vector3:V3,Vector2:V2,Euler:Eu,Color:Col,Object3D:O3,Group:class extends O3{},Scene:class extends O3{constructor(){super();this.background=null;this.fog=null;}},
 Mesh:class extends O3{constructor(g,m){super();this.geometry=g||new Geo();this.material=m||new Mat();this.isMesh=true;}},
 Points:class extends O3{constructor(g,m){super();this.geometry=g;this.material=m;}}, Sprite:class extends O3{constructor(m){super();this.material=m;}},
 BufferGeometry:Geo,BufferAttribute:BA,Float32BufferAttribute:BA,
 MeshBasicMaterial:Mat,MeshStandardMaterial:Mat,MeshToonMaterial:Mat,MeshLambertMaterial:Mat,MeshPhongMaterial:Mat,PointsMaterial:Mat,ShaderMaterial:Mat,SpriteMaterial:Mat,LineBasicMaterial:Mat,
 CanvasTexture:Tex,Texture:Tex,DataTexture:Tex,TextureLoader:Loader,PerspectiveCamera:Cam,OrthographicCamera:Cam,WebGLRenderer:Rend,
 Fog:class{constructor(c,n,f){this.color=new Col(c);this.near=n;this.far=f;}},
 Clock:class{constructor(){this.t=performance.now();} getDelta(){const n=performance.now(),d=(n-this.t)/1000;this.t=n;return d;} getElapsedTime(){return performance.now()/1000;} start(){} },
 Raycaster:class{setFromCamera(){} intersectObjects(){return [];}} , Quaternion:class{set(){return this} setFromEuler(){return this} copy(){return this}}, Matrix4:class{makeRotationY(){return this} identity(){return this}},
 MathUtils:{lerp:(a,b,t)=>a+(b-a)*t,clamp:(v,a,b)=>Math.max(a,Math.min(b,v)),degToRad:d=>d*Math.PI/180,randFloat:(a,b)=>a+Math.random()*(b-a)}});
["BoxGeometry","PlaneGeometry","CircleGeometry","ConeGeometry","CylinderGeometry","IcosahedronGeometry","SphereGeometry","RingGeometry","OctahedronGeometry","TorusGeometry","DodecahedronGeometry","TetrahedronGeometry","CapsuleGeometry","ShapeGeometry","ExtrudeGeometry","LatheGeometry"].forEach(n=>T[n]=class extends Geo{});
["DirectionalLight","PointLight","HemisphereLight","AmbientLight","SpotLight"].forEach(n=>T[n]=class extends O3{constructor(c,i){super();this.color=new Col(c);this.intensity=i;this.shadow={mapSize:{width:0,height:0,set(){}},camera:{left:0,right:0,top:0,bottom:0,near:0,far:0,updateProjectionMatrix(){}},bias:0};this.target=new O3();}});
Object.assign(T,{DoubleSide:2,FrontSide:0,BackSide:1,AdditiveBlending:2,NormalBlending:1,MultiplyBlending:4,sRGBEncoding:3001,LinearEncoding:3000,RepeatWrapping:1000,ClampToEdgeWrapping:1001,MirroredRepeatWrapping:1002,
 NearestFilter:1003,LinearFilter:1006,LinearMipmapLinearFilter:1008,RGBAFormat:1023,PCFSoftShadowMap:2,ACESFilmicToneMapping:4,NoToneMapping:0,REVISION:"128"});
window.THREE=T;
})();
