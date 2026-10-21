import asyncio
import unittest
from types import SimpleNamespace

from fastapi.testclient import TestClient
from redis.exceptions import ConnectionError as RedisConnectionError

from api.current_user import session_key, session_user_id
from core.config import settings
from core.passwords import hash_password, verify_password
from db.redis import get_redis
from db.session import get_db
from main import app


class MemorySessions:
    def __init__(self):
        self.values = {}
        self.ttl = {}

    async def get(self, key):
        return self.values.get(key)

    async def set(self, key, value, ex=None):
        self.values[key] = value
        self.ttl[key] = ex

    async def delete(self, key):
        self.values.pop(key, None)


class FakeUsers:
    def __init__(self, user):
        self.user = user

    async def scalar(self, statement):
        name = next(iter(statement.compile().params.values()))
        return self.user if name == self.user.user_name else None


class AuthenticationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = SimpleNamespace(user_id=777, user_name='test_user',
                                   user_password_hash=hash_password('test-password-123'))

    def setUp(self):
        self.sessions = MemorySessions()
        app.dependency_overrides[get_redis] = lambda: self.sessions

        async def users():
            yield FakeUsers(self.user)
        app.dependency_overrides[get_db] = users
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()

    def login(self):
        return self.client.post('/api/users/auth', json={
            'user_name': self.user.user_name, 'password': 'test-password-123',
        })

    def test_password_hash_and_legacy_invalid_hash(self):
        self.assertTrue(verify_password('test-password-123', self.user.user_password_hash))
        self.assertFalse(verify_password('wrong', self.user.user_password_hash))
        self.assertFalse(verify_password('anything', '!'))

    def test_login_cookie_ttl_rotation_and_logout(self):
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['user_id'], 777)
        token = self.client.cookies.get(settings.SESSION_COOKIE_NAME)
        self.assertEqual(len(token), 64)
        self.assertIn('HttpOnly', response.headers['set-cookie'])
        self.assertIn('SameSite=lax', response.headers['set-cookie'])
        self.assertEqual(self.sessions.values[session_key(token)], '777')
        self.assertEqual(self.sessions.ttl[session_key(token)], settings.SESSION_TTL_SECONDS)
        self.assertEqual(self.login().status_code, 200)
        self.assertNotIn(session_key(token), self.sessions.values)
        new_token = self.client.cookies.get(settings.SESSION_COOKIE_NAME)
        self.assertNotEqual(token, new_token)
        self.assertEqual(self.client.post('/api/users/logout').status_code, 204)
        self.assertNotIn(session_key(new_token), self.sessions.values)
        self.assertIsNone(self.client.cookies.get(settings.SESSION_COOKIE_NAME))
        self.assertEqual(self.client.get('/api/costs/draft', headers={
            'Cookie': f'{settings.SESSION_COOKIE_NAME}={new_token}',
        }).status_code, 401)

    def test_invalid_credentials_do_not_create_a_session(self):
        for name, password in [('test_user', 'wrong'), ('missing', 'test-password-123')]:
            response = self.client.post('/api/users/auth', json={
                'user_name': name, 'password': password,
            })
            self.assertEqual(response.status_code, 401)
            self.assertNotIn('set-cookie', response.headers)
        self.assertFalse(self.sessions.values)

    def test_guest_is_denied_for_all_creator_methods(self):
        for method, url, body in [
            ('GET', '/api/costs/draft', None), ('POST', '/api/costs', None),
            ('PUT', '/api/costs/1', {'cost_description': 'x', 'cost_behavior': 'fixed', 'cost_code': 25}),
            ('DELETE', '/api/costs/1', None), ('POST', '/api/costs/1/likes', {'is_liked': 1}),
        ]:
            with self.subTest(method=method, url=url):
                self.assertEqual(self.client.request(method, url, json=body).status_code, 401)

    def test_unknown_malformed_and_expired_cookie(self):
        for token in ['forged', 'a'*64]:
            self.assertIsNone(asyncio.run(session_user_id(token, self.sessions)))
        token = 'b'*64
        self.sessions.values[session_key(token)] = 'invalid-user-id'
        self.assertIsNone(asyncio.run(session_user_id(token, self.sessions)))

    def test_redis_failure_does_not_authenticate(self):
        class FailedRedis:
            async def get(self, key):
                raise RedisConnectionError('offline')
        app.dependency_overrides[get_redis] = lambda: FailedRedis()
        response = self.client.get('/api/costs/draft', headers={
            'Cookie': f'{settings.SESSION_COOKIE_NAME}=' + 'a'*64,
        })
        self.assertEqual(response.status_code, 503)

    def test_swagger_schema_has_no_request_fields_for_server_managed_data(self):
        schema = self.client.get('/openapi.json').json()
        self.assertEqual(len(schema['paths']), 8)
        self.assertEqual(set(schema['components']['schemas']['CostPublish']['properties']),
                         {'cost_description', 'cost_behavior', 'cost_code'})
        self.assertEqual(self.client.get('/docs').status_code, 200)


if __name__ == '__main__':
    unittest.main()
