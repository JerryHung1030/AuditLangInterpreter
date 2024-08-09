"""
===============================================================================
    Module Name: Semantic Tree Builder
    Description:  This script is designed to parse and build a semantic tree 
                  structure from a set of rules. It supports various types of 
                  rules, including file rules, directory rules, command rules, 
                  process rules, and registry rules. The script also validates 
                  the rules and handles errors related to invalid syntax or 
                  conditions.

    Author:       Jerry Hung, Bolt Lin
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
    
    Usage:        The main class `SemanticTreeBuilder` can be instantiated and 
                  used to parse rules and build a semantic tree. The tree can 
                  then be converted to JSON format or used for further processing.

    Requirements: Python 3.10.12
                   
    Notes:        None
===============================================================================
"""

import json
from typing import List, Dict, Optional, Union, Tuple
from enum import Enum
import re

class SemanticTreeError(Enum):
    INVALID_ID = ("E001", "Invalid id")
    INVALID_CONDITION = ("E002", "Invalid condition")
    UNKNOWN_RULE_TYPE = ("E003", "Unknown rule type")
    INVALID_FILE_RULE = ("E004", "Invalid file rule")
    INVALID_DIRECTORY_RULE = ("E005", "Invalid directory rule")
    INVALID_COMMAND_RULE = ("E006", "Invalid command rule")
    INVALID_PROCESS_RULE = ("E007", "Invalid process rule")
    INVALID_REGISTRY_RULE = ("E008", "Invalid registry rule")
    INVALID_CONTENT_OPERATOR = ("E009", "Invalid content operator")
    INVALID_COMPARE_EXPRESSION = ("E010", "Invalid compare expression")
    UNKNOWN_ERROR = ("E011", "Unknown error")

class ExecutionNode:
    def __init__(self, type: str, main_target: str, sub_target: str = None, target_pattern: str = None):
        self.type = type                        # Type of the execution node (e.g., 'f' for file, 'd' for directory, 'r' for registry)
        self.main_target = main_target          # Main target path or command
        self.sub_target = sub_target            # Sub target, such as registry key value
        self.target_pattern = target_pattern    # Pattern used to match the target, if any

    def to_dict(self):
        return {
            "type": self.type,
            "main_target": self.main_target,
            "sub_target": self.sub_target,
            "target_pattern": self.target_pattern
        }

    def __str__(self):
        return json.dumps(self.to_dict(), indent=2)

class ContentRule:
    def __init__(self, content_operator: str, value: str, compare_operator: str = None, compare_value: str = None, negation: bool = False):
        self.content_operator = content_operator    # Operator used for content matching (e.g., 'r' for regex)
        self.value = value                          # Value to match
        self.compare_operator = compare_operator    # Operator used for comparison (e.g., '<=', '>=')
        self.compare_value = compare_value          # Value to compare against
        self.negation = negation                    # Boolean indicating if the rule is negated

    def to_dict(self):
        return {
            "content_operator": self.content_operator,
            "value": self.value,
            "compare_operator": self.compare_operator,
            "compare_value": self.compare_value,
            "negation": self.negation
        }

    def __str__(self):
        return json.dumps(self.to_dict(), indent=2)

class FileRule:
    def __init__(self, execution_node: ExecutionNode, content_rules: List[ContentRule] = None, negation: bool = False):
        self.execution_node = execution_node                        # Single ExecutionNode for the file
        self.content_rules = content_rules if content_rules else [] # List of ContentRules applied to the file
        self.negation = negation                                    # Boolean indicating if the rule is negated

    def to_dict(self):
        return {
            "execution_node": self.execution_node.to_dict(),                    # Adjusted to use a single execution node
            "content_rules": [rule.to_dict() for rule in self.content_rules],   # Corrected key from 'content_rule' to 'content_rules'
            "negation": self.negation
        }

    def __str__(self):
        return json.dumps(self.to_dict(), indent=2)

