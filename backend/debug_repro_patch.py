from fastapi.testclient import TestClient
import asyncio
import sys
from pathlib import Path

# Ensure package imports resolve like pytest does (backend/src on sys.path)
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from agent.api.app import app
from agent.services import config_store

client = TestClient(app)

async def create_generation():
    await config_store.store.init_db()
    async with config_store.store._Session() as session:
        g = config_store.GenerationConfig(model_name="gpt-test", temperature=0.5, max_tokens=100, system_prompt="hi", metadata_={})
        session.add(g)
        await session.commit()
        await session.refresh(g)
        return int(g.id)

gen_id = asyncio.get_event_loop().run_until_complete(create_generation())
asyncio.get_event_loop().run_until_complete(config_store.store.reload())

print('gen_id=', gen_id)

r = client.get('/admin/generation/config')
print('GET /admin/generation/config ->', r.status_code, r.json())

r = client.patch(f'/admin/generation/{gen_id}', json={"temperature": 0.2})
print('PATCH ->', r.status_code)
try:
    print(r.json())
except Exception:
    print(r.text)
