# A Transparent Multimodal Demonstrator for Four Chronic-Disease Research Modules

**Manuscript type:** Software / research artifact description  
**Authors and affiliations:** To be supplied and verified by the research team  
**Target journal:** Not specified  
**Version:** Final project draft, 11 October 2026

## Abstract

**Background:** A supplied research proposal describes an expandable and
explainable framework for studying diabetes, cardiovascular, renal, and liver
diseases using heterogeneous health information. Turning such a proposal into
software requires a clear distinction between planned clinical research and
behavior that can actually be inspected.

**Objective:** To implement a local, transparent software demonstrator of the
proposal's four-module and multimodal framing without presenting unvalidated
outputs as clinical predictions.

**Methods:** A React and Tailwind CSS interface communicates with a Flask
application programming interface. Users can enter bounded example values and
an optional free-text note, adjust non-negative modality weights, and inspect
four separately displayed handcrafted indices and their rule contributions.
A small synthetic table supports interface exploration. Request validation,
CSV upload checks, API tests, and a single lifecycle script are included.
Uploaded CSV files are stored locally but are not used by the scoring
endpoint.

**Results:** The delivered artifact implements the interface, local API,
synthetic fixture, validation checks, and contribution display. The supplied
source was a research proposal; it contained no runnable reference
implementation, clinical dataset, trained model, or completed test-set
evaluation. Therefore, this article reports no clinical performance,
calibration, explanation-fidelity, or generalization results.

**Conclusion:** The demonstrator makes a limited software workflow
reproducible and its rule behavior inspectable. Its scores are uncalibrated
illustrative indices, not probabilities, diagnoses, or medical advice. The
implementation is not a clinical decision-support tool and does not implement
the proposal's learned algorithms, SHAP, LIME, counterfactual explanations,
or continual learning.

**Keywords:** multimodal health research; explainable artificial intelligence;
software demonstrator; synthetic data; reproducibility; clinical machine
learning

## 1. Introduction

Chronic-disease prediction research spans data integration, model evaluation,
and communication of uncertainty. A proposal supplied with this project
describes a common framework for diabetes mellitus (DM), cardiovascular
disease (CVD), chronic kidney disease (CKD), and chronic liver disease (CLD),
with demographic, clinical, biochemical, lifestyle, and physiological
information as candidate modalities [1]. It further outlines a research
programme in which model comparison precedes work on incremental expansion
and adaptation.

A software interface alone cannot substantiate predictive validity or
explainability. In the supplied bundle, the source is a proposal rather than
a reproducibility package: no reference implementation, clinical cohort,
fitted parameters, or completed evaluation is provided. This work therefore
addresses a bounded engineering objective: implement an inspectable
four-module demonstration, identify its inputs and rule contributions, and
make the boundary between demonstration and clinical evidence explicit.

The principal contribution is an executable local application with a
structured-input and note-text interface, validated API contracts, a
synthetic example fixture, tests, and reproducible lifecycle commands. It is
not a new clinical prediction method, and it does not evaluate the
effectiveness of machine learning or explanation algorithms.

## 2. Scope and research questions

The supplied proposal motivates four disease areas and heterogeneous patient
information [1]. This demonstrator represents structured measurements and
note text as two user-visible input channels. It supports exploration of the
following software questions:

1. Can four condition-specific outputs share one small local API while
   remaining independently inspectable?
2. Can a user adjust two modality weights and see which handcrafted terms
   contributed to each illustrative output?
3. Can the application expose its data provenance and limitations alongside
   the output?

These questions concern software behavior. They are not claims of clinical
utility, diagnostic accuracy, or explanation fidelity.

## 3. Materials and methods

### 3.1 Application architecture

The single-page user interface is implemented in React and styled with
Tailwind CSS. It provides an overview, a full assessment form, and a data and
methodology view. The local Flask service exposes health and dataset
metadata, a CSV upload endpoint, and a JSON scoring endpoint. During local
development, the frontend proxies API requests to the backend. The project
lifecycle script creates dependencies and starts or stops both services.

### 3.2 Example inputs and data handling

The bundled comma-separated-value (CSV) fixture contains ten synthetic
records with demographic, anthropometric, biochemical, and lifestyle
fields. Synthetic examples are used for interface demonstration only; they
do not train, calibrate, or validate the scoring rules. The assessment form
accepts bounded values for age, body mass index (BMI), glucose, systolic
blood pressure, cholesterol, creatinine, estimated glomerular filtration
rate (eGFR), alanine aminotransferase (ALT), aspartate aminotransferase
(AST), smoking, and alcohol-use indicators, as well as an optional note
limited to 2,000 characters.

CSV uploads are limited to 5 MB, decoded as UTF-8, and checked for required
example columns. Accepted files receive generated filenames and are saved
under the local project input directory. Uploaded data are not read by the
scoring endpoint. The application is not designed or approved to handle
identifiable or clinical patient records.

### 3.3 Illustrative scoring and explanation display

For each condition, the backend applies handcrafted, bounded transformations
to selected structured values and counts matches against a short list of
note-text cues. The two component indices are combined using non-negative
user-supplied weights normalized to sum to one. The displayed output is
clipped to a 0–100 range and accompanied by a qualitative interface band.

