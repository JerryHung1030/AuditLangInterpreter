import os
import yaml
from collections import defaultdict
import matplotlib.pyplot as plt
import logging

# Configure logging to write to a file
logging.basicConfig(filename='debug_log.txt', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# OS folders to include
# os_folders = [
#     'almalinux', 'centos', 'darwin', 
#     'debian', 'rhel', 'sunos', 'ubuntu', 'windows'
# ]
os_folders = [
    'ubuntu22.04'
]

def parse_yaml_files(base_dir):
    data = defaultdict(lambda: defaultdict(int))

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

                                for check in checks:
                                    rules = check.get('rules', None)
                                    if rules is None or len(rules) == 0:
                                        logging.warning(f"No or empty 'rules' found in check ID {check.get('id', 'unknown')} in {script_file}")
                                        continue

                                    for rule in rules:
                                        rule_type = rule.split(':')[0]
                                        if rule.startswith('not '):
                                            continue
                                        if rule_type in ['f', 'd', 'c', 'r', 'p']:
                                            data[rule_type][os_type] += 1

                            except yaml.YAMLError as exc:
                                logging.error(f"Error parsing {script_path}: {exc}")
            logging.info(f"Data for {os_type}: {dict(data[os_type])}")

    return data

def plot_data(data):
    # Prepare data for plotting
    rule_types = ['f', 'd', 'c', 'r', 'p']
    rule_labels = ['file', 'directory', 'command', 'registry', 'process']
    os_types = list(next(iter(data.values())).keys())
    
    fig, ax = plt.subplots(figsize=(14, 8))

    width = 0.6  # Width of each bar (set smaller to make bars thinner)
    bottom = [0] * len(rule_types)
    x = range(len(rule_types))
    
    for os_type in os_types:
        values = [data[rule_type][os_type] for rule_type in rule_types]
        bars = ax.bar(x, values, width=width, bottom=bottom, label=os_type)

        bottom = [i+j for i, j in zip(bottom, values)]

        # Add text labels for each bar
        for i, bar in enumerate(bars):
            height = bar.get_height()
            if height > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_y() + height / 2,
                    f'{int(height)}',
                    ha='center',
                    va='center',
                    color='black',
                    fontsize=10
                )

    ax.set_xlabel('Rule Types')
    ax.set_ylabel('Count')
    ax.set_title('OS Types Distribution Across Rule Types')
    ax.set_xticks(x)
    ax.set_xticklabels(rule_labels, rotation=45, ha="right")
    ax.legend(title='OS Types')

    plt.tight_layout()
    plt.savefig('rule_type_os_distribution_stacked_thin.png')
    plt.show()

base_directory = '.'  # Set to current directory
data = parse_yaml_files(base_directory)
plot_data(data)
