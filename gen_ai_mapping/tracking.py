import os

from pathlib import Path
import importlib
import json
from langchain_community.llms import VLLMOpenAI
from langchain.prompts import PromptTemplate
import mlflow
import requests
import sys
import warnings
from utils import extract_schema_csv, read_ontology, load_ontology, get_experiment_params
from llm_metrics import get_text_similarity, get_rml_metrics
from utils import get_token_kubeflow

# Ignore all deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


def get_llm_inference(prompt: str, experiment_params: dict):
    llm_url = "https://kubeflow.ai.inesdata-project.eu/openai/v1/completions"
    host_kf_url = "mixtral87b.gmv-vnavarro.kserve.ai.inesdata-project.eu"
    kf_token = get_token_kubeflow()
    
    headers = {
        'Authorization': f'Bearer {kf_token}',
        'Content-Type': 'application/json',
        'Host': host_kf_url,
    }

    json_data = {
        'model': experiment_params["model_id"],
        'prompt': prompt,
        'temperature': experiment_params["temp"],
        'stream': False,
        'max_tokens': 1000,
    }

    response = requests.post(llm_url, headers=headers, json=json_data)
    json_out = json.loads(response.content)
    output = json_out['choices'][0]['text']
    
    return output
    

def get_llm_model(experiment_params: dict):
    llm = VLLMOpenAI(
       openai_api_base="https://kubeflow.ai.inesdata-project.eu/openai/v1",
       openai_api_key="EMPTY",
       model=experiment_params["model_id"],
       temperature=experiment_params["temp"],
    )
    
    print("LLM loaded")
    return llm


def get_experiment_prompt(experiment_name: str, experiment_params: dict):
    prompt_template_module = importlib.import_module("experiments." + experiment_name + ".prompt_template")
    
    csv_schema = extract_schema_csv(experiment_params["data_source"])
    
    if eval(experiment_params["chunked"]):
        ontology = load_ontology(experiment_params["ontology"])
        prompts = []
        for ontology_field in ontology:
            # prompt_template = PromptTemplate(
            #     input_variables=["ontology", "data_source"],
            #     template=prompt_template_module.get_prompt(csv_schema, ontology_field),
            # )
            prompt_template = prompt_template_module.get_prompt(csv_schema, ontology_field)
            prompts.append(prompt_template)
        print(f"{len(prompts)} prompts generated with chunking")
        return prompts
    else:
        ontology = read_ontology(experiment_params["ontology"])
        # prompt_template = PromptTemplate(
        #     input_variables=["ontology", "data_source"],
        #     template=prompt_template_module.get_prompt(csv_schema, ontology),
        # )
        prompt_template = prompt_template_module.get_prompt(csv_schema, ontology)
    
    return prompt_template


def get_experiment_prompt_txt(experiment_name: str):
    
    with open(f'experiments/{experiment_name}/prompt_template.txt', 'r') as file:
        prompt_template = file.read() 
    
    prompt_template = PromptTemplate(
        input_variables=["ontology", "data_source_schema"],
        template=prompt_template,
    )
    
    return prompt_template
    
    
def track_experiment(experiment_name: str, experiment_params: dict, prompt):
    ontology = read_ontology(experiment_params["ontology"])
    data_source_schema = extract_schema_csv(experiment_params["data_source"])
    # Test the chain
    mlflow.set_experiment(experiment_name + '_mlflow')
    
    # Enable LangChain autologging
    mlflow.langchain.autolog(log_models=True, log_input_examples=True)

    with mlflow.start_run():
        # Log model
        # model_info = mlflow.langchain.log_model(
        #     lc_model=chain,
        #     artifact_path=experiment_name + 'model'
        # )
        # model_uri = model_info.model_uri
        # print(f"MODEL URI: {model_uri}")
        
        # Log params
        mlflow.log_params(experiment_params)
        
        # Perform LLM model inference
        result = get_llm_inference(prompt, experiment_params)  # chain.invoke({"ontology": ontology, "data_source_schema": data_source_schema})
        
        metrics = {}
        path_expected_output_file = experiment_params["expected_result"]
        with open(path_expected_output_file, 'r') as f:
            expected_result = f.read()
        text_similarity = get_text_similarity(result, expected_result)
        metrics.update({'text_similarity': text_similarity})
        
        # Log metrics
        mlflow.log_metrics(metrics)
        
    return result, metrics
    
    
def execute_experiment(experiment_name: str):
    uri = "http://node13626-inesdata-map.jelastic.labs.gmv.com:11302"
    mlflow.set_tracking_uri(uri)
    
    experiment_params = get_experiment_params(experiment_name)

    # llm = get_llm_model(experiment_params)
    
    if eval(experiment_params["chunked"]): # todo
        results_array = []
        metrics_array = []
        prompt_templates = get_experiment_prompt(experiment_name, experiment_params)

        for prompt_template in prompt_templates:
            # chain = prompt_template | llm

            results, metrics = track_experiment(experiment_name, experiment_params, prompt_template)
            results_array.append(results)
            metrics_array.append(metrics)
        print(results_array)
        print(metrics_array)
        
        return "".join(results_array)
    else:
        prompt_template = get_experiment_prompt(experiment_name, experiment_params)
        
        # chain = prompt_template | llm
        
        results, metrics = track_experiment(experiment_name, experiment_params, prompt_template)
        print(results)
        print(metrics)
        
    return results

