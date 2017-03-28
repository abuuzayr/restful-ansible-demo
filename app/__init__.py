from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response

from .ansible import Playbook


class App(object):

    def __init__(self):
        self._config = Configurator()
        self._config.add_route('hello', '/v1/hello')
        self._config.add_view(self.route_hello_world, route_name='hello')

        self._app = self._config.make_wsgi_app()
        self._port = 3000
        self._ip = '0.0.0.0'
        self._server = make_server(self._ip, self._port, self._app)


    def run(self):
        print('Listening on {0}:{1}'.format(self._ip, self._port))
        self._server.serve_forever()


    def route_hello_world(self, req):
        pb = Playbook(
            playbooks=['hello.yml'],
            options={
                'remote_user': 'root',
                'inventory': 'cp1.groventure.com,',
                'verbosity': 2,
                'extra_vars': ['hello_name=hellyna'],
            },
        )

        pb.play()
        return Response('<body><h1>Hello World!</h1></body>')
