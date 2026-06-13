

# Website Validation Notes

This file documents the validation work carried out for the ICD-O to CRUK/TCGA mapping website. The purpose of these notes is to explain how the website was tested, what issues were found, what fixes were applied, and how the tests were repeated after the fixes.

The validation tests assess whether the website correctly applies the mapping schemas by checking three main points:

1. Whether the selected ICD-O topography and histology inputs are passed correctly from the website to the Python mapping pipeline.
2. Whether the correct mapping schema level is triggered, including simple, intermediate, complex, special, rare, and umbrella mapping rules.
3. Whether the expected CRUK and TCGA outputs are generated.
The main validation results are summarised in website_validation_table.csv. This notes file provides the supporting explanation for those results, including the reasoning behind failed tests, partial passes, review cases, and fixes made during development.
The validation process included:
* Initial validation tests for common and schema-specific mappings.
* Investigation of parent/child topography handling issues.
* Direct runner checks to compare website behaviour with command-line mapping behaviour.
* Backend fixes in app.py.
* Schema fixes where specific histology codes were missing.
* Retesting after backend and schema fixes.
* Stress tests using unusual histology combinations and false-positive TCGA checks.
* Edge-case tests for rare, unusual, or biologically challenging site-histology combinations.
Overall, the validation showed that many early failures were caused by backend input preparation, where the website sometimes passed broader parent or umbrella ICD-O topography terms instead of the selected child topography term. After updating app.py, the selected child topography terms were passed correctly and several mappings were successfully retested. Further schema-level fixes were then applied where specific histology codes were missing from the relevant mapping rules.
Notes structure
The notes below are organised into the following sections:
1. Initial validation tests
2. Overall validation finding
3. Direct runner checks
4. Backend fix and retesting
5. Schema fixes and retesting
6. Additional stress testing
7. Edge-case and unusual histology testing
8. Remaining review cases and limitations

------------

### HIST-001: Kidney + chromophobe histology

Input tested:

* Topography: C64 Kidney
* Histology: 8317/3 Renal cell carcinoma, chromophobe type

Expected behaviour:

* The intermediate schema should return Kidney cancer.
* The intermediate schema should return TCGA KICH.

Observed behaviour:

* The histology term was found and added as a tag.
* Kidney cancer was generated.
* KICH was not returned.
* TCGA output was empty.
* When the parent C64-C68 Urinary tract tag was removed and only C64 Kidney was left, the website showed “Failed to run Python mapping”.
* The Flask backend showed POST /run-mapping 400.

Conclusion:
The kidney CRUK mapping worked, and the chromophobe histology term was available in the website. However, the histology-based TCGA override for KICH was not applied. The failure after removing the parent topography tag suggests that the website/backend may not currently handle child-only topography terms correctly.

---

### HIST-002: Kidney + clear cell histology

Input tested:

* Topography: C64 Kidney
* Histology: 8310/3 Clear cell adenocarcinoma, NOS

Expected behaviour:

* The intermediate schema should return Kidney cancer.
* The intermediate schema should return TCGA KIRC.

Observed behaviour:

* The histology term was found and added as a tag.
* Kidney cancer was generated.
* KIRC was not returned.
* TCGA output was empty.
* The downloaded JSON showed that C64 Kidney and the clear cell histology term were both present in the dataset filters.
* However, the mapping output used C64-C68 Urinary tract as the input term and matched the simple schema.

Conclusion:
The clear cell histology term was available and selected correctly, but the kidney-specific TCGA override for KIRC was not applied. The likely issue is that the mapping step used the parent C64-C68 Urinary tract term instead of the selected child term C64 Kidney.

---

### HIST-003: Kidney + papillary histology

Input tested:

* Topography: C64 Kidney
* Histology: 8260/3 Papillary adenocarcinoma, NOS

Expected behaviour:

* The intermediate schema should return Kidney cancer.
* The intermediate schema should return TCGA KIRP.

Observed behaviour:

* The histology term was found and added as a tag.
* Kidney cancer was generated.
* KIRP was not returned.
* TCGA output was empty.
* The downloaded JSON showed that C64 Kidney and the papillary histology term were both present in the dataset filters.
* However, the mapping output used C64-C68 Urinary tract as the input term and matched the simple schema.

Conclusion:
The papillary histology term was available and selected correctly, but the kidney-specific TCGA override for KIRP was not applied. This appears to be the same issue observed for KICH and KIRC: the website/backend is using the parent C64-C68 Urinary tract mapping rather than applying the child-specific kidney histology override.
------------

## Breast histology validation :

These tests assessed whether C50 Breast returns the expected CRUK and TCGA outputs when different breast-related histology terms are selected. The expected behaviour was that the website would generate Breast cancer as the CRUK term and BRCA (Breast invasive carcinoma) as the TCGA term.

Overall, the breast histology tests passed. In each case, the selected histology term was found in the website and added as a tag. The mapping output used C50 Breast as the input topography term, and both Breast cancer and BRCA were generated correctly.

---

### HIST-004: Breast + infiltrating duct carcinoma

Input tested:

* Topography: C50 Breast
* Histology: 8500/3 Infiltrating duct carcinoma, NOS

Expected behaviour:

* The mapping should return Breast cancer.
* The mapping should return TCGA BRCA.

Observed behaviour:

* The histology term was found and added as a tag.
* Breast cancer was generated.
* BRCA was generated.
* The mapping output used C50 Breast as the input term.

Conclusion:
This test passed. It confirms that TCGA output can be generated through the website for C50 Breast.

---

### HIST-005: Breast + lobular carcinoma

Input tested:

* Topography: C50 Breast
* Histology: 8520/3 Lobular carcinoma, NOS

Expected behaviour:

* The mapping should return Breast cancer.
* The mapping should return TCGA BRCA.

Observed behaviour:

* The histology term was found and added as a tag.
* Breast cancer was generated.
* BRCA was generated.
* The mapping output used C50 Breast as the input term.

Conclusion:
This test passed. The lobular carcinoma histology term did not prevent the expected Breast cancer and BRCA outputs from being generated.

---

### HIST-006: Breast + infiltrating duct and lobular carcinoma

Input tested:

* Topography: C50 Breast
* Histology: 8522/3 Infiltrating duct and lobular carcinoma

Expected behaviour:

* The mapping should return Breast cancer.
* The mapping should return TCGA BRCA.

Observed behaviour:

* The histology term was found and added as a tag.
* Breast cancer was generated.
* BRCA was generated.
* The mapping output used C50 Breast as the input term.

Conclusion:
This test passed. The website correctly generated the expected CRUK and TCGA outputs for a mixed ductal and lobular breast histology term.

---

### HIST-007: Breast + mucinous adenocarcinoma

Input tested:

* Topography: C50 Breast
* Histology: 8480/3 Mucinous adenocarcinoma

Expected behaviour:

* The mapping should return Breast cancer.
* The mapping should return TCGA BRCA.

Observed behaviour:

* The histology term was found and added as a tag.
* Breast cancer was generated.
* BRCA was generated.
* The mapping output used C50 Breast as the input term.

Conclusion:
This test passed. Searching by the histology name without typing the code still allowed the correct coded histology term, 8480/3 Mucinous adenocarcinoma, to be selected.

---

### HIST-008: Breast + intraductal papillary adenocarcinoma with invasion

Input tested:

* Topography: C50 Breast
* Histology: 8503/3 Intraductal papillary adenocarcinoma with invasion

Expected behaviour:

* The mapping should return Breast cancer.
* The mapping should return TCGA BRCA.

Observed behaviour:

* The histology term was found and added as a tag.
* Breast cancer was generated.
* BRCA was generated.
* The mapping output used C50 Breast as the input term.

Conclusion:
This test passed. The website correctly generated the expected Breast cancer and BRCA outputs for this breast histology term.

---

### Summary of breast histology tests

The breast histology tests show that TCGA outputs can be generated correctly through the website. This is important because it suggests that the kidney issue is not a general TCGA-generation problem. Instead, the kidney problem appears to be more specifically related to how the website/backend handles the C64 Kidney child topography under the C64-C68 Urinary tract parent.


------------------------







-----------------
## Lung histology validation

These tests assessed whether C34 Bronchus and lung produces lung-specific CRUK and TCGA outputs when different lung-associated histology terms are selected. The expected behaviour was that the website/backend would use the selected child topography term, C34 Bronchus and lung, together with the selected histology term.

For LUAD and LUSC-related histologies, a TCGA output was expected. For small cell carcinoma and large cell carcinoma, a specific TCGA output was not necessarily expected, but the mapping was still expected to remain lung-specific rather than using the broader respiratory system parent term.

