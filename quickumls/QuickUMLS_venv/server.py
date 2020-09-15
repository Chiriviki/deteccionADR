from quickumls import QuickUMLS
import json
import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler



class Tagger:
    """
    Etiquetador con QuickUMLS

    TODO POsibilidad de cambiar configuracion de qUMLS
    """

    SEMTYPES = {

        # DRUGS
        'T116',
        'T195',
        'T123',
        'T122',
        'T103',
        'T120',
        'T104',
        'T200',
        'T196',
        'T126',
        'T131',
        'T125',
        'T129',
        'T130',
        'T197',
        'T114',
        'T109',
        # 'T121',
        'T192',
        'T127',

        # DISORDERS
        'T020',
        'T190',
        'T049',
        'T019',
        'T047',
        'T050',
        # 'T033',
        'T037',
        'T048',
        'T191',
        'T046',
        'T184'
    }

    def __init__(self):
        print("Init QuickUMLS...")
        self.matcher = QuickUMLS('/data/quickUMLS/', accepted_semtypes=Tagger.SEMTYPES)

    def match(self, text):

        # Busca coincidencias
        matches = self.matcher.match(text, best_match=True, ignore_syntax=False)

        # json no permite escribir sets, convierte en lista
        for match in matches:
            for m in match:
                m['semtypes'] = list(m['semtypes'])

        return json.dumps(matches)


tagger = Tagger()


class ServerHandler(SimpleHTTPRequestHandler):

    def do_POST(self):
        print('Conexion recibida')

        # Obtiene el mensaje
        length = int(self.headers.get('content-length'))
        message_enc = self.rfile.read(length)
        message = message_enc.decode()

        # Pasa tagger
        matches = tagger.match(message)

        # Headers de la respuesta
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # Envía respuesta
        #response = response.replace("\\\\", "\\")  # Caracteres especiales json mete una barra extra
        response_cod = matches.encode()
        self.wfile.write(response_cod)


def run(server_class=HTTPServer, port=40000):

    server_address = ('', port)
    ServerHandler.tagger = Tagger
    httpd = server_class(server_address, ServerHandler)
    httpd.serve_forever()


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=40000)
    args = parser.parse_args()
    run(port=args.port)