"""
===============================================================================
    Name: Main Script Processor
    Description:  This script serves as the entry point for processing YAML 
                  files using the `ScriptProcessor` class. It reads the YAML 
                  content from a file, validates the structure, builds a 
                  semantic tree, and outputs the result. The script handles 
                  errors gracefully, logging detailed messages and exiting 
                  with appropriate status codes in case of failure.

    Author:       Jerry Hung
    Email:        chiehlee.hung@gmail.com
    Created Date: 2024-08-08
    Last Updated: 2024-09-11
    Version:      1.0.3 beta
    
    License:      Commercial License
                  This software is licensed under a commercial license. 
                  Redistribution and use in source and binary forms, with or 
                  without modification, are not permitted without explicit 
                  written permission from the author.

                  Unauthorized copying of this software, via any medium, is 
                  strictly prohibited.

    Usage:        Run this script with the path to a YAML file as an argument:
                      $ python main.py <path_to_yml_file>

                  The script will validate the YAML file and generate a 
                  semantic tree in JSON format if successful. If errors occur, 
                  detailed logs will be printed, and the script will exit with 
                  a non-zero status code.

    Requirements: Python 3.10.12
                  
    Notes:        This script is part of the Script Validation and Processing 
                  system, version 1.0.0.
===============================================================================
"""

import sys
import os
import yaml
import random
import paramiko  # For SSH connection to get OS info
from datetime import datetime
from loguru import logger
from script_processor import ScriptProcessor

def generate_unique_filename(directory, base_filename, extension):
    """
    Generate a unique filename by appending a serial number if the file exists.
    """
    counter = 0
    filename = f"{base_filename}.{extension}"
    full_path = os.path.join(directory, filename)
    while os.path.exists(full_path):
        counter += 1
        filename = f"{base_filename}_{counter}.{extension}"
        full_path = os.path.join(directory, filename)
    return full_path

def get_os_info(ssh_details):
    """
    Retrieve the operating system information from the remote host via SSH.
    """
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            ssh_details['hostname'],
            port=ssh_details['port'],
            username=ssh_details['username'],
            password=ssh_details['password']
        )
        stdin, stdout, stderr = ssh.exec_command('cat /etc/os-release')
        output = stdout.read().decode()
        ssh.close()
        for line in output.splitlines():
            if line.startswith('PRETTY_NAME'):
                os_info = line.split('=')[1].strip().strip('"')
                return os_info
            elif line.startswith('NAME'):
                os_info = line.split('=')[1].strip().strip('"')
                return os_info
        return "Unknown"
    except Exception as e:
        logger.error(f"Error retrieving OS information: {str(e)}")
        return "Unknown"

class FlowSequence(list):
    pass

def represent_flow_sequence(dumper, data):
    return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)

class CustomDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

    def represent_mapping(self, tag, mapping, flow_style=None):
        # Override this method to prevent keys from being quoted
        value = []
        node = yaml.MappingNode(tag, value, flow_style=flow_style)
        if self.alias_key is not None:
            self.represented_objects[self.alias_key] = node
        best_style = True
        for item_key, item_value in mapping.items():
            node_key = self.represent_data(item_key)
            if isinstance(node_key, yaml.ScalarNode) and node_key.style is not None:
                node_key.style = None  # Remove style from keys to prevent quotes
            node_value = self.represent_data(item_value)
            if not (isinstance(node_key, yaml.ScalarNode) and not node_key.style) or \
               not (isinstance(node_value, yaml.ScalarNode) and not node_value.style):
                best_style = False
            value.append((node_key, node_value))
        if flow_style is None:
            if self.default_flow_style is not None:
                node.flow_style = self.default_flow_style
            else:
                node.flow_style = best_style
        return node

def str_presenter(dumper, data):
    if '\n' in data:
        # Use block style for multiline strings
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    else:
        # Use double quotes for strings that might need escaping
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

CustomDumper.add_representer(str, str_presenter)
CustomDumper.add_representer(FlowSequence, represent_flow_sequence)
CustomDumper.add_representer(int, CustomDumper.represent_int)
CustomDumper.add_representer(float, CustomDumper.represent_float)
CustomDumper.add_representer(bool, CustomDumper.represent_bool)

