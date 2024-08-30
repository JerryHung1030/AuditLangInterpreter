"""
===============================================================================
    Program Name: Semantic Tree Executor
    Description:  This script is designed to execute a semantic tree structure 
                  that represents various types of system checks and validations. 
                  It supports execution on remote systems via SSH, covering file 
                  existence, directory listings, process checks, command execution, 
                  and registry key checks.

    Author:       Jerry Hung, Bolt Lin
    Email:        chiehlee.hung@gmail.com
    Created Date: 2024-08-09
    Last Updated: 2024-08-29
    Version:      0.1.2
    
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

    Usage:        The main class SemanticTreeExecutor can be instantiated with 
                  SSH details to execute the semantic tree on a remote system. 
                  The results of the execution are returned as a structured 
                  output, indicating success or failure of each check.

    Requirements: Python 3.10.12, Paramiko
    
    Notes:        None
===============================================================================
"""

import paramiko
import re
from typing import Dict, Optional, Union, Tuple, List, Any
import json
import sys
from enum import Enum

class ExecutionError(Enum):
    MISMATCH_OS_TYPE = ("E101", "Mismatch in OS types")
    INVALID_NODE_TYPE = ("E102", "Invalid node type")
    INVALID_CONFIGURATION = ("E103", "Invalid configuration for node type")
    SSH_EXECUTION_FAILED = ("E104", "SSH command execution failed")
    OS_DETECTION_FAILED = ("E105", "Failed to determine the actual OS type")
    COMMAND_FAILED = ("E106", "Command execution failed")
    FILE_NOT_FOUND = ("E107", "File not found during execution")
    DIRECTORY_NOT_FOUND = ("E108", "Directory not found during execution")
    PROCESS_NOT_FOUND = ("E109", "Process not found")
    REGISTRY_KEY_NOT_FOUND = ("E110", "Registry key not found")
    REGISTRY_ACCESS_FAILED = ("E111", "Failed to access registry key")
    FILE_READ_FAILED = ("E112", "Failed to read file content")
    INVALID_CONTENT_OPERATOR = ("E113", "Invalid content operator provided")
    NUMERIC_COMPARE_FAILED = ("E114", "Failed to compare numeric values")
    PATTERN_MATCH_FAILED = ("E115", "Pattern match failed")
    INVALID_FILE_LIST = ("E116", "Invalid or empty file list provided")
    UNKNOWN_ERROR = ("E117", "Unknown error occurred during execution")

class SSHManager:
    def __init__(self, hostname: str, username: str, password: str, port: int = 22):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.client = None

    def connect(self) -> None:
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.hostname, port=self.port, username=self.username, password=self.password)
            print(f"Connected to {self.hostname} on port {self.port}")
        except paramiko.AuthenticationException:
            raise Exception(f"Authentication failed when connecting to {self.hostname}")
        except paramiko.SSHException as e:
            raise Exception(f"Could not establish SSH connection: {str(e)}")
        except Exception as e:
            raise Exception(f"Connection failed: {str(e)}")

    def execute_command(self, command: str, ) -> Tuple[str, str, int]:
        if not self.client:
            raise Exception("SSH connection not established")

        try:
            # print(f"Executing command: {command}")
            stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            exit_status = stdout.channel.recv_exit_status()
            # print(f"Command output: {output}")
            # print(f"Command error: {error}")
            # print(f"Exit status: {exit_status}")
            return output, error, exit_status
        except paramiko.SSHException as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    def close(self) -> None:
        """
        Close the SSH connection.
        """
        if self.client:
            self.client.close()
            self.client = None
            print(f"Disconnected from {self.hostname}")

