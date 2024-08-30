"""
===============================================================================
    Program Name: API V1
    Description:  This module defines version 1 of the API endpoints for handling 
                  script validations, rule conversions, audit executions, and 
                  compliance report generation. It includes multiple POST and 
                  GET endpoints to interact with the audit system, leveraging 
                  OpenAI models for natural language processing tasks.
                  
                  **Implemented Endpoints:**
                  - `/audit/execute`: Executes an audit based on provided scripts and SSH information.
                  - `/audit/result`: Retrieves the audit results.
                  - `/rules/convert`: Converts natural language descriptions into compliance audit rules.
                  - `/qa/ask`: Provides answers to questions using an AI-based model.
                  - `/generate-audit-report`: Generates an audit report based on JSON audit results.

                  **Unimplemented Endpoints:**
                  - `/scripts/validate_description`: This endpoint is planned to validate the description of scripts but is not yet implemented.
                  - `/scripts/validate_rules`: This endpoint is planned to validate rules within scripts but is not yet implemented.
                  - `/audit/status/{task_id}`: This endpoint is intended to query the status of an ongoing audit but is currently not implemented.

    Author:       Dickson, Jerry Hung
    Email:        chiehlee.hung@gmail.com
    Created Date: 2024-08-12
    Last Updated: 2024-08-29
    Version:      0.1.1
    
    License:      Commercial License
                  This software is licensed under a commercial license. 
                  Redistribution and use in source and binary forms, with or 
                  without modification, are not permitted without explicit 
                  written permission from the author.
                  
                  You may use this software solely for internal business 
                  purposes within your organization. You may not distribute, 
                  sublicense, or resell this software or its modifications in 
                  any form.

                  Unauthorized copying of this software, via any medium, is 
                  strictly prohibited.

    Usage:        The module can be imported and the `router` object used to include 
                  the API endpoints in a FastAPI application. 
                  Example: from api_v1 import router as v1_router

    Requirements: Python 3.10.12, Paramiko, FastAPI, Pydantic, OpenAI SDK
    
    Notes:        This is a demo backend application, not intended for production use. 
                  Some parts of the code are placeholders and need further optimization:
                  
                  1. **Error Handling**: Improve error handling throughout the API to handle different exceptions more gracefully.
                  2. **Security Enhancements**: Sensitive information such as SSH credentials should not be hardcoded or stored in logs. Implement secure methods for handling credentials.
                  3. **Concurrency Management**: For better performance and scalability, implement proper concurrency handling using asynchronous functions and task management.
                  4. **Validation Logic**: The endpoints for validating script descriptions and rules (`/scripts/validate_description` and `/scripts/validate_rules`) need to be fully implemented with comprehensive validation logic.
                  5. **Status Tracking**: Implement the `/audit/status/{task_id}` endpoint to provide real-time status updates on ongoing audit tasks.
                  6. **Logging and Monitoring**: Add structured logging and monitoring to track API usage, errors, and performance metrics.
                  7. **API Security**: Ensure that all endpoints are properly secured, requiring authentication and authorization as needed.
                  8. **Documentation and Tests**: Provide thorough documentation and unit tests for each endpoint to ensure reliability and ease of maintenance.
===============================================================================
"""
from openai import OpenAI
import ipaddress
import json
import os
import sys
import re
import paramiko
from fastapi import APIRouter, Request, Path, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from semantic_tree_builder import SemanticTreeBuilder, SemanticTreeError
from script_validator import ScriptValidator, ValidationError
from script_processor import ScriptProcessorError
from semantic_tree_executor import ExecutionError, SSHManager, OSCommandBuilder, ExecutionResult, ExecutionNodeExecutor, ContentCheckResult, ContentRuleChecker, SemanticTreeExecutionResult, SemanticTreeExecutor
import asyncio

router = APIRouter()
current_id = 0

class Compliance(BaseModel):
    name: str
    control_list: List[str]

class Script(BaseModel):
    script_name: str
    description: str
    rationale: str
    mitigation: str
    detection_method: str
    os_version: str
    compliances: List[Compliance]
    condition: str
    rules: List[str]

