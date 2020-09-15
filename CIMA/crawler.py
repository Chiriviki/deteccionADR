import json
import re
from collections import defaultdict
from urllib import request

from bs4 import BeautifulSoup
from quickumls import QuickUMLSClient
import xml.etree.ElementTree as ET

DATA_PATH = "../../CIMA/data\\"
PRESCRIPCION_PATH = "../../CIMA/data/CIMA/prescripcion\\"

class Crawler:

    # TODO Es necesario volver a probarlo entero y ordenar un poco el codigo

    FICHAS_NAME = "fichas.json"
    NOT_FOUND_PATH = 'not_found.txt'

    def __init__(self):

        self.matcher = QuickUMLSClient()

    def crawl(self):

        # Obtiene los numeros de registro
        registros = self._get_n_registro()

        results = []

        # Recorre
        total = len(registros)
        for index, code in enumerate(registros):

            # Porciento completado
            percent = 100 * index / total
            print(f"{percent:3.2}%.......{code}")

            # Obtiene ficha tecnica
            try:
                ficha = self._get_ficha(code)
                results.append({"n_registro": code, "ficha": ficha})

            # Si no esta disponible guarda el numero en fichero
            except:
                self._set_not_found(code)
                continue

        path = DATA_PATH + "fichas.json"    # Escribe en fichero
        with open(path, "w+", encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)


    def _get_ficha(self, n_registro):

        """
        Obtiene apartados de indicaciones y reaciones de la
        ficha técnica del medicamento del registro.

        :param n_registro:
        :return: string con formato xml
        """

        url = f"https://cima.aemps.es/cima/dochtml/ft/{n_registro}/FT_{n_registro}.html"

        # Solicita web y obtene apartados 4.1 y 4.8
        response = request.urlopen(url)
        page = response.read().decode('utf-8')
        soup = BeautifulSoup(page, "html5lib")
        indicaciones = soup.find(text="4.1. Indicaciones terapéuticas").next_element
        reacciones = soup.find(text="4.8. Reacciones adversas").next_element

        # Quita etiquetas y espacios multiples
        deltagsandspaces = lambda str :  re.sub(r"\s\s+", ' ', re.sub(r'<.*?>', ' ', str))

        indicaciones = deltagsandspaces(indicaciones.text)
        reacciones = deltagsandspaces(reacciones.text)

        return {'indicaciones': indicaciones, 'reacciones': reacciones }


    def _get_n_registro(self):
        """
        Obtiene los codigos de medicamentos del fichero Prescripcion.xml
        :return:
        """
        print("Obteniendo números de registro...")

        prescripcion = ET.parse(PRESCRIPCION_PATH + "Prescripcion.xml").getroot()
        registros = prescripcion.findall('{*}prescription/{*}nro_definitivo')

        return [registro.text for registro in registros]


    def matches(self):
        """
        Recorre la lista de fichas tecnicas, y obtiene coincidencias UMLS
        Guarda resultados
        :return:
        """

        # Abre fichero de fichas
        fichas_file = DATA_PATH + "fichas.json"
        with open(fichas_file, encoding='utf-8') as f:
            fichas = json.load(f)
        matches = []

        # Recorre las fichas
        total = len(fichas)
        for index, ficha in enumerate(fichas):

            # Porciento completado
            percent = 100 * index / total
            print(f"{percent:.3f}%.......Nº {ficha['n_registro']}")

            # Obtiene coincidencias UMLS
            indicaciones = self.matcher.match(ficha["ficha"]['indicaciones'])
            reacciones = self.matcher.match(ficha["ficha"]['reacciones'])

            # Incluye en diccionario los resultados obtenidos
            matches.append({'n_registro': ficha['n_registro'],
                            'indicaciones': indicaciones,
                            'reacciones': reacciones})

        # Guarda el diccionario en fichero
        matches_file = DATA_PATH + "matches.json"
        with open(matches_file, "w+", encoding='utf-8') as f:
            json.dump(matches, f, indent=4, ensure_ascii=False)


    def _set_not_found(self, n_registro):
        """
        Guarda el registro como no encontrado en archivo not_found.txt
        :return:
        """

        file_name = DATA_PATH + "not_found.txt"
        with open(file_name, 'a', encoding='utf8') as f:
            f.write(n_registro)
            f.write('\n')

c = Crawler()
c.crawl()