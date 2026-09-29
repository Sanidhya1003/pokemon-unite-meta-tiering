## Data Source Note

The `/meta/fetch` endpoint is experimental because the live UniteAPI site may return Cloudflare bot-protection pages to automated requests. For reproducible local testing, use the bundled sample dataset through `/meta/load-sample`.

Recommended local flow:

```text
POST /meta/load-sample
GET  /meta/latest
POST /meta/tier
GET  /meta/tiers

This is important because your curl output confirmed Cloudflare challenge responses, including `HTTP/2 403` and `cf-mitigated: challenge`. :chatgpt-content-reference{index="0"}

---

## 4. Make sure `uvicorn` is actually in dependencies

Because you got this earlier:

```text
Failed to spawn: uvicorn
Run this from the project root:
uv add "uvicorn[standard]"
Also make sure FastAPI is there:
uv add fastapi
This will update:
pyproject.toml
uv.lock