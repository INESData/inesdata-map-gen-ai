import argparse
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from inference import get_inference


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

    output = get_inference(experiment_name, data_sources, ontologies)

    if output:
        output_dir = "/home/mapper/output/gen-ai"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            path_output_file = f"{output_dir}/exp{experiment_name}_output.ttl"

            with open(path_output_file, "w") as file:
                file.write(output)
    else:
        print("error")
    end = time.time()
    print(f"Execution time: {end - start}")


if __name__ == "__main__":
    main()