---

### HIST-009: Lung + adenocarcinoma

Input tested:

* Topography: C34 Bronchus and lung
* Histology: 8140/3 Adenocarcinoma, NOS

Expected behaviour:

* The mapping should return Lung cancer.
* The mapping should return TCGA LUAD.

Observed behaviour:

* The histology term was found and added as a tag.
* LUAD was not returned.
* TCGA output was empty.
* The downloaded JSON showed that C34 Bronchus and lung and 8140/3 Adenocarcinoma, NOS were both present in the dataset filters.
* However, the mapping output used C30-C39 Respiratory system and intrathoracic organs as the input term.
* The mapping matched the umbrella schema rather than a lung-specific mapping.
* Multiple broad respiratory CRUK terms were generated, including Lung cancer but also other respiratory system terms.

Conclusion:
The lung adenocarcinoma histology term was available and selected correctly, but the lung-specific TCGA override for LUAD was not applied. This appears to be caused by the mapping using the parent/umbrella topography term instead of C34 Bronchus and lung.

---

### HIST-010: Lung + squamous cell carcinoma

Input tested:

* Topography: C34 Bronchus and lung
* Histology: 8070/3 Squamous cell carcinoma, NOS

Expected behaviour:

* The mapping should return Lung cancer.
* The mapping should return TCGA LUSC.

Observed behaviour:

* The histology term was found and added as a tag.
* LUSC was not returned.
* TCGA output was empty.
* The downloaded JSON showed that C34 Bronchus and lung and 8070/3 Squamous cell carcinoma, NOS were both present in the dataset filters.
* However, the mapping output used C30-C39 Respiratory system and intrathoracic organs as the input term.
* The mapping matched the umbrella schema and returned broad respiratory CRUK terms.

Conclusion:
The squamous cell carcinoma histology term was available and selected correctly, but the lung-specific TCGA override for LUSC was not applied. This supports the same parent/child topography issue observed in the LUAD test.

---

### HIST-011: Lung + small cell carcinoma

Input tested:

* Topography: C34 Bronchus and lung
* Histology: 8041/3 Small cell carcinoma, NOS

Expected behaviour:

* The mapping should return Lung cancer.
* A specific TCGA output was not necessarily expected for this histology, but the mapping should remain lung-specific.

Observed behaviour:

* The histology term was found and added as a tag.
* TCGA output was empty.
* The downloaded JSON showed that C34 Bronchus and lung and 8041/3 Small cell carcinoma, NOS were both present in the dataset filters.
* However, the mapping output used C30-C39 Respiratory system and intrathoracic organs as the input term.
* The mapping matched the umbrella schema and returned broad respiratory CRUK terms rather than only lung-specific mapping.

Conclusion:
Although a TCGA output was not necessarily expected for small cell carcinoma, the mapping still appeared problematic because it used the respiratory system parent term rather than C34 Bronchus and lung.

---

### HIST-012: Lung + large cell carcinoma

Input tested:

* Topography: C34 Bronchus and lung
* Histology: 8012/3 Large cell carcinoma, NOS

Expected behaviour:

* The mapping should return Lung cancer.
* A specific TCGA output was not necessarily expected for this histology, but the mapping should remain lung-specific.

Observed behaviour:

* The histology term was found and added as a tag.
* TCGA output was empty.
* The downloaded JSON showed that C34 Bronchus and lung and 8012/3 Large cell carcinoma, NOS were both present in the dataset filters.
* However, the mapping output used C30-C39 Respiratory system and intrathoracic organs as the input term.
* The mapping matched the umbrella schema and returned broad respiratory CRUK terms.

Conclusion:
Although a TCGA output was not necessarily expected for large cell carcinoma, the mapping still appeared to use the broader respiratory parent term instead of the selected lung child term. This repeated the same parent/child topography issue seen in the other lung tests.

---

### Summary of lung histology tests

The lung histology tests showed a similar issue to the kidney histology tests. In each case, C34 Bronchus and lung and the selected histology term were present in the dataset filters. However, the mapping output used the parent/umbrella topography term C30-C39 Respiratory system and intrathoracic organs as the input term.

As a result, the mapping matched the umbrella schema and generated broad respiratory CRUK terms rather than applying a lung-specific mapping. For adenocarcinoma and squamous cell carcinoma, this prevented the expected TCGA outputs LUAD and LUSC from being generated.

This suggests that the issue is not limited to kidney. It may affect child topography terms where the website also includes a parent or umbrella topography term.

--------------------------
## Digestive histology validation

The colon and rectum tests showed the same parent/child topography issue observed in the kidney and lung tests. Although C18 Colon or C20 Rectum and the selected histology term were present in the dataset filters, the mapping output used the parent term C15-C26 Digestive organs as the input term.

As a result, the mapping matched the umbrella schema and generated broad digestive CRUK terms rather than applying colon-specific or rectum-specific mapping. This prevented the expected TCGA outputs COAD and READ from being generated.
---------------

## Skin melanoma histology validation

These tests assessed whether C44 Skin with melanoma-related histology terms generates the expected skin/melanoma CRUK and TCGA outputs. The expected behaviour was that melanoma histology terms would map to a skin cancer or melanoma-related CRUK term and TCGA SKCM.

Overall, the selected topography and histology terms were found and added as tags. Unlike the kidney, lung, and digestive tests, the mapping output used the correct topography term, C44 Skin. However, the TCGA output list was empty in all three tests.

The important observation is that SKCM was not completely absent from the mapping output. Instead, the mapping output showed `matched_schema_term: SKCM`, with `matched_level: complex` and `matched_rule: fallback`. This suggests that the mapping logic identified SKCM internally, but did not convert it into a generated TCGA filter object in the final TCGA output list.

---

### HIST-015: Skin + malignant melanoma

Input tested:
- Topography: C44 Skin
- Histology: 8720/3 Malignant melanoma, NOS

Expected behaviour:
- The mapping should return a skin cancer or melanoma-related CRUK term.
- The mapping should return TCGA SKCM.

Observed behaviour:
- The histology term was found and added as a tag.
- The mapping returned the broader CRUK term Skin cancer.
- The mapping output used C44 Skin as the input term.
- The mapping output showed `matched_schema_term: SKCM`.
- The TCGA output list was empty.

Conclusion:
The melanoma histology was recognised, and SKCM was identified internally as the matched schema term. However, SKCM was not added to the final TCGA output list.

---

### HIST-016: Skin + nodular melanoma

Input tested:
- Topography: C44 Skin
- Histology: 8721/3 Nodular melanoma

Expected behaviour:
- The mapping should return a skin cancer or melanoma-related CRUK term.
- The mapping should return TCGA SKCM.

Observed behaviour:
- The histology term was found and added as a tag.
- The mapping returned the broader CRUK term Skin cancer.
- The mapping output used C44 Skin as the input term.
- The mapping output showed `matched_schema_term: SKCM`.
- The TCGA output list was empty.

Conclusion:
The nodular melanoma histology was recognised, and SKCM was identified internally as the matched schema term. However, SKCM was not added to the final TCGA output list.

---

### HIST-017: Skin + low cumulative sun damage melanoma

Input tested:
- Topography: C44 Skin
- Histology: 8743/3 Low cumulative sun damage melanoma

Expected behaviour:
- The mapping should return a skin cancer or melanoma-related CRUK term.
- The mapping should return TCGA SKCM.

Observed behaviour:
- The histology term was found and added as a tag.
- The mapping returned the broader CRUK term Skin cancer.
- The mapping output used C44 Skin as the input term.
- The mapping output showed `matched_schema_term: SKCM`.
- The TCGA output list was empty.
- The website label differed from the originally searched term “superficial spreading melanoma”.

Conclusion:
The melanoma-related histology was recognised, and SKCM was identified internally as the matched schema term. However, SKCM was not added to the final TCGA output list. This repeats the same complex/fallback output issue seen in the other skin melanoma tests.

---

### Summary of skin melanoma tests

The skin melanoma tests show a different issue from the kidney, lung, and digestive parent/child topography problem. For skin, the correct topography term C44 Skin was used. However, although SKCM was identified as the `matched_schema_term`, the final TCGA output list remained empty.

This suggests a possible issue in the complex/fallback mapping output, where the mapping identifies the correct TCGA schema term internally but does not convert it into a generated TCGA filter object.
--------

## Brain histology validation

These tests assessed whether C71 Brain generates brain-specific CRUK and TCGA outputs when glioma-related histology terms are selected. The expected behaviour was that the website/backend would use the selected child topography term, C71 Brain, together with the selected glioma histology term.

---