class OSCommandBuilder:
    def __init__(self, os_type: str):
        self.os_type = os_type

    def build_file_existence_command(self, filepath: str) -> str:
        if self.os_type == 'linux':
            return f"test -f {filepath} && echo 'exists' || echo 'not exists'"
        elif self.os_type == 'windows':
            return f"if exist {filepath} (echo exists) else (echo not exists)"
        else:
            raise ValueError(f"Unsupported OS type: {self.os_type}")

    def build_directory_listing_command(self, directory: str, pattern: str) -> str:
        if self.os_type == 'linux':
            return f"ls {directory} | grep '{pattern}'"
        elif self.os_type == 'windows':
            return f"dir {directory} /b | findstr {pattern}"
        else:
            raise ValueError(f"Unsupported OS type: {self.os_type}")

    def build_stat_command(self, filepath: str) -> str:
        if self.os_type == 'linux':
            return f"stat {filepath}"
        elif self.os_type == 'windows':
            return f"Get-Item {filepath} | Format-List -Property Mode,Owner,Group"
        else:
            raise ValueError(f"Unsupported OS type: {self.os_type}")

    def build_process_check_command(self, process_name: str) -> str:
        if self.os_type == 'linux':
            return f"ps aux | grep '{process_name}' | grep -v grep"
        elif self.os_type == 'windows':
            return f"tasklist /FI \"IMAGENAME eq {process_name}\""
        else:
            raise ValueError(f"Unsupported OS type: {self.os_type}")

    def build_registry_check_command(self, registry_path: str, registry_key: str) -> str:
        if self.os_type == 'windows':
            return f'reg query "{registry_path}" /v {registry_key}'
        else:
            raise ValueError("Registry checks are only supported on Windows OS.")

    def build_registry_key_existence_command(self, registry_path: str) -> str:
        if self.os_type == 'windows':
            return f'reg query "{registry_path}"'
        else:
            raise ValueError("Registry checks are only supported on Windows OS.")

    def build_read_file_command(self, filepath: str) -> str:
        if self.os_type == 'linux':
            return f"cat {filepath}"
        elif self.os_type == 'windows':
            return f"type {filepath}"
        else:
            raise ValueError(f"Unsupported OS type: {self.os_type}")

class ExecutionResult:
    def __init__(self, success: bool, output: Optional[str] = None, error: Optional[str] = None):
        self.success = success
        self.output = output
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error
        }

