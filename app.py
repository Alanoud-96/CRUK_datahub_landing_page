from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_MAPPING_DIR = os.path.join(BASE_DIR, "python_mapping")

if PYTHON_MAPPING_DIR not in sys.path:
    sys.path.insert(0, PYTHON_MAPPING_DIR)

from runner import run_runner_pipeline

app = Flask(__name__)
CORS(app)

ICD_O_MORPHOLOGY_PATTERN = re.compile(r"^\d{4}/\d")


def extract_dataset_context(payload):
    dataset_filters = payload.get("datasetFilters", [])

    input_terms = []
    histology = None
    existing_cruk_labels = []
    age_range_max = None

    for item in dataset_filters:
        category = item.get("category")
        label = item.get("label")

        if category == "icdOTopography":
            input_terms.append({
                "id": item.get("id"),
                "label": label,
                "category": category,
                "primaryGroup": item.get("primaryGroup", "cancer-type"),
                "description": item.get("description", "")
            })

        elif (
            category in {"histology", "icdOHistology", "icdOMorphology"}
            or (label and ICD_O_MORPHOLOGY_PATTERN.match(label))
        ) and not histology:
            histology = label

        elif category == "crukTerms" and label and not item.get("isGenerated"):
            existing_cruk_labels.append(label)

    coverage = payload.get("coverage", {})
    age_range_max = coverage.get("typicalAgeRangeMax")

    return input_terms, histology, existing_cruk_labels, age_range_max


def merge_mapping_terms_into_dataset_filters(payload, mapping_result):
    dataset_filters = payload.get("datasetFilters", [])

    existing_ids = {item.get("id") for item in dataset_filters if item.get("id")}
    existing_keys = {
        (
            item.get("category"),
            item.get("label"),
            item.get("primaryGroup")
        )
        for item in dataset_filters
    }

    for result in mapping_result.get("results", []):
        for group_name in ["CRUK", "TCGA"]:
            for item in result.get(group_name, []):
                item_key = (
                    item.get("category"),
                    item.get("label"),
                    item.get("primaryGroup")
                )

                if item.get("id") in existing_ids or item_key in existing_keys:
                    continue

                dataset_filters.append({
                    "id": item.get("id"),
                    "label": item.get("label"),
                    "category": item.get("category"),
                    "primaryGroup": item.get("primaryGroup", "cancer-type"),
                    "description": item.get("description", ""),
                    "isGenerated": True,  # marks auto-mapped terms so special rules ignore them
                })

                if item.get("id"):
                    existing_ids.add(item.get("id"))

                existing_keys.add(item_key)

    payload["datasetFilters"] = dataset_filters
    return payload


@app.route("/run-mapping", methods=["POST"])
def run_mapping():
    try:
        payload = request.json

        if not payload:
            return jsonify({"error": "No JSON payload received"}), 400

        input_terms, histology, existing_cruk_labels, age_range_max = extract_dataset_context(payload)

        if not input_terms:
            return jsonify({"error": "No icdOTopography term found in datasetFilters"}), 400

        mapping_result = run_runner_pipeline(
            input_terms=input_terms,
            histology=histology,
            existing_cruk_labels=existing_cruk_labels,
            age_range_max=age_range_max
        )

        payload["mapping_output"] = mapping_result
        payload = merge_mapping_terms_into_dataset_filters(payload, mapping_result)

        return jsonify(payload)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)