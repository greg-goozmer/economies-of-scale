"""Exercise real PostgreSQL/Redis/MinIO through HTTP; never touch existing cards."""
import json
import uuid
from pathlib import Path

import httpx
from redis import Redis

from core.config import settings
from api.current_user import session_key


ROOT = Path(__file__).resolve().parents[1]


def run(base_url="http://127.0.0.1:8000"):
    results = []

    def check(label, response, expected):
        assert response.status_code == expected, (label, response.status_code, response.text)
        results.append({"check": label, "status": expected})
        return response

    with httpx.Client(base_url=base_url, timeout=30) as owner, httpx.Client(base_url=base_url, timeout=30) as other, httpx.Client(base_url=base_url, timeout=30) as guest:
        username = "lr4_check_" + uuid.uuid4().hex[:10]
        credentials = {"user_name": username, "password": "Local-test-LR4-2026!"}
        owner_user = check('register owner', owner.post('/api/users', json=credentials), 201).json()
        check('duplicate name', guest.post('/api/users', json=credentials), 409)
        check('bad password', guest.post('/api/users/auth', json={**credentials, 'password': 'wrong'}), 401)
        check('guest catalog', guest.get('/api/costs'), 200)
        check('guest feed', guest.get('/api/costs/feed'), 200)
        payload = {'cost_description': 'Проверка авторизации ЛР4', 'cost_behavior': 'fixed', 'cost_code': 25}
        check('guest publication', guest.put('/api/costs/1', json=payload), 401)
        check('login', owner.post('/api/users/auth', json=credentials), 200)
        token = owner.cookies.get(settings.SESSION_COOKIE_NAME)
        redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        assert redis.get(session_key(token)) == str(owner_user['user_id'])
        assert 0 < redis.ttl(session_key(token)) <= settings.SESSION_TTL_SECONDS
        results.append({'check': 'Redis stores real user ID and TTL', 'ok': True})
        files = {'image': ('cost.png', (ROOT/'docs/postman/fixtures/example_cost.png').read_bytes(), 'image/png'),
                 'video': ('cost.mp4', (ROOT/'docs/postman/fixtures/example_cost.mp4').read_bytes(), 'video/mp4')}
        draft = check('create authenticated draft', owner.post('/api/costs', data={'cost_name': 'Проверка ЛР4 ' + username}, files=files), 201).json()
        assert draft['cost_creator_id'] == owner_user['user_id']
        cost_id = draft['cost_id']
        check('only one draft', owner.post('/api/costs', data={'cost_name': 'Second draft'}, files=files), 409)
        check('own draft', owner.get('/api/costs/draft'), 200)
        check('guest cannot read draft', guest.get('/api/costs/draft'), 401)
        check('register other user', other.post('/api/users', json={**credentials, 'user_name': username+'_other'}), 201)
        check('login other user', other.post('/api/users/auth', json={**credentials, 'user_name': username+'_other'}), 200)
        check('other user cannot publish', other.put(f'/api/costs/{cost_id}', json=payload), 404)
        check('other user cannot delete', other.delete(f'/api/costs/{cost_id}'), 404)
        check('publish owner draft', owner.put(f'/api/costs/{cost_id}', json=payload), 200)
        check('cannot publish twice', owner.put(f'/api/costs/{cost_id}', json=payload), 404)
        check('like', owner.post(f'/api/costs/{cost_id}/likes', json={'is_liked': 1}), 200)
        liked = check('personalized feed', owner.get('/api/costs/feed', params={'cost_id': cost_id}), 200).json()
        assert liked['is_owner'] == 1 and liked['is_liked'] == 1
        anonymous = check('anonymous feed', guest.get('/api/costs/feed', params={'cost_id': cost_id}), 200).json()
        assert anonymous['is_owner'] == 0 and anonymous['is_liked'] == 0
        check('logout', owner.post('/api/users/logout'), 204)
        assert redis.get(session_key(token)) is None
        check('replay revoked cookie', guest.get('/api/costs/draft', headers={'Cookie': f'{settings.SESSION_COOKIE_NAME}={token}'}), 401)
        check('login again', owner.post('/api/users/auth', json=credentials), 200)
        expired_token = owner.cookies.get(settings.SESSION_COOKIE_NAME)
        redis.delete(session_key(expired_token))
        check('expired session is denied', owner.get('/api/costs/draft'), 401)
        check('public list still works with expired cookie', owner.get('/api/costs'), 200)
        check('login for cleanup', owner.post('/api/users/auth', json=credentials), 200)
        check('soft delete test card', owner.delete(f'/api/costs/{cost_id}'), 204)
        check('deleted card not visible', guest.get('/api/costs/feed', params={'cost_id': cost_id}), 404)
        check('owner logout', owner.post('/api/users/logout'), 204)
        check('other logout', other.post('/api/users/logout'), 204)
        redis.close()
    return results


if __name__ == '__main__':
    import sys
    evidence = run(sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8000')
    target = ROOT / 'local_lab_artifacts/lab4/live_checks.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'{len(evidence)} live checks passed; {target}')
