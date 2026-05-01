import json
import os
from typing import Any, Dict, List, Optional, Tuple

from mapping_utils import resolve_labels_to_objects


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

SCHEMA_PATH = os.path.join(PROJECT_ROOT, "schemas", "schema_rare_1.1.2.json")
LABEL_KEY_DICT_PATH = os.path.join(PROJECT_ROOT, "label_key_dict.json")
LONGER_FILTER_DATA_PATH = os.path.join(PROJECT_ROOT, "longer_filter_data.json")


def load_json_file(filepath: str) -> Any:
    with open(filepath, encoding="utf-8") as file:
        return json.load(file)


RARE_SCHEMA = load_json_file(SCHEMA_PATH)
LABEL_KEY_DICT = load_json_file(LABEL_KEY_DICT_PATH)
LONGER_FILTER_DATA = load_json_file(LONGER_FILTER_DATA_PATH)


def deduplicate_strings(items: List[str]) -> List[str]:
    seen = set()
    unique_items = []

    for item in items:
        if item not in seen:
            seen.add(item)
            unique_items.append(item)

    return unique_items


def normalise_label(label: Optional[str]) -> str:
    if not isinstance(label, str):
        return ""
    return label.strip().lower()


def collect_dataset_filters(dataset: Dict[str, Any]) -> List[Dict[str, Any]]:
    dataset_filters = dataset.get("datasetFilters", [])
    collected = []

    def search_node(node: Any) -> None:
        if isinstance(node, dict):
            if "label" in node:
                collected.append(node)
            for value in node.values():
                search_node(value)
        elif isinstance(node, list):
            for item in node:
                search_node(item)

    search_node(dataset_filters)
    return collected


def extract_histology_labels(dataset: Dict[str, Any]) -> List[str]:
    histology_labels = []

    for item in collect_dataset_filters(dataset):
        label = item.get("label", "")
        if isinstance(label, str) and len(label) >= 6 and label[:4].isdigit() and label[4] == "/":
            histology_labels.append(label)

    return deduplicate_strings(histology_labels)


def extract_topography_labels(dataset: Dict[str, Any]) -> List[str]:
    topography_labels = []

    for item in collect_dataset_filters(dataset):
        label = item.get("label", "")
        primary_group = item.get("primaryGroup", "")

        if isinstance(label, str) and label.startswith("C") and primary_group == "cancer-type":
            topography_labels.append(label)

    return deduplicate_strings(topography_labels)


def extract_cruk_labels(dataset: Dict[str, Any]) -> List[str]:
    cruk_labels = []

    for item in collect_dataset_filters(dataset):
        category = item.get("category", "")
        label = item.get("label", "")

        if category == "crukTerms" and isinstance(label, str):
            cruk_labels.append(label)

    return deduplicate_strings(cruk_labels)


def match_topography_exact(rule: Dict[str, Any], topography_labels: List[str]) -> bool:
    allowed = rule.get("topography_exact", [])
    allowed_normalised = {normalise_label(item) for item in allowed}
    input_normalised = {normalise_label(item) for item in topography_labels}
    return bool(allowed_normalised.intersection(input_normalised))


def match_histology_exact(rule: Dict[str, Any], histology_labels: List[str]) -> bool:
    allowed = rule.get("histology_exact", [])
    allowed_normalised = {normalise_label(item) for item in allowed}
    input_normalised = {normalise_label(item) for item in histology_labels}
    return bool(allowed_normalised.intersection(input_normalised))


def match_cruk_label(rule: Dict[str, Any], cruk_labels: List[str]) -> bool:
    rule_label = normalise_label(rule.get("cruk_label"))
    input_labels = {normalise_label(item) for item in cruk_labels}
    return rule_label in input_labels


def evaluate_rule(
    rule: Dict[str, Any],
    topography_labels: List[str],
    histology_labels: List[str],
    cruk_labels: List[str]
) -> bool:
    match_type = rule.get("match_type")

    if match_type == "topography_exact":
        return match_topography_exact(rule, topography_labels)

    if match_type == "histology_exact":
        return match_histology_exact(rule, histology_labels)

    if match_type == "topography_exact_and_histology_exact":
        return (
            match_topography_exact(rule, topography_labels)
            and match_histology_exact(rule, histology_labels)
        )

    if match_type == "cruk_label":
        return match_cruk_label(rule, cruk_labels)

    if match_type == "fallback":
        return True

    return False


def get_ordered_rare_rules(rare_rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    priority_order = [
        "topography_exact_and_histology_exact",
        "topography_exact",
        "histology_exact",
        "cruk_label",
        "fallback"
    ]

    ordered_rules = []

    for match_type in priority_order:
        for rule in rare_rules:
            if rule.get("match_type") == match_type:
                ordered_rules.append(rule)

    return ordered_rules


def get_rare_mapped_terms(dataset: Dict[str, Any]) -> Tuple[
    Optional[str],
    Optional[str],
    List[Dict[str, Any]],
    List[Dict[str, Any]]
]:
    topography_labels = extract_topography_labels(dataset)
    histology_labels = extract_histology_labels(dataset)
    cruk_labels = extract_cruk_labels(dataset)

    rare_rules = RARE_SCHEMA.get("rare_rules", [])
    ordered_rules = get_ordered_rare_rules(rare_rules)

    for rule in ordered_rules:
        if evaluate_rule(rule, topography_labels, histology_labels, cruk_labels):
            return_cruk_labels = rule.get("return_CRUK", [])
            return_tcga_labels = rule.get("return_TCGA", [])

            matched_term = ", ".join(return_cruk_labels) or None
            matched_rule = rule.get("rule_name")

            cruk_objects = resolve_labels_to_objects(
                return_cruk_labels,
                LABEL_KEY_DICT,
                LONGER_FILTER_DATA
            )

            tcga_objects = resolve_labels_to_objects(
                return_tcga_labels,
                LABEL_KEY_DICT,
                LONGER_FILTER_DATA
            )

            return matched_term, matched_rule, cruk_objects, tcga_objects

    return None, None, [], []