# Development draft — E-XMAI research demonstrator

**Working title:** A Transparent Multimodal Demonstrator for Four Chronic-Disease Research Modules

**Author details:** To be completed by the research team. The supplied source PDF
does not identify author names, affiliations, or a publication date.

## Abstract

The supplied research proposal outlines an expandable and explainable framework
for studying diabetes, cardiovascular, renal, and liver diseases using
heterogeneous health information. We translated its initial multi-condition and
multimodal framing into a small local web demonstrator. The application accepts
bounded structured example values and an optional free-text note, computes four
handcrafted illustrative indices, and displays the terms that contribute to
each result. A React and Tailwind CSS frontend communicates with a Flask API;
a synthetic fixture, request validation, API tests, local CSV upload, and a
single lifecycle script support inspection and reproducibility. The available
source is a proposal, not a trained model report. No clinical dataset, fitted
model, or completed evaluation was supplied. Consequently, this work reports no
clinical performance, calibration, explanation fidelity, or generalization
results. Outputs are explicitly marked as unvalidated demonstrations, not
probabilities or diagnoses. The implementation is a transparent software
scaffold from which properly governed validation studies may be planned.

**Keywords:** multimodal health research; explainable AI; software demonstrator;
synthetic data; reproducibility; clinical machine learning

## 1. Introduction

Chronic-disease prediction research must account for more than predictive
accuracy: data provenance, validation design, the meaning of an output, and
the ability to scrutinize a model's reasoning all matter. The supplied
proposal frames these questions across four disease areas and heterogeneous
patient information [1]. It also describes later work on explainability and
incremental extension.

An implementation cannot establish those research claims merely by presenting
a dashboard. Because the supplied bundle contains no runnable model code or
clinical evaluation data, the present deliverable addresses a narrower
question: can the proposal's four-module and multimodal structure be represented
in a small, inspectable application without making unsupported clinical
claims? It provides an explicit local interface and separates what has been
implemented from what remains a research objective.

## 2. Source-derived scope and research questions

The source proposal describes diabetes mellitus, cardiovascular disease,
chronic kidney disease, and chronic liver disease as initial prediction
targets. Demographic, clinical, biochemical, lifestyle, and physiological
information are described as potential inputs. The proposed research
progression distinguishes a common framework, a later expandable/continual
learning study, and an adaptive/personalized stage [1].

This software artifact addresses only a demonstration of the initial
multi-condition interface. It poses two implementation questions:

1. Can the four modules share one validated request and response contract while
   retaining separately inspectable outputs?
2. Can structured example inputs and simple note-text cues be combined with
   visible, traceable contributions and an explicit research-only disclaimer?

These are software questions, not hypotheses about clinical efficacy.

## 3. Demonstrator design

### 3.1 Application components

The frontend is a React single-page application styled with Tailwind CSS. Its
overview displays one illustrative index for each disease module and the
largest associated rule terms. An assessment view accepts example demographic,
anthropometric, biochemical, and lifestyle fields together with an optional
note. Two user-adjustable weights control the structured and note-text
components; the backend normalizes non-negative weights before fusion.

A local Flask API provides health status, synthetic-dataset metadata, CSV
upload validation, and scoring. Requests are checked for supported numeric
ranges and finite values. Imported CSV files are saved with generated names
under the project input directory. They are not loaded by the scoring
endpoint.

### 3.2 Data and scoring boundary

The bundled ten-row table is generated synthetic example data. It supports
interface inspection only and is not a clinical cohort or a model-training
dataset. The scoring code uses transparent handcrafted transformations and
simple exact cue matching against an optional text note. The fused number is
an uncalibrated index between zero and one hundred.

The displayed signed contributions are terms from these rules. They are not
SHAP or LIME attributions, causal effects, counterfactual explanations, or
evidence that a feature increases an individual's disease probability. The
qualitative bands are interface labels and are not medical thresholds.

### 3.3 Reproducibility and software checks

The project includes one setup/start/stop script, a Python unit-test suite, a
JSON API example, and generated screenshots. The input materials and outputs
are kept in dedicated directories. The local service does not require an
external inference API. These measures make this small implementation
inspectable; they do not establish clinical reproducibility or validity.

## 4. Results

The completed artifact contains four independently presented demonstration
modules, a two-modality weight control, local rule-term explanations, input
validation, synthetic data metadata, local CSV storage, API tests, and a
responsive web interface. Its result is an implemented software workflow.

No clinical model was trained or tested. No patient-level or population-level
performance metric is reported. In particular, accuracy, sensitivity,
specificity, F1, AUROC, AUPRC, calibration, subgroup performance, explanation
stability, and continual-learning retention cannot be computed from the
provided materials. Reporting values for these measures would be unsupported.

## 5. Limitations and next research steps

The score rules are not learned from data, calibrated, or validated. The text
component is a small exact-string cue list; it does not understand negation,
temporality, context, or clinical language. The synthetic records do not
represent population prevalence or disease relationships. The application
does not implement model training, SHAP, LIME, counterfactuals, incremental
learning, or a clinically governed deployment.

A subsequent empirical study would need an approved and documented cohort,
prespecified labels and eligibility criteria, leakage-resistant training and
test partitions, missing-data and preprocessing plans, external validation,
calibration and subgroup analyses, and transparent reporting. Explanation
methods would require their own fidelity and stability evaluation. Adding
diseases incrementally would require sequential tasks and explicit
old-task-retention measurements rather than a user-interface switch.

## 6. Conclusion

This work turns a supplied multidisease research proposal into a local
software demonstrator while keeping proposed algorithms and experiments
separate from implemented behavior. Its contribution is an inspectable
application scaffold, not a validated predictor. Clinical use and claims of
predictive or explanatory performance are outside its evidence base.

## Declarations

- **Ethics and consent:** Not applicable to this synthetic software
  demonstration; no human-subject data were used.
- **Data availability:** The bundled example CSV is synthetic. The supplied
  proposal is included in the project input folder.
- **Funding, conflicts, author contributions:** To be completed by the authors.
- **Generative assistance:** The manuscript was drafted with AI assistance
  from the supplied proposal and implementation context. Authors must verify,
  revise, and disclose assistance in accordance with the target journal's
  current policy.

## References

1. *Development of an Expandable Explainable AI Framework for Multimodal
   Prediction of Diabetes, Cardiovascular, Renal and Liver Diseases.* Proposal
   supplied as a project source PDF; author(s), institution, and year were not
   stated in the supplied file.
2. Lundberg SM, Lee SI. A unified approach to interpreting model predictions.
   *Advances in Neural Information Processing Systems.* 2017;30.
3. Ribeiro MT, Singh S, Guestrin C. “Why Should I Trust You?” Explaining the
   Predictions of Any Classifier. In: *Proceedings of the 22nd ACM SIGKDD
   International Conference on Knowledge Discovery and Data Mining*; 2016.
   doi:10.1145/2939672.2939778.

## Change record for the final manuscript

The final version below tightens the abstract, distinguishes the proposal's
research roadmap from the running prototype, labels the score as an
uncalibrated index, adds concrete privacy/evaluation limitations, and records
missing author and ethics metadata rather than inventing it.