class SSHInfo(BaseModel):
    target_system_name: str
    target_system_type: str
    port: int
    username: str
    ip: str
    password: str

class AuditRequest(BaseModel):
    scripts: List[Script]
    ssh_info: SSHInfo

class QARequest(BaseModel):
    question: str

class QAResponse(BaseModel):
    answer: str

class ConvertRequest(BaseModel):
    description: str

class ConvertResponse(BaseModel):
    rule: str

class AuditReportRequest(BaseModel):
    audit_results: dict

class AuditReportResponse(BaseModel):
    report: str

    
def generate_unique_id():
    global current_id
    current_id += 1
    return current_id

def get_current_id():
    global current_id
    return current_id

def debug_print(message: str):
    """
    Print a debug message in a structured format.
    """
    print(f"[DEBUG] {message}")

temp_storage: Dict[int, Dict] = {}

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

client = OpenAI(api_key=api_key)

BACKGROUND_PROMPT = """
你是一名資安合規稽核員。你的角色是確保組織遵守安全標準和最佳實踐。你負責評估安全政策、程序和控制措施，以識別任何差距並提出改進建議。
請使用繁體中文回答問題。
"""

SYSTEM_PROMPT = r"""
You are a machine designed to convert natural language descriptions into a custom compliance audit rule language. The following rules and examples provide you with the necessary background to perform this conversion accurately. Please follow the provided guidelines strictly when interpreting and converting descriptions.
Please generate only the compliance audit rule without providing any additional explanation or description. Return the rule alone!!!!

#### Rules Overview

Rules are used to check the existence of files, directories, registry keys and values, running processes, and recursively test for the existence of files inside directories. They can also be used for content checking, such as checking file contents, command output, and registry value data.

Rules start with a location and a type of location as the target of the test, followed by the actual test specification. These tests fall into two categories: existence checks and content checks. The location type is defined in the Rule Types table below, and the location itself could be a file name, directory, process name, command, or registry key.

There are five main types of rules, as described below:

#### Rule Types

| Type      | Character |
|-----------|-----------|
| File      | f         |
| Directory | d         |
| Process   | p         |
| Command   | c         |
| Registry  | r         |

#### Content Comparison Operators

| Operation                    | Operator | Example                                      |
|------------------------------|----------|----------------------------------------------|
| Literal comparison, exact match | (omitted) | `f:/file -> CONTENT`                         |
| Regex match                  | r:       | `f:/file -> r:REGEX`                         |
| Numeric comparison (integers)| n:       | `f:/file -> n:REGEX_WITH_CAPTURE_GROUP compare <= VALUE` |

#### Numeric Comparison Operators

| Arithmetic Relational Operator | Operator | Example                                           |
|--------------------------------|----------|---------------------------------------------------|
| Less than                      | <        | `n:SomeProperty (\d) compare < 42`                |
| Less than or equal to          | <=       | `n:SomeProperty (\d) compare <= 42`               |
| Equal to                       | ==       | `n:SomeProperty (\d) compare == 42`               |
| Not equal to                   | !=       | `n:SomeProperty (\d) compare != 42`               |
| Greater than or equal to       | >=       | `n:SomeProperty (\d) compare >= 42`               |
| Greater than                   | >        | `n:SomeProperty (\d) compare > 42`                |

#### Negation

You can place `not` at the beginning of a rule to negate it. For example:

```
not f:/some_file -> some_text
```

The rule above fails if `some_text` is found within the contents of `some_file`.

#### Existence Checking Rules

Existence checks are created by setting rules without a content operator. The general form is as follows:

```
RULE_TYPE:target
```

**Examples:**

- `f:/etc/sshd_config` checks the existence of the `/etc/sshd_config` file.
- `d:/etc` checks the existence of the `/etc` directory.
- `not p:sshd` tests for the presence of processes called `sshd` and fails if one is found.
- `r:HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Lsa` checks for the existence of the `HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Lsa` key.
- `r:HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Lsa -> LimitBlankPasswordUse` checks for the existence of the `LimitBlankPasswordUse` value in the key.

#### Content Checking Rules

The general form of a rule testing for content is as follows:

```
RULE_TYPE:target -> CONTENT_OPERATOR:value
```

**Examples:**

- `f:/etc/ssh_config -> !r:PermitRootLogin` checks if `PermitRootLogin` is not present in the file.
- `c:systemctl is-enabled cups -> r:^enabled` checks that the command output contains a line starting with `enabled`.
- `f:$sshd_file -> n:^\s*MaxAuthTries\s*\t*(\d+) compare <= 4` checks that `MaxAuthTries` is less than or equal to 4.
- `r:HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Lsa -> LimitBlankPasswordUse -> 1` checks that the `LimitBlankPasswordUse` value is `1`.

#### Notes and Warnings

- The context of a content check is limited to a **line**.
- It is **mandatory** to respect the spaces around the `>` and `compare` separators.
- If the **target** of a rule that checks for contents does not exist, the result will be `Not applicable` as it could not be checked.

**Negating Content Operators:**

Be cautious when negating content operators, as it makes them evaluate as **Passed** for anything that does not match the specified check. For example, the rule `f:/etc/ssh_config -> !r:PermitRootLogin` is evaluated as **Passed** if it finds any line that does not contain `PermitRootLogin`.

**Chaining Content Operators:**

Content check operators can be chained using the `&&` (AND) operator as follows:

```
f:/etc/ssh_config -> !r:^# && r:Protocol && r:2 && r:3 && r:qwer && r:asdf && r:zxcv
```

This rule reads as **Pass** if there's a line whose first character is not `#` and contains `Protocol` and `2`.

#### Rule Syntax Examples

**File Rules:**

- Check that a file exists: `f:/path/to/file`
- Check that a file does not exist: `not f:/path/to/file`
- Check file contents (literal match): `f:/path/to/file -> content`
- Check file contents against regex: `f:/path/to/file -> r:REGEX`
- Check a numeric value: `f:/path/to/file -> n:*REGEX(\d+)* compare <= Number`

**Directory Rules:**

- Check if a directory exists: `d:/path/to/directory`
- Check if a directory contains a specific file: `d:/path/to/directory -> file`
- Check if a directory contains files that match a regex: `d:/path/to/directory -> r:^files`
- Check files matching `file_name` for content: `d:/path/to/directory -> file_name -> content`

**Process Rules:**

- Check if a process is running: `p:process_name`
- Check if a process is **not** running: `not p:process_name`

**Command Rules:**

- Check the output of a command: `c:command -> output`
- Check the output of a command using regex: `c:command -> r:REGEX`
- Check a numeric value: `c:command -> n:REGEX_WITH_A_CAPTURE_GROUP compare >= number`

**Registry Rules (Windows Only):**

- Check if a registry exists: `r:path/to/registry`
- Check if a registry key exists: `r:path/to/registry -> key`
- Check registry key contents: `r:path/to/registry -> key -> content`

#### Composite Rules

Composite rules allow combining multiple checks in a single statement. For example:

- Check if there is a line that does not begin with `#` and contains `Port 22`: `f:/etc/ssh/sshd_config -> !r:^# && r:Port\.+22`
- Check if there is no line that does not begin with `#` and contains `Port 22`: `not f:/etc/ssh/sshd_config -> !r:^# && r:Port\.+22`

#### Additional Examples

- Check for file contents, whole line match: `f:/proc/sys/net/ipv4/ip_forward -> 1`
- Check if a file exists: `f:/proc/sys/net/ipv4/ip_forward`
- Check if a process is running: `p:avahi-daemon`
- Check value of registry: `r:HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\Netlogon\Parameters -> MaximumPasswordAge -> 0`
- Check if a directory contains specific files: `d:/home -> ^.mysql_history$`
- Check if a directory exists: `d:/etc/mysql`
- Check the running configuration of `sshd` for the maximum authentication tries allowed: `c:sshd -T -> !r:^\s*maxauthtries\s+4\s*$`
- Check if root is the only account with UID 0: `f:/etc/passwd -> !r:^# && !r:^root: && r:^\w+:\w+:0:`

"""