class DirectoryRule:
    def __init__(self, execution_node: ExecutionNode, file_rules: List[FileRule] = None, negation: bool = False):
        self.execution_node = execution_node                # ExecutionNode for the directory
        self.file_rules = file_rules if file_rules else []  # List of FileRules applied to the directory
        self.negation = negation                            # Boolean indicating if the rule is negated

    def to_dict(self):
        return {
            "execution_node": self.execution_node.to_dict(),
            "file_rules": [rule.to_dict() for rule in self.file_rules],
            "negation": self.negation
        }

    def __str__(self):
        return json.dumps(self.to_dict(), indent=2)

class CommandRule:
    def __init__(self, execution_node: ExecutionNode, content_rules: List[ContentRule] = None, negation: bool = False):
        self.execution_node = execution_node                        # ExecutionNode for the command
        self.content_rules = content_rules if content_rules else [] # List of ContentRules applied to the command output
        self.negation = negation                                    # Boolean indicating if the rule is negated

    def to_dict(self):
        return {
            "execution_node": self.execution_node.to_dict(),
            "content_rules": [rule.to_dict() for rule in self.content_rules],
            "negation": self.negation
        }

    def __str__(self):
        return json.dumps(self.to_dict(), indent=2)

class ProcessRule:
    def __init__(self, execution_node: ExecutionNode, negation: bool = False):
        self.execution_node = execution_node    # ExecutionNode for the process
        self.negation = negation                # Boolean indicating if the rule is negated

    def to_dict(self):
        return {
            "execution_node": self.execution_node.to_dict(),
            "negation": self.negation
        }

    def __str__(self):
        return json.dumps(self.to_dict(), indent=2)

class RegistryRule:
    def __init__(self, execution_node: ExecutionNode, content_rules: List[ContentRule] = None, negation: bool = False):
        self.execution_node = execution_node                        # ExecutionNode for the registry key
        self.content_rules = content_rules if content_rules else [] # List of ContentRules applied to the registry key
        self.negation = negation                                    # Boolean indicating if the rule is negated

    def to_dict(self):
        return {
            "execution_node": self.execution_node.to_dict(),
            "content_rules": [rule.to_dict() for rule in self.content_rules],
            "negation": self.negation
        }

    def __str__(self):
        return json.dumps(self.to_dict(), indent=2)

class ConditionNode:
    def __init__(self, id: str, condition: str, rules: List):
        self.id = id                # the script id
        self.condition = condition  # Condition type ('all', 'any', 'none')
        self.rules = rules          # List of rules or ConditionNodes

    def to_dict(self):
        return {
            "id": self.id,
            "condition": self.condition,
            "rules": [rule.to_dict() for rule in self.rules]
        }

    def __str__(self):
        return json.dumps(self.to_dict(), indent=2)