### HIST-018: Brain + glioblastoma

Input tested:
- Topography: C71 Brain
- Histology: 9440/3 Glioblastoma, NOS

Expected behaviour:
- The mapping should return Brain tumours.
- The mapping should return TCGA GBM.

Observed behaviour:
- The histology term was found and added as a tag.
- GBM was not returned.
- TCGA output was empty.
- The downloaded JSON showed that C71 Brain and 9440/3 Glioblastoma, NOS were both present in the dataset filters.
- However, the mapping output used C69-C72 Eye, brain and other parts of central nervous system as the input term.
- The mapping matched the umbrella schema and returned broad CNS CRUK terms: Eye cancer, Brain tumours, and Spinal cord tumours.

Conclusion:
The glioblastoma histology term was available and selected correctly, but the brain-specific TCGA output GBM was not generated. This appears to be another example of the parent/child topography issue.

---

### HIST-019: Brain + astrocytoma

Input tested:
- Topography: C71 Brain
- Histology: 9400/3 Astrocytoma, NOS

Expected behaviour:
- The mapping should return Brain tumours.
- A brain-specific TCGA output such as LGG or GBM may be expected depending on the schema logic.

Observed behaviour:
- The histology term was found and added as a tag.
- No brain-specific TCGA output was returned.
- TCGA output was empty.
- The downloaded JSON showed that C71 Brain and 9400/3 Astrocytoma, NOS were both present in the dataset filters.
- However, the mapping output used C69-C72 Eye, brain and other parts of central nervous system as the input term.
- The mapping matched the umbrella schema and returned broad CNS CRUK terms.

Conclusion:
The astrocytoma histology term was available and selected correctly, but the mapping did not remain brain-specific. Instead, it used the CNS umbrella parent term.

---

### HIST-020: Brain + oligodendroglioma

Input tested:
- Topography: C71 Brain
- Histology: 9450/3 Oligodendroglioma, NOS

Expected behaviour:
- The mapping should return Brain tumours.
- The mapping should return TCGA LGG.

Observed behaviour:
- The histology term was found and added as a tag.
- LGG was not returned.
- TCGA output was empty.
- The downloaded JSON showed that C71 Brain and 9450/3 Oligodendroglioma, NOS were both present in the dataset filters.
- However, the mapping output used C69-C72 Eye, brain and other parts of central nervous system as the input term.
- The mapping matched the umbrella schema and returned broad CNS CRUK terms.

Conclusion:
The oligodendroglioma histology term was available and selected correctly, but the expected brain-specific TCGA output LGG was not generated. This repeats the same parent/child topography issue observed in kidney, lung, digestive, and CNS tests.

---

### Summary of brain histology tests

The brain histology tests showed the same parent/child topography issue observed in several other groups. Although C71 Brain and the selected glioma histology terms were present in the dataset filters, the mapping output used the parent/umbrella term C69-C72 Eye, brain and other parts of central nervous system as the input term.

As a result, the mapping matched the umbrella schema and generated broad CNS CRUK terms rather than applying brain-specific histology mapping or generating TCGA outputs such as GBM or LGG.
----------
## Special, rare, bone, and sarcoma validation

These tests assessed special sex-specific mappings, rare cancer fallback behaviour, and sarcoma/bone-related mappings. The aim was to check whether the website/backend correctly handles special mapping rules and whether rare or sarcoma-related cases return the expected CRUK and TCGA outputs.

The ICD-O histology groups shown in the website, such as `954-957 Nerve sheath tumors` or `918-924 Osseous and chondromatous neoplasms`, represent parent histology categories. The specific selected histology term appears underneath the group, such as `9540/3 Malignant peripheral nerve sheath tumor, NOS` or `9180/3 Osteosarcoma, NOS`.

---

### HIST-021: Prostate + adenocarcinoma

Input tested:
- Topography: C61 Prostate gland
- Histology: 8140/3 Adenocarcinoma, NOS

Expected behaviour:
- The mapping should return Prostate cancer or a prostate-specific CRUK term.
- The mapping should return TCGA PRAD.

Observed behaviour:
- The mapping returned Men's cancer.
- TCGA MISC was generated instead of PRAD.
- The mapping output used the parent term C60-C63 Male genital organs rather than C61 Prostate gland.

Conclusion:
This appears to be another parent/child topography issue. The website selected C61 Prostate gland, but the mapping used the broader male genital organs parent term, preventing prostate-specific PRAD generation.

---

### HIST-022: Ovary + serous carcinoma

Input tested:
- Topography: C56 Ovary
- Histology: 8441/3 Serous carcinoma, NOS

Expected behaviour:
- The mapping should return Ovarian cancer or a relevant women’s cancer term.
- The mapping should return TCGA OV.

Observed behaviour:
- The mapping returned Women's cancers (gynaecological cancer).
- TCGA output was empty.
- The mapping output used the parent term C51-C58 Female genital organs rather than C56 Ovary.

Conclusion:
The ovary-specific TCGA output OV was not generated because the mapping used the broader female genital organs parent term.

---

### HIST-023: Cervix + squamous cell carcinoma

Input tested:
- Topography: C53 Cervix uteri
- Histology: 8070/3 Squamous cell carcinoma, NOS

Expected behaviour:
- The mapping should return Cervical cancer or a relevant women’s cancer term.
- The mapping should return TCGA CESC.

Observed behaviour:
- The mapping returned Women's cancers (gynaecological cancer).
- TCGA output was empty.
- The mapping output used the parent term C51-C58 Female genital organs rather than C53 Cervix uteri.

Conclusion:
The cervix-specific TCGA output CESC was not generated because the mapping used the broader female genital organs parent term.

---

### HIST-024: Corpus uteri + endometrioid adenocarcinoma

Input tested:
- Topography: C54 Corpus uteri
- Histology: 8380/3 Endometrioid adenocarcinoma, NOS

Expected behaviour:
- The mapping should return Womb cancer or a relevant women’s cancer term.
- The mapping should return TCGA UCEC.

Observed behaviour:
- The mapping returned Women's cancers (gynaecological cancer).
- TCGA output was empty.
- The mapping output used the parent term C51-C58 Female genital organs rather than C54 Corpus uteri.

Conclusion:
The uterus-specific TCGA output UCEC was not generated because the mapping used the broader female genital organs parent term.

---

### HIST-025: Peripheral nerve sheath tumour rare cancer test

Input tested:
- Topography: C47 Peripheral nerves and autonomic nervous system
- Histology: 9540/3 Malignant peripheral nerve sheath tumor, NOS

Expected behaviour:
- The mapping should return Rare cancer.
- No TCGA output was necessarily expected.

Observed behaviour:
- Rare cancer was generated.
- TCGA output was empty.
- The mapping matched the rare cancer fallback rule.

Conclusion:
This test passed. The rare cancer fallback behaved as expected.

---

### HIST-026: Bone + osteosarcoma

Input tested:
- Topography: C40-C41 Bones, joints and articular cartilage
- Histology: 9180/3 Osteosarcoma, NOS

Expected behaviour:
- The mapping should return Bone cancer.
- No TCGA output was necessarily expected.

Observed behaviour:
- Bone cancer was generated.
- TCGA output was empty.

Conclusion:
This test passed. The bone cancer mapping behaved as expected.

---

### HIST-027: Soft tissue sarcoma

Input tested:
- Topography: C49 Connective, subcutaneous and other soft tissues
- Histology: 8800/3 Sarcoma, NOS

Expected behaviour:
- The mapping should return Soft tissue sarcoma.
- The mapping should return TCGA SARC.

Observed behaviour:
- Soft tissue sarcoma was generated.
- TCGA SARC was generated.
- The mapping matched the complex sarcoma_generic rule.

Conclusion:
This test passed. It confirms that complex mapping can generate both the expected CRUK and TCGA outputs when the topography and histology are handled correctly.

---

### Summary of special and rare tests

The special male and female genital organ tests showed the same parent/child topography issue seen in other groups. Although child terms such as C61 Prostate gland, C56 Ovary, C53 Cervix uteri, and C54 Corpus uteri were present in the dataset filters, the mapping output used the broader parent terms C60-C63 Male genital organs or C51-C58 Female genital organs. This prevented more specific TCGA outputs such as PRAD, OV, CESC, and UCEC from being generated.

In contrast, the rare cancer, bone cancer, and soft tissue sarcoma tests behaved more as expected. The C47 rare cancer case returned Rare cancer, the bone case returned Bone cancer, and the C49 sarcoma case successfully returned both Soft tissue sarcoma and TCGA SARC.
-------------------

****** ## Overall validation finding  لازم اتاكد 

