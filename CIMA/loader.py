import json
import xml.etree.ElementTree as ET
from collections import defaultdict

from quickumls import QuickUMLSClient


def load(fichas_matches_path):

    print("Cargando CIMA UMLS")

    # Carga fichero de de matches en ficha tecnica
    # diccionario de la forma { n_reg : { indicaciones : [matches], reacciones : [matches] }}
    with open(fichas_matches_path, 'r', encoding='utf-8') as f:
        ficha_matches = json.load(f)

    ficha_cuis = {}

    # limpia los resultados
    for n_reg in ficha_matches:
        # Tan solo se queda con cui de cada match
        ficha_cuis[n_reg] = {
            "indicaciones": select_match(ficha_matches[n_reg]["indicaciones"]),
            "reacciones": select_match(ficha_matches[n_reg]["reacciones"])}

    del ficha_matches

    with open("../../CIMA/data/CIMA/ficha_cuis.json", "w+", encoding='utf-8') as f:
        json.dump(ficha_cuis, f, indent=4, ensure_ascii=False)

    # Obtiene dcsa de cada nreg
    dcsa_nreg = get_dcsa(ficha_cuis.keys())

    # Obtiene cuis de dcsa y a cada nombre les asigna los nreg que lo contienen
    cui_dcsa_nreg = get_dcsa_names_cuis(dcsa_nreg)

    # Guarda
    with open("../../CIMA/data\\cui_n_reg.json", "w+", encoding='utf-8') as f:
        json.dump(cui_dcsa_nreg, f, indent=4, ensure_ascii=False)


def get_dcsa(regs):
    """
    Obtiene dcsa para cada numero de registro
    :param regs:
    :return:
    """

    # Obtiene codigo dcsa de cada registro
    print("Obteniendo codigos dcsa")
    prescripcion = ET.parse(".\prescripcion\Prescripcion.xml" ).getroot()
    dcsa_nreg = defaultdict(list)

    # Alamcena en diccionario de forma {dcsa : [ns_reg...]}
    for reg in regs:
        cod_dcsa = prescripcion.find('{*}prescription[{*}nro_definitivo=\'' + reg + '\']/{*}cod_dcsa').text
        dcsa_nreg[cod_dcsa].append(reg)

    del prescripcion

    return dcsa_nreg


def select_match(matches):
    """
    Selecciona un conjunto de cuis en base a coinciencias
    Para este caso coge TODAS las etiquetas
    :param matches:
    :return:
    """

    # Para evitar repetidos y se encuentren indexados

    return list(set([m['cui'] for match in matches for m in match]))


def get_dcsa_names_cuis(dcsa_nreg):
    """
    Partiendo del diciconario dcsa->nregs,
    Obtiene nombres para cada dcsa
    Pasa quickUMLS a los nombres
    :param dcsa_nreg:
    :return: diccionario cui -> nregs
    """

    # Obtiene dcsa nombres para cada codigo dcsa
    print("Obteniendo nombres...")
    dcsa = ET.parse(".\prescripcion\DICCIONARIO_DCSA.xml", ).getroot()

    # Diccionario de forma cui -> n_reg que tienen dcsa
    cui_dcsa_nreg = defaultdict(list)

    # Matcher
    matcher = QuickUMLSClient()

    # Recorre dcsa obtenidos de prescripcion
    for codigo in dcsa_nreg.keys():

        # Obtiene nombre para el codigo
        dcsa_nombre = dcsa.find('{*}dcsa[{*}codigodcsa=\'' + codigo + '\']/{*}nombredcsa').text

        # Pasa quickumls en el nombre
        cuis = select_match(matcher.match(dcsa_nombre))

        # Guarda en el diccionario
        for cui in cuis:
            cui_dcsa_nreg[cui] += dcsa_nreg[codigo]

    del dcsa

    return cui_dcsa_nreg


if __name__ == "__main__":
    load("../../CIMA/data/CIMA/matches.json")
