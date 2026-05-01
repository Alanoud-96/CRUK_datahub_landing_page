import json
import os

from mapping_utils import (
    deduplicate_by_id,
    resolve_labels_to_objects,
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


def get_intermediate_mapped_terms(input_term, histology_text=None):
    term_key = None

    if input_term["label"] in topography_mappings:
        term_key = input_term["label"]
    elif input_term["category"] in topography_mappings:
        term_key = input_term["category"]

    if term_key is None:
        return None, [], []

    mapping = topography_mappings[term_key]

    cruk_terms = mapping.get("default_CRUK") or []
    default_tcga_terms = mapping.get("default_tcga") or []
    tcga_labels_to_use = list(default_tcga_terms)

    overrides = mapping.get("overrides", [])
    override_applied = False

    if histology_text is not None:
        histology_text = histology_text.strip()

        for override in overrides:
            override_histologies = override.get("histology", [])

            if histology_text in override_histologies:
                tcga_value = override.get("tcga")

                if tcga_value is None:
                    tcga_labels_to_use = []
                elif isinstance(tcga_value, list):
                    tcga_labels_to_use = list(tcga_value)
                else:
                    tcga_labels_to_use = [tcga_value]

                override_applied = True
                break

    cruk_objects = resolve_labels_to_objects(cruk_terms, label_key_dict, filter_data)
    tcga_objects = resolve_labels_to_objects(tcga_labels_to_use, label_key_dict, filter_data)

    if override_applied:
        tcga_objects = deduplicate_by_id(tcga_objects)

    return term_key, cruk_objects, tcga_objects