Across multiple histology validation tests, a repeated issue was observed where the selected child topography term was present in the dataset filters, but the mapping output used the broader parent or umbrella topography term as the input term. This was seen in kidney, lung, digestive, brain/CNS, and sex-specific cancer tests.

This caused the mapping to match simple, umbrella, or special parent-level rules rather than the expected child-specific or histology-based rules. As a result, several expected TCGA outputs were not generated, including KIRC, KIRP, KICH, LUAD, LUSC, COAD, READ, GBM, LGG, PRAD, OV, CESC, and UCEC.

This suggests that the issue is likely in how the website/backend passes selected ICD-O topography filters into the Python mapping, rather than in all schemas themselves. The selected child topography is visible in the downloaded datasetFilters, but the mapping input term often becomes the parent topography.

Some mappings did work correctly, including breast to BRCA, soft tissue sarcoma to SARC, rare cancer fallback, and bone cancer mapping. This shows that TCGA generation and CRUK generation can work when the correct input term is used.

A separate issue was observed in the skin melanoma tests: SKCM was identified internally as the matched_schema_term, but it was not added to the final TCGA output list.
---*******

### Direct runner check

To check whether the issue was caused by the schemas/runner or by the website/backend, I ran the mapping directly from the terminal using:

`python3 python_mapping/runner.py --label "C64 Kidney" --histology "8310/3 Clear cell adenocarcinoma"`

The direct runner test matched C64 Kidney at the intermediate level and returned Kidney cancer with TCGA kidney outputs. This shows that the runner can apply the intermediate kidney mapping when the child topography term is passed directly.

This suggests that the website issue is likely caused before or during the backend input preparation step, where the selected child topography term appears in datasetFilters but the mapping receives or uses the broader parent term instead.

-----------
### Direct runner comparison: child vs parent topography

To determine whether the issue was caused by the schemas/runner or by the website/backend input handling, I ran the same kidney histology test directly through the terminal using both the child topography and the parent topography.

When the runner was given the child term `C64 Kidney` with `8310/3 Clear cell adenocarcinoma`, it matched the intermediate schema and returned Kidney cancer with TCGA kidney outputs.

When the runner was given the parent term `C64-C68 Urinary tract` with the same histology, it matched the simple schema and returned broad urinary tract CRUK outputs, with an empty TCGA list.

This reproduces the website behaviour and suggests that the website/backend is likely passing or prioritising the parent topography term instead of the selected child topography term. Therefore, the repeated missing TCGA outputs in kidney, lung, digestive, brain, and sex-specific tests are most likely caused by input preparation or topography selection before the runner is called, rather than by the schemas themselves.

## Backend fix: Child topography selection in `app.py`

After identifying that the website/backend was passing the parent topography term instead of the selected child term, I updated the `extract_dataset_context` function in `app.py` so that ICD-O child topography terms are also recognised and preferred over broader parent terms when both are present.

I then repeated the kidney validation test using:
- Topography: C64 Kidney
- Histology: 8310/3 Clear cell adenocarcinoma, NOS

After the fix, the mapping output used `C64 Kidney` as the input term, matched the intermediate schema, and generated Kidney cancer with TCGA kidney outputs. This confirms that the parent/child topography issue was caused by backend input preparation rather than the schema logic itself.

### Kidney retesting after `app.py` fix

After updating `app.py` to recognise and prefer ICD-O child topography terms, I repeated three kidney histology override tests using C64 Kidney.

The chromophobe kidney test used:
- Topography: C64 Kidney
- Histology: 8317/3 Renal cell carcinoma, chromophobe type

After the fix, the mapping used `C64 Kidney` as the input term, matched the intermediate schema, and generated Kidney cancer with TCGA KICH.

The clear cell kidney test used:
- Topography: C64 Kidney
- Histology: 8310/3 Clear cell adenocarcinoma, NOS

After the fix, the mapping used `C64 Kidney` as the input term, matched the intermediate schema, and generated Kidney cancer with TCGA kidney outputs. This confirmed that the parent/child topography issue was fixed, although the clear cell case returned multiple kidney TCGA outputs rather than only KIRC.

The papillary kidney test used:
- Topography: C64 Kidney
- Histology: 8260/3 Papillary adenocarcinoma, NOS

After the fix, the mapping used `C64 Kidney` as the input term, matched the intermediate schema, and generated Kidney cancer with TCGA KIRP.

Overall, the kidney retesting confirmed that the website/backend now passes the selected child topography term correctly to the runner. The previous failure was caused by backend input preparation rather than the intermediate schema failing to recognise C64 Kidney.

Important follow-up observation:
The chromophobe and papillary kidney tests generated specific TCGA outputs (KICH only and KIRP only). However, the clear cell kidney test returned multiple kidney TCGA outputs (KIRC, KIRP, and KICH) rather than KIRC alone. This suggests a separate issue from the parent/child topography bug. The backend fix successfully passed C64 Kidney to the runner, but the clear cell histology override may be missing, mismatched by label, or not replacing the default kidney TCGA outputs correctly.

### KIRC specificity fix

During kidney retesting, the clear cell kidney case initially returned multiple kidney TCGA outputs rather than KIRC only. The intermediate schema was checked and showed that the KIRC override contained `8312/3 Renal cell carcinoma, NOS`, but did not include the website histology label `8310/3 Clear cell adenocarcinoma, NOS`.

I added `8310/3 Clear cell adenocarcinoma, NOS` to the KIRC override in `schema_intermediate_1.1.2.json`.

After retesting, the mapping used `C64 Kidney` as the input term, matched the intermediate schema, and generated Kidney cancer with TCGA KIRC only. This confirms that the KIRC specificity issue was caused by a missing histology label in the intermediate schema override.

### Lung retesting after `app.py` fix

After updating `app.py` to recognise and prefer ICD-O child topography terms, I repeated the lung histology validation tests using C34 Bronchus and lung.

The lung adenocarcinoma test used:
- Topography: C34 Bronchus and lung
- Histology: 8140/3 Adenocarcinoma, NOS

After the fix, the mapping used `C34 Bronchus and lung` as the input term, matched the intermediate schema, and generated Lung cancer with TCGA LUAD. This test passed.

The lung squamous cell carcinoma test used:
- Topography: C34 Bronchus and lung
- Histology: 8070/3 Squamous cell carcinoma, NOS

The first attempt contained mixed histology tags, so the test was repeated with only `8070/3 Squamous cell carcinoma, NOS` selected. After repeating the test, the mapping used `C34 Bronchus and lung` as the input term, matched the intermediate schema, and generated Lung cancer with TCGA LUSC. This test passed.

The small cell carcinoma test used:
- Topography: C34 Bronchus and lung
- Histology: 8041/3 Small cell carcinoma, NOS

After the fix, the mapping used `C34 Bronchus and lung` as the input term and generated Lung cancer. However, the TCGA output contained the default lung TCGA outputs LUAD and LUSC. This confirms that the parent/child topography issue was fixed, but the TCGA behaviour for small cell carcinoma may need separate schema review.

The large cell carcinoma test used:
- Topography: C34 Bronchus and lung
- Histology: 8012/3 Large cell carcinoma, NOS

After the fix, the mapping used `C34 Bronchus and lung` as the input term and generated Lung cancer. However, the TCGA output again contained the default lung TCGA outputs LUAD and LUSC. This confirms that the backend fix worked, but the TCGA default behaviour for large cell carcinoma may also need review.

Overall, the lung retesting confirmed that the website/backend now passes the selected child topography term correctly to the runner. The previous lung failures were caused by backend input preparation rather than the intermediate schema failing to recognise C34 Bronchus and lung. LUAD and LUSC now work correctly when the relevant histology terms are selected. The small cell and large cell cases should be reviewed separately to decide whether default LUAD/LUSC outputs are appropriate or whether these histologies should have different TCGA handling.


### Digestive retesting after `app.py` fix

After updating `app.py` to recognise and prefer ICD-O child topography terms, I repeated the digestive histology validation tests using C18 Colon and C20 Rectum.

The colon test used:
- Topography: C18 Colon
- Histology: 8140/3 Adenocarcinoma, NOS

After the fix, the mapping used `C18 Colon` as the input term and generated Bowel cancer, Colorectal cancer, and TCGA COAD. This test passed.

The rectum test used:
- Topography: C20 Rectum
- Histology: 8140/3 Adenocarcinoma, NOS

After the fix, the mapping used `C20 Rectum` as the input term and generated Rectal cancer and TCGA READ. This test passed.

