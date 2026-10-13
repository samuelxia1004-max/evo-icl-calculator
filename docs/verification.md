# Release verification

2026-10-14 · v3.0 research demonstrator

- Raw workbook rerun deterministically reproduced the 399-eye registry, 370-eye complete core model cohort and 341/29 development/time split. Workbook SHA-256 is recorded in the research report; the workbook was neither modified nor committed.
- 13 Node numerical/integrity tests cover an independent Python reference, geometry, missing and malformed values, units, intervals, probabilities, WTW mode, CSV, cohort counts, absence of individual rows and bundle/source agreement.
- Browser regression covers 7 workspaces in Chinese and English, desktop 1440×1050 and mobile 390×844, field/slider changes, both eyes, missing values, PI levels, target bounds, scenarios, follow-up, batch, JSON scenario restoration, consent-gated synthetic sharing, model dialog, report generation, menu behaviour and overflow. No page errors or failed local asset requests.
- Actual PDF.js 4.10.38 extracted synthetic native-text PDF measurements. Actual Tesseract.js 6.0.1 recognized a generated synthetic image with English measurement labels; ACD, LT and both STS fields matched the reference. This is not a clinical report OCR accuracy study; Chinese/noisy images and real device exports still require review.
- Poster rendered as one A0 page (approximately 841×1189 mm). Its header, 6 content blocks, conclusion and footer pass DOM overflow checks; preview was visually inspected. Font licensing is included.
- Screenshots and synthetic printable summaries were generated locally. No clinical input files were used for browser testing.

These checks confirm the research software implementation, not medical-device authorization, ethics approval, causal validity or clinical utility. The exact conference format and clinical metadata remain pending.
