# Semantic Tree Builder Usage Guide

## Overview

The Semantic Tree Builder is a Python-based tool designed to parse and build semantic tree structures from a set of rules defined in YAML files. It supports various types of rules, including file rules, directory rules, command rules, process rules, and registry rules. The tool also validates the rules and handles errors related to invalid syntax or conditions.

## Prerequisites

Before using the Semantic Tree Builder, ensure that your environment meets the following requirements:

- Python 3.10.12
- pip (Python package installer)

## Setting Up the Environment

### 1. Clone the Repository

If you haven't already cloned the repository, you can do so using Git:

```bash
git clone [this_project]
cd this_project
```

### 2. Create a Virtual Environment

It is recommended to use a virtual environment to manage dependencies. To create and activate a virtual environment, follow these steps:

#### On macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### On Windows:

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### 3. Install Dependencies

Once the virtual environment is activated, install the required Python packages by running:

```bash
pip install -r requirements.txt
```

## Running the Main Program

### 1. Prepare Your YAML File

Ensure that your YAML file is structured correctly and follows the required format. The YAML file should include a `checks` section with one or more scripts, each containing rules that can be parsed and validated by the tool.

### 2. Run the Main Program

To run the main program, execute the following command:

```bash
cd core/src
python3 main.py <path_to_yml_file>
```

Replace `<path_to_yml_file>` with the actual path to your YAML file.

### 3. Interpreting the Output

The program will output either a JSON representation of the semantic tree if the processing is successful or detailed error messages if any validation or tree-building errors occur.

- **Success Output**: A JSON string representing the semantic tree.
- **Error Output**: A structured dictionary containing error codes, error messages, and details.

## Running Tests with pytest

### 1. Running the Tests

Navigate to the root directory of the project and run the following command to execute all tests:

```bash
cd rule_exec_engine/core/tests
pytest test_semantic_tree_builder.py
```

### 2. Viewing Test Results

After running the tests, pytest will display a summary of the test results, including the number of tests passed, failed, or skipped. Detailed output for failed tests will be provided, including the assertion errors and stack traces.

## Additional Notes

- **Error Handling**: The program is designed to halt processing as soon as an error is encountered, providing clear feedback about the issue.
- **Extensibility**: The tool can be extended with additional rule types or validators if needed.
- **Licensing**: This software is licensed under a commercial license. Redistribution and use in source and binary forms, with or without modification, are not permitted without explicit written permission from the author.

This guide should provide you with a comprehensive overview of how to set up, run, and test the Semantic Tree Builder. If you encounter any issues or have further questions, please refer to the project's documentation or contact the author for support.