import requests
import json
from pprint import pprint

import argparse


def read_ontology(file):
    with open(file, 'r', encoding='utf-8') as file:
        content = file.read()
    
    return content

def read_schema_csv(file):
    with open(file, 'r', encoding='utf-8') as archivo:
        first_line = archivo.readline().strip()
        columns = first_line.split(',')
    return columns

def inference(file):
    pass
    
def LLM_consume(db_schema, ontology):
    
    prompt = f"""
    Necesito generar un fichero RML (RDF Mapping Language) que mapee una base de datos relacional a RDF usando una ontología específica.

    ### Ontología:
    {ontology}

    ### Esquema de la base de datos (en formato CSV):
    {db_schema}

    ### Requisitos:
    1. Usa la ontología proporcionada para definir las clases y propiedades en el RML.
    2. Cada columna del esquema de la base de datos debe mapearse a una propiedad adecuada de la ontología.
    3. Genera un mapeo para cada tabla en el esquema CSV.
    4. Asegúrate de definir los `TriplesMap`, `LogicalSource`, `SubjectMap`, `PredicateObjectMap`, y cualquier otra estructura necesaria de acuerdo con la especificación RML.
    5. El RML generado debe ser válido y compatible con motores de mapeo RML, como RMLMapper.

    Proporciona el contenido completo del fichero RML en formato texto.
    """

    headers = {
        'Content-Type': 'application/json',
    }

    json_data = {
        'model': 'TheBloke/Mixtral-8x7B-Instruct-v0.1-GPTQ',
        'prompt': prompt,
        'max_tokens': 900,
        'temperature': 0,
    }

    response = requests.post('http://localhost:8081/v1/completions', headers=headers, json=json_data)
    json_out = json.loads(response.content)
    output = json_out['choices'][0]['text']
    
    return output



def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-o', '--ontology', help='Ontology file')
    parser.add_argument('-csv', '--csv_file', help='CSV file')

    args = parser.parse_args()
    ontology_file = args.ontology
    csv_file = args.csv_file
    
    ontology_str = read_ontology(ontology_file)
    csv_schema = read_schema_csv(csv_file)
    
    print(ontology_str)
    print(csv_schema)
    
    LLM_consume(ontology_str, csv_schema)
    
    
if __name__ == "__main__":
    main()