class ExecutionNodeExecutor:
    def __init__(self, node_type: str, main_target: str, sub_target: Optional[str], target_pattern: Optional[str], os_type: str):
        self.node_type = node_type
        self.main_target = main_target
        self.sub_target = sub_target
        self.target_pattern = target_pattern
        self.os_type = os_type
        self.command_builder = OSCommandBuilder(os_type)

    def execute(self, ssh_manager: SSHManager) -> ExecutionResult:
        try:
            actual_os_type = self.determine_actual_os_type(ssh_manager)
            if self.os_type != actual_os_type:
                return ExecutionResult(success=False, error=ExecutionError.MISMATCH_OS_TYPE.value[1])

            if self.node_type == 'd':
                return self.check_directory_existence(ssh_manager)
            elif self.node_type == 'f':
                if self.target_pattern:
                    return self.list_files_with_pattern(ssh_manager)
                return self.check_file_existence(ssh_manager)
            elif self.node_type == 'c':
                return self.run_command(ssh_manager)
            elif self.node_type == 'p':
                return self.check_process_existence(ssh_manager)
            elif self.node_type == 'r':
                return self.check_registry_key(ssh_manager)
            else:
                return ExecutionResult(success=False, error=ExecutionError.INVALID_NODE_TYPE.value[1])

        except Exception as e:
            return ExecutionResult(success=False, error=f"{ExecutionError.COMMAND_FAILED.value[1]}: {str(e)}")

    def determine_actual_os_type(self, ssh_manager: SSHManager) -> str:
        try:
            output, error, exit_status = ssh_manager.execute_command('uname')
            if exit_status != 0:
                raise Exception("Failed to detect OS type")
            if 'Linux' in output:
                return 'linux'.strip()
            return 'windows'.strip()
        except Exception as e:
            raise Exception(f"{ExecutionError.OS_DETECTION_FAILED.value[1]}: {str(e)}")

    def check_directory_existence(self, ssh_manager: SSHManager) -> ExecutionResult:
        if self.sub_target or self.target_pattern:
            return ExecutionResult(success=False, error=ExecutionError.INVALID_CONFIGURATION.value[1])

        try:
            command = self.command_builder.build_directory_listing_command(self.main_target, "")
            output, error, exit_status = ssh_manager.execute_command(command)
            if exit_status == 0 and output:
                return ExecutionResult(success=True, output=self.main_target)
            return ExecutionResult(success=False, output=self.main_target)
        except Exception as e:
            return ExecutionResult(success=False, error=f"{ExecutionError.SSH_EXECUTION_FAILED.value[1]}: {str(e)}")

    def check_file_existence(self, ssh_manager: SSHManager) -> ExecutionResult:
        if self.sub_target or self.target_pattern:
            return ExecutionResult(success=False, error=ExecutionError.INVALID_CONFIGURATION.value[1])

        try:
            command = self.command_builder.build_file_existence_command(self.main_target)
            output, error, exit_status = ssh_manager.execute_command(command)
            if exit_status == 0 and "exists" in output:
                return ExecutionResult(success=True, output=self.main_target)
            return ExecutionResult(success=False, output=self.main_target)
        except Exception as e:
            return ExecutionResult(success=False, error=f"{ExecutionError.SSH_EXECUTION_FAILED.value[1]}: {str(e)}")

    def list_files_with_pattern(self, ssh_manager: SSHManager) -> ExecutionResult:
        if not self.target_pattern or self.sub_target:
            return ExecutionResult(success=False, error=ExecutionError.INVALID_CONFIGURATION.value[1])

        try:
            command = self.command_builder.build_directory_listing_command(self.main_target, self.target_pattern)
            output, error, exit_status = ssh_manager.execute_command(command)
            
            if exit_status == 0 and output:
                # Split the output into a list of file names
                file_list = output.strip().split("\n")
                # Prepend the main_target (directory path) to each file name
                full_file_paths = [f"{self.main_target}/{file_name}" for file_name in file_list]
                return ExecutionResult(success=True, output=json.dumps(full_file_paths))
            
            return ExecutionResult(success=False)
        
        except Exception as e:
            return ExecutionResult(success=False, error=f"{ExecutionError.SSH_EXECUTION_FAILED.value[1]}: {str(e)}")

    def run_command(self, ssh_manager: SSHManager) -> ExecutionResult:
        if self.sub_target or self.target_pattern:
            return ExecutionResult(success=False, error=ExecutionError.INVALID_CONFIGURATION.value[1])

        try:
            if self.os_type == "linux":                                         # for test use, need to be revised
                command = "export LC_ALL=C && echo systemadmin!23 | sudo -S " + self.main_target   # for test use, need to be revised
            output, error, exit_status = ssh_manager.execute_command(command)
            if output is not None and len(str(output).strip()) > 0 and error is not None and len(str(error).strip()) > 0:
                return ExecutionResult(success=True, output=output.strip() + "\n" + error.strip())
            if output is not None and len(str(output).strip()) > 0:
                return ExecutionResult(success=True, output=output.strip())
            else:
                if error is not None and len(str(error).strip()) > 0:
                    return ExecutionResult(success=True, output=error.strip())
                else:
                    return ExecutionResult(success=False, error="Command failed with no result")
        except Exception as e:
            return ExecutionResult(success=False, error=f"{ExecutionError.SSH_EXECUTION_FAILED.value[1]}: {str(e)}")

    def check_process_existence(self, ssh_manager: SSHManager) -> ExecutionResult:
        if self.sub_target or self.target_pattern:
            return ExecutionResult(success=False, error=ExecutionError.INVALID_CONFIGURATION.value[1])

        try:
            command = self.command_builder.build_process_check_command(self.main_target)
            output, error, exit_status = ssh_manager.execute_command(command)
            if exit_status == 0 and output:
                return ExecutionResult(success=True, output=self.main_target)
            return ExecutionResult(success=False, output=self.main_target)
        except Exception as e:
            return ExecutionResult(success=False, error=f"{ExecutionError.SSH_EXECUTION_FAILED.value[1]}: {str(e)}")

    def check_registry_key(self, ssh_manager: SSHManager) -> ExecutionResult:
        try:
            if not self.sub_target:
                command = self.command_builder.build_registry_key_existence_command(self.main_target)
            else:
                command = self.command_builder.build_registry_check_command(self.main_target, self.sub_target)

            output, error, exit_status = ssh_manager.execute_command(command)
            if exit_status == 0 and output:
                return ExecutionResult(success=True, output=output.strip())
            return ExecutionResult(success=False, output=output.strip())
        except Exception as e:
            return ExecutionResult(success=False, error=f"{ExecutionError.SSH_EXECUTION_FAILED.value[1]}: {str(e)}")

class ContentCheckResult:
    def __init__(self, success: bool, error: Optional[str] = None, details: Optional[str] = None):
        self.success = success
        self.error = error
        self.details = details

    def to_dict(self) -> Dict[str, Union[bool, Optional[str]]]:
        return {
            "success": self.success,
            "error": self.error,
            "details": self.details,
        }

    def __repr__(self):
        return f"ContentCheckResult(success={self.success}, error={self.error}, details={self.details})"

