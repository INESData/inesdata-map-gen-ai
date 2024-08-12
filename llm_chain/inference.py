import requests
import json
from pprint import pprint

import argparse
from pathlib import Path


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
    I need to generate an RML (RDF Mapping Language) file that maps a relational database to RDF using a specific ontology.

    ### Ontology:
    {ontology}

    ### Database schema (in CSV format):
    {db_schema}

    ### Requirements:
    1. Use the provided ontology to define the classes and properties in the RML.
    2. Each column in the database schema should be mapped to an appropriate property in the ontology.
    3. Generate a mapping for each table in the CSV schema.
    4. Ensure that `TriplesMap`, `LogicalSource`, `SubjectMap`, `PredicateObjectMap`, and any other necessary structures are defined according to the RML specification.
    5. The generated RML must be valid and compatible with RML mapping engines, such as RMLMapper.

    Provide the complete content of the RML file in text format. Do not include line breaks at the beginning of the file or triple quotes.
    """


    headers = {
        'Content-Type': 'application/json',
    }

    json_data = {
        'model': 'TheBloke/Mixtral-8x7B-Instruct-v0.1-GPTQ',
        'prompt': prompt,
        'max_tokens': 450,
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

    output = LLM_consume(ontology_str, csv_schema)
    
    parent_dir = Path(ontology_file).parent
    path_output_file = parent_dir / 'output_RML.ttl'

    with open(path_output_file, 'w') as file:
        file.write(output) 
    
if __name__ == "__main__":
    main()