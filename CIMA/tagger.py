import json
import os

from quickumls import QuickUMLSClient

from itertools import count


class CIMADRTagger:

    def tag(self, text):
        # Resetea iterator para dar ids
        self.id_counter = count(start=1, step=1)

        # Obtiene entidades y relaciones
        entities = self.extract_entities(text)
        relations = self.extract_relations(text, entities)

        return entities + relations

    def extract_relations(self, text, tags):

        dirname = os.path.dirname(__file__)
        cui_nreg = os.path.join(dirname, 'data', 'cui_n_reg.json')
        ficha_cuis = os.path.join(dirname, 'data', 'ficha_cuis.json')

        # Abre los archivos y obtiene relaciones indi y reac
        with open(cui_nreg, 'r', encoding='utf-8') as f:
            cui_nreg = json.load(f)

        with open(ficha_cuis, 'r', encoding='utf-8') as f:
            ficha_cuis = json.load(f)

        # TODO Se puede mejorar con list comprehension
        relaciones = []

        drugs = [tag for tag in tags if 'CHEM' in tag['semgroup']]
        disorders = [tag for tag in tags if 'DISO' in tag['semgroup']]

        # Para cada entidad
        for tag_drug in drugs:

            # verifica si existe en relaciones de CIMA
            if tag_drug['cui'] in cui_nreg:

                # Recorre etiquetas disorders
                for tag_disor in disorders:

                    # Obtiene registros que tiene cui dcsa
                    for nreg in cui_nreg[tag_drug['cui']]:

                        # Comprueba las etiquetas aasociadas a cada registro
                        if tag_disor['cui'] in ficha_cuis[nreg]['indicaciones']:  # indicaciones

                            # Añade relacion de indicacion
                            relaciones.append({"id": next(self.id_counter),
                                               "type": "rel_indicacion",
                                               "n_reg": nreg,
                                               "ent_1_id": tag_drug['id'],
                                               "ent_2_id": tag_disor['id']})

                        if tag_disor['cui'] in ficha_cuis[nreg]['reacciones']:  # reacciones

                            # Añade relacion de reaccion
                            relaciones.append({"id": next(self.id_counter),
                                               "type": "rel_reaccion",
                                               "n_reg": nreg,
                                               "ent_1_id": tag_drug['id'],
                                               "ent_2_id": tag_disor['id']})

        return relaciones

    def extract_entities(self, text):
        # Pasa QuickUMLS
        matcher = QuickUMLSClient()
        matches = matcher.match(text)

        """quickumls devuelve una array para cada ngram ordenado por similitud con todas las coincidencias.
         para aumentar la recuperacion en las deteccion de relaciones
         Se tomará cada uno como una etiqueta """
        # TODO para mejorar el rendimiento establecer alguna preferencia

        # Genera identificadores para las coincidencias
        matches = [dict(m, id=next(self.id_counter), type='entity') for match in matches for m in match]

        # Devuelve lista de entidades
        return matches


def __test__():
    tagger = CIMADRTagger()
    text = "El paracetamol para el dolor de cabeza. Me ha recetado Pregabalina para la epilepsia, y me ha causado " \
           "Anorexia "
    print(f"Probando tagger: '{text}'")
    tags = tagger.tag(text)

    print(tags)
