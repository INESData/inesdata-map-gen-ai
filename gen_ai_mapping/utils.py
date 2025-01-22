import importlib
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse
from langchain.prompts import PromptTemplate

import pandas as pd
import requests
from bs4 import BeautifulSoup
from rdflib import Graph
from sqlalchemy import create_engine


def connect_to_db():
    # PostgreSQL database URL
    db_driver, db_host = os.getenv("SPRING_DATASOURCE_URL").split("://", 1)
    db_driver_name = db_driver.split(":")[-1]
    db_user = os.getenv("SPRING_DATASOURCE_USERNAME")
    db_pass = os.getenv("SPRING_DATASOURCE_PASSWORD")
    db_url = f"{db_driver_name}://{db_user}:{db_pass}@{db_host}"

    try:
        # Create a SQLAlchemy engine
        engine = create_engine(db_url)
        return engine
    except Exception as e:
        print(f"An error occurred connecting to INESDATA-MAP DB: {e}")
        return None


def get_ontologies(ids):
    """
    Connects to INESDATA-MAP PostgreSQL database and
    fetches data from ontology table.

    Parameters:
        ids (list): ID's of specified ontologies.

    Returns:
        list: list of contents of all specififed ontologies.
    """
    ontologies_data = []
    # Connect to PostgreSQL database
    engine = connect_to_db()

    try:
        # Crear una conexión utilizando el engine
        connection = engine.raw_connection()

        # Connect to the database and fetch the data into a DataFrame
        ids_str = str(ids).replace("[", "").replace("]", "")
        query = f"select id, content from ontology where id in ({ids_str});"
        onto_df = pd.read_sql(query, connection)

        for index, row in onto_df.iterrows():
            # Obtén el OID del resultado
            oid = row["content"]
            # Obtener el Large Object usando el OID
            large_object = connection.lobject(oid)
            # Leer el contenido completo del Large Object
            onto_data = large_object.read()
            ontologies_data.append(onto_data)

        return ontologies_data

    except Exception as e:
        print(f"An error occurred loading the ontologies: {e}")
        return None


def load_ontologies_str(onto_ids: list):
    content = ""
    ontologies_data = get_ontologies(onto_ids)
    try:
        for ontology_data in ontologies_data:
            content += ontology_data
        return content
    except Exception as e:
        print(f"An error occurred loading the ontologies content: {e}")
        return None


def load_ontologies_rdf(onto_ids: list):
    ontologies = []
    ontologies_data = get_ontologies(onto_ids)
    try:
        for ontology_data in ontologies_data:
            graph = Graph()
            ontology = graph.parse(data=ontology_data)
            ontologies.append(ontology)
    except Exception as e:
        print(f"An error occurred loading the ontologies elements: {e}")

    return ontologies


def get_data_sources(ids: list):
    """
    Connects to INESDATA-MAP PostgreSQL database and fetches data from data_source table.

    Parameters:
        ids (list): ID's of specified data sources.

    Returns:
        list: list of filenames of all specififed data sources.
    """
    ds_files = []
    # Connect to PostgreSQL database
    engine = connect_to_db()

    try:
        # Create a connection using the engine
        connection = engine.raw_connection()

        # Connect to the database and fetch the data into a DataFrame
        ids_str = str(ids).replace("[", "").replace("]", "")
        query = (
            f"select id, file_name, file_path from data_source where id in ({ids_str});"
        )
        ds_df = pd.read_sql(query, connection)

        for index, row in ds_df.iterrows():
            # Obtain file path
            filepath = row["file_path"]
            filename = row["file_name"]
            # Obtain the file obj using the path
            file = filepath + "/" + filename
            ds_files.append(file)

        return ds_files

    except Exception as e:
        print(f"An error occurred loading the data sources: {e}")
        return None


def extract_ds_schemas(ds_ids: list):
    ds_schemas = []
    ds_filenames = get_data_sources(ds_ids)
    try:
        for ds_filename in ds_filenames:
            ds_filetype = ds_filename.split(".")[-1]
            # Extract the data soruce schema
            if ds_filetype == "csv":
                ds_schema = extract_schema_csv(ds_filename)
            elif ds_filetype == "xml":
                ds_schema = extract_schema_xml(ds_filename)
            elif ds_filetype == "json":
                ds_schema = extract_schema_json(ds_filename)
            else:
                ds_schema = None
            ds_schemas.append(",".join(ds_schema))
        return "/n".join(ds_schemas)
    except Exception as e:
        print(f"An error occurred loading the data sources schemas: {e}")
        return None


def extract_schema_csv(file: str):
    with open(file, "r", encoding="utf-8") as f:
        first_line = f.readline().strip()
        columns = first_line.split(",")

    return columns


