import json
import os

from python_mapping.mapping_utils import (
    extract_node_fields,
    find_raw_node_by_key,
    deduplicate_by_id,
    collect_child_icdo_terms,
)


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

SCHEMA_PATH = os.path.join(PROJECT_ROOT, "schemas", "schema_simple_1.1.2.json")
FILTER_DATA_PATH = os.path.join(PROJECT_ROOT, "longer_filter_data.json")
LABEL_KEY_DICT_PATH = os.path.join(PROJECT_ROOT, "label_key_dict.json")

with open(SCHEMA_PATH, encoding="utf-8") as file:
    schema = json.load(file)

with open(LABEL_KEY_DICT_PATH, encoding="utf-8") as file:
    label_key_dict = json.load(file)

with open(FILTER_DATA_PATH, encoding="utf-8") as file:
    filter_data = json.load(file)

topography_mappings = schema["topography_mappings"]


def build_test_terms_from_schema():
    all_test_terms = []

    for schema_term in topography_mappings.keys():
        parent_key = label_key_dict.get(schema_term)

        if parent_key is None:
            print(f"[WARNING] Schema term not found in label_key_dict: {schema_term}")
            continue

        parent_node = find_raw_node_by_key(filter_data, parent_key)

        if parent_node is None:
            print(f"[WARNING] Schema term key not found in longer_filter_data: {schema_term} -> {parent_key}")
            continue

        parent_term = extract_node_fields(parent_node)

        all_test_terms.append(parent_term)
        all_test_terms.extend(collect_child_icdo_terms(parent_node))

    return deduplicate_by_id(all_test_terms)