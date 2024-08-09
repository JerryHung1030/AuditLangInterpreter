"""
===============================================================================
    Module Name: Script Processor
    Description:  This module provides the ScriptProcessor class, which handles 
                  the end-to-end processing of YAML files. The processing 
                  involves validating the file using the ScriptValidator and 
                  building a semantic tree with the SemanticTreeBuilder. The 
                  module is designed to capture and handle errors at each step 
                  and return structured error messages or a semantic tree in 
                  JSON format.

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

    Usage:        Instantiate the `ScriptProcessor` class and call the `process`
                  method with the YAML file content as a string to validate the 
                  file and build the semantic tree. The output will be either a 
                  JSON string of the tree or a structured error message.

    Requirements: Python 3.10.12
                  
    Notes:        This module is part of the Script Validation and Processing 
                  system, version 1.0.0.
===============================================================================
"""

import json
from typing import Union, Dict, List
from enum import Enum

from script_validator import ScriptValidator, ValidationError
from semantic_tree_builder import SemanticTreeBuilder, SemanticTreeError

class ScriptProcessorError(Enum):
    FILE_VALIDATION_FAILED = ("P001", "File validation failed")
    TREE_BUILDING_FAILED = ("P002", "Tree building failed")
    UNKNOWN_ERROR = ("P003", "Unknown error")

class ScriptProcessor:
    def __init__(self):
        self.validator = ScriptValidator()
        self.tree_builder = SemanticTreeBuilder()

    def process(self, file_content: str) -> Union[str, Dict[str, Union[str, List[Dict[str, Union[str, int]]]]]]:
        try:
            # Step 1: Validate the YAML file
            script_data = self.validator.validate_file(file_content)
            
            # Step 2: Build the semantic tree for each check in the script
            results = []
            for check in script_data['checks']:
                tree = self.tree_builder.build_tree({
                    'id': check['id'],
                    'condition': check['condition'],
                    'rules': check['rules']
                })
                
                # Step 3: Check for errors during tree building
                if tree is None:
                    errors = self.tree_builder.get_errors()
                    return {
                        "status": "error",
                        "error_code": ScriptProcessorError.TREE_BUILDING_FAILED.value[0],
                        "error_message": ScriptProcessorError.TREE_BUILDING_FAILED.value[1],
                        "details": errors
                    }
                results.append(self.tree_builder.tree_to_json(tree))
            
            # Step 4: Return the JSON string of the tree if all checks passed
            return json.dumps(results, separators=(',', ':'))
        
        except ValidationError as sve:
            return {
                "status": "error",
                "error_code": ScriptProcessorError.FILE_VALIDATION_FAILED.value[0],
                "error_message": ScriptProcessorError.FILE_VALIDATION_FAILED.value[1],
                "details": sve.errors
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error_code": ScriptProcessorError.UNKNOWN_ERROR.value[0],
                "error_message": ScriptProcessorError.UNKNOWN_ERROR.value[1],
                "details": str(e)
            }