USER_PROMPT_TEMPLATE = """
Convert the following natural language description into a compliance audit rule, adhering to the rules and syntax provided.

Description: {user_input}
"""

AUDIT_SYSTEM_PROMPT = r"""
You are a cybersecurity audit report generator. You will receive a JSON file containing detailed audit results for a specific script. Your task is to analyze the JSON content, understand the audit findings, and refer to the rules applied during the audit process. Based on this analysis, you must generate a concise and precise audit report.

### Structure of the Audit Results

The audit results JSON structure includes several key sections:

1. **scripts**: This section provides information about the script that was audited, including:
   - `script_name`: The name of the script.
   - `description`: A brief description of the script.
   - `rationale`, `mitigation`, `detection_method`, `os_version`: Additional details that may provide context about the script and its purpose.
   - `compliances`: Lists compliance requirements or standards that the script is expected to meet.
   - `condition`: Indicates whether all rules must pass (`all`) or any rule can pass (`any`) for the overall result to be considered a pass.
   - `rules`: A list of specific checks or tests that were conducted on the script. Each rule is a string that defines the target and the type of check (e.g., file existence, content match, etc.).

2. **ssh_info**: Contains information about the target system where the script was executed, including:
   - `target_system_name`, `target_system_type`, `port`, `username`, `ip`, `password`: Details about the SSH connection used for auditing.

3. **execution_results**: This section contains the results of the audit:
   - `result`: Indicates the overall result of the audit (`pass` or `fail`).
   - `condition`: Reiterates the condition (e.g., `all`, `any`) under which the audit was evaluated.
   - `rule_results`: A list of boolean values corresponding to the `rules` in the `scripts` section:
     - `true` indicates that the rule passed successfully.
     - `false` indicates that the rule failed.

### How to Generate the Report

Based on the JSON structure, your task is to:

1. Provide an overview of the audit findings, summarizing the key outcomes.
2. Clearly explain any issues found, specifically highlighting the rules that were not met. These can be identified by the `false` values in the `rule_results` list, which correspond to the rules listed in the `rules` array.
3. Briefly describe the implications of the audit results on system security.
4. Offer recommendations for remediation or further action based on the audit results.

Your response should be structured, clear, and avoid unnecessary details. The goal is to provide a straightforward report that is easy for both technical and non-technical stakeholders to understand.

Below are the rule formats for your reference:
#### Rules Overview

Rules are used to check the existence of files, directories, registry keys and values, running processes, and recursively test for the existence of files inside directories. They can also be used for content checking, such as checking file contents, command output, and registry value data.

Rules start with a location and a type of location as the target of the test, followed by the actual test specification. These tests fall into two categories: existence checks and content checks. The location type is defined in the Rule Types table below, and the location itself could be a file name, directory, process name, command, or registry key.

There are five main types of rules, as described below:

#### Rule Types

| Type      | Character |
|-----------|-----------|
| File      | f         |
| Directory | d         |
| Process   | p         |
| Command   | c         |
| Registry  | r         |

#### Content Comparison Operators

| Operation                    | Operator | Example                                      |
|------------------------------|----------|----------------------------------------------|
| Literal comparison, exact match | (omitted) | `f:/file -> CONTENT`                         |
| Regex match                  | r:       | `f:/file -> r:REGEX`                         |
| Numeric comparison (integers)| n:       | `f:/file -> n:REGEX_WITH_CAPTURE_GROUP compare <= VALUE` |

#### Numeric Comparison Operators

| Arithmetic Relational Operator | Operator | Example                                           |
|--------------------------------|----------|---------------------------------------------------|
| Less than                      | <        | `n:SomeProperty (\d) compare < 42`                |
| Less than or equal to          | <=       | `n:SomeProperty (\d) compare <= 42`               |
| Equal to                       | ==       | `n:SomeProperty (\d) compare == 42`               |
| Not equal to                   | !=       | `n:SomeProperty (\d) compare != 42`               |
| Greater than or equal to       | >=       | `n:SomeProperty (\d) compare >= 42`               |
| Greater than                   | >        | `n:SomeProperty (\d) compare > 42`                |

#### Negation

You can place `not` at the beginning of a rule to negate it. For example:

```
not f:/some_file -> some_text
```

The rule above fails if `some_text` is found within the contents of `some_file`.

#### Existence Checking Rules

Existence checks are created by setting rules without a content operator. The general form is as follows:

```
RULE_TYPE:target
```

**Examples:**

- `f:/etc/sshd_config` checks the existence of the `/etc/sshd_config` file.
- `d:/etc` checks the existence of the `/etc` directory.
- `not p:sshd` tests for the presence of processes called `sshd` and fails if one is found.
- `r:HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Lsa` checks for the existence of the `HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Lsa` key.
- `r:HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Lsa -> LimitBlankPasswordUse` checks for the existence of the `LimitBlankPasswordUse` value in the key.

#### Content Checking Rules

The general form of a rule testing for content is as follows:

```
RULE_TYPE:target -> CONTENT_OPERATOR:value
```

**Examples:**

- `f:/etc/ssh_config -> !r:PermitRootLogin` checks if `PermitRootLogin` is not present in the file.
- `c:systemctl is-enabled cups -> r:^enabled` checks that the command output contains a line starting with `enabled`.
- `f:$sshd_file -> n:^\s*MaxAuthTries\s*\t*(\d+) compare <= 4` checks that `MaxAuthTries` is less than or equal to 4.
- `r:HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Lsa -> LimitBlankPasswordUse -> 1` checks that the `LimitBlankPasswordUse` value is `1`.

#### Notes and Warnings

- The context of a content check is limited to a **line**.
- It is **mandatory** to respect the spaces around the `>` and `compare` separators.
- If the **target** of a rule that checks for contents does not exist, the result will be `Not applicable` as it could not be checked.

**Negating Content Operators:**

Be cautious when negating content operators, as it makes them evaluate as **Passed** for anything that does not match the specified check. For example, the rule `f:/etc/ssh_config -> !r:PermitRootLogin` is evaluated as **Passed** if it finds any line that does not contain `PermitRootLogin`.

**Chaining Content Operators:**

Content check operators can be chained using the `&&` (AND) operator as follows:

```
f:/etc/ssh_config -> !r:^# && r:Protocol && r:2 && r:3 && r:qwer && r:asdf && r:zxcv
```

This rule reads as **Pass** if there's a line whose first character is not `#` and contains `Protocol` and `2`.

#### Rule Syntax Examples

**File Rules:**

- Check that a file exists: `f:/path/to/file`
- Check that a file does not exist: `not f:/path/to/file`
- Check file contents (literal match): `f:/path/to/file -> content`
- Check file contents against regex: `f:/path/to/file -> r:REGEX`
- Check a numeric value: `f:/path/to/file -> n:*REGEX(\d+)* compare <= Number`

**Directory Rules:**

- Check if a directory exists: `d:/path/to/directory`
- Check if a directory contains a specific file: `d:/path/to/directory -> file`
- Check if a directory contains files that match a regex: `d:/path/to/directory -> r:^files`
- Check files matching `file_name` for content: `d:/path/to/directory -> file_name -> content`

**Process Rules:**

- Check if a process is running: `p:process_name`
- Check if a process is **not** running: `not p:process_name`

**Command Rules:**

- Check the output of a command: `c:command -> output`
- Check the output of a command using regex: `c:command -> r:REGEX`
- Check a numeric value: `c:command -> n:REGEX_WITH_A_CAPTURE_GROUP compare >= number`

**Registry Rules (Windows Only):**

- Check if a registry exists: `r:path/to/registry`
- Check if a registry key exists: `r:path/to/registry -> key`
- Check registry key contents: `r:path/to/registry -> key -> content`

#### Composite Rules

Composite rules allow combining multiple checks in a single statement. For example:

- Check if there is a line that does not begin with `#` and contains `Port 22`: `f:/etc/ssh/sshd_config -> !r:^# && r:Port\.+22`
- Check if there is no line that does not begin with `#` and contains `Port 22`: `not f:/etc/ssh/sshd_config -> !r:^# && r:Port\.+22`

#### Additional Examples

- Check for file contents, whole line match: `f:/proc/sys/net/ipv4/ip_forward -> 1`
- Check if a file exists: `f:/proc/sys/net/ipv4/ip_forward`
- Check if a process is running: `p:avahi-daemon`
- Check value of registry: `r:HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\Netlogon\Parameters -> MaximumPasswordAge -> 0`
- Check if a directory contains specific files: `d:/home -> ^.mysql_history$`
- Check if a directory exists: `d:/etc/mysql`
- Check the running configuration of `sshd` for the maximum authentication tries allowed: `c:sshd -T -> !r:^\s*maxauthtries\s+4\s*$`
- Check if root is the only account with UID 0: `f:/etc/passwd -> !r:^# && !r:^root: && r:^\w+:\w+:0:`

"""

