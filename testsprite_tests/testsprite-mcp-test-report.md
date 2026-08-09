# TestSprite AI Testing Report (MCP)

## 1️⃣ Document Metadata

- **Project:** RubricLensAi
- **Test date:** 2026-08-09
- **Target:** Local Vite app at `http://localhost:5173/` with the deterministic Worker mock
- **Prepared by:** TestSprite MCP with failure triage by Codex
- **Purpose:** Seed the committed `testsprite_tests/` suite required by the TestSprite GitHub App

## 2️⃣ Requirement Validation Summary

- **Document input**
  - ✅ `TC001` Analyze pasted report with the matching rubric — TestSprite cloud passed. [Code](./TC001_Analyze_pasted_report_with_the_matching_rubric.py) · [Run](https://www.testsprite.com/dashboard/mcp/tests/5712335e-72a4-429a-92f2-389ed67fa3fc/test/9cfce4f6-e2f3-4209-bf84-e0879df5c800)
  - ✅ `TC013` Replace the current document — TestSprite cloud passed. [Code](./TC013_Replace_the_current_document.py) · [Run](https://www.testsprite.com/dashboard/mcp/tests/5712335e-72a4-429a-92f2-389ed67fa3fc/test/10011a7c-b5eb-46ec-a44f-acb4c25f8179)
- **Document type and rubric templates**
  - ✅ `TC007` See the rubric update when the document type changes — TestSprite cloud passed. [Code](./TC007_See_the_rubric_update_when_the_document_type_changes.py) · [Run](https://www.testsprite.com/dashboard/mcp/tests/5712335e-72a4-429a-92f2-389ed67fa3fc/test/5b49b03a-c772-4b35-8300-949ab8773371)
- **Advanced rubric editing**
  - ✅ `TC005` Keep advanced rubric changes with the current tab draft — corrected requirement and TestSprite cloud rerun passed. [Code](./TC005_Keep_advanced_rubric_changes_with_the_current_tab_draft.py) · [Run](https://www.testsprite.com/dashboard/mcp/tests/e826c4fd-c8a9-4d16-81fe-14363b29f903/test/0d999961-43d0-4c6d-b06a-97ce64323c9e)
  - ✅ `TC010` Add and remove rubric criteria — TestSprite cloud passed. [Code](./TC010_Add_and_remove_rubric_criteria.py) · [Run](https://www.testsprite.com/dashboard/mcp/tests/5712335e-72a4-429a-92f2-389ed67fa3fc/test/7a3ef49f-f381-4734-a3d7-b6ff675a3b31)
  - ✅ `TC017` Validate rubric errors and continue editing — TestSprite cloud passed. [Code](./TC017_Validate_rubric_errors_and_continue_editing.py) · [Run](https://www.testsprite.com/dashboard/mcp/tests/5712335e-72a4-429a-92f2-389ed67fa3fc/test/b8451e81-594d-4bef-a333-a7dc428b7309)
- **Appendix handling**
  - ✅ `TC012` Handle appendix exclusion before analysis — TestSprite cloud passed. [Code](./TC012_Handle_appendix_exclusion_before_analysis.py) · [Run](https://www.testsprite.com/dashboard/mcp/tests/5712335e-72a4-429a-92f2-389ed67fa3fc/test/dfba4747-cd29-45cf-a6ce-b08860dfa3d7)
  - ✅ `TC015` Keep appendix text in the document and analyze — TestSprite cloud passed. [Code](./TC015_Keep_appendix_text_in_the_document_and_analyze.py) · [Run](https://www.testsprite.com/dashboard/mcp/tests/5712335e-72a4-429a-92f2-389ed67fa3fc/test/9efae0a4-7772-4623-b617-e86b38806f75)
- **AI document analysis**
  - ✅ `TC009` Mark a rubric criterion not applicable and analyze successfully — TestSprite cloud passed. [Code](./TC009_Mark_a_rubric_criterion_not_applicable_and_analyze_successfully.py) · [Run](https://www.testsprite.com/dashboard/mcp/tests/5712335e-72a4-429a-92f2-389ed67fa3fc/test/45f09a53-f1ed-4cb5-b36b-34b0b84e9e7a)
  - ✅ `TC018` Fix missing input validation and complete analysis — TestSprite cloud passed. [Code](./TC018_Fix_missing_input_validation_and_complete_analysis.py) · [Run](https://www.testsprite.com/dashboard/mcp/tests/5712335e-72a4-429a-92f2-389ed67fa3fc/test/41e9f0a0-9b0d-411c-b3c9-e1b44e6d408b)
  - ⚠️ `TC003` Analyze an uploaded PDF and review extracted text before scoring — committed test passes locally with the included synthetic PDF; MCP cloud remained blocked because it did not expose repository fixture paths to its generation agent. [Code](./TC003_Analyze_an_uploaded_PDF_and_review_extracted_text_before_scoring.py) · [Blocked run](https://www.testsprite.com/dashboard/mcp/tests/e826c4fd-c8a9-4d16-81fe-14363b29f903/test/199e9c0e-130f-48f2-92a1-922d4aedd5c0)
  - ⚠️ `TC019` Review extraction quality for a multi-column PDF before analysis — committed test passes locally with the included synthetic PDF; MCP cloud had the same fixture-path limitation. [Code](./TC019_Review_extraction_quality_for_a_multi_column_PDF_before_analysis.py) · [Blocked run](https://www.testsprite.com/dashboard/mcp/tests/e826c4fd-c8a9-4d16-81fe-14363b29f903/test/a56a5267-1a79-4736-a5f2-172bac2664c0)
- **Draft reset**
  - ⚠️ `TC014` Clear a drafted analysis and return to a blank state — committed test passes locally after accepting the confirmation dialog and checking both session-storage keys. The regenerated MCP test failed because it incorrectly treated permanent rubric guidance as stale analysis output. [Code](./TC014_Clear_a_drafted_analysis_and_return_to_a_blank_state.py) · [Misclassified run](https://www.testsprite.com/dashboard/mcp/tests/e826c4fd-c8a9-4d16-81fe-14363b29f903/test/5755751f-bbf8-4a20-86d9-4e92795b1299)
- **Legal information**
  - ✅ `TC020` Review legal information and return to the analyzer — TestSprite cloud passed. [Code](./TC020_Review_legal_information_and_return_to_the_analyzer.py) · [Run](https://www.testsprite.com/dashboard/mcp/tests/5712335e-72a4-429a-92f2-389ed67fa3fc/test/413cdb45-c8e6-4237-923f-45d03a9ec400)
  - ✅ `TC021` Read the privacy policy from the dedicated page — TestSprite cloud passed. [Code](./TC021_Read_the_privacy_policy_from_the_dedicated_page.py) · [Run](https://www.testsprite.com/dashboard/mcp/tests/5712335e-72a4-429a-92f2-389ed67fa3fc/test/4b71a8d0-2723-4fd1-88e0-92e48463b87f)

## 3️⃣ Coverage & Matching Metrics

| Evidence | Passed | Failed | Blocked | Notes |
| --- | ---: | ---: | ---: | --- |
| Initial TestSprite cloud run | 11 | 2 | 2 | 15 generated cases |
| Corrected-case local browser run | 4 | 0 | 0 | Exercises the exact intended flows and included fixtures |
| TestSprite cloud rerun | 1 | 1 | 2 | Confirms TC005; three outcomes are runner/test-generation limitations described above |

- **Committed executable tests:** 15 Python browser scripts across all 7 product areas in the generated suite.
- **Plan-to-code coverage:** 15 of 27 planned cases have executable files (55.6%).
- **Combined behavior evidence:** all 15 committed flows passed either TestSprite cloud or the corrected local browser run.
- **Syntax validation:** all 15 committed Python files parse successfully.

## 4️⃣ Key Gaps / Risks

- The MCP generator cannot attach repository PDF fixtures to its remote agent. The committed GitHub suite resolves fixtures relative to each test file, but the first PR check remains the authoritative proof that the GitHub App exposes those files correctly.
- TestSprite regenerated TC014 with assertions against permanent rubric guidance instead of analysis output. The committed test narrows the assertion to observable reset behavior: empty document, hidden Start-over button, and cleared session draft keys.
- Twelve lower-priority cases remain in the 27-case plan without generated code. They are not required to eliminate “No tests detected,” but should be generated later when TestSprite credits permit.
- TestSprite GitHub App still requires a preview deployment status on each pull request before it can execute tests against that revision.
