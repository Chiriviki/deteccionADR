import http.client
import json
import docker
import os


class QuickUMLSClient:

    def __init__(self, host='127.0.0.1', port='40000'):

        self._run_container()
        self.host = host
        self.port = port

        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'semgroups.txt')

        # Carga semtypes y semgroups
        with open(filename, 'r') as f:
            self.semgroups = {line.split("|")[2]:
                             line.split("|")[0]
                        for line in f.read().splitlines()}


    def _run_container(self):
        """
        Si el contenedor no existe lo crea,
        Ejecuta el servidor en el contenedor
        :return:
        """

        # TODO añadir la gestion de puerto
        # TODO Importante --> Varias instancias de la clase traten de iniciar multiples servidores
        """
            En condiciones normales, funciona correctamente. El problema es:
            - Nueva instancia con servidor corriendo, salta excepcion y crea el contenedor, pero se queda sin instancia.
            Por lo que hay que eliinarlo manualmente,
            - Si no se llama a "del" despues de su uso, no destruye el contenedor.
            - 
        """
        # TODO intentar comunicarse por socket de docker

        # client = docker.from_env()
        # self.container = client.containers.run('quickumls', command='python server.py', ports={40000: 40000},
        #                                          detach=True)
        print("quickUMLS Iniciado")


    def _stop_container(self):
        """
        Si existe el contenedor lo para
        """

        # self.container.stop()
        # self.container.remove() # TODO Para que funcione es necesario eliminar el contenedor al final
        print("quickUMLS Terminado")


    def __del__(self):
        self._stop_container()


    def match(self, text):
        """
        Etiqueta texto en UMLS por medio del servidor
        Devuelve solo las coincidencias con algun semtype incluido perteneciente a
        los semgroups pasados por parametro
        :param text:
        :return:
        """
        # Envía solicitud
        headers = {'Content-type': 'application/json'}
        req = text.encode()
        conn = http.client.HTTPConnection(self.host + ':' + self.port)
        conn.request('POST', '/post', req, headers)

        # Obtiene respuesta
        response = conn.getresponse().read()

        decod = response.decode()

        results = json.loads(decod)

        # TODO El servidor debe gestionar de alguna manera el filtro por semtype
        # Añade semgroup a cada coincidencia

        for result in results:
            for match in result:
                match['semgroup']= list(set([self.semgroups[semtype] for semtype in match['semtypes']]))

        conn.close()
        return results