class ContentRuleChecker:
    def __init__(
        self,
        node_type: str,
        content_rules: List[Dict],  # Now handling a list of content rules
        ssh_manager: SSHManager,
        command_builder: OSCommandBuilder,
        os_type: str
    ):
        self.node_type = node_type
        self.content_rules = content_rules  # Store all content rules
        self.ssh_manager = ssh_manager
        self.command_builder = command_builder
        self.os_type = os_type

    def check(self, content: Union[str, List[str]]) -> ContentCheckResult:
        try:
            if self.node_type == 'c':
                return self.check_command_output(content)
            elif self.node_type == 'f':
                return self.check_file_content(content)
            elif self.node_type in ['d', 'p']:
                return ContentCheckResult(success=True)
            else:
                return ContentCheckResult(success=False, error=ExecutionError.INVALID_NODE_TYPE.value[1])
        except Exception as e:
            return ContentCheckResult(success=False, error=f"{ExecutionError.UNKNOWN_ERROR.value[1]}: {str(e)}")

    def check_command_output(self, content: str) -> ContentCheckResult:
        try:
            print(f"[DEBUG] Checking command output")
            print(f"[DEBUG] Content to check:\n{content}")

            return self._check_lines(content.splitlines())

        except Exception as e:
            return ContentCheckResult(success=False, error=f"{ExecutionError.UNKNOWN_ERROR.value[1]}: {str(e)}")

    def check_file_content(self, content: Union[str, List[str]]) -> ContentCheckResult:
        try:
            if isinstance(content, str):
                content = self._parse_content(content)

            if isinstance(content, list):
                if not content:
                    return ContentCheckResult(success=False, error="No files matched the pattern.")

                results = []
                for file_path in content:
                    print(f"[DEBUG] Reading and checking file: {file_path}")
                    result = self.read_and_check_file(file_path)
                    if not result.success:
                        print(f"[DEBUG] Failed with file: {file_path}. Error: {result.error}")
                        results.append(False)
                    else:
                        results.append(result.success)

                final_result = all(results)
                return ContentCheckResult(success=final_result)

            else:
                return ContentCheckResult(success=False, error=ExecutionError.INVALID_FILE_RULE.value[1])

        except Exception as e:
            return ContentCheckResult(success=False, error=f"{ExecutionError.UNKNOWN_ERROR.value[1]}: {str(e)}")

    def read_and_check_file(self, file_path: str) -> ContentCheckResult:
        try:
            print(f"[DEBUG] Reading and checking file: {file_path}")
            command = self.command_builder.build_read_file_command(file_path)

            if self.os_type == "linux":
                command = "export LC_ALL=C && echo systemadmin!23 | sudo -S " + command
            output, error, exit_status = self.ssh_manager.execute_command(command)

            if exit_status != 0:
                print(f"[DEBUG] Failed to read file. Error: {error}")
                return ContentCheckResult(success=False, error=f"Failed to read file {file_path}: {error}")

            print(f"[DEBUG] File content:\n{output}")

            return self._check_lines(output.splitlines())

        except Exception as e:
            return ContentCheckResult(success=False, error=f"{ExecutionError.UNKNOWN_ERROR.value[1]}: {str(e)}")
        
    def _check_lines(self, lines: List[str]) -> ContentCheckResult:
        # Iterate through each line in the content
        for line in lines:
            # Check if the line matches all rules
            if all(self._check_line_against_rule(line, rule) for rule in self.content_rules):
                print(f"[DEBUG] Line matched all rules: {line}")
                return ContentCheckResult(success=True)

        print(f"[DEBUG] No line matched all rules")
        return ContentCheckResult(success=False)

    def _check_line_against_rule(self, line: str, rule: Dict) -> bool:
        content_operator = rule.get('content_operator')
        value = rule.get('value')
        negation = rule.get('negation', False)

        if content_operator == 'r':
            match = bool(re.search(value, line))
            print(f"[DEBUG] Regex match result: {match} for pattern: {value}")

        elif content_operator == 'n':
            match = self.numeric_compare(line, value)
            print(f"[DEBUG] Numeric compare result: {match} for value: {value}")

        elif content_operator is None:
            match = value in line
            print(f"[DEBUG] Substring match result: {match} for value: {value}")

        else:
            print(f"[DEBUG] Invalid content operator: {content_operator}")
            return False

        # Apply negation if required
        if negation:
            match = not match
            print(f"[DEBUG] Negation applied. Final match result: {match}")

        return match

    def numeric_compare(self, content: str, value: str) -> bool:
        try:
            print(f"[DEBUG] Performing numeric comparison on content: {content}")
            match = re.search(value, content)
            if not match:
                print(f"[DEBUG] No numeric match found for value: {value}")
                return False

            number = int(match.group(1))
            compare_value = int(self.compare_value)
            print(f"[DEBUG] Extracted number: {number}, Compare value: {compare_value}")

            if self.compare_operator == '>':
                return number > compare_value
            elif self.compare_operator == '>=':
                return number >= compare_value
            elif self.compare_operator == '<':
                return number < compare_value
            elif self.compare_operator == '<=':
                return number <= compare_value
            elif self.compare_operator == '==':
                return number == compare_value
            elif self.compare_operator == '!=':
                return number != compare_value
            else:
                print(f"[DEBUG] Invalid compare operator: {self.compare_operator}")
                return False
        except Exception as e:
            raise ValueError(f"{ExecutionError.INVALID_COMPARE_EXPRESSION.value[1]}: {str(e)}")

    def _parse_content(self, content: str) -> List[str]:
        try:
            content_list = json.loads(content)
            if isinstance(content_list, list):
                return content_list
            else:
                print(f"[DEBUG] Parsed content is not a list: {content_list}")
                return [content]
        except json.JSONDecodeError:
            print(f"[DEBUG] Content is a single file path, not a JSON list: {content}")
            return [content]

