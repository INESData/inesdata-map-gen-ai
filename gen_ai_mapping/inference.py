import requests
import json
from pprint import pprint

import argparse
from pathlib import Path
import time
import importlib
from tracking import execute_experiment
import sys


def main():
    start = time.time()
    parser = argparse.ArgumentParser()

    parser.add_argument('-exp', '--experiment_name', help='Experiment Name')
    
    args = parser.parse_args()
    experiment_name = args.experiment_name

    output = execute_experiment('exp' + experiment_name)

    if output:
        path_output_file = f"/home/jovyan/vllm-work/data/output/exp{experiment_name}_output.ttl"

        with open(path_output_file, 'w') as file:
            file.write(output)
    else:
        print('error')
    end = time.time()
    print(f"Execution time: {end - start}")
    
    
if __name__ == "__main__":
    main()