Overall, the digestive retesting confirmed that the backend now passes the selected child topography terms correctly to the runner. The previous digestive issue was caused by backend input preparation, where the mapping used the broader parent term `C15-C26 Digestive organs` instead of the selected child topography terms. After the fix, both colon and rectum generated the expected CRUK and TCGA outputs.


### Skin and brain retesting after backend and schema fixes

After the backend parent/child topography fix, I repeated the skin melanoma and brain glioma validation tests. The purpose was to confirm whether the website/backend now passed the selected child topography terms correctly, and to identify whether any remaining TCGA failures were due to missing schema rules or missing histology labels.

#### Skin melanoma retesting

The skin tests used:
- Topography: C44 Skin

For `8720/3 Malignant melanoma, NOS`, the mapping used `C44 Skin` as the input term, matched the complex `skin_melanoma` rule, and generated Melanoma skin cancer with TCGA SKCM.

For `8721/3 Nodular melanoma`, the mapping also used `C44 Skin` as the input term, matched the complex `skin_melanoma` rule, and generated Melanoma skin cancer with TCGA SKCM.

However, the earlier test for `8743/3 Low cumulative sun damage melanoma` did not generate TCGA SKCM. On checking `schema_complex_1.1.2.json`, I found that the SKCM `skin_melanoma` rule included `8720/3`, `8721/3`, `8742/3`, and `8744/3`, but did not include `8743/3`.

I added `8743/3` to the SKCM `skin_melanoma` histology code list. After retesting `C44 Skin` with `8743/3 Low cumulative sun damage melanoma`, the mapping returned Melanoma skin cancer and TCGA SKCM. This confirmed that the missing SKCM output was caused by a missing histology code in the complex schema rule.

#### Brain glioma retesting

The brain tests used:
- Topography: C71 Brain

For `9440/3 Glioblastoma, NOS`, the mapping used `C71 Brain` as the input term, matched the intermediate schema, and generated Brain tumours with TCGA GBM. This showed that the backend fix worked for C71 Brain and that the existing GBM override was functioning correctly.

The earlier tests for `9400/3 Astrocytoma, NOS` and `9450/3 Oligodendroglioma, NOS` used `C71 Brain` correctly, but did not generate TCGA LGG. On checking `schema_intermediate_1.1.2.json`, I found that the LGG override under `C71 Brain` existed, but it only included `9380/3 Glioma, malignant` and `9401/3 Astrocytoma, anaplastic`. It did not include `9400/3 Astrocytoma, NOS` or `9450/3 Oligodendroglioma, NOS`.

I added `9400/3 Astrocytoma, NOS` and `9450/3 Oligodendroglioma, NOS` to the LGG override. After retesting, both histology terms generated Brain tumours with TCGA LGG.

Overall, the skin and brain retesting showed that the backend child topography fix worked correctly. The remaining failures were caused by missing histology codes or missing histology labels in the schema rules, which were then added and successfully validated.


### Sex-specific, rare, bone, and soft tissue retesting after backend fix

After updating `app.py` to recognise and prefer ICD-O child topography terms, I repeated the sex-specific, rare, bone, and soft tissue validation tests. These tests were used to confirm whether the website/backend now passes the selected detailed topography term to the runner instead of the broader parent term.

#### Sex-specific cancer retesting

The prostate test used:
- Topography: C61 Prostate gland
- Histology: 8140/3 Adenocarcinoma, NOS

After the fix, the mapping used `C61 Prostate gland` as the input term and generated Prostate cancer with TCGA PRAD. This confirmed that the previous issue where the mapping used the broader parent term `C60-C63 Male genital organs` was resolved.

The ovary test used:
- Topography: C56 Ovary
- Histology: 8441/3 Serous carcinoma, NOS

After the fix, the mapping used `C56 Ovary` as the input term and generated Ovarian cancer with TCGA OV. This confirmed that the previous issue where the mapping used the broader parent term `C51-C58 Female genital organs` was resolved.

The cervix test used:
- Topography: C53 Cervix uteri
- Histology: 8070/3 Squamous cell carcinoma, NOS

After the fix, the mapping used `C53 Cervix uteri` as the input term and generated Cervical cancer with TCGA CESC.

The corpus uteri test used:
- Topography: C54 Corpus uteri
- Histology: 8380/3 Endometrioid adenocarcinoma, NOS

After the fix, the mapping used `C54 Corpus uteri` as the input term and generated Endometrial cancer with TCGA UCEC.

Overall, the sex-specific retesting confirmed that the backend child topography selection fix resolved the previous parent-level mapping issue for male and female genital organ sites.

#### Rare, bone, and soft tissue retesting

The rare peripheral nerve test used:
- Topography: C47 Peripheral nerves and autonomic nervous system
- Histology: 9540/3 Malignant peripheral nerve sheath tumor, NOS

After retesting, the mapping returned Malignant schwannoma with no TCGA output. This was more specific than the earlier general Rare cancer fallback and matched the `malignant_schwannoma_by_histology` rule.

This does not contradict the earlier HIST-025 result. HIST-025 documented the initial baseline behaviour, where the case returned the general Rare cancer fallback. FIX-021 documented the later retest, where the mapping returned the more specific Malignant schwannoma label.


The bone test used:
- Topography: C40-C41 Bones, joints and articular cartilage
- Histology: 9180/3 Osteosarcoma, NOS

The mapping returned Bone cancer with no TCGA output. This behaved as expected for the bone validation test.

The soft tissue sarcoma test used:
- Topography: C49 Connective, subcutaneous and other soft tissues
- Histology: 8800/3 Sarcoma, NOS

The mapping returned Soft tissue sarcoma with TCGA SARC. This confirmed that the complex `sarcoma_generic` rule works correctly and can generate both CRUK and TCGA outputs.

Overall, these retests confirmed that the backend fix improved child topography handling across sex-specific cancer sites and that the rare, bone, and soft tissue mapping rules behaved as expected.

### Additional unusual histology stress testing

After completing the main validation and schema fixes, I performed an additional set of unusual histology stress tests. These were selected to test whether the mapping pipeline could handle more specific or less generic histology terms, rather than only common adenocarcinoma or squamous carcinoma examples.

The aim of these tests was not only to check whether outputs were correct, but also to identify cases where the schemas may need further biological or TCGA-specific review.

#### Digestive and hepatobiliary stress tests

The stomach test used:
- Topography: C16 Stomach
- Histology: 8490/3 Signet ring cell carcinoma

This case was selected because signet ring cell carcinoma is a more specific gastric histology than generic adenocarcinoma. The mapping returned Gastric cancer and TCGA STAD, confirming that the stomach mapping still worked for this more unusual histological subtype.

The pancreatic neuroendocrine test used:
- Topography: C25 Pancreas
- Histology: 8246/3 Neuroendocrine carcinoma, NOS

This case was selected because pancreatic neuroendocrine carcinoma is biologically different from typical pancreatic adenocarcinoma. The mapping returned Pancreatic cancer, but no TCGA output. This was recorded as partial pass / review needed rather than a direct failure, because assigning PAAD may not be appropriate for a neuroendocrine tumour.

The hepatocellular carcinoma test used:
- Topography: C22 Liver and intrahepatic bile ducts
- Histology: 8170/3 Hepatocellular carcinoma, NOS

This case returned Liver cancer with TCGA LIHC.

The cholangiocarcinoma test used:
- Topography: C22 Liver and intrahepatic bile ducts
- Histology: 8160/3 Cholangiocarcinoma

This case returned Liver cancer with TCGA CHOL.

These two liver-related tests were selected together because they use the same broad topography area but represent different tumour types. The results showed that the schema could separate hepatocellular carcinoma from cholangiocarcinoma using histology, producing LIHC and CHOL respectively.

#### Urinary, endocrine, and germ cell stress tests

The bladder test used:
- Topography: C67 Bladder
- Histology: 8120/3 Transitional cell carcinoma, NOS

This was selected because transitional/urothelial carcinoma is the characteristic bladder cancer histology and is different from generic adenocarcinoma or squamous carcinoma. The mapping returned Bladder cancer with TCGA BLCA.

The thyroid test used:
- Topography: C73 Thyroid gland
- Histology: 8260/3 Papillary adenocarcinoma, NOS

This was selected because papillary carcinoma is an important thyroid histology. The mapping returned Thyroid cancer with TCGA THCA.

The testis test used:
- Topography: C62 Testis
- Histology: 9061/3 Seminoma, NOS

This was selected because seminoma is a germ cell tumour histology, not a generic carcinoma. The mapping returned Testicular cancer with TCGA TGCT.

#### Head and neck squamous stress tests

The oropharynx test used:
- Topography: C10 Oropharynx
- Histology: 8070/3 Squamous cell carcinoma, NOS