def extract_schema_xml(file_path: str):
    # Parse XML and obtain the root
    tree = ET.parse(file_path)
    root = tree.getroot()
    # Schema dict to store the structure
    schema = {}

    # XML Tree stack
    stack = [(root, schema)]
    # Go through the XML tree using the stack
    while stack:
        element, parent_schema = stack.pop()
        # Create the entry for the current element
        element_schema = {"attributes": list(element.attrib.keys()), "children": {}}
        # Insert the element schema in the parent dict
        parent_schema[element.tag] = element_schema
        # Add children to the stack
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
                schema[key] = {
                    "type": "object",
                    "properties": extract_schema_json("", value, depth + 1),
                }
            elif isinstance(value, list) and len(value) > 0:
                # Take the first element as an example for list items
                schema[key] = {
                    "type": "array",
                    "items": extract_schema_json("", value[0], depth + 1),
                }
            else:
                schema[key] = {"type": type(value).__name__}
        return schema
    elif isinstance(data, list) and len(data) > 0:
        return {"type": "array", "items": extract_schema_json("", data[0], depth + 1)}
    else:
        return {"type": type(data).__name__}


def get_experiment_params(experiment_path: str):
    if experiment_path != "":
        with open(experiment_path + "llm_params.json") as f:
            params = json.load(f)
    else:
        with importlib.resources.open_text(
            "gen_ai_mapping", experiment_path + "llm_params.json"
        ) as f:
            params = json.load(f)

    return params


def get_experiment_prompt(
    experiment_path: str,
    experiment_params: dict,
    data_sources_ids: list,
    ontologies_ids: list,
):
    if experiment_path != "":
        experiments_module_path = experiment_path.replace("/", ".")
    else:
        experiments_module_path = ""
    prompt_template_module = importlib.import_module(
        experiments_module_path + "prompt_template"
    )

    ds_schemas = extract_ds_schemas(data_sources_ids)

    if eval(experiment_params["chunked"]):
        ontologies = load_ontologies_rdf(ontologies_ids)
        prompts = []
        for ontology in ontologies:
            for ontology_field in ontology:
                prompt_template = prompt_template_module.get_prompt(
                    ds_schemas, ontology_field
                )
                prompts.append(prompt_template)
        print(f"{len(prompts)} prompts generated with chunking")
        return prompts
    else:
        ontologies = load_ontologies_str(ontologies_ids)
        prompt_template = prompt_template_module.get_prompt(ds_schemas, ontologies)

    return prompt_template


def get_experiment_prompt_txt(experiment_path: str):
    with open(experiment_path + "prompt_template.txt", "r") as file:
        prompt_template = file.read()

    prompt_template = PromptTemplate(
        input_variables=["ontology", "data_source_schema"],
        template=prompt_template,
    )

    return prompt_template


def get_token_kubeflow():
    username = os.getenv("KUBEFLOW_USERNAME")
    password = os.getenv("KUBEFLOW_PASSWORD")
    # take the token if exists
    if os.path.exists(f"token_{username}"):
        with open(f"token_{username}", "r") as file:
            lines = file.readlines()
            token = lines[0].strip().split(": ")[1]
            expiration_date = int(lines[1].strip().split(": ")[1])

        current_time_utc = datetime.now(timezone.utc)
        # unix format
        current_timestamp = current_time_utc.timestamp()

        # Check dates
        if current_timestamp > expiration_date:  # expired cookie
            token = extract_new_token(username, password)
            return token
        else:  # not expired
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
    auth_url = parsed_data["auth_url"]

    # Authentication parameters (Query String)
    params = {
        "client_id": parsed_data["client_id"],
        "redirect_uri": parsed_data["redirect_uri"],
        "response_type": parsed_data["response_type"],
        "scope": parsed_data["scope"],
        "state": parsed_data["state"],
    }

    # 1. Make a GET request to obtain the login page
    response = session.get(auth_url, params=params)

    # Parse the HTML content to extract the login form (using BeautifulSoup for this)
    soup = BeautifulSoup(response.text, "html.parser")

    # 2. Extract the login form (assuming there's a form with username and password fields)
    login_form = soup.find("form")
    login_url = login_form[
        "action"
    ]  # URL to send login data (probably within Keycloak)

    # Credentials (input in the form)
    login_data = {"username": username, "password": password}

    # 3. Send the form data to the login URL
    response = session.post(login_url, data=login_data)

    authservice_session = session.cookies.get("authservice_session")
    if authservice_session:
        # Accedemos al campo de expiración
        expiration_time = session.cookies._cookies[domain_kubeflow]["/"][
            "authservice_session"
        ].expires
        expiration_date = datetime.fromtimestamp(expiration_time)
        with open(f"token_{username}", "w") as file:
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
        "auth_url": auth_url,
        "client_id": query_params.get("client_id", [""])[0],
        "redirect_uri": query_params.get("redirect_uri", [""])[0],
        "response_type": query_params.get("response_type", [""])[0],
        "scope": " ".join(query_params.get("scope", [])),
        "state": query_params.get("state", [""])[0],
    }

    return parsed_data
