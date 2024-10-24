import json
from rdflib import Graph
    
def read_ontology(file: str):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return content


def load_ontology(file):
    graph = Graph()
    ontology = graph.parse(file, format='ttl')
    
    return ontology


def read_schema_csv(file: str):
    with open(file, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()
        columns = first_line.split(',')
        
    return columns

        
def get_experiment_params(experiment_name: str):
    with open('experiments/' + experiment_name + '/llm_params.json') as f:
        params = json.load(f)
    
    return params