# # Validate Script Description
# @router.post('/scripts/validate_description')
# async def validate_description(request: Request):
#     return_obj = {}
#     try:
#         body = await request.body()
#         data = json.loads(body)
#         return_obj['success'] = False

#         script_name = data.get('script_name')
#         if script_name is not None and len(str(script_name).strip()) > 0:
#             pass
#         else:
#             return_obj['error'] = 'script_name cannot be empty'
#             return return_obj

#         description = data.get('description')
#         if description is not None and len(str(description).strip()) > 0:
#             pass
#         else:
#             return_obj['error'] = 'description cannot be empty'
#             return return_obj

#         rationale = data.get('rationale')
#         if rationale is not None and len(str(rationale).strip()) > 0:
#             pass
#         else:
#             return_obj['error'] = 'rationale cannot be empty'
#             return return_obj

#         mitigation = data.get('mitigation')
#         if mitigation is not None and len(str(mitigation).strip()) > 0:
#             pass
#         else:
#             return_obj['error'] = 'mitigation cannot be empty'
#             return return_obj

#         detection_method = data.get('detection_method')
#         if detection_method is not None and detection_method in ['auto', 'semi-auto', 'manual']:
#             pass
#         else:
#             return_obj['error'] = "detection_method must be one of 'auto', 'semi-auto', or 'manual'"
#             return return_obj