The per-feature values displayed in the interface are terms from those
handwritten rules. They are not Shapley Additive exPlanations (SHAP)
attributions, Local Interpretable Model-agnostic Explanations (LIME), causal
effects, or counterfactuals. The text matching does not perform clinical
language understanding and does not account for negation, temporal context,
or uncertainty. Neither the score nor the band has been calibrated or
validated against a health outcome.

### 3.4 Software verification

Backend unit tests cover four-module response structure, note-cue
traceability, normalized weights, invalid values, synthetic dataset
metadata, and CSV header validation. The frontend is built with the existing
Vite build command. A saved JSON example and application screenshots are
included with the project outputs. These checks verify software behavior,
not clinical validity.

## 4. Results

The implementation provides a local interface for four disease modules,
editable example inputs, structured and note-text weighting, ranked
handcrafted contribution terms, synthetic dataset metadata, bounded local CSV
upload, input validation, and a single lifecycle script. A JSON example and
screenshots document the software workflow.

No disease-prediction experiment was performed. There are no supported
estimates for accuracy, precision, recall, F1-score, sensitivity,
specificity, area under the receiver operating characteristic curve
(AUROC), area under the precision-recall curve (AUPRC), calibration,
generalization, subgroup performance, explanation stability, or catastrophic
forgetting. Such values are intentionally omitted rather than inferred from
synthetic records or handcrafted rules.

## 5. Discussion

This artifact translates part of a proposed research architecture into a
working interface while retaining visible traceability between input values,
simple rule terms, and output indices. Its scope is materially narrower than
the supplied programme: it demonstrates modular presentation and adjustable
input fusion but does not implement the proposal's supervised model
comparison or expandable learning experiments.

The distinction matters for interpretation. A polished dashboard can
otherwise encourage readers to mistake a numeric display for a calibrated
clinical probability. This application labels results as illustrative and
reports no patient evidence. Its local upload feature is a file-handling
demonstration only and should not be understood as a data-ingestion path for
clinical inference.

### 5.1 Limitations and future work

The scoring rules are manually specified, use a small cue vocabulary, and
are neither learned nor empirically validated. The synthetic table is not a
representative cohort. No model comparison, clinical evaluation, external
validation, calibration, fairness assessment, uncertainty estimation, or
prospective study was conducted. No SHAP, LIME, counterfactual,
continual-learning, or catastrophic-forgetting method is implemented.

Empirical follow-up would first require lawful access to a defined and
appropriately governed dataset, verified outcome labels, prespecified
eligibility and preprocessing, leakage-resistant data partitioning, and an
independent test set. Any proposed model and explanation technique would
need suitable validation, calibration, subgroup and robustness assessment,
and clear reporting. A sequential-learning study would additionally need
specified task order and measures of both new-task performance and retention
on prior tasks. These are future requirements, not results of the present
artifact.

## 6. Conclusion

The project delivers a reproducible local software demonstrator for
exploring a four-module, two-input-channel interface motivated by a supplied
research proposal. It provides no evidence that its scores predict disease
or support clinical decisions. Further research must establish data
governance, implement and validate fitted models, and evaluate explanations
before any clinical claim or deployment is considered.

## Declarations

- **Ethics approval and consent:** No human-subject dataset was used in this
  software demonstration. Institutional requirements must be determined for
  any subsequent empirical study.
- **Data availability:** The bundled example table is synthetic. The source
  proposal is retained in the project's `input/` directory.
- **Funding:** Not supplied; authors to complete.
- **Conflicts of interest:** Not supplied; authors to complete.
- **Author contributions:** To be completed and approved by the named authors.
- **Acknowledgments:** The supplied source proposal informed the demonstrator
  scope. Authors should acknowledge all contributors as appropriate.
- **Generative-AI disclosure:** AI assistance was used to draft and organize
  this software-artifact manuscript from the supplied source and code
  context. The authors must verify the text, citations, and journal-specific
  disclosure requirements.

## References

1. *Development of an Expandable Explainable AI Framework for Multimodal
   Prediction of Diabetes, Cardiovascular, Renal and Liver Diseases.* Proposal
   supplied as a project source PDF. Author(s), affiliation, and year were
   not stated in the supplied file.
2. Lundberg SM, Lee SI. A unified approach to interpreting model predictions.
   In: *Advances in Neural Information Processing Systems 30*; 2017.
3. Ribeiro MT, Singh S, Guestrin C. “Why Should I Trust You?” Explaining the
   Predictions of Any Classifier. In: *Proceedings of the 22nd ACM SIGKDD
   International Conference on Knowledge Discovery and Data Mining*; 2016.
   doi:10.1145/2939672.2939778.

## Submission-readiness note

This is a journal-style final project draft, not a journal-specific accepted
manuscript. Before submission, the authors must supply verified authorship and
affiliation details, confirm references and permissions, complete required
declarations, select a journal and apply its current formatting and AI-use
policy, and independently run any required similarity/originality checks.
No plagiarism-check outcome or journal acceptance is claimed.
