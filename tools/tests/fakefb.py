"""가짜 Firebase (테스트용) — GET(shallow) · PUT · PATCH · POST · DELETE · 스트리밍은 503 (폴링으로 돌게)"""
import json, re
from harness import route
DB = {}
def db_get(path):
    o = DB
    for k in [x for x in path.split("/") if x]:
        if not isinstance(o, dict) or k not in o: return None
        o = o[k]
    return o
def db_put(path, v):
    ks = [x for x in path.split("/") if x]; o = DB
    for k in ks[:-1]:
        if not isinstance(o.get(k), dict): o[k] = {}
        o = o[k]
    if v is None: o.pop(ks[-1], None)
    else: o[ks[-1]] = v
async def fake(r):
    url = r.request.url
    if "firebasedatabase.app" in url or "firebaseio.com" in url:
        if "text/event-stream" in (r.request.headers.get("accept") or ""): return await r.fulfill(status=503, body="no")
        full = re.sub(r"^https://[^/]+", "", url); path = full.split("?")[0]; qs = full.split("?")[1] if "?" in full else ""
        path = path[:-5] if path.endswith(".json") else path
        m = r.request.method
        if path == "/hy/ok": return await r.fulfill(status=200, body="true", content_type="application/json")
        if m == "GET":
            v = db_get(path)
            if "shallow=true" in qs and isinstance(v, dict): v = {k: True for k in v}
            return await r.fulfill(status=200, body=json.dumps(v), content_type="application/json")
        if m in ("PUT", "PATCH"):
            v = json.loads(r.request.post_data or "null")
            if m == "PATCH" and isinstance(v, dict):
                for k, x in v.items(): db_put(path + "/" + k, x)
            else: db_put(path, v)
            return await r.fulfill(status=200, body=json.dumps(v), content_type="application/json")
        if m == "POST":   # (v623) 🛡 오류 기록 = 자동 키로 넣기
            import time, random
            k = "-T%d%04d" % (int(time.time()*1000), random.randint(0, 9999)); v = json.loads(r.request.post_data or "null"); db_put(path + "/" + k, v)
            return await r.fulfill(status=200, body=json.dumps({"name": k}), content_type="application/json")
        if m == "DELETE": db_put(path, None); return await r.fulfill(status=200, body="null", content_type="application/json")
        return await r.fulfill(status=400, body="x")
    return await route(r)
