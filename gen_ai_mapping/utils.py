import importlib
from io import StringIO
import json
import numpy as np
import os
import ast
import traceback
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse
from langchain.prompts import PromptTemplate
import mysql.connector
import pandas as pd
import psycopg2
import requests
from bs4 import BeautifulSoup
from rdflib import Graph
from sqlalchemy import create_engine

from llm_metrics import RML_COLS_STR


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
        print(traceback.format_exc())
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
        query = f"select id, content, title, url from ontology where id in ({ids_str});"
        onto_df = pd.read_sql(query, connection)

        for index, row in onto_df.iterrows():
            onto_data = {}
            # Obtén el OID del resultado
            oid = row["content"]
            # Obtener el Large Object usando el OID
            large_object = connection.lobject(oid)
            # Leer el contenido completo del Large Object
            onto_data["data"] = large_object.read()
            onto_data["name"] = row["title"]
            onto_data["url"] = row["url"]
            ontologies_data.append(onto_data)

        return ontologies_data

    except Exception as e:
        print(f"An error occurred loading the ontologies: {e}")
        print(traceback.format_exc())
        return None


def load_ontologies_str(onto_ids: list):
    content = ""
    ontologies_data = get_ontologies(onto_ids)
    try:
        for ontology_data in ontologies_data:
            content += (
                f"{ontology_data['name']}: {ontology_data['url']}\n{ontology_data['data']}\n\n"
            )
        return content
    except Exception as e:
        print(f"An error occurred loading the ontologies content: {e}")
        print(traceback.format_exc())
        return None


def read_ontology_rdf(ontology_data):
    try:  # rdf ontos
        graph = Graph()
        ontology_rdf_graph = graph.parse(data=ontology_data, format="xml")
        return ontology_rdf_graph
    except Exception as e:  # owl ontos
        try:
            ontology_chunks = [o for o in ontology_data.split(os.linesep * 2)]
            return ontology_chunks
        except Exception as e:
            print(f"An error occurred loading the ontologies elements: {e}")
            print(traceback.format_exc())


def load_ontologies_list(onto_ids: list):
    ontologies = []
    ontologies_data = get_ontologies(onto_ids)
    try:
        for ontology_data in ontologies_data:
            ontology = f"{ontology_data['name']}:\n{ontology_data['url']}\n{ontology_data['data']}"
            ontologies.append(ontology)
    except Exception as e:
        print(f"An error occurred loading the ontologies list: {e}")
        print(traceback.format_exc())

    return ontologies


def get_data_sources_df(ids: list):
    """
    Connects to INESDATA-MAP PostgreSQL database and fetches data from data_source table.

    Parameters:
        ids (list): ID's of specified data sources.

    Returns:
        DataFrame: a dataframe of all specififed data sources.
    """
    ds_df = pd.DataFrame([])
    # Connect to PostgreSQL database
    engine = connect_to_db()

    try:
        # Create a connection using the engine
        connection = engine.raw_connection()

        # Connect to the database and fetch the data into a DataFrame
        ids_str = str(ids).replace("[", "").replace("]", "")
        query = f"select id, name, type, file_type, file_path, file_name, database_type, connection_string, user_name, password from data_source where id in ({ids_str});"
        ds_df = pd.read_sql(query, connection)
        return ds_df

    except Exception as e:
        print(f"An error occurred loading the data sources: {e}")
        print(traceback.format_exc())
        return None


def extract_ds_schemas(ds_ids: list):
    ds_schemas_data = []
    ds_df = get_data_sources_df(ds_ids)
    try:
        for ix, row in ds_df.iterrows():
            ds_schema_data = {}
            if row["type"] == 'FILE':
                ds_filename = row["file_path"] + "/" + row["file_name"]
                ds_schema_data["name"] = row["name"]
                ds_filetype = row["file_type"].lower()
                # Extract the data soruce schema
                if ds_filetype == "csv":
                    ds_schema_data["schema"] = extract_schema_csv(ds_filename)
                elif ds_filetype == "xml":
                    ds_schema_data["schema"] = extract_schema_xml(ds_filename)
                elif ds_filetype == "json":
                    ds_schema_data["schema"] = extract_schema_json(ds_filename)
                else:
                    ds_schema_data["schema"] = None
            elif row["type"] == 'DATABASE':# Extract the database connection parameters
                host, dbname = row["connection_string"].rsplit("/", 1)
                host, port = host.rsplit(":", 1)
                db_driver, host = host.split("://", 1)
                db_params = {
                    "host": host,
                    "dbname": dbname,
                    "user": row["user_name"],
                    "password": row["password"],
                    "port": port,
                }
                if row['database_type'] == 'POSTGRESQL':
                    # Extract the schema from the database
                    ds_schema_data["schema"] = extract_schema_db_postgres(**db_params)
                elif row['database_type'] == 'MYSQL':
                    ds_schema_data["schema"] = extract_schema_db_mysql(**db_params)
                else:
                    ds_schema_data["schema"] = None
            ds_schemas_data.append(
                f"{ds_schema_data['name']}: {','.join(ds_schema_data['schema'])}"
            )
        return "/n".join(ds_schemas_data)
    except Exception as e:
        print(f"An error occurred loading the data sources schemas: {e}")
        print(traceback.format_exc())
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
    

