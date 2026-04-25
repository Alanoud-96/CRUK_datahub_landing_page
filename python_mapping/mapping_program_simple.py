import json
import os
from mapping_utils import find_objects_by_labels, find_object_by_key, find_raw_node_by_key, deduplicate_by_id, resolve_labels_to_objects, collect_child_icdo_terms


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

def get_mapped_terms(input_term):
    term_key = None

    if input_term["label"] in topography_mappings:
        term_key = input_term["label"]
    elif input_term["category"] in topography_mappings:
        term_key = input_term["category"]

    if term_key is None:
        cruk_objects = []
        tcga_objects = []
    else:
        mapping = topography_mappings[term_key]
        cruk_terms = mapping.get("default_CRUK") or []
        tcga_terms = mapping.get("default_tcga") or []

        cruk_objects = resolve_labels_to_objects(cruk_terms, label_key_dict, filter_data)
        tcga_objects = resolve_labels_to_objects(tcga_terms, label_key_dict, filter_data)

    return term_key, cruk_objects, tcga_objects


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

        parent_term = {
            "id": parent_node.get("id"),
            "label": parent_node.get("label"),
            "category": parent_node.get("category"),
            "primaryGroup": parent_node.get("primaryGroup"),
            "description": parent_node.get("description")
        }

        all_test_terms.append(parent_term)
        all_test_terms.extend(collect_child_icdo_terms(parent_node))

    return deduplicate_by_id(all_test_terms)
