import json
import os
import re

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

SCHEMA_PATH = os.path.join(PROJECT_ROOT, "schemas", "schema_complex_1.1.2.json")
FILTER_DATA_PATH = os.path.join(PROJECT_ROOT, "longer_filter_data.json")
LABEL_KEY_DICT_PATH = os.path.join(PROJECT_ROOT, "label_key_dict.json")

with open(SCHEMA_PATH, encoding="utf-8") as f:
    schema = json.load(f)

with open(LABEL_KEY_DICT_PATH, encoding="utf-8") as f:
    label_key_dict = json.load(f)

with open(FILTER_DATA_PATH, encoding="utf-8") as f:
    filter_data = json.load(f)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

COMPLEX_SECTIONS = [
    "histology_driven_mappings",
    "umbrella_or_special_mappings",
    "multi_site_or_overlap_mappings",
]

NODE_FIELDS = ("id", "label", "category", "primaryGroup", "description")


# ---------------------------------------------------------------------------
# Filter data lookup helpers
# ---------------------------------------------------------------------------

def _extract_node_fields(node):
    """Return the standard display fields from a filter_data node."""
    return {field: node.get(field) for field in NODE_FIELDS}


def find_objects_by_labels(data, target_labels):
    """
    Recursively search the filter_data tree for nodes whose 'label'
    matches any entry in target_labels.
    """
    matched_objects = []

    def search_node(node):
        if isinstance(node, dict):
            if node.get("label") in target_labels:
                matched_objects.append(_extract_node_fields(node))
            for value in node.values():
                search_node(value)
        elif isinstance(node, list):
            for item in node:
                search_node(item)

    search_node(data)
    return matched_objects


def find_object_by_key(data, target_key):
    """
    Recursively search the filter_data tree for a dict key matching target_key
    whose value is itself a dict. Returns the first matching object.
    """
    found_object = None

    def search_node(node):
        nonlocal found_object
        if found_object is not None:
            return

        if isinstance(node, dict):
            for key, value in node.items():
                if key == target_key and isinstance(value, dict):
                    found_object = _extract_node_fields(value)
                    return
                search_node(value)

        elif isinstance(node, list):
            for item in node:
                search_node(item)

    search_node(data)
    return found_object


def find_raw_node_by_key(data, target_key):
    """
    Recursively search the filter_data tree for a dict key matching target_key
    whose value is itself a dict. Returns the raw matching node.
    """
    found_node = None

    def search_node(node):
        nonlocal found_node
        if found_node is not None:
            return

        if isinstance(node, dict):
            for key, value in node.items():
                if key == target_key and isinstance(value, dict):
                    found_node = value
                    return
                search_node(value)

        elif isinstance(node, list):
            for item in node:
                search_node(item)

    search_node(data)
    return found_node


def deduplicate_by_id(items):
    """Remove duplicate dicts by their 'id' field, keeping first occurrence."""
    seen = set()
    unique_items = []

    for item in items:
        item_id = item.get("id")
        if item_id not in seen:
            seen.add(item_id)
            unique_items.append(item)

    return unique_items


def resolve_labels_to_objects(labels, label_key_dict, filter_data):
    """
    Resolve schema labels to filter_data objects.

    Resolution order:
        1. key-based lookup via label_key_dict
        2. fallback label-based lookup
    """
    if not labels:
        return []

    matched_objects = []

    for label in labels:
        obj = None

        target_key = label_key_dict.get(label)
        if target_key is not None:
            obj = find_object_by_key(filter_data, target_key)

        if obj is None:
            results = find_objects_by_labels(filter_data, [label])
            if results:
                obj = results[0]

        if obj is not None:
            matched_objects.append(obj)

    return deduplicate_by_id(matched_objects)


# ---------------------------------------------------------------------------
# ICD-O code extraction helpers
# ---------------------------------------------------------------------------

def extract_histology_code(histology_text):
    """
    Extract the ICD-O morphology code (XXXX/B) from the start of a histology string.
    """
    if histology_text is None:
        return None

    histology_text = histology_text.strip()
    match = re.match(r"^(\d{4}/\d)", histology_text)
    return match.group(1) if match else histology_text