class SemanticTreeBuilder:
    def __init__(self):
        self.errors = []

    def add_error(self, error_code: SemanticTreeError, detail: str, id: int, rule_number: int):
        self.errors.append({
            "code": error_code.value[0],
            "message": error_code.value[1],
            "detail": detail,
            "id": id,
            "rule_number": rule_number
        })

    def parse_rule(self, rule: str, id: int, index: int) -> Union[FileRule, DirectoryRule, CommandRule, ProcessRule, RegistryRule, None]:
        try:
            # Check for negation
            negation = rule.startswith('not ')
            if negation:
                rule = rule[4:]

            # Identify the type of rule and parse accordingly
            if rule.startswith('f:'):
                return self.parse_file_rule(rule[2:], negation, id, index)
            elif rule.startswith('d:'):
                return self.parse_directory_rule(rule[2:], negation, id, index)
            elif rule.startswith('c:'):
                return self.parse_command_rule(rule[2:], negation, id, index)
            elif rule.startswith('p:'):
                return self.parse_process_rule(rule[2:], negation, id, index)
            elif rule.startswith('r:'):
                return self.parse_registry_rule(rule[2:], negation, id, index)
            else:
                self.add_error(SemanticTreeError.UNKNOWN_RULE_TYPE, rule, id, index)
                return None
        except Exception as e:
            self.add_error(SemanticTreeError.UNKNOWN_ERROR, str(e), id, index)
            return None

    def parse_file_rule(self, rule: str, negation: bool, id: int, index: int) -> Optional[FileRule]:
        # Split on '->', accounting for rules without content checks
        parts = rule.split(' -> ')

        # Check the basic format
        if len(parts) == 0 or len(parts) > 2 or not parts[0].strip():
            self.add_error(SemanticTreeError.INVALID_FILE_RULE, f"Invalid rule format: {rule}", id, index)
            print(f"Error: Invalid rule format: {rule}")
            return None
        
        file_rules = []

        # Split multiple files targets
        file_targets = parts[0].split(',')

        for file in file_targets:
            file = file.strip()
            if not file:
                continue

            execution_node = ExecutionNode(type='f', main_target=file)
            content_rules = []

            # Handle content rules if '->' is present
            if len(parts) == 2:
                content_rules = self.parse_content_rule(parts[1], "file", id, index)
                if content_rules is None:
                    self.add_error(SemanticTreeError.INVALID_FILE_RULE, f"Failed to parse content rules: {parts[1]}", id, index)
                    print(f"Error: Failed to parse content rules: {parts[1]}")
                    return None

            # Create and add the FileRule with execution nodes and content rules
            file_rule = FileRule(execution_node=execution_node, content_rules=content_rules, negation=negation)
            file_rules.append(file_rule)

        return file_rules

    def parse_directory_rule(self, rule: str, negation: bool, id: int, index: int) -> Optional[List[DirectoryRule]]:
        # Split the rule into parts by '->', handling potential content checks
        parts = rule.split(' -> ')

        # Check the basic format
        if len(parts) == 0 or not parts[0].strip():
            self.add_error(SemanticTreeError.INVALID_DIRECTORY_RULE, f"Invalid rule format: {rule}", id, index)
            print(f"Error: Invalid rule format: {rule}")
            return None

        # Initialize the list for directory rules
        directory_rules = []

        # Split multiple directory targets
        directory_targets = parts[0].split(',')

        for directory in directory_targets:
            directory = directory.strip()
            if not directory:
                continue

            # Create execution node for each directory
            execution_node_d = ExecutionNode(type='d', main_target=directory)

            # Initialize file rules to empty list
            file_rules = []

            # Handle file rules if '->' is present
            if len(parts) > 1:
                file_rule_part = parts[1].strip()

                # Check for negation
                negation_f = file_rule_part.startswith('!')
                if negation_f:
                    file_rule_part = file_rule_part[1:]

                if file_rule_part.startswith('r:'):
                    pattern = file_rule_part[2:].strip()  # remove 'r:'
                    execution_node_f = ExecutionNode(type='f', main_target=None, target_pattern=pattern)
                else:
                    execution_node_f = ExecutionNode(type='f', main_target=file_rule_part)

                # Process content rules if a second '->' exists
                content_rules = []
                if len(parts) > 2:
                    content_rules = self.parse_content_rule(parts[2], "directory", id, index)
                    if content_rules is None:
                        self.add_error(SemanticTreeError.INVALID_DIRECTORY_RULE, f"Failed to parse content rules: {parts[2]}", id, index)
                        print(f"Error: Failed to parse content rules: {parts[2]}")
                        return None

                # Create and add the FileRule with execution nodes and content rules
                file_rule = FileRule(execution_node=execution_node_f, content_rules=content_rules, negation=negation_f)
                file_rules.append(file_rule)

            # Create a DirectoryRule for each directory target
            directory_rule = DirectoryRule(execution_node=execution_node_d, file_rules=file_rules, negation=negation)
            directory_rules.append(directory_rule)

        return directory_rules

    def parse_command_rule(self, rule: str, negation: bool, id: int, index: int) -> Optional[CommandRule]:
        # Split the rule into parts by '->'
        rule = rule.replace(' -> -> ', ' -> ')
        parts = rule.split(' -> ')

        # Check if we have at least two parts for a valid command rule
        if len(parts) < 2:
            self.add_error(SemanticTreeError.INVALID_COMMAND_RULE, rule, id, index)
            print(f"Error: Invalid command rule format: {rule}")
            return None

        # The first part is the command execution node
        execution_node = ExecutionNode(type='c', main_target=parts[0].strip())

        # Initialize the list for content rules
        content_rules = []

        # Process the first level of content rules
        first_level_rules = parts[1].strip()
        first_level_content_rules = self.parse_content_rule(first_level_rules, "command", id, index)
        if first_level_content_rules is None:
            print(f"Error: Failed to parse first level content rules: {first_level_rules}")
            return None
        content_rules.extend(first_level_content_rules)

        # Process the second level of content rules if present
        if len(parts) > 2:
            second_level_rules = ' -> '.join(parts[2:]).strip()  # Reconstruct the second level rules
            second_level_content_rules = self.parse_content_rule(second_level_rules, "command", id, index)
            if second_level_content_rules is None:
                self.add_error(SemanticTreeError.INVALID_COMMAND_RULE, f"Failed to parse second level content rules: {second_level_rules}", id, index)
                print(f"Error: Failed to parse second level content rules: {second_level_rules}")
                return None
            content_rules.extend(second_level_content_rules)

        # Create and return the CommandRule
        command_rule = CommandRule(execution_node=execution_node, content_rules=content_rules, negation=negation)
        return command_rule

    def parse_process_rule(self, rule: str, negation: bool, id: int, index: int) -> ProcessRule:
        if rule.startswith('r:'):
            rule = rule[2:]
            execution_node = ExecutionNode(type='p', main_target=None, target_pattern=rule)
        else:
            execution_node = ExecutionNode(type='p', main_target=rule)
        return ProcessRule(execution_node=execution_node, negation=negation)

    def parse_registry_rule(self, rule: str, negation: bool, id: int, index: int) -> Optional[RegistryRule]:
        parts = rule.split(' -> ')
        if len(parts) < 1:
            self.add_error(SemanticTreeError.INVALID_REGISTRY_RULE, rule, id, index)
            return None

        main_target = parts[0]
        sub_target = parts[1] if len(parts) > 1 else None
        target_pattern = None
        content_rules = []

        if len(parts) > 2:
            content_rules = self.parse_content_rule(' -> '.join(parts[2:]), "registry", id, index)
            if content_rules is None:
                self.add_error(SemanticTreeError.INVALID_REGISTRY_RULE, rule, id, index)
                return None

        execution_node = ExecutionNode(type='r', main_target=main_target, sub_target=sub_target, target_pattern=target_pattern)
        return RegistryRule(execution_node=execution_node, content_rules=content_rules, negation=negation)

    def parse_content_rule(self, rule: str, caller: str, id: int, index: int) -> Optional[List['ContentRule']]:
        content_rules = []
        rule_parts = rule.split(' && ')

        for part in rule_parts:
            negation, part = self._check_negation(part.strip())

            if caller == "registry" and part and not part.startswith('r:') and not part.startswith('n:'):
                # For registry rules, if the part is not starting with 'r:' or 'n:', treat it as a sub_target value
                content_rules.append(ContentRule(
                    content_operator=None,
                    value=part,
                    compare_operator=None,
                    compare_value=None,
                    negation=negation
                ))
            else:
                if part.startswith('r:'):
                    content_operator, value = 'r', part[2:].strip()
                    if not self._is_valid_regex(value):
                        self.add_error(SemanticTreeError.INVALID_CONTENT_OPERATOR, f"Invalid regex in rule: {part}", id, index)
                        print(f"Error: Invalid regex in rule: {value}")
                        return None

                elif part.startswith('n:'):
                    parsed_numeric_rule = self._parse_numeric_rule(part[2:].strip(), id, index)
                    if parsed_numeric_rule is None:
                        print(f"Error: Invalid numeric rule format: {part[2:].strip()}")
                        return None
                    content_operator, value, compare_operator, compare_value = parsed_numeric_rule

                else:
                    self.add_error(SemanticTreeError.INVALID_CONTENT_OPERATOR, f"Rule must start with 'r:' or 'n:': {part}", id, index)
                    print(f"Error: Rule must start with 'r:' or 'n:': {part}")
                    return None

                content_rules.append(ContentRule(
                    content_operator=content_operator,
                    value=value,
                    compare_operator=compare_operator if content_operator == 'n' else None,
                    compare_value=compare_value if content_operator == 'n' else None,
                    negation=negation
                ))

        return content_rules

    def _check_negation(self, part: str) -> Tuple[bool, str]:
        return (part.startswith('!'), part[1:]) if part.startswith('!') else (False, part)

    def _is_valid_regex(self, regex: str) -> bool:
        try:
            re.compile(regex)
            return True
        except re.error:
            return False

    def _parse_numeric_rule(self, part: str, id: int, index: int) -> Optional[Tuple[str, str, str, str]]:
        # Use regex to split the parts correctly considering multiple spaces ()
        match = re.match(r'^(.*?)\s+compare\s+([<>]=?|==|!=)\s*(\d+)$', part.strip())
        if not match:
            self.add_error(SemanticTreeError.INVALID_COMPARE_EXPRESSION, f"Numeric rule format error: {part}", id, index)
            return None

        regex, operator, number = match.groups()

        if not self._is_valid_regex(regex):
            self.add_error(SemanticTreeError.INVALID_COMPARE_EXPRESSION, f"Invalid regex in numeric rule: {regex}", id, index)
            return None

        return 'n', regex, operator, number

    def build_tree(self, obj: Dict) -> Union[ConditionNode, None]:
        try:
            id = obj.get('id', None)
            if not isinstance(id, int):
                self.add_error(SemanticTreeError.INVALID_ID, f"Invalid id type: {id}", id, 0)
                return None

            condition = obj.get('condition', None)
            if condition not in ['all', 'any', 'none']:
                self.add_error(SemanticTreeError.INVALID_CONDITION, f"Invalid condition: {condition}", id, 0)
                return None

            rules = obj.get('rules', [])
            parsed_rules = []
            for index, rule in enumerate(rules):
                parsed_rule = self.parse_rule(rule, id, index + 1)
                if parsed_rule:
                    if isinstance(parsed_rule, list):
                        parsed_rules.extend(parsed_rule)
                    else:
                        parsed_rules.append(parsed_rule)
                else:
                    print(f"Failed to parse rule: {rule}")

            # Check if there are any accumulated errors after parsing all rules
            if any(error for error in self.errors if error['id'] == id):
                print("Errors encountered during build_tree:")
                for error in self.errors:
                    print(error)
                return None

            # Return the condition node only if no errors were encountered
            condition_node = ConditionNode(id=id, condition=condition, rules=parsed_rules)
            return condition_node

        except Exception as e:
            self.add_error(SemanticTreeError.UNKNOWN_ERROR, str(e), id, 0)
            print(f"Exception encountered: {e}")
            return None

    def tree_to_json(self, tree: ConditionNode) -> str:
        return json.dumps(tree.to_dict(), separators=(',', ':'))

    def get_errors(self) -> List[Dict[str, Union[str, int]]]:
        return self.errors

    def print_tree(self, tree: ConditionNode):
        print(json.dumps(tree.to_dict(), indent=2))
