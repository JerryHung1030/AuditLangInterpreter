import os
import yaml
from collections import defaultdict
import matplotlib.pyplot as plt
import logging

# Configure logging to write to a file
logging.basicConfig(filename='debug_log.txt', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# OS folders to include
os_folders = [
    'almalinux', 'centos', 'darwin', 
    'debian', 'rhel', 'sunos', 'ubuntu', 'windows', 'tested_data'
]

def parse_yaml_files(base_dir):
    data = defaultdict(lambda: defaultdict(int))
    script_counts = defaultdict(int)
    total_checks = 0
    total_rules = 0

    for os_type in os.listdir(base_dir):
        if os_type not in os_folders or os_type == 'env':
            continue
        
        os_path = os.path.join(base_dir, os_type)
        if os.path.isdir(os_path):
            logging.info(f"Processing OS type: {os_type}")
            
            # Recursively walk through directories and files
            for root, dirs, files in os.walk(os_path):
                for script_file in files:
                    if script_file.endswith('.yml'):
                        script_path = os.path.join(root, script_file)
                        logging.info(f"Processing file: {script_path}")
                        with open(script_path, 'r') as file:
                            try:
                                content = yaml.safe_load(file)
                                checks = content.get('checks', None)
                                if checks is None or len(checks) == 0:
                                    logging.warning(f"No or empty 'checks' found in {script_file}")
                                    continue

                                # Increment the script count for this OS type
                                script_counts[os_type] += len(checks)
                                total_checks += len(checks)

                                for check in checks:
                                    rules = check.get('rules', None)
                                    if rules is None or len(rules) == 0:
                                        logging.warning(f"No or empty 'rules' found in check ID {check.get('id', 'unknown')} in {script_file}")
                                        continue
                                    
                                    total_rules += len(rules)

                                    for rule in rules:
                                        rule_type = rule.split(':')[0]
                                        if rule.startswith('not '):
                                            continue
                                        if rule_type in ['f', 'd', 'c', 'r', 'p']:
                                            data[os_type][rule_type] += 1

                            except yaml.YAMLError as exc:
                                logging.error(f"Error parsing {script_path}: {exc}")
            logging.info(f"Data for {os_type}: {dict(data[os_type])}")
            logging.info(f"Script count for {os_type}: {script_counts[os_type]}")

    return data, script_counts, total_checks, total_rules

def plot_data(data, script_counts, total_checks, total_rules):
    # Prepare data for plotting
    categories = ['f', 'd', 'c', 'r', 'p']
    labels = ['file', 'directory', 'command', 'registry', 'process']
    os_types = list(data.keys())
    values = {label: [data[os_type][category] for os_type in os_types] for category, label in zip(categories, labels)}

    # Calculate the maximum value to set the y-limit with some padding
    max_value = max([max(values[label]) for label in labels] + [max(script_counts.values())]) * 1.1  # Add 10% padding

    # Plot
    fig, ax1 = plt.subplots(figsize=(20, 10))
    
    bottom = [0] * len(os_types)
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd', '#8c564b']  # Custom colors to avoid conflict with red

    for i, label in enumerate(labels):
        bars = ax1.bar(os_types, values[label], bottom=bottom, label=label, color=colors[i])
        bottom = [i+j for i,j in zip(bottom, values[label])]

        # Add text labels for each bar
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax1.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_y() + height / 2,
                    f'{int(height)}',
                    ha='center',
                    va='center',
                    color='black',
                    fontsize=10
                )

    # Plot the script counts as a line plot
    ax1.plot(os_types, [script_counts[os_type] for os_type in os_types], color='red', marker='o', linestyle='-', label='Script Count', linewidth=2)
    
    # Add text labels for each script count on the left side of the points
    for i, os_type in enumerate(os_types):
        ax1.text(i - 0.1, script_counts[os_type], f'{script_counts[os_type]}', color='red', fontsize=10, ha='right', va='center')

    ax1.set_xlabel('OS Types')
    ax1.set_ylabel('Count')
    ax1.set_ylim(0, max_value)  # Set the y-axis limit with some space at the top
    ax1.set_title('Rule Types and Script Counts Across OS Types')
    ax1.set_xticks(range(len(os_types)))
    ax1.set_xticklabels(os_types, rotation=45, ha="right")
    ax1.legend(title='Rule Types & Script Count')

    # Display total counts in the title
    plt.suptitle(f"Total Checks: {total_checks}, Total Rules: {total_rules}", fontsize=16)

    plt.tight_layout()
    plt.savefig('os_rule_script_distribution.png')
    plt.show()

base_directory = '.'  # Set to current directory
data, script_counts, total_checks, total_rules = parse_yaml_files(base_directory)
plot_data(data, script_counts, total_checks, total_rules)
