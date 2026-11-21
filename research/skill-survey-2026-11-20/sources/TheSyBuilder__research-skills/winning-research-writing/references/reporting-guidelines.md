# Reporting guidelines

Reporting guidelines tell a reader what a study of a given design must disclose for its results to be appraised. They do not make a study rigorous, repair missing methods, or predict acceptance. Use them to find omissions while drafting methods and results, and when a journal requires a completed checklist.

## Route by design

Always open the current official statement, checklist, and explanation document, plus any extension that fits. The [EQUATOR Network](https://www.equator-network.org/) library is the index. Versions change, so confirm each one on its official site before citing it.

| Study design | Starting guideline | Check also |
| --- | --- | --- |
| Randomized trial, results | CONSORT 2025 | CONSORT-AI for AI interventions, and extensions for cluster, noninferiority, pilot, or harms |
| Randomized trial, protocol | SPIRIT 2025 | SPIRIT-AI |
| Systematic review or meta-analysis | PRISMA 2020 | Extensions for protocols, scoping reviews, searches, and diagnostic accuracy |
| Cohort, case-control, cross-sectional | STROBE | Design-specific and routinely-collected-data extensions |
| Diagnostic accuracy | STARD 2015 | STARD-AI for AI-centered studies |
| Clinical prediction model | TRIPOD+AI | TRIPOD-LLM for healthcare LLM studies within its scope |
| Case report | CARE | Consent requirements |
| In vivo animal research | ARRIVE 2.0 | |
| Quality improvement | SQUIRE 2.0 | |
| Health economic evaluation | CHEERS 2022 | |
| Qualitative research | SRQR | COREQ for interviews and focus groups |
| Machine-learning-based science | REFORMS | The venue's own checklist, such as the NeurIPS paper checklist or the ACL Responsible NLP checklist |

If no guideline fits, search EQUATOR rather than forcing the nearest one. Say which guideline was used and why when the choice is not obvious.

## Record coverage

For each item of the chosen guideline, record one of three states: addressed, with the manuscript location; not applicable, with a reason; or missing. Missing items become author queries or limitations, never invented content. A complete coverage record means each item has a state. It does not mean each item is reported well.

Do not reproduce official checklist wording in the manuscript unless the journal asks for the checklist itself. Keep the record internal unless the author or journal needs it.

## Fit with the argument

Use the guideline to check completeness after the argument is set, not to dictate section order. Where the guideline expects an element the paper's contribution type makes central, such as a participant flow diagram for a trial or a leakage analysis for an ML benchmark, treat it as a candidate figure in [Scientific figures](figures.md).

Adapted in part from the reporting-guideline reference in [K-Dense scientific-writing](https://github.com/K-Dense-AI/claude-scientific-writer), MIT license.
