from __future__ import absolute_import

import json

from ds.models import App
from ds.testutils import TestCase


class AppIndexBase(TestCase):
    path = '/api/0/apps/'

    def setUp(self):
        self.user = self.create_user()
        self.repo = self.create_repo()
        super(AppIndexBase, self).setUp()


class AppListTest(AppIndexBase):
    def setUp(self):
        super(AppListTest, self).setUp()

    def test_no_filters(self):
        app = self.create_app(
            repository=self.repo,
        )
        resp = self.client.get(self.path)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 1
        assert data[0]['id'] == str(app.id)

    def test_name_filter(self):
        app = self.create_app(
            repository=self.repo,
            name='foobar',
        )
        resp = self.client.get(self.path + '?name=' + app.name)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 1
        assert data[0]['id'] == str(app.id)

        resp = self.client.get(self.path + '?name=nothing')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 0


class AppCreateTest(AppIndexBase):
    def test_simple(self):
        resp = self.client.post(self.path, data={
            'name': 'foobar',
            'provider': 'shell',
            'provider_config': '{"command": "/usr/bin/true"}',
            'repository': 'git@example.com:repo-name.git',
        })
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert data['id']

        app = App.query.get(data['id'])
        assert app.name == 'foobar'
        assert app.provider == 'shell'
        assert app.provider_config == {'command': '/usr/bin/true'}

    def test_invalid_provider(self):
        resp = self.client.post(self.path, data={
            'name': 'foobar',
            'provider': 'dummy',
            'provider_config': '{"command": "/usr/bin/true"}',
            'repository': 'git@example.com:repo-name.git',
        })
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data['error_name'] == 'invalid_provider'

    def test_invalid_provider_config(self):
        resp = self.client.post(self.path, data={
            'name': 'foobar',
            'provider': 'shell',
            'provider_config': '{}',
            'repository': 'git@example.com:repo-name.git',
        })
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data['error_name'] == 'invalid_provider_config'