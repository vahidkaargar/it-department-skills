#!/usr/bin/env python3
"""skillserve — localhost HTTP API over the skills catalog, for AI agents.

Sits behind nginx 127.0.0.1:3333. Binds 127.0.0.1:3401 (never LAN).

Endpoints (GET only):
  /health                      -> {"ok": true, "skills": N}
  /search?q=...&n=5[&category=][&source=][&full=1]
                                -> hints only by default: {name,path,category,score}.
                                   Agent reads the ONE SKILL.md via /get instead of
                                   paying for N descriptions here. full=1 -> whole record.
  /get?name=<skill>            -> record(s) + full SKILL.md body
  /catalog                     -> CATALOG.md (text/markdown)
  /rules?q=...  /rules?always=1[&full=1]
                                -> hints only by default: {name,path,score}. full=1 adds
                                   kind/always_on/desc.

Reuses skillfind's index + scoring via module import — one source of truth.
Stdlib only. Run: python3 skillserve.py  (or via start-nginx-3333.sh)
"""
import importlib.machinery
import importlib.util
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

BIND = ("127.0.0.1", 3401)
CATALOG_DIR = os.path.join(os.path.expanduser("~"), ".agents", "skills-catalog")
CATALOG_MD = os.path.join(CATALOG_DIR, "CATALOG.md")

_spec = importlib.util.spec_from_loader(
    "skillfind", importlib.machinery.SourceFileLoader(
        "skillfind", os.path.join(CATALOG_DIR, "scripts", "skillfind")))
skillfind = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(skillfind)


def q1(params, key, default=None):
    vals = params.get(key)
    return vals[0].strip() if vals and vals[0].strip() else default


class Handler(BaseHTTPRequestHandler):
    server_version = "skillserve/1.0"

    def log_message(self, fmt, *args):  # quiet; nginx has the access log
        pass

    def send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", f"{ctype}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, obj, code=200):
        self.send(code, json.dumps(obj, separators=(",", ":")))

    def do_GET(self):
        try:
            url = urlparse(self.path)
            params = parse_qs(url.query)
            data, rules_data = skillfind.load_index()
            skills, rules = data["skills"], rules_data["rules"]

            if url.path == "/health":
                return self.send_json({"ok": True, "skills": len(skills),
                                       "built": data["meta"]["built_at_human"]})

            if url.path == "/catalog":
                with open(CATALOG_MD, encoding="utf-8") as f:
                    return self.send(200, f.read(), "text/markdown")

            if url.path == "/search":
                query = q1(params, "q")
                if not query:
                    return self.send_json({"error": "missing ?q="}, 400)
                try:
                    limit = max(1, min(25, int(q1(params, "n", "5"))))
                except ValueError:
                    return self.send_json({"error": "?n= must be an integer"}, 400)
                category, source = q1(params, "category"), q1(params, "source")
                pool = [s for s in skills
                        if (not category or s["category"] == category)
                        and (not source or source in s["sources"])]
                terms = [t.lower() for t in query.split() if t.strip()]
                scored = sorted(((skillfind.score(s, terms), s) for s in pool),
                                key=lambda x: -x[0])
                hits = [(sc, s) for sc, s in scored if sc > 0][:limit]
                if q1(params, "full"):
                    top = [dict(s, score=sc) for sc, s in hits]
                else:
                    top = [{"name": s["name"], "path": s["path"],
                            "category": s["category"], "score": sc}
                           for sc, s in hits]
                return self.send_json({"query": query, "results": top})

            if url.path == "/get":
                name = q1(params, "name")
                if not name:
                    return self.send_json({"error": "missing ?name="}, 400)
                matches = [s for s in skills if s["name"] == name or s["dir"] == name]
                if not matches:
                    return self.send_json({"error": f"no skill named {name!r}"}, 404)
                out = []
                for s in matches:
                    rec = dict(s)
                    try:  # path comes from the index, never from the client
                        with open(s["path"], encoding="utf-8", errors="replace") as f:
                            rec["skill_md"] = f.read(65536)
                    except OSError as e:
                        rec["skill_md_error"] = str(e)
                    out.append(rec)
                return self.send_json({"results": out})

            if url.path == "/rules":
                full = bool(q1(params, "full"))

                def shape(r, sc=None):
                    if full:
                        return dict(r, score=sc) if sc is not None else dict(r)
                    hint = {"name": r["name"], "path": r["path"]}
                    if sc is not None:
                        hint["score"] = sc
                    return hint

                if q1(params, "always"):
                    return self.send_json({"results": [shape(r) for r in rules if r["always_on"]]})
                query = q1(params, "q")
                if not query:
                    return self.send_json({"results": [shape(r) for r in rules]})
                terms = [t.lower() for t in query.split()]
                hits = [(sum(2 if t in r["name"].lower() else
                             1 if t in r.get("desc", "").lower() else 0
                             for t in terms), r) for r in rules]
                hits = sorted([h for h in hits if h[0] > 0], key=lambda h: -h[0])[:10]
                return self.send_json({"results": [shape(r, sc) for sc, r in hits]})

            return self.send_json(
                {"error": "unknown endpoint",
                 "endpoints": ["/health", "/search?q=", "/get?name=", "/catalog",
                               "/rules?q= | /rules?always=1"]}, 404)
        except BrokenPipeError:
            pass
        except Exception as e:  # never crash the server on one bad request
            try:
                self.send_json({"error": f"internal: {e.__class__.__name__}: {e}"}, 500)
            except Exception:
                pass


def main():
    server = ThreadingHTTPServer(BIND, Handler)
    print(f"skillserve on http://{BIND[0]}:{BIND[1]} (localhost only)", file=sys.stderr)
    server.serve_forever()


if __name__ == "__main__":
    main()