#         os_version = data.get('os_version')
#         if os_version is not None and os_version in ['ubuntu 22.04']:
#             pass
#         else:
#             return_obj['error'] = "os_version must be 'ubuntu 22.04'"
#             return return_obj

#         compliance_list = data.get('compliances')
#         if compliance_list is not None and len(compliance_list) > 0:
#             pass
#         else:
#             return_obj['error'] = 'compliances must contain at least one compliance'
#             return return_obj

#         for compliance_obj in compliance_list:
#             compliance_name = compliance_obj.get('name')
#             if compliance_name is not None and compliance_name in ['NIST 800-53r5']:
#                 pass
#             else:
#                 return_obj['error'] = "compliance name must be a recognized standard like 'NIST 800-53r5'"
#                 return return_obj
#             control_list = compliance_obj.get('control_list')
#             if control_list is not None and len(control_list) > 0:
#                 pass
#             else:
#                 return_obj['error'] = "control_list cannot be empty for any compliance"
#                 return return_obj
#         # 通過驗證
#         return_obj['success'] = True
#         return return_obj
#     except Exception as e:
#         print('★★★★★★ Validate Script Description fail!!! ' + str(e))
#         return_obj['success'] = False
#         return_obj['error'] = 'System problem,please contact administrator'
#         return return_obj


