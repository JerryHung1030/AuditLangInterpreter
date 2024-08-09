"""
===============================================================================
    Program Name: Semantic Tree Builder Unit Tests
    Description:  This script contains unit tests for the Semantic Tree Builder, 
                  validating the functionality of parsing and building a semantic 
                  tree structure from a set of rules. The tests cover various rule 
                  types and ensure that the generated tree or error handling behaves 
                  as expected.

    Author:       Jerry Hung
    Email:        chiehlee.hung@gmail.com
    Created Date: 2024-07-10
    Last Updated: 2024-08-08
    Version:      1.0.0
    
    License:      Commercial License
                  This software is licensed under a commercial license. 
                  Redistribution and use in source and binary forms, with or 
                  without modification, are not permitted without explicit 
                  written permission from the author.
                  
                  You may use this software solely for internal business 
                  purposes within iiicsti. You may not distribute, 
                  sublicense, or resell this software or its modifications in 
                  any form.

                  Unauthorized copying of this software, via any medium, is 
                  strictly prohibited.
    
    Usage:        This script uses pytest to run unit tests against the 
                  Semantic Tree Builder. Test cases are loaded from YAML files, 
                  and the generated tree or errors are compared to the expected 
                  outputs.

    Requirements: Python 3.10.12
                  pytest
                  pyyaml
                   
    Notes:        To run the tests, use the command: pytest <script_name>.py
===============================================================================
"""

import pytest
import yaml
import json
import os
from typing import Dict
from rule_exec_engine.semantic_tree_builder import (
    ExecutionNode,
    ContentRule,
    FileRule,
    DirectoryRule,
    CommandRule,
    ProcessRule,
    RegistryRule,
    ConditionNode,
    SemanticTreeBuilder,
    SemanticTreeError
)

@pytest.fixture(scope='module')
def semantic_tree_builder():
    return SemanticTreeBuilder()

def load_yaml_file(file_path: str) -> Dict:
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def load_test_cases(file_path: str) -> Dict:
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Load all test cases from the configuration file
test_cases_path = os.path.join(os.path.dirname(__file__), 'test_data_mappings.yml')
test_cases = load_test_cases(test_cases_path)

@pytest.mark.parametrize("case", test_cases['test_data_mappings'])
def test_build_tree_to_json(semantic_tree_builder, case):
    input_data_path = os.path.join(os.path.dirname(__file__), case['input'])
    expected_output_path = os.path.join(os.path.dirname(__file__), case['expected_output'])
    
    input_data = load_yaml_file(input_data_path)
    expected_output = load_yaml_file(expected_output_path)['checks']
    
    for check in input_data['checks']:
        check_id = check['id']
        print(f"Running test case: {check_id}")

        valid_tree_data = {
            'id': check_id,
            'condition': check['condition'],
            'rules': check['rules']
        }

        generated_tree = semantic_tree_builder.build_tree(valid_tree_data)
        expected_item = next((item for item in expected_output if item['id'] == check_id), None)
        
        if 'errors' in expected_item:
            expected_error = expected_item['errors']
            assert generated_tree is None, (
                f"Test case {check_id} failed. Expected error but tree was generated.\n"
                f"Expected Errors: {json.dumps(expected_error, indent=2)}\n"
                f"Generated Tree: {semantic_tree_builder.tree_to_json(generated_tree)}"
            )
            
            # Check for expected errors in the actual errors list
            errors = semantic_tree_builder.get_errors()
            assert errors, (
                f"Test case {check_id} failed. Expected errors but got none.\n"
                f"Expected Errors: {json.dumps(expected_error, indent=2)}"
            )
            
            # Find the error for the specific check_id and compare code and index
            matched_error = next((error for error in errors if error['id'] == check_id), None)
            assert matched_error, (
                f"Test case {check_id} failed. No matching error found in actual errors.\n"
                f"Expected Errors: {json.dumps(expected_error, indent=2)}\n"
                f"Actual Errors: {json.dumps(errors, indent=2)}"
            )
            
            assert matched_error['code'] == expected_error['code'], (
                f"Test case {check_id} failed. Expected error code {expected_error['code']} but got {matched_error['code']}."
                f"Expected Errors: {json.dumps(expected_error, indent=2)}\n"
                f"Actual Errors: {json.dumps(errors, indent=2)}"
            )
            assert matched_error['rule_number'] == expected_error['rule_number'], (
                f"Test case {check_id} failed. Expected rule index {expected_error['rule_number']} but got {matched_error['rule_number']}."
                f"Expected Errors: {json.dumps(expected_error, indent=2)}\n"
                f"Actual Errors: {json.dumps(errors, indent=2)}"
            )
        else:
            assert generated_tree is not None, (
                f"Test case {check_id} failed. Tree was not generated.\n"
                f"Expected Tree: {json.dumps(expected_item, indent=2)}\n"
                f"Actual Errors: {json.dumps(semantic_tree_builder.get_errors(), indent=2)}"
            )
            
            generated_json = json.loads(semantic_tree_builder.tree_to_json(generated_tree))
            assert generated_json == expected_item, (
                f"Test case {check_id} failed. Generated tree does not match expected.\n"
                f"Expected Tree: {json.dumps(expected_item, indent=2)}\n"
                f"Generated Tree: {json.dumps(generated_json, indent=2)}"
            )
