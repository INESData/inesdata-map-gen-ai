import requests
import json
from pprint import pprint

import argparse
from pathlib import Path
import sys

sys.path.insert(1, '/home/jovyan/jfog/gen-ai-rml-api')

from experiments.sample1.prompt_template import get_prompt


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
    headers = {
        'Content-Type': 'application/json',
    }

    json_data = {
        'model': 'TheBloke/Mixtral-8x7B-Instruct-v0.1-GPTQ',
        'prompt': get_prompt(db_schema, ontology),
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