class SemanticTreeExecutionResult:
    def __init__(self, success: bool, results: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        self.success = success
        self.results = results if results is not None else {}
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "results": self.results,
            "error": self.error
        }

    def __repr__(self):
        return f"SemanticTreeExecutionResult(success={self.success}, results={self.results}, error={self.error})"

class SemanticTreeExecutor:
    def __init__(self, hostname: str, username: str, password: str, port: int = 22):
        self.ssh_manager = SSHManager(hostname, username, password, port)

    def connect(self) -> bool:
        try:
            self.ssh_manager.connect()
            return True
        except Exception as e:
            print(f"Failed to connect to {self.ssh_manager.hostname}: {str(e)}")
            return False

    def execute_tree(self, semantic_tree: Dict) -> SemanticTreeExecutionResult:
        # Attempt to connect to the SSH server
        if not self.connect():
            return SemanticTreeExecutionResult(success=False, error='Failed to connect to SSH')

        results = {}
        checks = semantic_tree.get('checks', [])
        # Default to 'linux' if not provided
        os_type = semantic_tree.get('os_type', 'linux')

        for check in checks:
            check_id = check['id']
            condition = check['condition']

            print(f"\n--- Executing check ID: {check_id} with condition: {condition} ---")

            rule_results = self._execute_rules(check['rules'], os_type)
            if isinstance(rule_results, SemanticTreeExecutionResult):
                # If an error occurred during rule execution, return it immediately
                self.ssh_manager.close()
                return rule_results

            # Print all rule results for this check ID
            print(f"[DEBUG] Rule results for check ID {check_id}: {rule_results}")

            # Determine the final check result based on the condition
            check_pass = self._evaluate_condition(condition, rule_results)
            if check_pass is None:
                self.ssh_manager.close()
                return SemanticTreeExecutionResult(
                    success=False,
                    error=f"Invalid condition specified at check ID {check_id}"
                )

            # Store the check result with rule details and condition
            results[check_id] = {
                'result': 'pass' if check_pass else 'fail',
                'condition': condition,
                'rule_results': rule_results
            }

            print(f"Check ID: {check_id} result: {results[check_id]['result']}")

        # Close the SSH connection after all checks
        self.ssh_manager.close()
        return SemanticTreeExecutionResult(success=True, results=results)


    def _execute_rules(self, rules: List[Dict], os_type: str) -> Union[List[bool], SemanticTreeExecutionResult]:
        rule_results = []
        for rule in rules:
            exec_node = rule['execution_node']
            print(f"\nExecuting rule with execution node: {exec_node}")

            execution_result = self._execute_node(exec_node, os_type)
            if not execution_result.success:

                print(f"Execution failed for rule {exec_node}: {execution_result.error}")
                rule_results.append(False)
                continue

            if exec_node['type'] == 'd' and 'file_rules' in rule:
                file_rule_results = self._process_file_rules(rule['file_rules'], execution_result.output, os_type)
                if isinstance(file_rule_results, SemanticTreeExecutionResult):
                    return file_rule_results
                rule_results.extend(file_rule_results)
            else:
                content_check_result = self._check_content_rules(rule, execution_result.output, os_type)
                if isinstance(content_check_result, SemanticTreeExecutionResult):
                    return content_check_result
                rule_results.append(content_check_result)

        return rule_results

    def _execute_node(self, exec_node: Dict, os_type: str) -> ExecutionResult:
        executor = ExecutionNodeExecutor(
            node_type=exec_node['type'],
            main_target=exec_node['main_target'],
            sub_target=exec_node.get('sub_target'),
            target_pattern=exec_node.get('target_pattern'),
            os_type=os_type,
        )
        execution_result = executor.execute(self.ssh_manager)
        print(f"Execution result: {execution_result.to_dict()}")
        return execution_result

    def _process_file_rules(self, file_rules: List[Dict], directory_output: str, os_type: str) -> Union[List[bool], SemanticTreeExecutionResult]:
        file_rule_results = []
        for file_rule in file_rules:
            exec_node = file_rule['execution_node']

            execution_result = self._execute_node(exec_node, os_type)
            if not execution_result.success:

                print(f"Execution failed for file rule {exec_node}: {execution_result.error}")
                file_rule_results.append(False)
                continue

            content_check_result = self._check_content_rules(file_rule, execution_result.output, os_type)
            if isinstance(content_check_result, SemanticTreeExecutionResult):
                return content_check_result
            file_rule_results.append(content_check_result)

        return file_rule_results

    def _check_content_rules(self, rule: Dict, exec_output: str, os_type: str) -> Union[bool, SemanticTreeExecutionResult]:
        try:
            # Initialize the ContentRuleChecker with all content_rules
            checker = ContentRuleChecker(
                node_type=rule['execution_node']['type'],
                content_rules=rule.get('content_rules', []),
                ssh_manager=self.ssh_manager,
                command_builder=OSCommandBuilder(os_type),
                os_type=os_type
            )

            content_result = checker.check(exec_output)
            print(f"Content result: {content_result.to_dict()}")

            if not content_result.success:
                print(f"Content check failed for rule {rule['execution_node']}: {content_result.error}")
                return False

            return not content_result.success if rule['negation'] else content_result.success

        except Exception as e:
            return SemanticTreeExecutionResult(success=False, error=f"{ExecutionError.UNKNOWN_ERROR.value[1]}: {str(e)}")

    def _evaluate_condition(self, condition: str, rule_results: List[bool]) -> Optional[bool]:
        if condition == 'all':
            return all(rule_results)
        elif condition == 'any':
            return any(rule_results)
        elif condition == 'none':
            return not any(rule_results)
        else:
            print(f"Invalid condition: {condition}")
            return None