This case was selected to test the complex HNSC rule, which depends on both a head and neck topography and squamous histology. The mapping returned Head and neck cancer with TCGA HNSC, confirming that the complex rule worked for this site.

The tongue test used:
- Topography: C02 Other and unspecified parts of tongue
- Histology: 8070/3 Squamous cell carcinoma, NOS

This case was selected to compare another head and neck squamous site against the oropharynx result. The mapping returned Tongue cancer but no TCGA output. This was recorded as partial pass / review needed. It may indicate that tongue cancer is currently handled as a site-specific simple mapping rather than triggering the complex HNSC rule. This should be reviewed to decide whether tongue squamous carcinoma should also map to HNSC.

Overall, these unusual histology tests showed that the pipeline can correctly handle several non-generic histology cases, including signet ring carcinoma, transitional cell carcinoma, papillary thyroid carcinoma, hepatocellular carcinoma, cholangiocarcinoma, seminoma, and oropharyngeal squamous cell carcinoma. The pancreatic neuroendocrine and tongue squamous cases were useful review cases because they produced biologically plausible CRUK outputs but did not generate TCGA outputs.


---------------
### Negative and false-positive stress testing

After completing the main validation tests, I performed additional negative and false-positive stress tests. These tests were selected to check whether the mapping pipeline avoids generating inappropriate TCGA outputs when the topography is correct but the histology does not match the expected TCGA cancer type.

The purpose of these tests was to evaluate specificity, not just successful mapping. A useful mapping pipeline should generate expected outputs when both site and histology support the rule, but should avoid false-positive TCGA outputs when the histology is biologically different.

#### Skin and melanoma specificity tests

The skin squamous test used:
- Topography: C44 Skin
- Histology: 8070/3 Squamous cell carcinoma, NOS

This was selected to check that skin topography alone does not generate TCGA SKCM. The mapping returned Squamous cell skin cancer with no TCGA output. This confirmed that the SKCM rule is specific to melanoma histology and does not produce a false positive for squamous cell skin cancer.

The eye melanoma test used:
- Topography: C69 Eye and adnexa
- Histology: 8720/3 Malignant melanoma, NOS

This was selected because melanoma histology can occur in both cutaneous and uveal sites. The mapping returned Eye cancer with TCGA UVM, not SKCM. This confirmed that uveal melanoma is separated from cutaneous melanoma and that melanoma histology alone does not incorrectly generate SKCM.

#### Head and neck squamous specificity test

The gum squamous test used:
- Topography: C03 Gum
- Histology: 8070/3 Squamous cell carcinoma, NOS

This was selected to test whether another oral cavity/head and neck squamous site triggers the HNSC complex rule. The mapping returned Head and neck cancer with TCGA HNSC. This confirmed that the complex head_neck_squamous rule works for gum squamous carcinoma.

#### Review cases: broad default TCGA outputs

The breast sarcoma test used:
- Topography: C50 Breast
- Histology: 8800/3 Sarcoma, NOS

The mapping used C50 Breast correctly and generated Breast cancer with TCGA BRCA. This was recorded as partial pass / review needed. The backend child topography handling worked, but the TCGA output should be reviewed because sarcoma histology may not be appropriate for Breast invasive carcinoma.

The colon squamous test used:
- Topography: C18 Colon
- Histology: 8070/3 Squamous cell carcinoma, NOS

The mapping used C18 Colon correctly and generated Bowel cancer, Colorectal cancer, and TCGA COAD. This was recorded as partial pass / review needed because COAD represents colon adenocarcinoma, while the tested histology was squamous cell carcinoma. This may indicate that the default COAD output is too broad for unusual colon histologies.

The kidney squamous test used:
- Topography: C64 Kidney
- Histology: 8070/3 Squamous cell carcinoma, NOS

The mapping used C64 Kidney correctly and generated Kidney cancer with the default kidney TCGA outputs KIRC, KIRP, and KICH. This was recorded as partial pass / review needed because squamous cell carcinoma does not specifically support these renal TCGA subtypes. This suggests that the kidney default TCGA outputs may need further review for unusual histologies.

The lung small cell test used:
- Topography: C34 Bronchus and lung
- Histology: 8041/3 Small cell carcinoma, NOS
This stress test deliberately revisited the small cell lung behaviour observed during FIX-007, but framed it as a false-positive TCGA check rather than as a backend retest.

The mapping used C34 Bronchus and lung correctly and generated Lung cancer with default lung TCGA outputs LUAD and LUSC. This was recorded as partial pass / review needed because small cell lung carcinoma is biologically different from both lung adenocarcinoma and lung squamous cell carcinoma.

Overall, these negative stress tests confirmed that the backend child topography fix worked correctly. They also showed that some schema default TCGA mappings may be too broad for unusual or biologically distinct histologies. These cases are useful for documenting limitations and future schema refinement.
---------

### Additional subtype and same-site histology stress testing

I performed another set of stress tests to check whether the schemas behave consistently for different histology subtypes within the same topography, and whether TCGA outputs are avoided when the histology is biologically different from the TCGA cancer type.

#### Bone subtype test

The bone chondrosarcoma test used:
- Topography: C40-C41 Bones, joints and articular cartilage
- Histology: 9220/3 Chondrosarcoma, NOS

This was selected as a second bone subtype after osteosarcoma. The mapping returned Bone cancer with no TCGA output, which was expected. This confirmed that the umbrella bone mapping works for another bone histology subtype and does not generate an inappropriate TCGA output.

#### Esophagus same-site histology comparison

The esophagus adenocarcinoma test used:
- Topography: C15 Esophagus
- Histology: 8140/3 Adenocarcinoma, NOS

The esophagus squamous test used:
- Topography: C15 Esophagus
- Histology: 8070/3 Squamous cell carcinoma, NOS

Both tests generated Oesophageal cancer with TCGA ESCA. These two tests were selected together because esophageal cancer can include different major histological presentations. The results showed that the esophagus mapping can support both adenocarcinoma and squamous carcinoma under the same TCGA cancer type.

#### Sarcoma subtype test

The soft tissue liposarcoma test used:
- Topography: C49 Connective, subcutaneous and other soft tissues
- Histology: 8850/3 Liposarcoma, NOS

This was selected to test whether the sarcoma mapping works for a specific sarcoma subtype rather than only the generic `8800/3 Sarcoma, NOS` term. The mapping matched the liposarcoma complex rule and generated Soft tissue sarcoma with TCGA SARC.

#### Non-melanoma skin test

The skin basal cell carcinoma test used:
- Topography: C44 Skin
- Histology: 8090/3 Basal cell carcinoma, NOS

This was selected to test non-melanoma skin mapping and to confirm that C44 Skin does not generate SKCM unless melanoma histology is present. The mapping returned Basal cell skin cancer with no TCGA output.

#### Rectum squamous review case

The rectum squamous test used:
- Topography: C20 Rectum
- Histology: 8070/3 Squamous cell carcinoma, NOS

The mapping used C20 Rectum correctly and generated Rectal cancer with TCGA READ. This was recorded as partial pass / review needed because READ represents rectum adenocarcinoma, while the tested histology was squamous cell carcinoma. The CRUK output was plausible, but the TCGA output may be too broad for this unusual histology.

Overall, this set of tests strengthened the validation by adding subtype-level checks and additional false-positive TCGA review cases.

-------------------
### Cardiovascular and vascular sarcoma stress testing

I performed additional stress tests using heart/mediastinum and soft tissue topographies with vascular and sarcoma-type histologies. These tests were selected because tumours involving the heart and blood vessels are rare, and they are useful for checking whether the schemas can handle unusual sarcoma histologies without producing inappropriate fallback outputs.

#### Soft tissue vascular and sarcoma positive controls

The soft tissue leiomyosarcoma test used:
- Topography: C49 Connective, subcutaneous and other soft tissues
- Histology: 8890/3 Leiomyosarcoma, NOS

The mapping returned Soft tissue sarcoma with TCGA SARC. This confirmed that the leiomyosarcoma complex rule works correctly for a soft tissue topography.

The soft tissue hemangiosarcoma test used:
- Topography: C49 Connective, subcutaneous and other soft tissues
- Histology: 9120/3 Hemangiosarcoma

The mapping returned Soft tissue sarcoma with TCGA SARC. This confirmed that a blood vessel tumour histology can map to Soft tissue sarcoma and SARC when the topography is C49.

The soft tissue Kaposi sarcoma test used:
- Topography: C49 Connective, subcutaneous and other soft tissues
- Histology: 9140/3 Kaposi sarcoma

