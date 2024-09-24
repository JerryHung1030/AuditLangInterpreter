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
    Last Updated: 2024-09-10
    Version:      0.1.9
    
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

from loguru import logger
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
        """
        Establishes an SSH connection to the specified host.
        Logs connection details and any errors encountered.
        """
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.hostname, port=self.port, username=self.username, password=self.password)
            logger.info(f"Connected to {self.hostname} on port {self.port}")
        except paramiko.AuthenticationException:
            logger.error(f"Authentication failed when connecting to {self.hostname}")
            raise Exception(f"Authentication failed when connecting to {self.hostname}")
        except paramiko.SSHException as e:
            logger.error(f"Could not establish SSH connection: {str(e)}")
            raise Exception(f"Could not establish SSH connection: {str(e)}")
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            raise Exception(f"Connection failed: {str(e)}")

    def execute_command(self, command: str) -> Tuple[str, str, int]:
        """
        Executes the specified command over the SSH connection.
        Logs the command being executed and any output, errors, or exit statuses encountered.
        """
        if not self.client:
            raise Exception("SSH connection not established")
        
        COMMAND_SEPARATOR = "===== Executing Command ====="
        OUTPUT_SEPARATOR = "----- Command Output -----"
        ERROR_SEPARATOR = "##### Command Error #####"

        try:
            logger.info(COMMAND_SEPARATOR)
            logger.info(f"Executing command: {command}")
            logger.info(COMMAND_SEPARATOR + "\n")
            
            stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode('utf-8').strip()
            error = stderr.read().decode('utf-8').strip()
            exit_status = stdout.channel.recv_exit_status()
            
            logger.info(OUTPUT_SEPARATOR)
            logger.info(f"Command output: {output if output else 'No output'}")
            logger.info(OUTPUT_SEPARATOR + "\n")
            
            logger.info(ERROR_SEPARATOR)
            logger.info(f"Command error: {error if error else 'No error'}")
            logger.info(ERROR_SEPARATOR + "\n")
            
            logger.info(f"Exit status: {exit_status}")
            
            return output, error, exit_status

        except paramiko.SSHException as e:
            logger.error(f"Failed to execute command: {str(e)}")
            raise Exception(f"Failed to execute command: {str(e)}")
        
    def execute_command_with_sudo(self, command: str, os_type: str, use_sudo: bool = False) -> Tuple[str, str, int]:
        if use_sudo and os_type:
            if os_type == "linux":
                command = f"export LC_ALL=C && echo {self.password} | sudo -S {command}"
        output, error, exit_status = self.execute_command(command)
        return output.strip(), error.strip(), exit_status

    def close(self) -> None:
        """
        Closes the SSH connection.
        Logs disconnection details.
        """
        if self.client:
            self.client.close()
            self.client = None
            logger.info(f"Disconnected from {self.hostname}")

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

    def build_directory_exsistence_command(self, directory: str) -> str:
        if self.os_type == 'linux':
            return f"ls {directory}"
        elif self.os_type == 'windows':
            return f"dir {directory} /b"
        else:
            raise ValueError(f"Unsupported OS type: {self.os_type}")

    def build_directory_listing_command(self, directory: str) -> str:
        if self.os_type == 'linux':
            # Find command to list files up to 3 levels deep recursively
            return f"find {directory} -maxdepth 3 -type f"
        elif self.os_type == 'windows':
            # Using 'dir' for Windows, recursively list all files
            return f"dir {directory} /s /b"
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
            logger.debug(f"Executing node with type: {self.node_type}, main target: {self.main_target}")
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
                logger.error(f"Invalid node type: {self.node_type}")
                return ExecutionResult(success=False, error=ExecutionError.INVALID_NODE_TYPE.value[1])

        except Exception as e:
            logger.exception(f"Command execution failed: {str(e)}")
            return ExecutionResult(success=False, error=f"{ExecutionError.COMMAND_FAILED.value[1]}: {str(e)}")
    
    def determine_actual_os_type(self, ssh_manager: SSHManager) -> str:
        try:
            command = 'uname'
            output, error, exit_status = ssh_manager.execute_command_with_sudo(command, ssh_manager, use_sudo=True)
            logger.debug(f"OS type detected: {output.strip()}")
            if exit_status != 0:
                raise Exception("Failed to detect OS type")
            if 'Linux' in output:
                return 'linux'.strip()
            return 'windows'.strip()
        except Exception as e:
            logger.error(f"OS detection failed: {str(e)}")
            raise Exception(f"{ExecutionError.OS_DETECTION_FAILED.value[1]}: {str(e)}")

    def check_directory_existence(self, ssh_manager: SSHManager) -> ExecutionResult:
        if self.sub_target or self.target_pattern:
            logger.error("Invalid configuration: sub_target or target_pattern provided for directory check")
            return ExecutionResult(success=False, error=ExecutionError.INVALID_CONFIGURATION.value[1])

        try:
            command = self.command_builder.build_directory_exsistence_command(self.main_target)
            command = f"export LC_ALL=C && echo {ssh_manager.password} | sudo -S {command}"
            logger.debug(f"Executing directory existence check with command: {command}")
            output, error, exit_status = ssh_manager.execute_command_with_sudo(command, ssh_manager, use_sudo=True)
            if output:
                return ExecutionResult(success=True, output=self.main_target)
            return ExecutionResult(success=False, output=self.main_target)
        except Exception as e:
            logger.exception(f"Directory existence check failed: {str(e)}")
            return ExecutionResult(success=False, error=f"{ExecutionError.SSH_EXECUTION_FAILED.value[1]}: {str(e)}")

    def check_file_existence(self, ssh_manager: SSHManager) -> ExecutionResult:
        if self.sub_target or self.target_pattern:
            logger.error("Invalid configuration: sub_target or target_pattern provided for file check")
            return ExecutionResult(success=False, error=ExecutionError.INVALID_CONFIGURATION.value[1])

        try:
            command = self.command_builder.build_file_existence_command(self.main_target)
            command = f"export LC_ALL=C && echo {ssh_manager.password} | sudo -S {command}"
            logger.debug(f"Executing file existence check with command: {command}")
            output, error, exit_status = ssh_manager.execute_command_with_sudo(command, ssh_manager, use_sudo=True)
            output = output.strip() if output else ""

            if "not exists" in output:
                return ExecutionResult(success=False, output=self.main_target)
            elif "exists" in output:
                return ExecutionResult(success=True, output=self.main_target)
            else:
                logger.error("Unexpected output from file existence check.")
                return ExecutionResult(success=False, error="Unexpected output from file existence check.")

        except Exception as e:
            logger.exception(f"File existence check failed: {str(e)}")
            return ExecutionResult(success=False, error=f"{ExecutionError.SSH_EXECUTION_FAILED.value[1]}: {str(e)}")

    def list_files_with_pattern(self, ssh_manager: SSHManager) -> ExecutionResult:
        if not self.target_pattern or self.sub_target:
            logger.error("Invalid configuration: target_pattern is required and sub_target should be None")
            return ExecutionResult(success=False, error=ExecutionError.INVALID_CONFIGURATION.value[1])

        try:
            command = self.command_builder.build_directory_listing_command(self.main_target)
            command = f"export LC_ALL=C && echo {ssh_manager.password} | sudo -S {command}"
            logger.debug(f"Executing file listing with command: {command}")
            output, error, exit_status = ssh_manager.execute_command_with_sudo(command, ssh_manager, use_sudo=True)
            if output:
                filtered_files = self._filter_files_with_pattern(output, self.target_pattern)
                if filtered_files:
                    logger.debug(f"Files matching pattern: {filtered_files}")
                    return ExecutionResult(success=True, output=json.dumps(filtered_files))
                return ExecutionResult(success=False, error="No files matched the pattern")
            return ExecutionResult(success=False, error="No output from command")

        except Exception as e:
            logger.exception(f"Listing files with pattern failed: {str(e)}")
            return ExecutionResult(success=False, error=f"{ExecutionError.SSH_EXECUTION_FAILED.value[1]}: {str(e)}")


    def _filter_files_with_pattern(self, file_list: str, pattern: str) -> list:
        try:
            regex = re.compile(pattern)
            return [file.strip() for file in file_list.split("\n") if file.strip() and regex.search(file.strip())]
        except re.error as e:
            logger.error(f"Invalid regex pattern: {str(e)}")
            raise ValueError(f"Invalid regex pattern: {str(e)}")

    def run_command(self, ssh_manager: SSHManager) -> ExecutionResult:
        if self.sub_target or self.target_pattern:
            logger.error("Invalid configuration: sub_target or target_pattern provided for command execution")  # Error log
            return ExecutionResult(success=False, error=ExecutionError.INVALID_CONFIGURATION.value[1])

        try:
            if self.os_type == "linux":
                command = f"export LC_ALL=C && echo {ssh_manager.password} | sudo -S {self.main_target}"
            logger.debug(f"Running command: {command}")  # Debug log for command execution
            output, error, exit_status = ssh_manager.execute_command_with_sudo(command, ssh_manager, use_sudo=True)
            output = output.strip() if output else ""
            error = error.strip() if error else ""

            error = re.sub(r"\[sudo\] password for .+?: ?", "", error)

            if output and error:
                combined_output = f"{output}\n{error}"
                return ExecutionResult(success=True, output=combined_output)
            elif output:
                return ExecutionResult(success=True, output=output)
            elif error:
                return ExecutionResult(success=True, output=error)
            else:
                logger.error("Command failed with no result")
                return ExecutionResult(success=False, error="Command failed with no result")

        except Exception as e:
            logger.exception(f"Command execution failed: {str(e)}")
            return ExecutionResult(success=False, error=f"{ExecutionError.SSH_EXECUTION_FAILED.value[1]}: {str(e)}")

    def check_process_existence(self, ssh_manager: SSHManager) -> ExecutionResult:
        if self.sub_target or self.target_pattern:
            logger.error("Invalid configuration: sub_target or target_pattern provided for process check")
            return ExecutionResult(success=False, error=ExecutionError.INVALID_CONFIGURATION.value[1])

        try:
            command = self.command_builder.build_process_check_command(self.main_target)
            logger.debug(f"Checking process existence with command: {command}")
            output, error, exit_status = ssh_manager.execute_command_with_sudo(command, ssh_manager, use_sudo=True)
            if output:
                return ExecutionResult(success=True, output=self.main_target)
            return ExecutionResult(success=False, output=self.main_target)
        except Exception as e:
            logger.exception(f"Process existence check failed: {str(e)}")
            return ExecutionResult(success=False, error=f"{ExecutionError.SSH_EXECUTION_FAILED.value[1]}: {str(e)}")

    def check_registry_key(self, ssh_manager: SSHManager) -> ExecutionResult:
        try:
            if not self.sub_target:
                command = self.command_builder.build_registry_key_existence_command(self.main_target)
            else:
                command = self.command_builder.build_registry_check_command(self.main_target, self.sub_target)

            logger.debug(f"Checking registry key with command: {command}")
            output, error, exit_status = ssh_manager.execute_command_with_sudo(command, ssh_manager, use_sudo=True)
            if output:
                return ExecutionResult(success=True, output=output.strip())
            return ExecutionResult(success=False, output=output.strip())
        except Exception as e:
            logger.exception(f"Registry key check failed: {str(e)}")
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
        content_rules: List[Dict],
        ssh_manager: SSHManager,
        command_builder: OSCommandBuilder,
        os_type: str,
        rule_negation: bool
    ):
        self.node_type = node_type
        self.content_rules = content_rules
        self.ssh_manager = ssh_manager
        self.command_builder = command_builder
        self.os_type = os_type
        self.rule_negation  = rule_negation

    def check(self, content: Union[str, List[str]]) -> ContentCheckResult:
        try:
            if self.node_type == 'c':
                return self.check_command_output(content)
            elif self.node_type == 'f':
                return self.check_file_content(content)
            elif self.node_type in ['d', 'p']:
                return ContentCheckResult(success=True)
            else:
                logger.error("Invalid node type: {}", self.node_type)
                return ContentCheckResult(success=False, error=ExecutionError.INVALID_NODE_TYPE.value[1])
        except Exception as e:
            logger.exception("Error in content check: {}", str(e))
            return ContentCheckResult(success=False, error=f"{ExecutionError.UNKNOWN_ERROR.value[1]}: {str(e)}")

    def check_command_output(self, content: str) -> ContentCheckResult:
        try:
            logger.debug("Checking command output")
            logger.debug("Content to check:\n{}", content)
            return self._check_lines(content.splitlines())
        except Exception as e:
            logger.exception("Error checking command output: {}", str(e))
            return ContentCheckResult(success=False, error=f"{ExecutionError.UNKNOWN_ERROR.value[1]}: {str(e)}")

    def check_file_content(self, content: Union[str, List[str]]) -> ContentCheckResult:
        try:
            if isinstance(content, str):
                content = self._parse_content(content)

            if isinstance(content, list):
                if not content:
                    logger.error("No files matched the pattern")
                    return ContentCheckResult(success=False, error="No files matched the pattern.")

                results = []
                for file_path in content:
                    logger.debug("Reading and checking file: {}", file_path)
                    result = self.read_and_check_file(file_path)
                    if not result.success:
                        logger.debug("Failed with file: {}. Error: {}", file_path, result.error)
                        results.append(False)
                    else:
                        results.append(result.success)

                final_result = any(results)
                return ContentCheckResult(success=final_result)

            else:
                logger.error("Invalid file rule")
                return ContentCheckResult(success=False, error=ExecutionError.INVALID_FILE_RULE.value[1])

        except Exception as e:
            logger.exception("Error checking file content: {}", str(e))
            return ContentCheckResult(success=False, error=f"{ExecutionError.UNKNOWN_ERROR.value[1]}: {str(e)}")

    def read_and_check_file(self, file_path: str) -> ContentCheckResult:
        try:
            logger.debug("Reading and checking file: {}", file_path)
            command = self.command_builder.build_read_file_command(file_path)
            
            output, error, exit_status = self.ssh_manager.execute_command_with_sudo(command, self.os_type, use_sudo=True)
            if exit_status != 0:
                logger.error("Failed to read file: {}. Error: {}", file_path, error)
                return ContentCheckResult(success=False, error=f"Failed to read file {file_path}: {error}")

            # If the file is empty
            if output.strip() == "":
                logger.debug("File is empty: {}", file_path)

                # If no content rules, we can return success immediately
                if not self.content_rules:
                    logger.debug("No content rules to check. Returning success.")
                    return ContentCheckResult(success=True)
                # If content rules exist, continue checking
                else:
                    logger.debug("Content rules exist. Proceeding to check rules.")

            # Continue to check file content if it’s not empty or rules exist
            logger.debug("File content:\n{}", output)
            return self._check_lines(output.splitlines())

        except Exception as e:
            logger.exception("Error reading and checking file: {}", str(e))
            return ContentCheckResult(success=False, error=f"{ExecutionError.UNKNOWN_ERROR.value[1]}: {str(e)}")

    def _check_lines(self, lines: List[str]) -> ContentCheckResult:
        match = False
    
        for line in lines:
            line_match = True
    
            for rule in self.content_rules:
                rule_match = self._does_line_match_rule(line, rule)
    
                if rule.get('negation', False):
                    rule_match = not rule_match
    
                if not rule_match:
                    line_match = False
                    break
    
            if line_match:
                match = True
                logger.debug("Line matched all rules: {}", line)
                break
    
        if self.rule_negation:
            match = not match
            logger.debug("ContentRuleChecker-level negation applied to final match result: {}", match)
    
        return ContentCheckResult(success=match)
    
    def _does_line_match_rule(self, line: str, rule: Dict) -> bool:
        content_operator = rule.get('content_operator')
        value = rule.get('value')
    
        if content_operator == 'r':  # Regex match
            match = bool(re.search(value, line))
            logger.debug("Checked line: {}, Regex pattern: {}, Match result: {}", line, value, match)
        elif content_operator == 'n':  # Numeric comparison
            match = self.numeric_compare(line, value, rule.get('compare_operator'), rule.get('compare_value'))
            logger.debug("Numeric compare result: {} for value: {}", match, value)
        elif content_operator is None:  # Substring match
            match = value in line
            logger.debug("Substring match result: {} for value: {}", match, value)
        else:
            logger.error("Invalid content operator: {}", content_operator)
            return False
    
        return match

    def numeric_compare(self, content: str, value: str, compare_operator: str, compare_value_str: str) -> bool:
        try:
            logger.debug("Performing numeric comparison on content: {}", content)
            match = re.search(value, content)
            if not match:
                logger.debug("No numeric match found for value: {}", value)
                return False

            number = int(match.group(1))
            compare_value = int(compare_value_str)
            logger.debug("Extracted number: {}, Compare value: {}", number, compare_value)

            if compare_operator == '>':
                return number > compare_value
            elif compare_operator == '>=':
                return number >= compare_value
            elif compare_operator == '<':
                return number < compare_value
            elif compare_operator == '<=':
                return number <= compare_value
            elif compare_operator == '==':
                return number == compare_value
            elif compare_operator == '!=':
                return number != compare_value
            else:
                logger.error("Invalid compare operator: {}", compare_operator)
                return False
        except Exception as e:
            logger.exception("Error in numeric comparison: {}", str(e))
            raise ValueError(f"{ExecutionError.INVALID_COMPARE_EXPRESSION.value[1]}: {str(e)}")

    def _parse_content(self, content: str) -> List[str]:
        try:
            content_list = json.loads(content)
            if isinstance(content_list, list):
                return content_list
            else:
                logger.debug("Parsed content is not a list: {}", content_list)
                return [content]
        except json.JSONDecodeError:
            logger.debug("Content is a single file path, not a JSON list: {}", content)
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
            logger.info(f"Connected to {self.ssh_manager.hostname}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to {self.ssh_manager.hostname}: {str(e)}")
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

            logger.info("##########################################################")
            logger.info(f"##### Executing check ID: {check_id} with condition: {condition} #####")
            logger.info("##########################################################")

            rule_results = self._execute_rules(check['rules'], os_type)
            if isinstance(rule_results, SemanticTreeExecutionResult):
                # If an error occurred during rule execution, return it immediately
                self.ssh_manager.close()
                return rule_results

            # Print all rule results for this check ID
            logger.debug(f"Rule results for check ID {check_id}: {rule_results}")

            # Determine the final check result based on the condition
            check_pass = self._evaluate_condition(condition, rule_results)
            if check_pass is None:
                self.ssh_manager.close()
                logger.error(f"Invalid condition specified at check ID {check_id}")
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

            logger.info(f"Check ID: {check_id} result: {results[check_id]['result']}")  # Log check result

        # Close the SSH connection after all checks
        self.ssh_manager.close()
        return SemanticTreeExecutionResult(success=True, results=results)

    def _execute_rules(self, rules: List[Dict], os_type: str) -> Union[List[bool], SemanticTreeExecutionResult]:
        rule_results = []

        for rule in rules:
            exec_node = rule['execution_node']
            rule_negation = rule.get('negation', False)  # Fetch negation flag once

            logger.info(f"Executing rule with execution node: {exec_node}")  # Log rule execution

            # Execute node and check for success
            execution_result = self._execute_node(exec_node, os_type)

            if not execution_result.success:
                if execution_result.error:  # If an error exists, print it
                    logger.error(f"Execution failed for rule {exec_node}: {execution_result.error}")
                
                # Always append negation if execution fails, regardless of the error
                rule_results.append(not execution_result.success if rule_negation else execution_result.success)
                continue

            if exec_node['type'] == 'd':
                # Process directory node
                file_rules = rule.get('file_rules', [])
                if file_rules:
                    # Pass negation into _process_file_rules
                    file_rule_results = self._process_file_rules(file_rules, execution_result.output, os_type, rule_negation)
                    if isinstance(file_rule_results, SemanticTreeExecutionResult):
                        return file_rule_results

                    # Apply negation if necessary and extend rule results
                    rule_results.extend(file_rule_results)
                else:
                    # Handle directory existence check
                    rule_results.append(execution_result.success)
            else:
                # Pass negation into _check_content_rules
                content_check_result = self._check_content_rules(rule, execution_result.output, os_type, rule_negation)
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
        logger.debug(f"Execution result: {execution_result.to_dict()}")
        return execution_result

    def _process_file_rules(self, file_rules: List[Dict], directory_output: str, os_type: str, negation: bool) -> Union[List[bool], SemanticTreeExecutionResult]:
        file_rule_results = []
        for file_rule in file_rules:
            exec_node = file_rule['execution_node']

            execution_result = self._execute_node(exec_node, os_type)
            if not execution_result.success:
                logger.error(f"Execution failed for file rule {exec_node}: {execution_result.error}")
                file_rule_results.append(False)
                continue

            # Pass negation into _check_content_rules
            content_check_result = self._check_content_rules(file_rule, execution_result.output, os_type, negation)
            if isinstance(content_check_result, SemanticTreeExecutionResult):
                return content_check_result
            file_rule_results.append(content_check_result)

        return file_rule_results

    def _check_content_rules(self, rule: Dict, exec_output: str, os_type: str, rule_negation: bool) -> Union[bool, SemanticTreeExecutionResult]:
        try:
            # Initialize ContentRuleChecker with negation flag
            checker = ContentRuleChecker(
                node_type=rule['execution_node']['type'],
                content_rules=rule.get('content_rules', []),
                ssh_manager=self.ssh_manager,
                command_builder=OSCommandBuilder(os_type),
                os_type=os_type,
                rule_negation=rule_negation
            )

            content_result = checker.check(exec_output)
            logger.debug(f"Content result: {content_result.to_dict()}")

            if not content_result.success:
                logger.error(f"Content check failed for rule {rule['execution_node']}: {content_result.error}")
                return False
            else:
                return True

        except Exception as e:
            logger.exception(f"Error during content check: {str(e)}")
            return SemanticTreeExecutionResult(success=False, error=f"{ExecutionError.UNKNOWN_ERROR.value[1]}: {str(e)}")

    def _evaluate_condition(self, condition: str, rule_results: List[bool]) -> Optional[bool]:
        if condition == 'all':
            return all(rule_results)
        elif condition == 'any':
            return any(rule_results)
        elif condition == 'none':
            return not any(rule_results)
        else:
            logger.error(f"Invalid condition: {condition}")
            return None