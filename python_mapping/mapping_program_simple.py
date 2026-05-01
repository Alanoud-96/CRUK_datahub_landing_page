import json
import os

from mapping_utils import resolve_labels_to_objects


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
