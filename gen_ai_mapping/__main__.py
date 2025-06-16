import argparse
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from inference import get_inference
from utils import store_llm_output, convert_to_web_format, store_llm_output_json


def main():
    start = time.time()
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-exp", "--experiment_name", help="Experiment Name", required=False
    )
    parser.add_argument("-ds", "--data_sources", help="Data Sources IDs")
    parser.add_argument("-o", "--ontologies", help="Ontologies IDs")

    args = parser.parse_args()
    experiment_name = args.experiment_name
    data_sources = args.data_sources
    ontologies = args.ontologies

    # if experiment is not defined: inference call from the web mapper-backend
    if experiment_name:
        experiment_name = f"exp{experiment_name}"
        llm_params = "llm_params"
    else:
        # LLM params: kubeflow or azure
        if os.getenv("KUBEFLOW_LLM_ENDPOINT"):
            llm_params = "kf_llm_params"
        elif os.getenv("AZURE_LLM_ENDPOINT"):
            llm_params = "azure_llm_params"
        else: # KF by default
            llm_params = "kf_llm_params"
    
    output = get_inference(experiment_name, data_sources, ontologies, llm_params)

    store_llm_output(output, experiment_name)

    web_formatted_output = convert_to_web_format(output, data_sources, ontologies)
    print(web_formatted_output)
    store_llm_output_json(web_formatted_output, experiment_name)

    end = time.time()
    print(f"Execution time: {end - start}")

    return web_formatted_output


if __name__ == "__main__":
    main()
