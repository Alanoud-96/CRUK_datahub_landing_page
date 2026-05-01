# Filter README

This document explains the filter categories used by the mapping program.

## Main categories

### icdOTopography
This category contains ICD-O topography terms. These describe the anatomical site of the cancer.

Example:
`C64 Kidney`

### icdOHistology / icdOMorphology / histology
These categories contain ICD-O morphology or histology information. These describe the tumour type or cell type.

Example:
`8312/3 Renal cell carcinoma`

### crukTerms
This category contains CRUK cancer terms returned by the mapping program.

Example:
`Kidney cancer`

### cancerTypes
This category contains cancer type filter objects from the filter data. Some TCGA-like labels may appear under this category depending on the source filter data.

Example:
`KIRC (Kidney renal clear cell carcinoma)`

## Output fields

Each mapped output object keeps the standard filter fields:

- `id`
- `label`
- `category`
- `primaryGroup`
- `description`

## Generated labels

Some labels may be added by the pipeline, for example:

- `Children's cancers`
- `Men's cancer`

These may include:

```json
"isGenerated": true
```

This means the label was added by the mapping pipeline and was not originally selected by the user.

## Mapping pipeline

The mapping is performed in stages using the runner:

1. simple mapping  
2. intermediate mapping  
3. complex mapping  
4. special mapping  
5. rare mapping  

Each stage only runs if the term was not matched in the previous stage.

## Runner

The mapping process is controlled by a main runner script:

```bash
python3 python_mapping/runner.py
```

## Mapping priority

The pipeline follows a priority order.

For example:
- simple mapping is attempted first
- if no match is found, intermediate is used
- and so on until rare mapping

This ensures the simplest and most accurate mapping is used where possible.

## Logging

The runner generates log files in the `logs/` folder.

These logs show:
- which mapping stage was used
- which terms were matched
- and the overall pipeline process

## Test cases

Test case builders are located in:

```text
test_cases/
```