def extract_topography_code(label_text):
    """
    Extract the ICD-O topography code (CXX or CXX.X) from a label string.
    Returns the two-digit code (e.g. C44).
    """
    if label_text is None:
        return None

    label_text = label_text.strip()
    match = re.match(r"^(C\d{2})(?:\.\d)?", label_text, re.IGNORECASE)
    return match.group(1).upper() if match else None


# ---------------------------------------------------------------------------
# Topography matching helpers
# ---------------------------------------------------------------------------

def topography_matches(term, allowed_topographies):
    """
    Check whether a term's topography code exactly matches any allowed code.
    Used for exact topography matching.
    """
    input_code = extract_topography_code(term.get("label", ""))
    if input_code is None:
        return False

    for topo in allowed_topographies:
        if extract_topography_code(topo) == input_code:
            return True

    return False


def topography_in_group(term, topography_codes):
    """
    Check whether a term's topography code falls within any listed range
    or exact code. Used for grouped topography matching.
    """
    input_code = extract_topography_code(term.get("label", ""))
    if input_code is None:
        return False

    input_match = re.match(r"^C(\d{2})$", input_code)
    if not input_match:
        return False

    input_num = int(input_match.group(1))

    for item in topography_codes:
        item = item.strip()
        range_match = re.match(r"^(C\d{2})-(C\d{2})$", item, re.IGNORECASE)

        if range_match:
            start_num = int(range_match.group(1)[1:])
            end_num = int(range_match.group(2)[1:])
            if start_num <= input_num <= end_num:
                return True
        else:
            if extract_topography_code(item) == input_code:
                return True

    return False


# ---------------------------------------------------------------------------
# Histology matching helper
# ---------------------------------------------------------------------------

def histology_matches(histology_text, allowed_histology_codes):
    """Check whether the extracted histology code matches an allowed code."""
    input_code = extract_histology_code(histology_text)
    if input_code is None:
        return False

    return input_code in allowed_histology_codes


# ---------------------------------------------------------------------------
# Rule evaluation
# ---------------------------------------------------------------------------

def rule_matches(term, histology_text, rule):
    """Evaluate a single schema rule against the input term and histology."""
    match_type = rule.get("match_type")

    if match_type == "histology_exact":
        return histology_matches(histology_text, rule.get("histology_codes", []))

    if match_type == "topography_exact":
        return topography_matches(term, rule.get("topography", []))

    if match_type == "topography_group":
        return topography_in_group(term, rule.get("topography_codes", []))

    if match_type == "topography_and_histology":
        return (
            topography_matches(term, rule.get("topography", []))
            and histology_matches(histology_text, rule.get("histology_codes", []))
        )

    if match_type == "topography_group_and_histology":
        return (
            topography_in_group(term, rule.get("topography_codes", []))
            and histology_matches(histology_text, rule.get("histology_codes", []))
        )

    return False


# ---------------------------------------------------------------------------
# Core complex mapping
# ---------------------------------------------------------------------------

def get_complex_mapped_terms(input_term, histology_text=None):
    """
    Map an input term and histology string to CRUK and TCGA objects
    using the complex schema.

    Returns:
        (schema_term, rule_name, cruk_objects, tcga_objects)

    If nothing matches:
        (None, None, [], [])
    """
    if histology_text is not None:
        histology_text = histology_text.strip()

    # Phase 1: full rule match
    for section_name in COMPLEX_SECTIONS:
        section = schema.get(section_name, {})

        for schema_term, mapping in section.items():
            for rule in mapping.get("rules", []):
                if rule_matches(input_term, histology_text, rule):
                    cruk_objects = resolve_labels_to_objects(
                        rule.get("cruk", []) or [], label_key_dict, filter_data
                    )
                    tcga_objects = resolve_labels_to_objects(
                        rule.get("tcga", []) or [], label_key_dict, filter_data
                    )
                    return schema_term, rule.get("rule_name"), cruk_objects, tcga_objects

    # Phase 2: fallback
    for section_name in COMPLEX_SECTIONS:
        section = schema.get(section_name, {})

        for schema_term, mapping in section.items():
            potentially_relevant = False

            for rule in mapping.get("rules", []):
                match_type = rule.get("match_type")

                if match_type == "histology_exact":
                    if histology_matches(histology_text, rule.get("histology_codes", [])):
                        potentially_relevant = True

                elif match_type == "topography_exact":
                    if topography_matches(input_term, rule.get("topography", [])):
                        potentially_relevant = True

                elif match_type == "topography_group":
                    if topography_in_group(input_term, rule.get("topography_codes", [])):
                        potentially_relevant = True

                elif match_type == "topography_and_histology":
                    if topography_matches(input_term, rule.get("topography", [])):
                        potentially_relevant = True

                elif match_type == "topography_group_and_histology":
                    if topography_in_group(input_term, rule.get("topography_codes", [])):
                        potentially_relevant = True

            if potentially_relevant:
                fallback = mapping.get("fallback", {})
                cruk_objects = resolve_labels_to_objects(
                    fallback.get("cruk", []) or [], label_key_dict, filter_data
                )
                tcga_objects = resolve_labels_to_objects(
                    fallback.get("tcga", []) or [], label_key_dict, filter_data
                )
                return schema_term, "fallback", cruk_objects, tcga_objects

    return None, None, [], []


