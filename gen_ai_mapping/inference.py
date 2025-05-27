import json
import os
import warnings

import mlflow
import requests

from llm_metrics import get_rml_metrics, get_text_similarity
from utils import (
    get_experiment_params,
    get_experiment_prompt,
    get_token_kubeflow,
    join_chunking_results,
)

# Ignore all deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


def get_llm_inference(prompt: str, experiment_params: dict):
    model = experiment_params["model_id"]
    
    if os.getenv("KUBEFLOW_LLM_ENDPOINT"):
        llm_url = os.getenv("KUBEFLOW_LLM_ENDPOINT")
        host_kf_url = os.getenv("KUBEFLOW_LLM_HOST")
        kf_token = get_token_kubeflow()
        
        headers = {
            "Authorization": f"Bearer {kf_token}",
            "Content-Type": "application/json",
            "Host": host_kf_url,
        }
        
        json_data = {
            "model": model,
            "prompt": prompt,
            "temperature": experiment_params["temp"],
            "stream": False,
            "max_tokens": 1000,
        }

        response = requests.post(llm_url, headers=headers, json=json_data)
        json_out = json.loads(response.content)
        output = json_out["choices"][0]["text"]
    else: # AZURE OPENAI
        llm_url = os.getenv("AZURE_LLM_ENDPOINT") + f"{model}/chat/completions?api-version=2024-12-01-preview"
        azure_api_key = os.getenv("AZURE_API_KEY")
        
        headers = {
            "api-key": azure_api_key,
            "Content-Type": "application/json",
        }
        json_data = {
            "messages": [
                {
                    "role": "system",
                    "content": prompt
                }
            ],
            "top_p": 1.0,
            "model": model,
            "temperature": experiment_params["temp"],
            "stream": False,
            "max_tokens": 1000,
        }

        response = requests.post(llm_url, headers=headers, json=json_data, verify=False)
        json_out = json.loads(response.content)
        output = json_out["choices"][0]["message"]["content"]
        
    print(output)
    return output


def track_experiment(experiment_name: str, experiment_params: dict, prompt):
    # Perform LLM model inference
    print(prompt)
    result = get_llm_inference(prompt, experiment_params)
    result = result.strip()

    metrics = {}

    if experiment_name:
        # Test the chain
        mlflow.set_experiment(experiment_name + "_mlflow")
        # Enable LangChain autologging
        mlflow.langchain.autolog(log_models=True, log_input_examples=True)

        # with mlflow.start_run():
        # Log params
        mlflow.log_params(experiment_params)

        # Calculate metrics
        path_expected_output_file = experiment_params["expected_result"]
        if os.path.exists(path_expected_output_file):
            with open(path_expected_output_file, "r") as f:
                expected_result = f.read()
            # text_similarity = get_text_similarity(result, expected_result)
            # metrics.update({"text_similarity": text_similarity})
            mapping_quality_f1_score = get_rml_metrics(expected_result, result)
            metrics.update({"mapping_quality_f1_score": mapping_quality_f1_score})

        # Log metrics
        mlflow.log_metrics(metrics)

    return result, metrics


def get_inference(prompt_experiment_name: str, data_sources_ids: list, ontologies_ids: list):
    mlflow_uri = os.getenv("MLFLOW_URI", None)
    if mlflow_uri:
        mlflow.set_tracking_uri(mlflow_uri)

    if prompt_experiment_name:
        experiment_path = f"experiments/{prompt_experiment_name}/"
    else:
        experiment_path = ""

    experiment_params = get_experiment_params(experiment_path)

    if eval(experiment_params["chunked"]):
        results_array = []
        metrics_array = []
        prompt_templates = get_experiment_prompt(
            experiment_path, experiment_params, data_sources_ids, ontologies_ids
        )

        for prompt_template in prompt_templates:
            results, metrics = track_experiment(
                prompt_experiment_name, experiment_params, prompt_template
            )
            results_array.append(results)
            metrics_array.append(metrics)
        print(results_array)
        joined_results_str = join_chunking_results(results_array)

        return joined_results_str
    else:
        prompt_template = get_experiment_prompt(
            experiment_path, experiment_params, data_sources_ids, ontologies_ids
        )
        results, metrics = track_experiment(
            prompt_experiment_name, experiment_params, prompt_template
        )
        print(results)

    return results