def extract_schema_db_postgres(
    host, dbname, user, password, port=5432, schema='public'
):
    """
    Extrae el esquema de una base de datos PostgreSQL.

    Args:
        host (str): Host de la BD
        dbname (str): Nombre de la BD
        user (str): Usuario
        password (str): Contraseña
        port (int, optional): Puerto. Por defecto 5432
        schema (str, optional): Esquema a consultar. Por defecto 'public'

    Returns:
        dict: Diccionario con detalle: {tabla: {columnas: [{name, type, key}]}}
    """
    conn = psycopg2.connect(
        host=host, database=dbname, user=user, password=password, port=port
    )
    cur = conn.cursor()

    final_schema = {}

    # Obtener tablas del esquema
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s AND table_type='BASE TABLE'
    """, (schema,))
    tables = [r[0] for r in cur.fetchall()]

    for table in tables:
        cur.execute("""
            SELECT
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """, (schema, table))
        columns = cur.fetchall()
        
        # Verificar si la columna es primary key
        cur.execute("""
            SELECT
                kcu.column_name
            FROM
                information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
                AND tc.table_schema = %s
                AND tc.table_name = %s
        """, (schema, table))
        pks = set([r[0] for r in cur.fetchall()])

        final_schema[table] = {
            'columnas': [
                {
                    'name': col[0],
                    'type': col[1],
                    'is_nullable': col[2],
                    'is_primary_key': col[0] in pks
                }
                for col in columns
            ]
        }

    cur.close()
    conn.close()
    return final_schema


def extract_schema_db_mysql(
    host, dbname, user, password, port=3306, schema=None
):
    """
    Extrae el esquema de una base de datos MySQL.

    Args:
        host (str): Host de la BD
        dbname (str): Nombre de la BD
        user (str): Usuario
        password (str): Contraseña
        port (int, optional): Puerto (default 3306)
        schema (str, optional): Esquema/Base de datos a consultar (default dbname)

    Returns:
        dict: Diccionario con el esquema: {tabla: {columnas: [{name, type, key}]}}
    """
    if schema is None:
        schema = dbname

    conn = mysql.connector.connect(
        host=host, database=schema, user=user, password=password, port=port
    )
    cur = conn.cursor()

    final_schema = {}

    # Obtener lista de tablas
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s AND table_type = 'BASE TABLE'
    """, (schema,))
    tables = [r[0] for r in cur.fetchall()]

    for table in tables:
        # Obtener columnas y si son PK
        cur.execute("""
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_key
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """, (schema, table))
        columns = cur.fetchall()

        final_schema[table] = {
            'columnas': [
                {
                    'name': col[0],
                    'type': col[1],
                    'is_nullable': col[2],
                    'is_primary_key': (col[3] == 'PRI')
                }
                for col in columns
            ]
        }

    cur.close()
    conn.close()
    return final_schema


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
    prompt_template_module = importlib.import_module(experiments_module_path + "prompt_template")

    ds_schemas = extract_ds_schemas(data_sources_ids)

    if eval(experiment_params["chunked"]):
        ontologies = load_ontologies_list(ontologies_ids)
        prompts = []
        for ontology in ontologies:
            ontology_elements = read_ontology_rdf(ontology)
            for ontology_element in ontology_elements:
                prompt_template = prompt_template_module.get_prompt(ds_schemas, ontology_element)
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


def join_chunking_results(results_array):
    results_df = pd.DataFrame([])
    for result in results_array:
        # convert csv string into dataframe given by LLM
        llm_output_df = get_llm_output_df(result)
        results_df = pd.concat([results_df, llm_output_df], axis=0, ignore_index=True)
    results_df = results_df.drop_duplicates().dropna()
    # Convert df to str
    results_str = StringIO()
    results_df.to_csv(results_str, sep="|", index=False)
    print(results_str.getvalue())

    return results_str.getvalue()


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
    login_url = login_form["action"]  # URL to send login data (probably within Keycloak)

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


