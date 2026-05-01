import json
import os

from python_mapping.mapping_utils import (
    extract_node_fields,
    find_raw_node_by_key,
    collect_child_icdo_terms,
)


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

SCHEMA_PATH = os.path.join(PROJECT_ROOT, "schemas", "schema_intermediate_1.1.2.json")
FILTER_DATA_PATH = os.path.join(PROJECT_ROOT, "longer_filter_data.json")
LABEL_KEY_DICT_PATH = os.path.join(PROJECT_ROOT, "label_key_dict.json")

with open(SCHEMA_PATH, encoding="utf-8") as file:
    schema = json.load(file)

with open(LABEL_KEY_DICT_PATH, encoding="utf-8") as file:
    label_key_dict = json.load(file)

with open(FILTER_DATA_PATH, encoding="utf-8") as file:
    filter_data = json.load(file)

topography_mappings = schema["topography_mappings"]


def build_intermediate_test_cases():
    histology_examples = {
        "C64 Kidney": [
            "8312/3 Renal cell carcinoma",
            "8260/3 Papillary adenocarcinoma, NOS",
            "8317/3 Renal cell carcinoma, chromophobe type",
        ],
        "C34 Bronchus and lung": [
            "8140/3 Adenocarcinoma, NOS",
            "8070/3 Squamous cell carcinoma, NOS",
        ],
        "C71 Brain": [
            "9440/3 Glioblastoma, NOS",
            "9401/3 Astrocytoma, anaplastic",
        ],
        "C22 Liver and intrahepatic bile ducts": [
            "8170/3 Hepatocellular carcinoma, NOS",
            "8160/3 Cholangiocarcinoma",
        ],
        "C25 Pancreas": [
            "8140/3 Adenocarcinoma, NOS",
            "8500/3 Infiltrating duct carcinoma, NOS",
        ],
        "C54 Corpus uteri": [
            "8380/3 Endometrioid adenocarcinoma, NOS",
            "8980/3 Carcinosarcoma, NOS",
        ],
        "C74 Adrenal gland": [
            "8370/3 Adrenal cortical carcinoma",
            "8700/3 Pheochromocytoma, NOS",
        ],
    }

    all_cases = []

    for schema_term in topography_mappings.keys():
        parent_key = label_key_dict.get(schema_term)

        if parent_key is None:
            continue

        parent_node = find_raw_node_by_key(filter_data, parent_key)

        if parent_node is None:
            continue

        parent_term = extract_node_fields(parent_node)
        child_terms = collect_child_icdo_terms(parent_node)
        terms_to_test = [parent_term] + child_terms

        for histology in histology_examples.get(schema_term, []):
            for term in terms_to_test:
                all_cases.append({
                    "term": term,
                    "histology": histology
                })

    return all_cases