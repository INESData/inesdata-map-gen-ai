import os

import json
from rdflib import Graph
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone
import xml.etree.ElementTree as ET


def read_ontology(file: str):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return content


def load_ontology(file):
    graph = Graph()
    ontology = graph.parse(file, format='ttl')
    
    return ontology


def extract_schema_csv(file: str):
    with open(file, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()
        columns = first_line.split(',')
        
    return columns


def extract_schema_xml(file_path: str):
    # Parse XML and obtain the root
    tree = ET.parse(file_path)
    root = tree.getroot()
    # Schema dict to store the structure
    schema = {}

    # XML Tree stack
    stack = [(root, schema)]
    # Recorrer el árbol usando la pila
    while stack:
        element, parent_schema = stack.pop()
        # Crear la entrada para el elemento actual
        element_schema = {
            "attributes": list(element.attrib.keys()),
            "children": {}
        }
        # Insertar el esquema del elemento en el diccionario del padre
        parent_schema[element.tag] = element_schema
        # Añadir hijos a la pila
        for child in element:
            stack.append((child, element_schema["children"]))

    return schema


def extract_schema_json(file_path, data=[], depth=0):
    """
    Extracts the schema from a JSON object.
    
    Parameters:
        file_path (str): Path to the JSON file.
        data (dict or list): JSON data loaded as a dictionary or list.
        depth (int): Current depth level for nested structures (default is 0).
        
    Returns:
        dict: A dictionary representing the schema of the JSON data.
    """
    if depth == 0:
        with open(file_path, "r") as file:
            data = json.load(file)
        
    if isinstance(data, dict):
        schema = {}
        for key, value in data.items():
            if isinstance(value, dict):
                schema[key] = {"type": "object", "properties": extract_schema_json('', value, depth+1)}
            elif isinstance(value, list) and len(value) > 0:
                # Take the first element as an example for list items
                schema[key] = {"type": "array", "items": extract_schema_json('', value[0], depth+1)}
            else:
                schema[key] = {"type": type(value).__name__}
        return schema
    elif isinstance(data, list) and len(data) > 0:
        return {"type": "array", "items": extract_schema_json('', data[0], depth+1)}
    else:
        return {"type": type(data).__name__}


def get_experiment_params(experiment_name: str):
    with open('experiments/' + experiment_name + '/llm_params.json') as f:
        params = json.load(f)
    
    return params


def get_token_kubeflow():
    username = os.getenv('KUBEFLOW_USERNAME')
    password = os.getenv('KUBEFLOW_PASSWORD')
    #take the token if exists
    if os.path.exists(f'token_{username}'):
        with open(f'token_{username}', 'r') as file:
            lines = file.readlines()
            token = lines[0].strip().split(": ")[1]
            expiration_date = int(lines[1].strip().split(": ")[1])
                
        current_time_utc = datetime.now(timezone.utc)
        # unix format
        current_timestamp = current_time_utc.timestamp()

        # Check dates
        if current_timestamp > expiration_date: #expired cookie
            token = extract_new_token(username, password)
            return token
        else: #not expired
            return token

    else:
        token = extract_new_token(username, password)
        return token
    
    
def extract_new_token(username, password):
    url_kubeflow = "https://kubeflow.ai.inesdata-project.eu/"
    parsed_url_kubeflow = urlparse(url_kubeflow)
    domain_kubeflow = parsed_url_kubeflow.netloc
    session = requests.Session()

    resp = session.get(url_kubeflow, allow_redirects=True)
    if resp.status_code != 200:
        raise RuntimeError(
            f"HTTP status code '{resp.status_code}' for GET against: {url_kubeflow}"
        )

    url_redir = resp.url
    
    parsed_data = parse_keycloak_url(url_redir)

    # Authentication URL
    auth_url = parsed_data['auth_url']

    # Authentication parameters (Query String)
    params = {
        'client_id': parsed_data['client_id'],
        'redirect_uri': parsed_data['redirect_uri'],
        'response_type': parsed_data['response_type'],
        'scope': parsed_data['scope'],
        'state': parsed_data['state']
    }

    # 1. Make a GET request to obtain the login page
    response = session.get(auth_url, params=params)

    # Parse the HTML content to extract the login form (using BeautifulSoup for this)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 2. Extract the login form (assuming there's a form with username and password fields)
    login_form = soup.find('form')
    login_url = login_form['action']  # URL to send login data (probably within Keycloak)

    # Credentials (input in the form)
    login_data = {
        'username': username,
        'password': password
    }

    # 3. Send the form data to the login URL
    response = session.post(login_url, data=login_data)

    authservice_session = session.cookies.get("authservice_session")
    if authservice_session:
    # Accedemos al campo de expiración
        expiration_time = session.cookies._cookies[domain_kubeflow]['/']['authservice_session'].expires
        expiration_date = datetime.fromtimestamp(expiration_time)
        with open(f'token_{username}', 'w') as file:
            file.write(f"token: {authservice_session}\n")
            file.write(f"expiration: {expiration_time}\n")

    return authservice_session


def parse_keycloak_url(url):
    # Parse the URL
    parsed_url = urlparse(url)

    # Extract the base part of the auth_url
    auth_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

    # Extract the query parameters
    query_params = parse_qs(parsed_url.query)

    # Format the parameters (scope is a list and state is a single value)
    parsed_data = {
        'auth_url': auth_url,
        'client_id': query_params.get('client_id', [''])[0],
        'redirect_uri': query_params.get('redirect_uri', [''])[0],
        'response_type': query_params.get('response_type', [''])[0],
        'scope': ' '.join(query_params.get('scope', [])),
        'state': query_params.get('state', [''])[0]
    }

    return parsed_data
