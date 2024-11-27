import importlib
import json
import os
import warnings

import mlflow
import requests
from langchain.prompts import PromptTemplate

from llm_metrics import get_rml_metrics, get_text_similarity
from utils import (
    extract_ds_schemas,
    get_experiment_params,
    get_token_kubeflow,
    load_ontologies_rdf,
    load_ontologies_str,
)

# Ignore all deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


def get_llm_inference(prompt: str, experiment_params: dict):
    llm_url = os.getenv("KUBEFLOW_LLM_ENDPOINT")
    host_kf_url = os.getenv("KUBEFLOW_LLM_HOST")
    kf_token = get_token_kubeflow()

    headers = {
        "Authorization": f"Bearer {kf_token}",
        "Content-Type": "application/json",
        "Host": host_kf_url,
    }

    json_data = {
        "model": experiment_params["model_id"],
        "prompt": prompt,
        "temperature": experiment_params["temp"],
        "stream": False,
        # "max_tokens": 1000,
    }

    response = requests.post(llm_url, headers=headers, json=json_data)
    json_out = json.loads(response.content)
    output = json_out["choices"][0]["text"]

    return output


def get_experiment_prompt(
    experiment_name: str,
    experiment_params: dict,
    data_sources_ids: list,
    ontologies_ids: list,
):
    prompt_template_module = importlib.import_module(
        "experiments." + experiment_name + ".prompt_template"
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


def get_experiment_prompt_txt(experiment_name: str):
    with open(f"experiments/{experiment_name}/prompt_template.txt", "r") as file:
        prompt_template = file.read()

    prompt_template = PromptTemplate(
        input_variables=["ontology", "data_source_schema"],
        template=prompt_template,
    )

    return prompt_template


def track_experiment(experiment_name: str, experiment_params: dict, prompt):
    # Test the chain
    mlflow.set_experiment(experiment_name + "_mlflow")

    # Enable LangChain autologging
    mlflow.langchain.autolog(log_models=True, log_input_examples=True)

    with mlflow.start_run():
        # Log params
        mlflow.log_params(experiment_params)

        # Perform LLM model inference
        result = get_llm_inference(prompt, experiment_params)

        metrics = {}
        path_expected_output_file = experiment_params["expected_result"]
        with open(path_expected_output_file, "r") as f:
            expected_result = f.read()
        text_similarity = get_text_similarity(result, expected_result)
        metrics.update({"text_similarity": text_similarity})

        # Log metrics
        mlflow.log_metrics(metrics)

    return result, metrics


def get_inference(
    prompt_experiment_name: str, data_sources_ids: list, ontologies_ids: list
):
    mlflow_uri = os.getenv("MLFLOW_URI")
    mlflow.set_tracking_uri(mlflow_uri)

    experiment_params = get_experiment_params(prompt_experiment_name)

    if eval(experiment_params["chunked"]):  # todo
        results_array = []
        metrics_array = []
        prompt_templates = get_experiment_prompt(
            prompt_experiment_name, experiment_params, data_sources_ids, ontologies_ids
        )

        for prompt_template in prompt_templates:
            results, metrics = track_experiment(
                prompt_experiment_name, experiment_params, prompt_template
            )
            results_array.append(results)
            metrics_array.append(metrics)
        print(results_array)
        print(metrics_array)

        return "".join(results_array)
    else:
        prompt_template = get_experiment_prompt(
            prompt_experiment_name, experiment_params, data_sources_ids, ontologies_ids
        )
        results, metrics = track_experiment(
            prompt_experiment_name, experiment_params, prompt_template
        )
        print(results)
        print(metrics)

    return results
