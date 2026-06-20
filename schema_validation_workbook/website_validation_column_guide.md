# Website Validation Table: Column Guide

This document explains the columns used in `website_validation_table.csv`. The validation table was used to record website-level testing for the ICD-O to CRUK/TCGA mapping workflow.

## Test ID

The `Test ID` identifies each validation case. The prefix indicates the type of test being performed:

* **HIST**: Initial histology/topography validation tests. These were used to check whether selected ICD-O topography and histology terms returned the expected schema, CRUK label, and TCGA output.
* **FIX**: Retesting after a fix. These cases were repeated after backend or schema changes to check whether previous issues had been resolved.
* **STRESS**: Stress-testing cases. These were designed to test more difficult or unusual mapping situations and check whether the mapping logic remained stable.
* **EDGE**: Edge-case and unusual histology tests. These focused on unusual, rare, or ambiguous histology combinations that may need closer review.
* **LIMIT**: Known limitation testing. These cases were used to document behaviour that reflects a known limitation of the current mapping structure.
* **TOPO** : Topography-only validation tests. These cases check whether selected ICD-O topography terms return the expected CRUK and/or TCGA labels when no histology term is provided.
* **RARE: Rare cancer validation tests**. These cases check whether rare topography terms are handled correctly by the rare cancer mapping logic.


## Validation Section

The `Validation Section` column groups the tests according to the stage or purpose of validation:

* **Initial validation**: The first round of validation tests, used to compare the website/backend output against the expected mapping result.
* **Retest after fix**: Tests repeated after backend or schema changes to confirm whether the issue was fixed.
* **Stress testing**: Additional tests using more difficult cases to check the robustness of the mapping logic.
* **Edge-case and unusual histology testing**: Tests focused on unusual histology terms or unusual site-histology combinations.
* **Known limitation testing**: Tests used to document behaviour that is understood as a limitation rather than a simple error.

* **Additional validation** : Extra validation cases added after the main validation set. These include topography-only checks and rare cancer checks used to clarify mapping behaviour when histology is not provided.

## Test Category

The `Test Category` column describes the specific purpose of each validation test:

* **Histology override validation**: Checks whether a histology-specific rule correctly overrides a broader or default topography mapping.
* **Baseline mapping validation**: Checks whether standard/simple mapping works correctly for expected cases.
* **Histology validation**: Checks whether the selected histology term is recognised and handled correctly.
* **Complex site-histology validation**: Tests mappings that depend on both site and histology together, rather than topography alone.
* **Sex-specific mapping validation**: Checks mappings for sex-specific cancer sites, such as prostate, ovary, cervix, or corpus uteri.
* **Rare mapping validation**: Checks whether rare cancer mappings are handled as expected.
* **Umbrella mapping validation**: Checks whether broader parent/umbrella terms are being used in the mapping and whether this affects the output.
* **Backend fix retest**: Repeats a test after a backend change to confirm whether the backend behaviour has improved.
* **Schema fix retest**: Repeats a test after a schema change to confirm whether the mapping rule now works correctly.
* **Unusual histology stress test**: Tests unusual histology terms to see whether they cause incorrect or unexpected outputs.
* **False-positive TCGA check**: Checks whether the mapping returns a TCGA code when it should not, or returns an overly broad TCGA output.
* **Subtype variation stress test**: Tests different histology subtypes within a similar cancer group to check whether subtype-specific outputs are handled correctly.
* **Same-site histology variation test**: Tests different histologies for the same ICD-O topography site to compare how the mapping changes.
* **Non-melanoma skin validation**: Checks skin cancer mappings that should not be treated as melanoma or SKCM.
* **Sarcoma mapping stress test**: Tests sarcoma-related site-histology combinations, especially where multiple sarcoma rules may overlap.
* **Unusual histology validation**: Checks whether unusual histology inputs are recognised and mapped appropriately.
* **Unusual histology review**: Marks unusual histology cases that may need closer manual review.
* **Schema hierarchy limitation**: Documents cases where the schema hierarchy affects the output and may limit more specific mapping.
* **Schema priority retest**: Repeats a test after changing schema priority order to check whether the correct schema is now selected.
* **Positive baseline mapping validation**: Confirms that a straightforward expected mapping returns the correct output.
* **Negative complex-rule validation**: Checks that complex rules do not incorrectly trigger for cases where they should not apply.
* **TCGA-empty validation**: Checks cases where a CRUK label may be returned, but no TCGA output is expected.
* **Schema rule collision review**: Reviews cases where more than one schema rule may overlap or compete.
* **Special mapping review**: Reviews cases handled by special-case mapping logic.
* **Gynaecological site-histology review**: Reviews mappings for gynaecological sites where site and histology combinations may affect the expected output.

* **Topography-only validation** : Checks whether selected ICD-O topography terms can return the expected mapping output without requiring an ICD-O histology term. These tests help confirm which mappings are based on topography alone.

* **Rare topography-only validation** : Checks whether rare cancer topography terms resolve to the expected rare cancer output when no histology term is provided. A no-histology warning may appear in these cases because the test intentionally omits histology.

## Input ICD-O Topography

The `Input ICD-O Topography` column records the ICD-O topography term used as the input in the website validation test.

## Input ICD-O Histology

The `Input ICD-O Histology` column records the ICD-O histology term selected during the test. This helps show whether the mapping is using the correct histology-specific rule.

## Expected Schema

The `Expected Schema` column records the schema that was expected to handle the mapping, such as simple, intermediate, complex, rare, special, or umbrella.

## Expected CRUK Label

The `Expected CRUK Label` column records the CRUK cancer label that was expected to be returned by the mapping.

## Expected TCGA Code

The `Expected TCGA Code` column records the TCGA code that was expected for the selected ICD-O topography and histology combination. If no TCGA output was expected, this may be left blank or noted accordingly.

## Observed Output

The `Observed Output` column records the actual output returned by the website or backend during the validation test.

## Validation Outcome

The `Validation Outcome` column records whether the test passed, failed, partially passed, or required review based on the comparison between the expected output and the observed output.

## Remarks

The `Remarks` column provides a short interpretation of the result. It explains why the test was marked as Pass, Fail, Partial Pass, or Under Review, and notes any mapping behaviour that may need further investigation.

## Resolution

The `Resolution` column records the current status of the issue or test case, such as whether it has been fixed, remains unresolved, or needs further review.

## Histology Coverage Note

The validation table includes 101 test cases with histology inputs, covering 40 unique ICD-O histology terms without duplicates.
