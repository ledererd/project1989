import yaml
import sys

def process_yaml(input_file):
    # Load YAML data from the input file
    with open(input_file, 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)

    # Convert YAML data to a single line
    yaml_string = yaml.dump(data)

    # Add three backslashes before each line break
    yaml_string = yaml_string.replace('\n', '\\\\\\\\n')

    # Add three backslashes before each double quote
    yaml_string = yaml_string.replace('"', '\\\\\\"')

    # Write the modified YAML string to the output file
    print(yaml_string, end='')

if __name__ == "__main__":
    # input is assumed to be the first argument, text is written to stdout
    # Process the YAML file
    process_yaml(sys.argv[1])