The mapping returned Soft tissue sarcoma with TCGA SARC. This confirmed that Kaposi sarcoma is handled as a sarcoma-type mapping under the C49 soft tissue topography.

#### Heart/mediastinum sarcoma tests

The heart/mediastinum leiomyosarcoma test used:
- Topography: C38 Heart, mediastinum, and pleura
- Histology: 8890/3 Leiomyosarcoma, NOS

The mapping returned Soft tissue sarcoma with TCGA SARC. This showed that the leiomyosarcoma complex rule could still trigger even when the topography was C38 rather than C49.

The heart/mediastinum hemangiosarcoma test used:
- Topography: C38 Heart, mediastinum, and pleura
- Histology: 9120/3 Hemangiosarcoma

The mapping used the correct C38 input term, but returned Mediastinal germ cell tumours with no TCGA output. This was recorded as partial pass / review needed. The backend input handling worked, but the biological output should be reviewed because hemangiosarcoma is a vascular sarcoma-type tumour, not a mediastinal germ cell tumour.

The heart/mediastinum Kaposi sarcoma test used:
- Topography: C38 Heart, mediastinum, and pleura
- Histology: 9140/3 Kaposi sarcoma

This also returned Mediastinal germ cell tumours with no TCGA output. This was recorded as partial pass / review needed for the same reason.

Overall, these tests showed that the C49 soft tissue sarcoma mappings work well for vascular and sarcoma-type histologies. However, C38 Heart, mediastinum, and pleura appears to have a broad fallback to Mediastinal germ cell tumours for some vascular sarcoma histologies. This may need further schema review to avoid inappropriate fallback outputs for rare cardiovascular sarcomas.
-------------
## Edge-case and unusual histology validation tests

I performed an additional set of rare and unusual histology validation tests to check how the mapping pipeline behaves with less common tumour types and site-histology combinations. These tests were selected to assess whether the schemas generate appropriate TCGA outputs, avoid false-positive TCGA mappings, or identify cases that need further review.

#### Rare and special site-histology tests

The testis seminoma test used:
- Topography: C62 Testis
- Histology: 9061/3 Seminoma, NOS

The mapping returned Testicular cancer with TCGA TGCT. This confirmed that the testicular germ cell tumour mapping worked correctly for seminoma histology.

The cholangiocarcinoma test used:
- Topography: C22 Liver and intrahepatic bile ducts
- Histology: 8160/3 Cholangiocarcinoma

The mapping returned Liver cancer with TCGA CHOL. This confirmed that the schema can distinguish cholangiocarcinoma from hepatocellular carcinoma within the same broad liver/intrahepatic bile duct topography area.

The pancreatic neuroendocrine carcinoma test used:
- Topography: C25 Pancreas
- Histology: 8246/3 Neuroendocrine carcinoma, NOS

The mapping returned Pancreatic cancer with no TCGA output. This was recorded as partial pass / review needed rather than a direct failure, because pancreatic neuroendocrine carcinoma is biologically different from typical pancreatic adenocarcinoma and may not be appropriate for PAAD.

#### Eye and CNS false-positive checks

The eye melanoma test used:
- Topography: C69 Eye and adnexa
- Histology: 8720/3 Malignant melanoma, NOS

The mapping returned Eye cancer with TCGA UVM. This confirmed that melanoma histology outside the skin does not incorrectly generate SKCM, and that uveal melanoma is separated from cutaneous melanoma.

The spinal cord glioma test used:
- Topography: C72 Spinal cord, cranial nerves, and other parts of central nervous system
- Histology: 9380/3 Glioma, malignant

The mapping returned Spinal cord tumours with no TCGA output. This was considered appropriate because the test should not automatically generate GBM or LGG when the topography is spinal cord rather than C71 Brain.

#### Unusual histology review cases

The corpus uteri squamous carcinoma test used:
- Topography: C54 Corpus uteri
- Histology: 8070/3 Squamous cell carcinoma, NOS

The mapping returned Endometrial cancer with TCGA UCEC. This was recorded as partial pass / review needed because the backend selected the correct child topography, but squamous histology may not be appropriate for a default UCEC output.

The thyroid squamous carcinoma test used:
- Topography: C73 Thyroid gland
- Histology: 8070/3 Squamous cell carcinoma, NOS

The mapping returned Thyroid cancer with TCGA THCA. This was recorded as partial pass / review needed because the output may reflect a broad default TCGA mapping for thyroid, even though the tested histology was unusual.

The rectum squamous carcinoma test used:
- Topography: C20 Rectum
- Histology: 8070/3 Squamous cell carcinoma, NOS

The mapping returned Rectal cancer with TCGA READ. This was recorded as partial pass / review needed because READ represents rectum adenocarcinoma, while the tested histology was squamous cell carcinoma.

The ovary unusual histology test used:
- Topography: C56 Ovary
- Histology: 8094/3 Basosquamous carcinoma

The mapping returned Ovarian cancer with TCGA OV. This was recorded as partial pass / review needed because OV represents ovarian serous cystadenocarcinoma, while the tested histology was basosquamous carcinoma. During this test, more than one histology option was selected in the interface, but the mapping output used 8094/3 Basosquamous carcinoma as the histology label, so this was the histology recorded in the validation table.

The prostate unusual histology test used:
- Topography: C61 Prostate gland
- Histology: 8094/3 Basosquamous carcinoma

The mapping returned Prostate cancer with TCGA PRAD. This was recorded as partial pass / review needed because PRAD represents prostate adenocarcinoma, while the tested histology was basosquamous carcinoma. As with the ovary test, more than one histology option was selected in the interface, but the mapping output used 8094/3 Basosquamous carcinoma as the histology label, so this was the histology recorded in the validation table.

Overall, these tests confirmed that several rare and special mappings worked correctly, including TGCT, CHOL, UVM, and spinal cord tumour handling. They also identified several review cases where the backend selected the correct child topography but the schema produced broad default TCGA outputs for unusual histologies. These cases are useful for documenting limitations and future schema refinement.
-------------

## Known limitation testing

### LIMIT-001: Adrenal gland + adrenal cortical carcinoma

Input tested:
- Topography: C74 Adrenal gland
- Histology: 8370/3 Adrenal cortical carcinoma

Expected behaviour:
- The intermediate schema should return Adrenal gland tumours.
- The intermediate schema should return TCGA ACC.

Observed behaviour:
- The selected topography and histology were both present in the downloaded dataset filters.
- The intermediate schema contains a matching ACC rule for C74 Adrenal gland with 8370/3 Adrenal cortical carcinoma.
- However, the website output matched the simple schema.
- Adrenal gland tumours was generated.
- TCGA ACC was not generated.

Conclusion:
This test documents a schema hierarchy limitation rather than a missing schema rule. Although the ACC rule exists in the intermediate schema, the website output matched the broader simple C74 topography mapping before the more specific topography-and-histology override was applied. This suggests that the mapping priority may need to be reviewed so that specific intermediate overrides are evaluated before broader simple topography rules in cases such as ACC.


### FIX-024: Retest after schema priority update

After reviewing the runner, the issue was traced to the schema evaluation order. The simple schema was originally evaluated before the intermediate schema, which allowed the broad C74 Adrenal gland rule to match before the more specific C74 + 8370/3 adrenal cortical carcinoma override was applied.

The runner priority was updated so that histology-dependent schemas are evaluated before the simple fallback schema. The updated order was:

umbrella → intermediate → complex → special → simple → rare

After retesting the same ACC input, the mapping matched the intermediate schema and generated Adrenal gland tumours with TCGA ACC correctly.

A small regression test set was then run to check that the priority update did not break existing mappings. The regression checks included kidney clear cell carcinoma, lung adenocarcinoma, skin melanoma, eye melanoma, breast carcinoma, and ACC. All six checks passed after the priority update.

This confirmed that the ACC issue was caused by schema priority rather than a missing intermediate schema rule.

--------
### STRESS-030: Pancreatic adenocarcinoma positive baseline

Input tested:

* Topography: C25 Pancreas
* Histology: 8140/3 Adenocarcinoma, NOS

Expected behaviour:

* The mapping should return Pancreatic cancer.
* The mapping should return TCGA PAAD.
* The intermediate schema should be triggered.

Observed behaviour:

* The mapping used C25 Pancreas with 8140/3 Adenocarcinoma, NOS.
* The intermediate schema was matched.
* Pancreatic cancer was generated.
* TCGA PAAD was generated.

Conclusion:
This test passed. It was added as a positive baseline for pancreatic adenocarcinoma. This is useful because it confirms that the expected PAAD mapping works for the canonical pancreatic adenocarcinoma histology. It also provides a comparison point for pancreatic neuroendocrine or unusual histology cases where a TCGA output may be absent or require review.
-----------------------