# # Validate Script Rules
# @router.post('/scripts/validate_rules')
# async def validate_rules(request: Request):
#     return_obj = {}
#     try:
#         # 檢核傳入參數
#         body = await request.body()
#         data = json.loads(body)
#         return_obj['success'] = False

#         condition = data.get('condition')
#         if condition is not None and len(str(condition).strip()) > 0:
#             if condition in ['none', 'any', 'all']:
#                 pass
#             else:
#                 return_obj['error'] = "condition must be one of 'none', 'any', or 'all'"
#                 return return_obj
#         else:
#             return_obj['error'] = 'condition cannot be empty'
#             return return_obj

#         rule_list = data.get('rule_list')
#         if rule_list is not None and len(rule_list) > 0:
#             pass
#         else:
#             return_obj['error'] = 'rule_list must contain at least one rule'
#             return return_obj

#         for rule_str in rule_list:
#             # TODO 呼叫核心功能驗證rule_str syntax, 結果請回傳到chk_syntax_result, 範例chk_syntax_result = some_api(rule_str)
#             chk_syntax_result = False
#             if not chk_syntax_result:
#                 return_obj['error'] = 'One or more rules in rule_list have invalid syntax'
#                 return return_obj

#         # 通過驗證
#         return_obj['success'] = True
#         return return_obj
#     except Exception as e:
#         print('★★★★★★ Validate Script Rules fail!!! ' + str(e))
#         return_obj['success'] = False
#         return_obj['error'] = 'System problem,please contact administrator'
#         return return_obj

