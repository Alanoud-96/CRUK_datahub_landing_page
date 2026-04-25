import argparse
import json
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from mapping_program_simple import get_mapped_terms
from mapping_program_intermediate import get_intermediate_mapped_terms
from mapping_program_complex import get_complex_mapped_terms

try:
    from mapping_program_special import get_special_mapped_terms
    SPECIAL_IMPORT_ERROR = None
except Exception as exc:
    get_special_mapped_terms = None
    SPECIAL_IMPORT_ERROR = str(exc)

try:
    from mapping_program_rare import get_rare_mapped_terms
    RARE_IMPORT_ERROR = None
except Exception as exc:
    get_rare_mapped_terms = None
    RARE_IMPORT_ERROR = str(exc)


# -------------------
# Logging setup
# -------------------
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "runner.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# -------------------
# Generic helpers
# -------------------
def save_json_file(output_path: str, data: Dict[str, Any]) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def has_mapping(cruk_terms: List[Dict[str, Any]], tcga_terms: List[Dict[str, Any]]) -> bool:
    return bool(cruk_terms or tcga_terms)


def deduplicate_strings(items: List[str]) -> List[str]:
    seen = set()
    unique_items = []

    for item in items:
        if item not in seen:
            seen.add(item)
            unique_items.append(item)

    return unique_items


def normalise_string(value: Optional[str]) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()