def main(file_path: str, ssh_details: dict):
    try:
        # Create 'reports' directory if it doesn't exist
        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)

        logs_dir = "logs"
        os.makedirs(logs_dir, exist_ok=True)

        # Generate a unique detection ID and timestamp
        detection_id = random.randint(1000, 9999)
        current_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{current_time_str}_{detection_id}"

        # Generate unique filenames for output file and log file
        output_file = generate_unique_filename(reports_dir, f"report_{base_name}", "yml")
        log_file = generate_unique_filename(logs_dir, f"log_{base_name}", "log")

        # Configure loguru to log to both stderr and a file
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
        logger.add(log_file, level="DEBUG")

        # Add these lines
        logger.info(f"Logging to file: {log_file}")
        logger.info(f"Report will be saved to: {output_file}")

        # Step 1: Read the YAML file content
        with open(file_path, "r") as file:
            file_content = file.read()

        # Parse the YAML data
        yaml_data = yaml.safe_load(file_content)
        checks = yaml_data.get('checks', [])

        # Step 2: Initialize ScriptProcessor
        processor = ScriptProcessor()

        # Step 3: Process the file content to generate the semantic tree JSON
        tree_json = processor.process(file_content)

        # Step 4: Check if processing resulted in an error
        if isinstance(tree_json, dict) and tree_json.get("status") == "error":
            # Log the error details if processing failed
            logger.error(f"Error Code: {tree_json.get('error_code')}")
            logger.error(f"Error Message: {tree_json.get('error_message')}")
            logger.error(f"Details: {tree_json.get('details')}")
            sys.exit(1)
        else:
            # Log the generated tree JSON string if processing succeeded
            logger.info("Generated Tree JSON:")
            logger.debug(tree_json)

        # Step 5: Execute the semantic tree using the executor method
        result = processor.executor(tree_json, ssh_details)

        # Step 6: Check and log the execution result
        if isinstance(result, dict) and result.get("status") == "error":
            # Log the error details if execution failed
            logger.error(f"Error Code: {result.get('error_code')}")
            logger.error(f"Error Message: {result.get('error_message')}")
            logger.error(f"Details: {result.get('details')}")
            sys.exit(1)
        else:
            # Log the execution results if succeeded
            logger.info("Execution Results:")
            logger.debug(result)

            # Initialize statistics counters
            total_checks = 0
            total_rules = 0
            passes = 0
            fails = 0

            # Get operating system info
            operating_system = get_os_info(ssh_details)

            # Map the result with the YAML rules
            for check in checks:
                check_id = check.get('id')
                if check_id is None:
                    continue  # Skip checks without an ID
                total_checks += 1  # Increment total checks

                # Get the check result
                check_result = result.get('results', {}).get(check_id)
                if check_result is None:
                    continue  # Skip if there's no result for this check

                # Determine pass or fail
                check_status = check_result.get('result')
                result_status = 'Passed' if check_status == 'pass' else 'Failed'

                # Count passes and fails
                if result_status == 'Passed':
                    passes += 1
                else:
                    fails += 1

                # Update the check with the result
                check['result'] = result_status

                # Update the rules with their results
                rule_results = check_result.get('rule_results', [])
                rules = check.get('rules', [])
                total_rules += len(rules)
                new_rules = []
                for i, rule in enumerate(rules):
                    rule_status = 'pass' if rule_results[i] else 'fail'
                    new_rules.append({rule_status: rule})
                check['rules'] = new_rules

                # Reformat the compliance field to use FlowSequence
                compliance_list = check.get('compliance', [])
                new_compliance = []
                for item in compliance_list:
                    if isinstance(item, dict):
                        for key, value in item.items():
                            if not isinstance(value, list):
                                value = [value]
                            # Ensure all elements are strings
                            value = [str(v) for v in value]
                            value = FlowSequence(value)
                            new_compliance.append({key: value})
                check['compliance'] = new_compliance

                # Ensure long text fields are single-line strings
                for field in ['description', 'rationale', 'impact', 'remediation']:
                    if field in check and isinstance(check[field], str):
                        check[field] = ' '.join(check[field].split())

            # Calculate pass percentage
            pass_percentage = (passes / total_checks * 100) if total_checks > 0 else 0

            # Prepare audit information in the specified order
            audit_info = {
                'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'endpoint': ssh_details['hostname'],
                'operating_system': operating_system,
                'total_checks': total_checks,
                'total_rules': total_rules,
                'pass_percentage': f"{pass_percentage:.2f}%",
                'fails_checks': fails,
                'passes_checks': passes
            }

            # Prepare the final output data in the specified order
            output_yaml = {
                'audit_info': audit_info,
                'checks': []
            }

            # Order the fields in each check as specified
            for check in checks:
                ordered_check = {
                    'id': check.get('id'),
                    'title': check.get('title'),
                    'result': check.get('result'),
                    'description': check.get('description'),
                    'rationale': check.get('rationale'),
                    'impact': check.get('impact'),
                    'remediation': check.get('remediation'),
                    'references': check.get('references'),
                    'compliance': check.get('compliance'),
                    'condition': check.get('condition'),
                    'rules': check.get('rules'),
                }
                output_yaml['checks'].append(ordered_check)

            # Write the output to a YAML file with proper formatting
            with open(output_file, 'w') as outfile:
                yaml.dump(
                    output_yaml,
                    outfile,
                    Dumper=CustomDumper,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                    width=4096  # Large width to prevent line wrapping
                )

            logger.info(f"Results have been written to {output_file}")

    except FileNotFoundError:
        logger.error(f"Error: The file '{file_path}' was not found.")
        sys.exit(2)
    except KeyError as e:
        logger.error(f"Missing required SSH detail: {str(e)}")
        sys.exit(3)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        sys.exit(4)

if __name__ == "__main__":
    if len(sys.argv) < 6:
        logger.info("Usage: python main.py <path_to_yml_file> <hostname> <username> <password> <port>")
        sys.exit(5)
    else:
        file_path = sys.argv[1]
        ssh_details = {
            'hostname': sys.argv[2],
            'username': sys.argv[3],
            'password': sys.argv[4],
            'port': int(sys.argv[5])
        }
        main(file_path, ssh_details)