@router.post('/audit/execute')
async def execute_audit(audit_request: AuditRequest):
    return_obj = {}
    try:
        data = audit_request.dict()
        return_obj['success'] = False

        task_id_val = generate_unique_id()

        request_json_file = f"{task_id_val}_request.json"
        with open(request_json_file, 'w') as f:
            json.dump(data, f, indent=4)

        ssh_info = data.get('ssh_info')
        if ssh_info is not None:
            pass
        else:
            return_obj['error'] = 'ssh_info cannot be empty'
            return return_obj

        scripts = data.get('scripts', [])
        if not scripts:
            return_obj['error'] = 'scripts cannot be empty'
            return return_obj

        script_info = scripts[0]
        condition = script_info.get('condition')
        rules = script_info.get('rules')

        if condition is None or rules is None:
            return_obj['error'] = 'condition and rules cannot be empty'
            return return_obj

        check = {
            "id": task_id_val,
            "condition": condition,
            "rules": rules
        }

        print("Generated Dict:", check)

        try:
            tree_builder = SemanticTreeBuilder()

            loop = asyncio.get_event_loop()
            tree = await loop.run_in_executor(None, tree_builder.build_tree, check)

            if tree is None:
                errors = tree_builder.get_errors()
                return {
                    "status": "error",
                    "error_code": ScriptProcessorError.TREE_BUILDING_FAILED.value[0],
                    "error_message": ScriptProcessorError.TREE_BUILDING_FAILED.value[1],
                    "details": errors
                }

            tree_json = json.loads(tree_builder.tree_to_json(tree))
            results = {
                "os_type": "linux",
                "checks": [tree_json]
            }

            tree_json_file = f"{task_id_val}_tree.json"
            with open(tree_json_file, 'w') as f:
                f.write(json.dumps(results, indent=4))

            executor = SemanticTreeExecutor(hostname='192.168.70.150', username='jerryhung', password='systemadmin!23', port=22)
            debug_print(f"Initialized SemanticTreeExecutor with hostname: {executor.ssh_manager.hostname}")

            try:
                semantic_tree = results
                debug_print("Semantic tree data loaded successfully.")
            except Exception as e:
                debug_print(f"Failed to load semantic tree data: {str(e)}")
                sys.exit(1)

            debug_print("Executing the semantic tree...")
            execution_results = executor.execute_tree(semantic_tree)
            if execution_results.success:
                debug_print("Semantic tree execution completed successfully.")
                debug_print(f"Execution results: {execution_results.results}")
            else:
                debug_print(f"Semantic tree execution failed with error: {execution_results.error}")

            result_data = data.copy()
            result_data['execution_results'] = execution_results.results

            result_json_file = f"{task_id_val}_result.json"
            with open(result_json_file, 'w') as f:
                json.dump(result_data, f, indent=4)

            return_obj['task_id'] = task_id_val
            return_obj['success'] = True
            return_obj['execution_results'] = execution_results.results if execution_results.success else execution_results.error
            return return_obj

        except asyncio.TimeoutError:
            return {
                "status": "error",
                "error_code": ScriptProcessorError.TREE_BUILDING_TIMEOUT.value[0],
                "error_message": "Tree building operation timed out.",
                "details": "The operation took longer than 8 seconds."
            }

        except Exception as e:
            return {
                "status": "error",
                "error_code": ScriptProcessorError.UNKNOWN_ERROR.value[0],
                "error_message": ScriptProcessorError.UNKNOWN_ERROR.value[1],
                "details": str(e)
            }

    except Exception as e:
        print('★★★★★★ Execute Audit fail!!! ' + str(e))
        return_obj['success'] = False
        return_obj['error'] = 'System problem, please contact administrator'
        return return_obj

