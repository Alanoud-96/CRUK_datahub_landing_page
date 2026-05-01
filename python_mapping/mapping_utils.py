NODE_FIELDS = ("id", "label", "category", "primaryGroup", "description")


def extract_node_fields(node):
    return {field: node.get(field) for field in NODE_FIELDS}


def find_objects_by_labels(data, target_labels):
    matched_objects = []

    def search_node(node):
        if isinstance(node, dict):
            if node.get("label") in target_labels:
                matched_objects.append(extract_node_fields(node))

            for value in node.values():
                search_node(value)

        elif isinstance(node, list):
            for item in node:
                search_node(item)

    search_node(data)
    return matched_objects


def find_object_by_key(data, target_key):
    found_object = None

    def search_node(node):
        nonlocal found_object

        if found_object is not None:
            return

        if isinstance(node, dict):
            for key, value in node.items():
                if key == target_key and isinstance(value, dict):
                    found_object = extract_node_fields(value)
                    return

                search_node(value)

        elif isinstance(node, list):
            for item in node:
                search_node(item)

    search_node(data)
    return found_object


def find_raw_node_by_key(data, target_key):
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
    seen = set()
    unique_items = []

    for item in items:
        item_id = item.get("id")
        if item_id not in seen:
            seen.add(item_id)
            unique_items.append(item)

    return unique_items


def resolve_labels_to_objects(labels, label_key_dict, filter_data):
    if not labels:
        return []

    matched_objects = []

    for label in labels:
        obj = None

        target_key = label_key_dict.get(label)

        if target_key is not None:
            obj = find_object_by_key(filter_data, target_key)

        if obj is None:
            fallback_results = find_objects_by_labels(filter_data, [label])
            if fallback_results:
                obj = fallback_results[0]

        if obj is not None:
            matched_objects.append(obj)

    return deduplicate_by_id(matched_objects)


def collect_child_icdo_terms(node):
    collected_terms = []

    if not isinstance(node, dict):
        return collected_terms

    children = node.get("children", {})
    if not isinstance(children, dict):
        return collected_terms

    for child_value in children.values():
        if not isinstance(child_value, dict):
            continue

        label = child_value.get("label", "")
        primary_group = child_value.get("primaryGroup", "")

        if primary_group == "cancer-type" and label.startswith("C"):
            collected_terms.append(extract_node_fields(child_value))

        collected_terms.extend(collect_child_icdo_terms(child_value))

    return collected_terms