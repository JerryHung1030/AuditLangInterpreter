# AuditLang Interpreter Interface

## Overview

**AuditLang Interpreter Interface** is a robust SSH-based auditing tool designed to automate system-level auditing tasks, including log analysis and configuration management. Users can define audit logic using a straightforward language within `.yml` files, enabling easy creation and management of audit scripts. The interface seamlessly integrates with various auditing tools, offering a unified and platform-independent solution for comprehensive system audits.

In future releases, the interface will be encapsulated into Python packages, enhancing modularity and simplifying integration with other Python-based systems and tools.

## Features

- **SSH-Based Auditing**: Perform audits on remote systems via secure SSH connections.
- **Simple Audit Definitions**: Define audit logic using an intuitive language within `.yml` files.
- **Batch Processing**: Efficiently handle multiple audit rules by batching them in YAML files.
- **Extensible Interface**: Easily integrate with a variety of auditing tools through a standardized interface.
- **Commit History Preservation**: Maintain a complete history of changes with full commit records.
- **Platform Agnostic**: Operates independently of the target audit operating system for broad compatibility.
- **Scalable Support**: Currently supports Ubuntu 20.04 with plans to extend to Windows, Debian, and Red Hat Enterprise Linux.

## Table of Contents

- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Steps](#steps)
- [Usage](#usage)
  - [Use Cases](#use-cases)
    - [Main Use Case](#main-use-case)
    - [Demo Use Case](#demo-use-case)
  - [Defining Audit Logic](#defining-audit-logic)
  - [Executing Audits](#executing-audits)
- [Interface Functions](#interface-functions)
  - [ScriptProcessor Class](#scriptprocessor-class)
- [Supported Platforms](#supported-platforms)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Installation

### Prerequisites

- **Python 3.10.12** or higher
- **Git** for repository management

### Steps

1. **Clone the Repository**

   ```bash
   git clone <your-repository-url>
   ```

2. **Navigate to the Project Directory**

   ```bash
   cd <repository-name>
   ```

3. **Install Dependencies**

   It's recommended to use a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   Then install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Use Cases

#### Main Use Case

The `main.py` script demonstrates how to utilize the **AuditLang Interpreter Interface**. It processes YAML audit files, executes defined audit checks on a target system via SSH, and generates detailed reports.

**Example Command:**

```bash
python main.py <path_to_yml_file> <ip> <username> <password> <port>
```

**Example:**

```bash
python main.py audits/ssh_audit.yml 192.168.1.100 admin secretpassword 22
```

This command processes the specified YAML file, executes the defined audit checks on the target system, and generates a comprehensive report.

#### Demo Use Case

The `demo/` directory provides a complete demonstration of the **AuditLang Interpreter Interface** in action, including backend, frontend, and Docker Compose setup. For detailed instructions on setting up and running the demo, please refer to the [Demo README](demo/README.md).

### Defining Audit Logic

Create audit rules using a simple language and organize them within `.yml` files. Below is an example structure:

```yaml
checks:
  - id: check_001
    title: Ensure SSH is installed
    description: SSH should be installed for remote access.
    condition: installed
    rules:
      - rule_1
      - rule_2
    compliance:
      PCI-DSS: ["Requirement 2.2.1", "Requirement 2.2.2"]
```

### Executing Audits

Use the provided `main.py` script to execute audits and generate reports.

```bash
python main.py <path_to_yml_file> <ip> <username> <password> <port>
```

**Example:**

```bash
python main.py audits/ssh_audit.yml 192.168.1.100 admin secretpassword 22
```

This command processes the specified YAML file, executes the defined audit checks on the target system, and generates a detailed report.

## Interface Functions

The core functionality of the **AuditLang Interpreter Interface** is encapsulated within the `ScriptProcessor` class, which provides methods to process audit scripts and execute audits via SSH.

### ScriptProcessor Class

Handles the end-to-end processing of audit scripts, including validation, semantic tree construction, and execution.

- **Initialization**

  ```python
  def __init__(self):
      self.validator = ScriptValidator()
      self.tree_builder = SemanticTreeBuilder()
  ```

- **Methods**

  - `process_yml(file_content: str) -> Union[str, Dict]`

    Validates the YAML content and builds a semantic tree.

  - `process_json(script_list: List[Dict]) -> Union[str, Dict]`

    Processes a list of JSON scripts to build a semantic tree.

  - `executor(tree_json: str, ssh_details: Dict) -> Dict`

    Executes the semantic tree on the target system via SSH.

#### Example Usage of ScriptProcessor

```python
from script_processor import ScriptProcessor

# Initialize the processor
processor = ScriptProcessor()

# Process a YAML file content
with open('audits/ssh_audit.yml', 'r') as file:
    yaml_content = file.read()
tree_json = processor.process_yml(yaml_content)

# Define SSH details
ssh_details = {
    'ip': '192.168.1.100',
    'username': 'admin',
    'password': 'secretpassword',
    'port': 22
}

# Execute the semantic tree
result = processor.executor(tree_json, ssh_details)

# Handle the result
if result['status'] == 'success':
    print("Audit completed successfully.")
    print(result['results'])
else:
    print("Audit failed.")
    print(result['error_message'])
```

## Supported Platforms

**AuditLang Interpreter Interface** has been successfully tested on:

- **Ubuntu 20.04**

Future support plans include:

- **Windows**
- **Debian**
- **Red Hat Enterprise Linux**

## Future Enhancements

- **Python Package Encapsulation**: Encapsulate interface functionalities into Python packages for enhanced modularity and integration.
- **Extended OS Support**: Broaden compatibility to include additional operating systems.
- **Enhanced Validation**: Implement comprehensive JSON validation for audit scripts.
- **GUI Integration**: Develop a graphical user interface for easier audit management.
- **Cloud Integration**: Enable auditing of cloud-based infrastructures and services.

## Contributing

Contributions are welcome! Follow these steps to contribute:

1. **Fork the Repository**
2. **Create a Feature Branch**

   ```bash
   git checkout -b feature/YourFeature
   ```

3. **Commit Your Changes**

   ```bash
   git commit -m "Add your feature"
   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/YourFeature
   ```

5. **Open a Pull Request**

Ensure your code adheres to the project's coding standards and includes appropriate tests.

## License

This project is licensed under the **GNU General Public License (GPL) v3.0**. Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. **Non-Commercial Use Only**: This software may not be used for commercial purposes without explicit written permission from the author.

2. **Source Code Availability**: Any modified versions of this software must also be licensed under the GPL v3.0.

3. **Preservation of License**: All copies of the software, including modified versions, must include this license notice.

**Unauthorized commercial use of this software is strictly prohibited.**

## Contact

For inquiries or support, please contact:

**Jerry Hung**  
Email: [chiehlee.hung@gmail.com](mailto:chiehlee.hung@gmail.com)

---

© 2024 AuditLang Interpreter Interface. All rights reserved.

---

**Note:** The GNU General Public License (GPL) v3.0 itself does not restrict commercial use. If you intend to prohibit commercial use, consider using a different license or consult with a legal professional to create a custom license that meets your requirements. Combining GPL with additional restrictions may violate the terms of the GPL, leading to potential legal issues.