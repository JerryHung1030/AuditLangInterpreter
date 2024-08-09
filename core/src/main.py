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
    Version:      1.0.0
    
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
import logging
from script_processor import ScriptProcessor

logging.basicConfig(level=logging.INFO)

def main(file_path: str):
    try:
        # Step 1: Read the YAML file content
        with open(file_path, "r") as file:
            file_content = file.read()

        # Step 2: Process the file content using ScriptProcessor
        processor = ScriptProcessor()
        result = processor.process(file_content)

        # Step 3: Check and print the result
        if isinstance(result, dict) and result.get("status") == "error":
            # Print the error details if processing failed
            logging.error(f"Error Code: {result.get('error_code')}")
            logging.error(f"Error Message: {result.get('error_message')}")
            logging.error(f"Details: {result.get('details')}")
            sys.exit(1)
        else:
            # Print the generated tree JSON string if processing succeeded
            logging.info("Generated Tree JSON:")
            print(result)

    except FileNotFoundError:
        logging.error(f"Error: The file '{file_path}' was not found.")
        sys.exit(2)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        sys.exit(3)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_yml_file>")
        sys.exit(4)
    else:
        main(sys.argv[1])