# # Query Audit Status
# @router.get('/audit/status/{task_id}')
# async def query_audit_status(_: Request, task_id=Path(..., description='')):
#     return_obj = {}
#     try:
#         # 檢核傳入參數
#         return_obj['success'] = False

#         if task_id is not None and isinstance(task_id, str):
#             try:
#                 task_id = int(task_id)
#             except Exception:
#                 return_obj['error'] = 'task_id is invalid or missing'
#                 return return_obj
#         else:
#             return_obj['error'] = 'task_id is invalid or missing'
#             return return_obj

#         # 通過驗證
#         # TODO 呼叫核心功能Query Audit Status,再修改以下程式
#         if True:
#             audit_status = {"task_id": "12345", "status": "executing", "progress": 50}
#             return audit_status
#         else:
#             return_obj['error'] = 'No audit found for the provided task_id'
#             return return_obj
#     except Exception as e:
#         print('★★★★★★ Query Audit Status fail!!! ' + str(e))
#         return_obj['success'] = False
#         return_obj['error'] = 'System problem,please contact administrator'
#         return return_obj


# Query Audit Results
@router.get('/audit/result')
async def query_audit_results():
    try:
        current_id = get_current_id()

        result_json_file = f"{current_id}_result.json"
        if not os.path.exists(result_json_file):
            return {
                "status": "error",
                "error_message": f"Result file for task_id {current_id} not found."
            }

        with open(result_json_file, 'r') as f:
            audit_results = json.load(f)

        return audit_results

    except Exception as e:
        print('★★★★★★ Query Audit Results fail!!! ' + str(e))
        return {
            "status": "error",
            "error_message": "System problem, please contact administrator",
            "details": str(e)
        }

# Convert Natural Language to Rule
@router.post('/rules/convert', response_model=ConvertResponse)
async def convert_to_rule(request: ConvertRequest):
    try:
        description = request.description

        if not description.strip():
            raise HTTPException(status_code=400, detail="Description cannot be empty")

        # Construct the user prompt using the provided description
        user_prompt = USER_PROMPT_TEMPLATE.format(user_input=description)

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ]
            )

            # Retrieve the content returned by the OpenAI API
            rule_content = response.choices[0].message.content.strip()

            # Use regular expression to filter lines that start with not, f:, d:, p:, c:, or r:
            rules = "\n".join(re.findall(r'^(?:not|f:|d:|p:|c:|r:).*$',
                                         rule_content, re.MULTILINE))

            if not rules:
                rules = "No valid rules found."

            return ConvertResponse(rule=rules)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to convert description to rule: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System problem, please contact administrator: {str(e)}")
    
# Q&A Answering
@router.post('/qa/ask', response_model=QAResponse)
async def qa_ask(request: QARequest):
    try:
        question = request.question

        if not question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        # Construct a request for the GPT-4 model
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": BACKGROUND_PROMPT},
                    {"role": "user", "content": question},
                ]
            )

            # Correctly access the content from the response object
            answer = response.choices[0].message.content.strip()
            return QAResponse(answer=answer)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve an answer from OpenAI API: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System problem, please contact administrator: {str(e)}")

@router.post('/generate-audit-report', response_model=AuditReportResponse)
async def generate_audit_report(request: AuditReportRequest):
    try:
        # Directly use audit_results to construct the user input content
        audit_data = request.audit_results
        user_input = f"Audit Results:\n{audit_data}"

        # Call OpenAI API to generate the audit report
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": AUDIT_SYSTEM_PROMPT},
                    {"role": "user", "content": user_input},
                ]
            )

            answer = response.choices[0].message.content.strip()
            return AuditReportResponse(report=answer)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate audit report from OpenAI API: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System problem, please contact administrator: {str(e)}")