# ---------------------------------------------------------------------------
# ICD-O child term collection
# ---------------------------------------------------------------------------

def collect_child_icdo_terms(node):
    """
    Recursively collect descendant ICD-O topography terms from a node's children.
    """
    collected_terms = []

    if not isinstance(node, dict):
        return collected_terms

    children = node.get("children", {})
    if not isinstance(children, dict):
        return collected_terms

    for child in children.values():
        if not isinstance(child, dict):
            continue

        if child.get("primaryGroup") == "cancer-type" and child.get("label", "").startswith("C"):
            collected_terms.append(_extract_node_fields(child))

        collected_terms.extend(collect_child_icdo_terms(child))

    return collected_terms


# ---------------------------------------------------------------------------
# Test case builder
# ---------------------------------------------------------------------------

_HISTOLOGY_EXAMPLES = {
    "UVM": [
        {
            "schema_term_label": "C69 Eye and adnexa",
            "histology": "8720/3 Malignant melanoma, NOS"
        }
    ],
    "SKCM": [
        {
            "schema_term_label": "C44 Skin",
            "histology": "8720/3 Malignant melanoma, NOS"
        }
    ],
    "HNSC": [
        {
            "schema_term_label": "C00 Lip",
            "histology": "8070/3 Squamous cell carcinoma, NOS"
        },
        {
            "schema_term_label": "C32 Larynx",
            "histology": "8070/3 Squamous cell carcinoma, NOS"
        }
    ],
    "LAML": [
        {
            "schema_term_label": "C42 Hematopoietic and reticuloendothelial systems",
            "histology": "9861/3 Acute myeloid leukemia, NOS"
        }
    ],
    "DLBC": [
        {
            "schema_term_label": "C42 Hematopoietic and reticuloendothelial systems",
            "histology": "9680/3 Diffuse large B-cell lymphoma, NOS"
        }
    ],
    "MESO": [
        {
            "schema_term_label": "C38 Heart, mediastinum, and pleura",
            "histology": "9050/3 Mesothelioma, malignant"
        }
    ],
    "SARC": [
        {
            "schema_term_label": "C49 Connective, subcutaneous and other soft tissues",
            "histology": "8800/3 Sarcoma, NOS"
        }
    ],
    "PCPG": [
        {
            "schema_term_label": "C74 Adrenal gland",
            "histology": "8700/3 Pheochromocytoma, NOS"
        }
    ],
    "CHOL": [
        {
            "schema_term_label": "C22 Liver and intrahepatic bile ducts",
            "histology": "8160/3 Cholangiocarcinoma"
        }
    ]
}


def build_complex_test_cases():
    """
    Build a flat list of representative complex test cases using parent
    topography terms and their child ICD-O terms.
    """
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

            parent_term = _extract_node_fields(parent_node)
            child_terms = collect_child_icdo_terms(parent_node)

            for term in [parent_term] + child_terms:
                all_cases.append({
                    "schema_term": schema_term,
                    "term": term,
                    "histology": histology,
                })

    return all_cases

