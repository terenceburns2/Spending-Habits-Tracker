import urllib3
from flask import Flask
from flask_testing import TestCase

class MyTest(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['LIVESERVER_PORT'] = 5000
        app.config['LIVESERVER_TIMEOUT'] = 10
        return app

    def test_server_is_online(self):
        http = urllib3.PoolManager()
        response = http.request('GET','http://127.0.0.1:5000/')
        self.assertEqual(response.status, 200)
