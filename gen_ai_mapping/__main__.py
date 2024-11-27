import argparse
import time

from inference import get_inference


def main():
    start = time.time()
    parser = argparse.ArgumentParser()

    parser.add_argument("-exp", "--experiment_name", help="Experiment Name")
    parser.add_argument("-ds", "--data_sources", help="Data Sources IDs")
    parser.add_argument("-o", "--ontologies", help="Ontologies IDs")

    args = parser.parse_args()
    experiment_name = args.experiment_name
    data_sources = args.data_sources
    ontologies = args.ontologies

    output = get_inference("exp" + experiment_name, data_sources, ontologies)

    if output:
        path_output_file = f"data/output/exp{experiment_name}_output.ttl"

        with open(path_output_file, "w") as file:
            file.write(output)
    else:
        print("error")
    end = time.time()
    print(f"Execution time: {end - start}")


if __name__ == "__main__":
    main()