def debug_print(message: str):
    """
    Print a debug message in a structured format.
    """
    print(f"[DEBUG] {message}")

if __name__ == "__main__":
    debug_print("Starting the semantic tree execution process...")

    if len(sys.argv) != 2:
        print("Usage: python3 semantic_tree_executor.py <expected_result_json_file>")
        sys.exit(1)

    json_file_path = sys.argv[1]
    debug_print(f"JSON file path received: {json_file_path}")

    # Initialize the semantic tree executor with SSH details
    executor = SemanticTreeExecutor(hostname='192.168.70.150', username='jerryhung', password='systemadmin!23', port=22)
    debug_print(f"Initialized SemanticTreeExecutor with hostname: {executor.ssh_manager.hostname}")

    try:
        # Load the semantic tree data from the specified file
        debug_print(f"Loading semantic tree data from {json_file_path}...")
        with open(json_file_path, 'r', encoding='utf-8') as f:
            semantic_tree = json.load(f)
        debug_print("Semantic tree data loaded successfully.")
    except Exception as e:
        debug_print(f"Failed to load semantic tree data: {str(e)}")
        sys.exit(1)

    # Execute the semantic tree and get results
    debug_print("Executing the semantic tree...")
    results = executor.execute_tree(semantic_tree)

    if results.success:
        debug_print("Semantic tree execution completed successfully.")
        debug_print(f"Execution results: {results.results}")
    else:
        debug_print(f"Semantic tree execution failed with error: {results.error}")