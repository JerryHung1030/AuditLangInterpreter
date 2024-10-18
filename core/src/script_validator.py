"""
===============================================================================
    Module Name: Script Validator
    Description:  This module defines the `ScriptValidator` class, responsible 
                  for validating the structure and content of YAML files 
                  according to specific rules. It checks for required fields 
                  and validates the types and formats of the content, ensuring 
                  that the YAML conforms to expected standards. The module 
                  also handles error reporting with detailed messages and error 
                  codes.

    Author:       Jerry Hung
    Email:        chiehlee.hung@gmail.com
    Created Date: 2024-08-08
    Last Updated: 2024-08-08
    Version:      1.0.1
    
    License:      Commercial License
                  This software is licensed under a commercial license. 
                  Redistribution and use in source and binary forms, with or 
                  without modification, are not permitted without explicit 
                  written permission from the author.

                  Unauthorized copying of this software, via any medium, is 
                  strictly prohibited.

    Usage:        The `ScriptValidator` class should be instantiated, and the 
                  `validate_file` method should be used to validate YAML file 
                  content. Errors encountered during validation are raised as 
                  `ValidationError` exceptions with structured error details.

    Requirements: Python 3.10.12
                  
    Notes:        This module is part of the Script Validation and Processing 
                  system, version 1.0.0.
===============================================================================
"""

import yaml
from enum import Enum
from loguru import logger


class ScriptValidationError(Enum):
    MISSING_TOP_LEVEL_FIELD = ("V001", "Missing required top-level field")
    EMPTY_CHECKS = ("V002", "'checks' section is empty or missing")
    INVALID_CHECKS_TYPE = ("V003", "'checks' should be a list")
    MISSING_SCRIPT_FIELD = ("V004", "Missing required field in script")
    EMPTY_SCRIPT_FIELD = ("V005", "Field cannot be empty in script")
    INVALID_RULES_TYPE = ("V006", "'rules' should be a list in script")
    INVALID_COMPLIANCE_TYPE = ("V007", "'compliance' should be a list in script")
    INVALID_COMPLIANCE_ENTRY = ("V008", "Each compliance entry should be a dictionary")
    INVALID_COMPLIANCE_VALUE = ("V009", "The compliance value should be a list")


class ValidationError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__("Validation error occurred")

    def __str__(self):
        return f"ValidationError: {self.errors}"


class ScriptValidator:
    def __init__(self):
        self.errors = []

    def validate_file(self, file_content: str) -> dict:
        try:
            logger.info("Starting validation for YAML file content.")
            data = yaml.safe_load(file_content)
            self.validate_structure(data)
            self.validate_checks(data.get('checks'))
            if self.errors:
                logger.error("Validation failed with errors: {}", self.errors)
                raise ValidationError(self.errors)
            logger.info("Validation passed successfully.")
            return data
        except yaml.YAMLError as e:
            logger.error("YAML format error: {}", str(e))
            raise ValidationError([{"code": "YAML_ERROR", "message": f"Invalid YAML format: {str(e)}"}])

    def validate_structure(self, data: dict):
        logger.debug("Validating YAML structure.")
        required_fields = ['checks']
        for field in required_fields:
            if field not in data:
                self.add_error(ScriptValidationError.MISSING_TOP_LEVEL_FIELD, field)
        if not data.get('checks'):
            self.add_error(ScriptValidationError.EMPTY_CHECKS)

    def validate_checks(self, checks: list):
        if not isinstance(checks, list):
            logger.error("Checks validation failed: 'checks' should be a list.")
            self.add_error(ScriptValidationError.INVALID_CHECKS_TYPE)
            return

        logger.debug("Validating individual checks.")
        for check in checks:
            self.validate_script(check)

    def validate_script(self, script: dict):
        logger.debug("Validating script with ID: {}", script.get('id', 'unknown'))
        required_fields = ['id', 'title', 'description', 'rationale', 'remediation', 'condition', 'rules']
        for field in required_fields:
            if field not in script:
                self.add_error(ScriptValidationError.MISSING_SCRIPT_FIELD, field, script.get('id', 'unknown'))
            elif not script.get(field):
                self.add_error(ScriptValidationError.EMPTY_SCRIPT_FIELD, field, script.get('id', 'unknown'))

        if 'rules' in script and not isinstance(script['rules'], list):
            self.add_error(ScriptValidationError.INVALID_RULES_TYPE, script.get('id', 'unknown'))

        if 'compliance' in script:
            self.validate_compliance(script['compliance'], script.get('id', 'unknown'))

    def validate_compliance(self, compliance: list, script_id: str):
        if not isinstance(compliance, list):
            self.add_error(ScriptValidationError.INVALID_COMPLIANCE_TYPE, script_id)
            return

        logger.debug("Validating compliance entries for script ID: {}", script_id)
        for item in compliance:
            if not isinstance(item, dict):
                self.add_error(ScriptValidationError.INVALID_COMPLIANCE_ENTRY, script_id)
                continue

            for key, value in item.items():
                if not isinstance(value, list):
                    self.add_error(ScriptValidationError.INVALID_COMPLIANCE_VALUE, script_id, key)

    def add_error(self, error_type: ScriptValidationError, *args):
        error = {
            "code": error_type.value[0],
            "message": error_type.value[1],
        }
        if args:
            error.update({"details": args})
        logger.error("Validation error: {}", error)
        self.errors.append(error)

    def get_errors(self):
        return self.errors