### STRESS-033: Oropharynx adenocarcinoma negative HNSC check

Input tested:

* Topography: C10 Oropharynx
* Histology: 8140/3 Adenocarcinoma, NOS

Expected behaviour:

* The mapping should return a CRUK head and neck/oropharyngeal cancer label.
* TCGA HNSC should not be generated because the histology is adenocarcinoma rather than squamous carcinoma.

Observed behaviour:

* The mapping used C10 Oropharynx with 8140/3 Adenocarcinoma, NOS.
* The complex mouth/oropharyngeal group was matched.
* Mouth and oropharyngeal cancer was generated.
* No TCGA output was generated.

Conclusion:
This test passed. It was added as a negative specificity check for the HNSC complex rule. The result showed that C10 Oropharynx with adenocarcinoma did not incorrectly generate TCGA HNSC, which supports the specificity of the HNSC mapping for appropriate squamous-related cases.
---------
### EDGE-011: Bone Ewing sarcoma with empty TCGA output

Input tested:

* Topography: C40 Bones, joints and articular cartilage of limbs
* Histology: 9364/3 Ewing sarcoma

Expected behaviour:

* The mapping should return Bone cancer.
* No TCGA output should be generated.

Observed behaviour:

* The mapping used C40 Bones, joints and articular cartilage of limbs with 9364/3 Ewing sarcoma.
* The complex bone group rule was matched.
* Bone cancer was generated.
* No TCGA output was generated.

Conclusion:
This test passed. It was added to check that Ewing sarcoma in a bone topography returns Bone cancer without incorrectly generating a TCGA output such as SARC. This supports the validation of TCGA-empty cases, where the correct behaviour is to avoid assigning an inappropriate TCGA study.
--------------------

### STRESS-029: Thyroid small cell carcinoma false-positive TCGA check

Input tested:

* Topography: C73 Thyroid gland
* Histology: 8041/3 Small cell carcinoma, NOS

Expected behaviour:

* The mapping should return Thyroid cancer.
* TCGA THCA should be reviewed because small cell carcinoma is an unusual thyroid histology and may not represent the canonical thyroid carcinoma cases covered by THCA.

Observed behaviour:

* The mapping used C73 Thyroid gland with 8041/3 Small cell carcinoma, NOS.
* The simple schema was matched.
* Thyroid cancer was generated.
* TCGA THCA was generated.

Conclusion:
This test was recorded as Under Review. The CRUK output was site-appropriate, but the TCGA THCA output may represent a broad default assignment for C73 Thyroid gland rather than a histology-specific match. This test therefore documents a possible false-positive TCGA output for an unusual thyroid histology.
----------

### STRESS-035: Brain sarcoma rule collision review

Input tested:

* Topography: C71 Brain
* Histology: 8800/3 Sarcoma, NOS

Expected behaviour:

* The mapping should avoid generating an inappropriate TCGA output.
* The output should be reviewed because the site and histology combination creates a possible rule collision between brain-specific and sarcoma-related mappings.

Observed behaviour:

* The mapping used C71 Brain with 8800/3 Sarcoma, NOS.
* The intermediate schema was matched.
* Brain tumours was generated.
* No TCGA output was generated.

Conclusion:
This test was recorded as Under Review. The result avoided inappropriate TCGA assignments such as GBM, LGG, or SARC, which is useful. However, the case remains a review case because the combination of a brain topography with a generic sarcoma histology is unusual and may require a more specific rule or an explicit fallback decision.
---------------
### STRESS-034: Skin Kaposi sarcoma false-positive SKCM check

Input tested:

* Topography: C44 Skin
* Histology: 9140/3 Kaposi sarcoma

Expected behaviour:

* The mapping should return a skin-related CRUK output.
* TCGA SKCM should not be generated, because Kaposi sarcoma is not cutaneous melanoma.

Observed behaviour:

* The mapping used C44 Skin with 9140/3 Kaposi sarcoma.
* The complex schema fallback was matched.
* Skin cancer was generated.
* No TCGA output was generated.

Conclusion:
This test was recorded as Under Review. The output avoided an inappropriate TCGA SKCM assignment, which is useful. However, the case remains under review because the complex fallback used the SKCM schema term while returning only a broad skin cancer CRUK output. This documents a fallback behaviour that may need clearer rule naming or explicit handling in future schema updates.
-------
### STRESS-031: Bladder adenocarcinoma false-positive BLCA check

Input tested:

* Topography: C67 Bladder
* Histology: 8140/3 Adenocarcinoma, NOS

Expected behaviour:

* The mapping should return Bladder cancer.
* The TCGA output should be reviewed because BLCA represents bladder urothelial carcinoma, while the selected histology was adenocarcinoma.

Observed behaviour:

* The mapping used C67 Bladder with 8140/3 Adenocarcinoma, NOS.
* The simple schema was matched.
* Bladder cancer was generated.
* TCGA BLCA was generated.

Conclusion:
This test was recorded as Under Review. The CRUK output was site-appropriate, but the TCGA BLCA output may represent a broad default assignment for C67 Bladder rather than a histology-specific match. This documents a possible false-positive TCGA output for a non-urothelial bladder histology.
-------
### STRESS-032: Stomach squamous carcinoma unusual histology check

Input tested:

* Topography: C16 Stomach
* Histology: 8070/3 Squamous cell carcinoma, NOS

Expected behaviour:

* The mapping should avoid generating an inappropriate TCGA STAD output for a discordant squamous histology.

Observed behaviour:

* The mapping used C16 Stomach with 8070/3 Squamous cell carcinoma, NOS.
* The complex `goj_exact` rule was matched.
* Gastro oesophageal junction cancers was generated.
* No TCGA output was generated.

Conclusion:
This test was recorded as Under Review. The output avoided an inappropriate TCGA STAD assignment, which is useful. However, the complex `goj_exact` match for C16 Stomach should be reviewed because it may represent a broad or unexpected grouping behaviour for this unusual site-histology combination.
-------
### EDGE-012: Testis malignant teratoma TCGA review

Input tested:

* Topography: C62 Testis
* Histology: 9080/3 Teratoma, malignant, NOS

Expected behaviour:

* The mapping should return Germ cell tumours and/or Men's cancer.
* The TCGA output should be reviewed to check whether TGCT or another output is appropriate.

Observed behaviour:

* The mapping used C62 Testis with 9080/3 Teratoma, malignant, NOS.
* The special schema was matched.
* Germ cell tumours and Men's cancer were generated.
* TCGA MISC was generated.

Conclusion:
This test was recorded as Under Review. The CRUK outputs were appropriate for a testicular germ cell tumour, but the TCGA output was MISC rather than a specific TGCT output. This documents a useful review case for the special mapping rules and TCGA assignment for testicular germ cell tumour subtypes.
----
### STRESS-036: Ovary endometrioid adenocarcinoma gynaecological mapping review

Input tested:

* Topography: C56 Ovary
* Histology: 8380/3 Endometrioid adenocarcinoma, NOS

Expected behaviour:

* The mapping should return an ovarian or gynaecological CRUK output.
* The TCGA output should be reviewed because this site-histology combination may create a possible distinction between ovarian and uterine/endometrial mapping.

Observed behaviour:

* The mapping used C56 Ovary with 8380/3 Endometrioid adenocarcinoma, NOS.
* The special schema was matched.
* Women's cancers (gynaecological cancer) was generated.
* No TCGA output was generated.

Conclusion:
This test was recorded as Under Review. The output avoided an inappropriate uterine TCGA assignment such as UCEC, which is useful. However, it returned a broad gynaecological CRUK label rather than a specific ovarian cancer label, so this case should be reviewed as a possible broad special-schema output.
--------
### STRESS-037: Corpus uteri serous carcinoma TCGA review

Input tested:

* Topography: C54 Corpus uteri
* Histology: 8441/3 Serous carcinoma, NOS

Expected behaviour:

* The mapping should return a uterine/womb cancer CRUK output.
* The TCGA output should be reviewed to determine whether UCEC should be generated for this uterine carcinoma case.

Observed behaviour:

* The mapping used C54 Corpus uteri with 8441/3 Serous carcinoma, NOS.
* The intermediate schema was matched.
* Womb cancer and Uterine cancer were generated.
* No TCGA output was generated.

Conclusion:
This test was recorded as Under Review. The CRUK outputs were site-appropriate and the mapping did not incorrectly generate an ovarian TCGA output. However, the absence of TCGA UCEC should be reviewed because this may represent a TCGA gap for this histology-specific uterine case.
-------


