import json
import os

from python_mapping.mapping_utils import (
    extract_node_fields,
    find_raw_node_by_key,
    collect_child_icdo_terms,
)


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

SCHEMA_PATH = os.path.join(PROJECT_ROOT, "schemas", "schema_complex_1.1.2.json")
FILTER_DATA_PATH = os.path.join(PROJECT_ROOT, "longer_filter_data.json")
LABEL_KEY_DICT_PATH = os.path.join(PROJECT_ROOT, "label_key_dict.json")

with open(SCHEMA_PATH, encoding="utf-8") as file:
    schema = json.load(file)

with open(LABEL_KEY_DICT_PATH, encoding="utf-8") as file:
    label_key_dict = json.load(file)

with open(FILTER_DATA_PATH, encoding="utf-8") as file:
    filter_data = json.load(file)


_HISTOLOGY_EXAMPLES = {
    "UVM": [{"schema_term_label": "C69 Eye and adnexa", "histology": "8720/3 Malignant melanoma, NOS"}],
    "SKCM": [{"schema_term_label": "C44 Skin", "histology": "8720/3 Malignant melanoma, NOS"}],
    "HNSC": [
        {"schema_term_label": "C00 Lip", "histology": "8070/3 Squamous cell carcinoma, NOS"},
        {"schema_term_label": "C32 Larynx", "histology": "8070/3 Squamous cell carcinoma, NOS"},
    ],
    "LAML": [{"schema_term_label": "C42 Hematopoietic and reticuloendothelial systems", "histology": "9861/3 Acute myeloid leukemia, NOS"}],
    "DLBC": [{"schema_term_label": "C42 Hematopoietic and reticuloendothelial systems", "histology": "9680/3 Diffuse large B-cell lymphoma, NOS"}],
    "MESO": [{"schema_term_label": "C38 Heart, mediastinum, and pleura", "histology": "9050/3 Mesothelioma, malignant"}],
    "SARC": [{"schema_term_label": "C49 Connective, subcutaneous and other soft tissues", "histology": "8800/3 Sarcoma, NOS"}],
    "PCPG": [{"schema_term_label": "C74 Adrenal gland", "histology": "8700/3 Pheochromocytoma, NOS"}],
    "CHOL": [{"schema_term_label": "C22 Liver and intrahepatic bile ducts", "histology": "8160/3 Cholangiocarcinoma"}],
}


def build_complex_test_cases():
    all_cases = []

    for schema_term, example_list in _HISTOLOGY_EXAMPLES.items():
        for example in example_list:
            parent_label = example["schema_term_label"]
            histology = example["histology"]

            parent_key = label_key_dict.get(parent_label)
            if parent_key is None:
                continue

            parent_node = find_raw_node_by_key(filter_data, parent_key)
            if parent_node is None:
                continue

            parent_term = extract_node_fields(parent_node)
            child_terms = collect_child_icdo_terms(parent_node)

            for term in [parent_term] + child_terms:
                all_cases.append({
                    "schema_term": schema_term,
                    "term": term,
                    "histology": histology,
                })

    return all_cases