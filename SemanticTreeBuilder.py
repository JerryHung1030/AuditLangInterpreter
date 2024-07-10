import yaml
import json
import argparse


class SemanticTreeBuilder:
    """
    SemanticTreeBuilder is responsible for building a semantic tree from wazuh yaml file.
    """

    def __init__(self) -> None:
        """
        Construct a SemanticTreeBuilder object.
        """
        pass

    @staticmethod
    def parse_rule(rule_str):
        """
        Parse a single rule string and create another string format.
        """
        rule_parts = rule_str.split(" -> ")
        target = rule_parts[0].strip()
        conditions = rule_parts[1].split(" && ")
        content_rules = []

        for condition in conditions:
            if " compare " in condition:
                condition_parts = condition.strip().split(" compare ")
                content_operator, value = condition_parts[0].strip().split(":")
                compare_operator, compare_value = condition_parts[1].strip().split(" ")
                content_rules.append(
                    {
                        "content_operator": content_operator.strip(),
                        "value": value.strip(),
                        "compare_operator": compare_operator.strip(),
                        "compare_value": compare_value.strip(),
                    }
                )
            else:
                content_operator, value = condition.strip().split(":")
                content_rules.append(
                    {
                        "content_operator": content_operator.strip(),
                        "value": value.strip(),
                    }
                )

        return {
            "target": target,
            "content_rules": content_rules,
        }

    @staticmethod
    def build_tree(parsed_checks):
        """
        Build the semantic tree from the parse rule string format.
        """
        trees = []
        for check in parsed_checks:
            tree = {"condition": check["condition"], "rules": []}
            for rule in check["parsed_rules"]:
                execution_node = {
                    "type": rule["target"].split(":")[0],
                    "target": rule["target"].split(":")[1],
                }
                tree["rules"].append({"execution_node": execution_node, "content_rules": rule["content_rules"]})
            trees.append(tree)
        return trees

    @staticmethod
    def tree_to_json(trees):
        """
        convert semantic tree to json format
        """
        return json.dumps(trees, indent=4)

    @staticmethod
    def gey_errors():
        """
        This function I have no idea.
        """
        pass


def main():
    """
    c: python SemanticTreeBuilder.py ./data/sample2.yml
    can see the result.
    """
    parser = argparse.ArgumentParser(description='Process YAML file to JSON.')
    parser.add_argument('input', type=str, help='Input YAML file path')
    parser.add_argument('output', type=str, nargs='?', help='Output JSON file path', default=None)

    args = parser.parse_args()

    # Load the YAML input file
    try:
        with open(args.input, 'r') as yml_file:
            yml_data = yaml.safe_load(yml_file)
    except Exception as e:
        print(f"Error loading YAML file: {e}")
        return None

    # Get the checks from the YAML data, there are many type in yaml data, i.e. policy, requirement, checks
    checks = yml_data.get('checks')

    if not checks:
        print("Checks not found in YAML file.")
        return None
    # Parse checks until there is no rules.
    parsed_checks = []
    for check in checks:
        condition = check.get('condition')
        rules = check.get('rules')
        if not condition or not rules:
            print(f"Condition or rules not found for check ID {check.get('id')}. Skipping this check.")
            continue

        parsed_rules = [SemanticTreeBuilder.parse_rule(rule) for rule in rules]
        parsed_checks.append({"condition": condition, "parsed_rules": parsed_rules})

    # Build the tree from the parsed checks
    trees = SemanticTreeBuilder.build_tree(parsed_checks)

    # Convert the trees to JSON
    json_output = SemanticTreeBuilder.tree_to_json(trees)
    print(json_output)


if __name__ == "__main__":
    main()
