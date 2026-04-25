import json
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

SCHEMA_PATH = os.path.join(PROJECT_ROOT, "schemas", "schema_special_1.1.2.json")
FILTER_DATA_PATH = os.path.join(PROJECT_ROOT, "longer_filter_data.json")
LABEL_KEY_DICT_PATH = os.path.join(PROJECT_ROOT, "label_key_dict.json")

with open(SCHEMA_PATH, encoding="utf-8") as f:
    schema = json.load(f)

with open(LABEL_KEY_DICT_PATH, encoding="utf-8") as f:
    label_key_dict = json.load(f)

with open(FILTER_DATA_PATH, encoding="utf-8") as f:
    filter_data = json.load(f)

special_rules = schema["special_rules"]


def collect_all_filter_objects(data):
    collected = []

    if isinstance(data, dict):
        if "label" in data and "id" in data and "category" in data:
            collected.append(data)

        for value in data.values():
            collected.extend(collect_all_filter_objects(value))

    elif isinstance(data, list):
        for item in data:
            collected.extend(collect_all_filter_objects(item))

    return collected


def find_objects_by_labels(data, target_labels):
    matched_objects = []
    seen_ids = set()

    all_objects = collect_all_filter_objects(data)

    for obj in all_objects:
        label = obj.get("label")
        obj_id = obj.get("id")

        if label in target_labels and obj_id not in seen_ids:
            matched_objects.append({
                "id": obj.get("id"),
                "label": obj.get("label"),
                "category": obj.get("category"),
                "primaryGroup": obj.get("primaryGroup"),
                "description": obj.get("description")
            })
            seen_ids.add(obj_id)

    return matched_objects


def normalise_label(value):
    if value is None:
        return ""
    return value.strip()


def extract_input_labels(dataset_filters):
    cruk_label = None
    topography_label = None
    histology_label = None

    for item in dataset_filters:
        category = item.get("category")
        label = item.get("label")

        # Skip auto-generated crukTerms so that special rules only fire on
        # original user-selected CRUK inputs, not on terms injected by a
        # previous mapping pass (which would cause rules like "Men's cancer"
        # to match datasets such as C51-C58 Female genital organs).
        if category == "crukTerms" and cruk_label is None and not item.get("isGenerated"):
            cruk_label = label

        elif category == "icdOTopography" and topography_label is None:
            topography_label = label

        elif category in {"icdOHistology", "icdOMorphology", "histology"} and histology_label is None:
            histology_label = label

    return cruk_label, topography_label, histology_label


def rule_matches(rule, cruk_label, topography_label, histology_label):
    match_type = rule.get("match_type")

    cruk_label = normalise_label(cruk_label)
    topography_label = normalise_label(topography_label)
    histology_label = normalise_label(histology_label)

    if match_type == "cruk_label":
        return cruk_label == normalise_label(rule.get("cruk_label"))

    if match_type == "histology_exact":
        return histology_label in rule.get("histology_exact", [])

    if match_type == "topography_exact":
        return topography_label in rule.get("topography_exact", [])

    if match_type == "topography_exact_and_histology_exact":
        return (
            topography_label in rule.get("topography_exact", [])
            and histology_label in rule.get("histology_exact", [])
        )

    return False


def get_matching_special_rules(cruk_label, topography_label, histology_label):
    matches = []

    for rule in special_rules:
        if rule_matches(rule, cruk_label, topography_label, histology_label):
            matches.append(rule)

    return matches


def get_return_cruk_labels(cruk_label, topography_label, histology_label):
    matched_rules = get_matching_special_rules(
        cruk_label,
        topography_label,
        histology_label
    )

    return_labels = []
    seen_labels = set()

    for rule in matched_rules:
        for label in rule.get("return_CRUK", []):
            normalised = normalise_label(label)
            if normalised and normalised not in seen_labels:
                return_labels.append(normalised)
                seen_labels.add(normalised)

    return return_labels


def get_return_tcga_labels(cruk_label, topography_label, histology_label):
    matched_rules = get_matching_special_rules(
        cruk_label,
        topography_label,
        histology_label
    )

    return_labels = []
    seen_labels = set()

    for rule in matched_rules:
        for label in rule.get("return_TCGA", []):
            normalised = normalise_label(label)
            if normalised and normalised not in seen_labels:
                return_labels.append(normalised)
                seen_labels.add(normalised)

    return return_labels


def get_missing_labels_from_label_key_dict(labels, label_dict):
    missing_labels = []

    for label in labels:
        if label not in label_dict:
            missing_labels.append(label)

    return missing_labels


def map_special_cruk_terms(dataset_filters):
    cruk_label, topography_label, histology_label = extract_input_labels(dataset_filters)

    matched_rules = get_matching_special_rules(
        cruk_label,
        topography_label,
        histology_label
    )

    return_cruk_labels = get_return_cruk_labels(
        cruk_label,
        topography_label,
        histology_label
    )

    return_tcga_labels = get_return_tcga_labels(
        cruk_label,
        topography_label,
        histology_label
    )

    missing_labels_in_label_key_dict = get_missing_labels_from_label_key_dict(
        return_cruk_labels,
        label_key_dict
    )

    resolved_cruk_objects = find_objects_by_labels(filter_data, return_cruk_labels)

    resolved_labels = {obj.get("label") for obj in resolved_cruk_objects}
    missing_labels_in_filter_data = [
        label for label in return_cruk_labels
        if label not in resolved_labels
    ]

    return {
        "input": {
            "cruk_label": cruk_label,
            "topography_label": topography_label,
            "histology_label": histology_label
        },
        "matched_rule_names": [rule.get("rule_name") for rule in matched_rules],
        "return_cruk_labels": return_cruk_labels,
        "return_tcga_labels": return_tcga_labels,
        "missing_labels_in_label_key_dict": missing_labels_in_label_key_dict,
        "missing_labels_in_filter_data": missing_labels_in_filter_data,
        "resolved_cruk_objects": resolved_cruk_objects
    }


def get_special_mapped_terms(dataset):
    dataset_filters = dataset.get("datasetFilters", [])

    result = map_special_cruk_terms(dataset_filters)

    matched_rule_names = result.get("matched_rule_names", [])
    resolved_cruk_objects = result.get("resolved_cruk_objects", [])
    return_tcga_labels = result.get("return_tcga_labels", [])

    matched_term = ", ".join(result.get("return_cruk_labels", [])) or None
    matched_rule = ", ".join(matched_rule_names) if matched_rule_names else None

    return matched_term, matched_rule, resolved_cruk_objects, return_tcga_labels


if __name__ == "__main__":
    pass