def ensure_list_of_objects(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        return []

    cleaned = []
    for item in value:
        if isinstance(item, dict):
            cleaned.append(item)

    return cleaned


# -------------------
# Context / validation helpers
# -------------------
def build_dataset_context(
    term: Dict[str, Any],
    histology: Optional[str] = None,
    existing_cruk_labels: Optional[List[str]] = None,
    extra_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    dataset_filters = [
        {
            "id": term.get("id"),
            "label": term.get("label"),
            "category": term.get("category"),
            "primaryGroup": term.get("primaryGroup", "cancer-type"),
            "description": term.get("description", "")
        }
    ]

    if histology:
        dataset_filters.append({
            "id": None,
            "label": histology,
            "category": "histology",
            "primaryGroup": "cancer-type",
            "description": ""
        })

    if existing_cruk_labels:
        for label in existing_cruk_labels:
            dataset_filters.append({
                "id": None,
                "label": label,
                "category": "crukTerms",
                "primaryGroup": "cancer-type",
                "description": "",
                "isGenerated": True,  # pipeline-constructed; must not trigger cruk_label special rules
            })

    return {
        "datasetFilters": dataset_filters,
        "metadata": extra_metadata or {}
    }


def get_topography_label(term: Dict[str, Any]) -> Optional[str]:
    label = term.get("label")
    if isinstance(label, str) and label.startswith("C"):
        return label
    return None


def get_histology_label(histology: Optional[str]) -> Optional[str]:
    if isinstance(histology, str) and histology.strip():
        return histology.strip()
    return histology


def detect_childhood_case(age_range_max: Optional[int]) -> bool:
    return isinstance(age_range_max, int) and age_range_max < 19


def detect_male_keywords(
    topography_label: Optional[str],
    histology_label: Optional[str],
) -> bool:
    # Only inspect anatomical inputs (topography and histology) to determine
    # whether a term is male-specific. Existing CRUK labels are deliberately
    # excluded: they are pipeline outputs, not evidence of male anatomy, and
    # including them caused "Men's cancer" to re-trigger on female datasets
    # when the label was already present from a previous mapping pass.
    #
    # Whole-word matching is required: substring matching would cause
    # "female" and "C51-C58 Female genital organs" to match "male",
    # and "menstrual" to match "men".
    import re
    keywords = [r"\bmale\b", r"\bman\b", r"\bmen\b"]

    searchable_values = [
        normalise_string(topography_label).lower(),
        normalise_string(histology_label).lower()
    ]

    return any(
        re.search(keyword, value)
        for value in searchable_values
        for keyword in keywords
    )


def validate_histology_for_deeper_levels(
    remaining_terms: List[Dict[str, Any]],
    histology_label: Optional[str],
    encountered_problems: List[str]
) -> None:
    if remaining_terms and not histology_label:
        problem = (
            "No histology string was provided for term(s) that were not resolved at simple level. "
            "Histology-dependent mapping levels may fail or be incomplete."
        )
        encountered_problems.append(problem)
        logger.warning(problem)


# -------------------
# Mapping response helpers
# -------------------
def unpack_mapping_response(
    response: Any
) -> Tuple[Optional[str], Optional[str], List[Dict[str, Any]], List[Dict[str, Any]]]:
    if not isinstance(response, tuple):
        return None, None, [], []

    if len(response) == 3:
        matched_term, cruk_terms, tcga_terms = response
        return matched_term, None, ensure_list_of_objects(cruk_terms), ensure_list_of_objects(tcga_terms)

    if len(response) == 4:
        matched_term, matched_rule, cruk_terms, tcga_terms = response
        return matched_term, None, ensure_list_of_objects(cruk_terms), ensure_list_of_objects(tcga_terms)

    return None, None, [], []


# -------------------
# Stage execution helper
# -------------------
def run_mapping_stage(
    stage_name: str,
    remaining_terms: List[Dict[str, Any]],
    mapper_fn: Optional[Callable[..., Any]],
    histology_label: Optional[str],
    existing_cruk_labels: Optional[List[str]],
    extra_metadata: Optional[Dict[str, Any]],
    mapper_mode: str
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    logger.info("Running %s mapping on %d remaining terms", stage_name.upper(), len(remaining_terms))

    if mapper_fn is None:
        if stage_name == "special":
            logger.warning(
                "%s mapping function is not available; skipping stage. Import error: %s",
                stage_name.upper(),
                SPECIAL_IMPORT_ERROR
            )
        elif stage_name == "rare":
            logger.warning(
                "%s mapping function is not available; skipping stage. Import error: %s",
                stage_name.upper(),
                RARE_IMPORT_ERROR
            )
        else:
            logger.warning("%s mapping function is not available; skipping stage.", stage_name.upper())

        return [], remaining_terms

    results = []
    next_remaining = []

    for term in remaining_terms:
        topography_label = get_topography_label(term)

        try:
            if mapper_mode == "term_only":
                response = mapper_fn(term)

            elif mapper_mode == "term_and_histology":
                response = mapper_fn(term, histology_label)

            elif mapper_mode == "dataset_context":
                dataset_context = build_dataset_context(
                    term=term,
                    histology=histology_label,
                    existing_cruk_labels=existing_cruk_labels,
                    extra_metadata=extra_metadata
                )
                response = mapper_fn(dataset_context)

            else:
                raise ValueError(f"Unsupported mapper_mode: {mapper_mode}")

            matched_term, matched_rule, cruk_terms, tcga_terms = unpack_mapping_response(response)

            if has_mapping(cruk_terms, tcga_terms):
                logger.info("Matched in %s: %s", stage_name.upper(), term.get("label"))

                result_record = {
                    "input_term": term,
                    "topography_label": topography_label,
                    "histology_label": histology_label,
                    "matched_level": stage_name,
                    "matched_schema_term": matched_term,
                    "matched_rule": matched_rule,
                    "CRUK": cruk_terms,
                    "TCGA": tcga_terms
                }

                results.append(result_record)
            else:
                next_remaining.append(term)

        except Exception:
            logger.exception(
                "Error while running %s mapping for term: %s",
                stage_name.upper(),
                term.get("label")
            )
            next_remaining.append(term)

    return results, next_remaining


# -------------------
# Main runner pipeline
# -------------------
def run_runner_pipeline(
    input_terms: List[Dict[str, Any]],
    histology: Optional[str] = None,
    existing_cruk_labels: Optional[List[str]] = None,
    age_range_max: Optional[int] = None,
    extra_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    results = []
    remaining_terms = list(input_terms)
    encountered_problems = []

    histology_label = get_histology_label(histology)
    childhood_case_detected = detect_childhood_case(age_range_max)

    if existing_cruk_labels is None:
        existing_cruk_labels = []

    if childhood_case_detected and "Children's cancers" not in existing_cruk_labels:
        existing_cruk_labels.append("Children's cancers")

    male_case_detected = any(
        detect_male_keywords(
            topography_label=get_topography_label(term),
            histology_label=histology_label,
        )
        for term in input_terms
    )

    if male_case_detected and "Men's cancer" not in existing_cruk_labels:
        existing_cruk_labels.append("Men's cancer")

    logger.info("Starting runner pipeline")
    logger.info("Number of input terms: %d", len(input_terms))
    logger.info("Histology label: %s", histology_label)
    logger.info("Existing CRUK labels: %s", existing_cruk_labels)
    logger.info("AgeRangeMax: %s", age_range_max)
    logger.info("Childhood case detected: %s", childhood_case_detected)
    logger.info("Male-specific case detected: %s", male_case_detected)

    # 1. SIMPLE
    stage_results, remaining_terms = run_mapping_stage(
        stage_name="simple",
        remaining_terms=remaining_terms,
        mapper_fn=get_mapped_terms,
        histology_label=histology_label,
        existing_cruk_labels=existing_cruk_labels,
        extra_metadata=extra_metadata,
        mapper_mode="term_only"
    )
    results.extend(stage_results)

    validate_histology_for_deeper_levels(remaining_terms, histology_label, encountered_problems)

    # 2. INTERMEDIATE
    stage_results, remaining_terms = run_mapping_stage(
        stage_name="intermediate",
        remaining_terms=remaining_terms,
        mapper_fn=get_intermediate_mapped_terms,
        histology_label=histology_label,
        existing_cruk_labels=existing_cruk_labels,
        extra_metadata=extra_metadata,
        mapper_mode="term_and_histology"
    )
    results.extend(stage_results)

    # 3. COMPLEX
    stage_results, remaining_terms = run_mapping_stage(
        stage_name="complex",
        remaining_terms=remaining_terms,
        mapper_fn=get_complex_mapped_terms,
        histology_label=histology_label,
        existing_cruk_labels=existing_cruk_labels,
        extra_metadata=extra_metadata,
        mapper_mode="term_and_histology"
    )
    results.extend(stage_results)

    # 4. SPECIAL
    stage_results, remaining_terms = run_mapping_stage(
        stage_name="special",
        remaining_terms=remaining_terms,
        mapper_fn=get_special_mapped_terms,
        histology_label=histology_label,
        existing_cruk_labels=existing_cruk_labels,
        extra_metadata=extra_metadata,
        mapper_mode="dataset_context"
    )
    results.extend(stage_results)

    # 5. RARE
    stage_results, remaining_terms = run_mapping_stage(
        stage_name="rare",
        remaining_terms=remaining_terms,
        mapper_fn=get_rare_mapped_terms,
        histology_label=histology_label,
        existing_cruk_labels=existing_cruk_labels,
        extra_metadata=extra_metadata,
        mapper_mode="dataset_context"
    )
    results.extend(stage_results)

    if remaining_terms:
        problem = (
            f"{len(remaining_terms)} term(s) remained unmatched after simple, intermediate, "
            f"complex, special, and rare."
        )
        encountered_problems.append(problem)
        logger.warning(problem)

        for term in remaining_terms:
            logger.info("Unmatched term: %s", term.get("label"))

    logger.info("Runner pipeline finished")

    return {
        "topography_labels": [get_topography_label(term) for term in input_terms],
        "histology_label": histology_label,
        "existing_cruk_labels": existing_cruk_labels,
        "age_range_max": age_range_max,
        "childhood_case_detected": childhood_case_detected,
        "male_case_detected": male_case_detected,
        "results": results,
        "unmatched": remaining_terms,
        "encountered_problems": deduplicate_strings(encountered_problems)
    }


# -------------------
# CLI
# -------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run simple -> intermediate -> complex -> special -> rare mapping pipeline."
    )

    parser.add_argument(
        "--label",
        required=True,
        help='ICD-O topography label, e.g. "C64 Kidney"'
    )
    parser.add_argument(
        "--category",
        default="icdOTopography",
        help='Input term category (default: "icdOTopography")'
    )
    parser.add_argument(
        "--histology",
        default=None,
        help='Optional histology string, e.g. "8312/3 Renal cell carcinoma, NOS"'
    )
    parser.add_argument(
        "--existing-cruk-label",
        action="append",
        default=[],
        help='Optional existing CRUK label(s). Can be repeated.'
    )
    parser.add_argument(
        "--age-range-max",
        type=int,
        default=None,
        help="Optional AgeRangeMax value for childhood cancer detection."
    )
    parser.add_argument(
        "--output",
        default=None,
        help='Optional output JSON file path, e.g. "outputs/runner_output.json"'
    )

    args = parser.parse_args()

    input_term = {
        "id": None,
        "label": args.label,
        "category": args.category,
        "primaryGroup": "cancer-type",
        "description": ""
    }

    output_data = run_runner_pipeline(
        input_terms=[input_term],
        histology=args.histology,
        existing_cruk_labels=args.existing_cruk_label,
        age_range_max=args.age_range_max
    )

    if args.output:
        save_json_file(args.output, output_data)
        logger.info("Saved output to %s", args.output)
    else:
        print(json.dumps(output_data, indent=2, ensure_ascii=False))