def store_llm_output(output, experiment_name):
    if output:
        output_dir = os.getenv("APP_DATAPROCESSINGPATH") + "/output/gen-ai"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        if experiment_name:
            path_output_file = f"{output_dir}/{experiment_name}_llm_output.csv"
        else:
            path_output_file = f"{output_dir}/llm_output.csv"

        with open(path_output_file, "w") as file:
            file.write(output)
    else:
        print("LLM error: no output generated")
        print(traceback.format_exc())


def get_llm_output_df(llm_output):
    llm_df = None
    try:
        # convert csv string into dataframe given by LLM
        llm_mapping = llm_output.strip().replace("\\", "")
        llm = pd.read_csv(StringIO(llm_mapping), sep="|", on_bad_lines="warn")
        # selecting the columns from llm df
        llm_df = llm[RML_COLS_STR + ["subject_template"]].copy().drop_duplicates(ignore_index=True).dropna(how="all")
        # striping blank spaces if present
        llm_df = llm_df.apply(lambda x: x.astype(str), axis=1).drop_duplicates(ignore_index=True).dropna(how="all")
        llm_df = llm_df.apply(
            lambda row: row.str.replace("\\_", "").replace("NONE", np.nan).str.strip()
        )
    except Exception as e:
        print(e)
        print(traceback.format_exc())

    return llm_df


def get_llm_output_objs(llm_output_item):
    objs = [
        {
            "key": llm_output_item["predicate_map_type"],
            "literalValue": llm_output_item["object_map_value"],
        },
        {
            "key": "rml:termtype",
            "literalValue": llm_output_item["object_termtype"],
        },
        {
            "key": "rml:datatype",
            "literalValue": llm_output_item["object_map_type"],
        },
    ]
    return objs


def get_llm_output_preds(llm_output_dict):
    preds = []
    for llm_output_item in llm_output_dict:
        predicate = {
            "predicate": llm_output_item["predicate_map_value"],
            "objectMap": get_llm_output_objs(llm_output_item),
        }
        preds.append(predicate)
    return preds


def convert_to_web_format(llm_output, data_sources, ontologies):
    data_sources = json.loads(data_sources)
    llm_output_json = {
        "name": "LLM mapping",
        "ontologyIds": ast.literal_eval(ontologies),
    }
    json_fields = []
    try:
        llm_output_df = get_llm_output_df(llm_output)
        # add ds_id column to llm df
        try:
            llm_output_df["logical_source_id"] = (
                llm_output_df["logical_source_value"].apply(lambda x: x.split("/")[-2]).values[0]
            )
        except Exception as e:
            llm_output_df["logical_source_id"] = ""
        for ds_id in data_sources:
            ds_llm_output_df = llm_output_df[
                (llm_output_df["logical_source_id"] == str(ds_id))
                | (llm_output_df["logical_source_id"] == "")
            ]
            ds_llm_output_dict = ds_llm_output_df.to_dict(orient="records")
            json_field = {
                "dataSourceId": ds_id,
                "logicalSource": {},
                "subject": {},
                "predicates": [],
            }
            if len(ds_llm_output_dict) > 0:
                if ds_llm_output_dict[0]["reference_formulation"] != "csv":
                    json_field["logicalSource"]["iterator"] = ds_llm_output_dict[0]["iterator"]
                json_field["subject"]["template"] = ds_llm_output_dict[0]["subject_template"]
                json_field["subject"]["className"] = ds_llm_output_dict[0]["subject_map_value"]
                json_field["predicates"] = get_llm_output_preds(ds_llm_output_dict)
                json_fields.append(json_field)
        llm_output_json["fields"] = json_fields
    except Exception as e:
        print(e)
        print(traceback.format_exc())
    return llm_output_json


def store_llm_output_json(output, experiment_name):
    if output:
        output_dir = os.getenv("APP_DATAPROCESSINGPATH") + "/output/gen-ai"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        if experiment_name:
            path_output_file = f"{output_dir}/{experiment_name}_llm_output.json"
        else:
            path_output_file = f"{output_dir}/llm_output.json"

        with open(path_output_file, "w") as file:
            json.dump(output, file)
    else:
        print("LLM error: no json output generated")
        print(traceback.format_exc())
