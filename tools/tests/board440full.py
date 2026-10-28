"""(v440) board440 끝까지 검사 — 한 패드 2·4·8명(진짜 3D) + 📺 TV + 패드 4대(가짜 3D, 따로 실행) · 오래 걸림 · SLOW"""
import os, sys, subprocess
H=os.path.dirname(os.path.abspath(__file__)); f=os.path.join(H, "board440.py")
r1=subprocess.call([sys.executable, f], env=dict(os.environ, HY_FULL="1"))
env=dict(os.environ, HY_TVONLY="1"); env.pop("HY_REAL3D", None)
r2=subprocess.call([sys.executable, f], env=env)
sys.exit(1 if (r1 or r2) else 0)
