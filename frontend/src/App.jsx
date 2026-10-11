import { useEffect, useMemo, useState } from "react";

const DEFAULTS = {
  age: 52,
  bmi: 27,
  glucose: 105,
  systolic_bp: 122,
  cholesterol: 190,
  creatinine: 0.9,
  egfr: 95,
  alt: 28,
  ast: 26,
  smoking: 0,
  alcohol_use: 0,
  clinical_note: "",
  clinical_weight: 75,
  text_weight: 25,
};

const EXAMPLE = {
  age: 63,
  bmi: 31.2,
  glucose: 142,
  systolic_bp: 146,
  cholesterol: 238,
  creatinine: 1.5,
  egfr: 58,
  alt: 48,
  ast: 38,
  smoking: 1,
  alcohol_use: 0,
  clinical_note: "Reports frequent urination and excessive thirst. Blood pressure elevated at recent visit.",
  clinical_weight: 75,
  text_weight: 25,
};

const NAV_ITEMS = [
  { id: "overview", label: "Risk overview", icon: "◫" },
  { id: "assessment", label: "Patient assessment", icon: "＋" },
  { id: "data", label: "Data & methodology", icon: "▤" },
];

function Icon({ children, className = "" }) {
  return <span aria-hidden="true" className={`inline-grid place-items-center ${className}`}>{children}</span>;
}

function Field({ label, name, unit, value, onChange, min, max, step = 1 }) {
  return (
    <label className="block">
      <span className="mb-1.5 flex items-center justify-between text-[12px] font-semibold text-ink-700">
        <span>{label}</span>
        {unit && <span className="font-normal text-ink-400">{unit}</span>}
      </span>
      <input
        className="field"
        type="number"
        name={name}
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={onChange}
        required
      />
    </label>
  );
}

function RiskCard({ item, selected, onSelect }) {
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`risk-card ${selected ? "risk-card-selected" : ""}`}
      style={{ "--disease": item.color }}
      aria-pressed={selected}
    >
      <div className="flex items-start justify-between">
        <div>
          <span className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink-400">{item.short}</span>
          <h3 className="mt-1 text-[15px] font-semibold text-ink-900">{item.name}</h3>
        </div>
        <span className="risk-dot" />
      </div>
      <div className="mt-5 flex items-end justify-between">
        <div className="flex items-baseline gap-1">
          <span className="text-[34px] font-semibold leading-none tracking-[-0.06em] text-ink-900">{item.score}</span>
          <span className="text-[12px] text-ink-400">/ 100</span>
        </div>
        <span className={`risk-label ${item.band.toLowerCase()}`}>{item.band}</span>
      </div>
      <div className="score-track mt-3"><span style={{ width: `${item.score}%`, background: item.color }} /></div>
      <p className="mt-3 text-[11px] text-ink-400">Illustrative index · not a probability</p>
    </button>
  );
}

function App() {
  const [page, setPage] = useState(() => {
    const hash = window.location.hash.slice(1);
    return ["overview", "assessment", "data"].includes(hash) ? hash : "overview";
  });
  const [form, setForm] = useState(DEFAULTS);
  const [prediction, setPrediction] = useState(null);
  const [dataset, setDataset] = useState(null);
  const [service, setService] = useState("checking");
  const [selectedKey, setSelectedKey] = useState("diabetes");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [uploadStatus, setUploadStatus] = useState("");

  useEffect(() => {
    fetch("/api/health")
      .then((response) => {
        if (!response.ok) throw new Error("API health check failed.");
        return response.json();
      })
      .then(() => setService("online"))
      .catch(() => setService("offline"));
    fetch("/api/dataset")
      .then((response) => {
        if (!response.ok) throw new Error("Dataset information could not be loaded.");
        return response.json();
      })
      .then(setDataset)
      .catch(() => setDataset(null));
    requestPrediction(DEFAULTS);
  }, []);

  async function requestPrediction(values) {
    setBusy(true);
    setError("");
    try {
      const payload = {
        ...values,
        clinical_weight: Number(values.clinical_weight),
        text_weight: Number(values.text_weight),
      };
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.error || "The assessment could not be calculated.");
      setPrediction(body);
      if (!body.results.some((item) => item.key === selectedKey)) setSelectedKey(body.results[0]?.key);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy(false);
    }
  }

  function updateField(event) {
    const { name, value, type, checked } = event.target;
    setForm((current) => ({ ...current, [name]: type === "checkbox" ? Number(checked) : value }));
  }

  function submitAssessment(event) {
    event.preventDefault();
    requestPrediction(form);
    setPage("overview");
  }

  const selected = useMemo(
    () => prediction?.results.find((item) => item.key === selectedKey) ?? prediction?.results[0],
    [prediction, selectedKey],
  );

  async function uploadCsv(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploadStatus("");
    const data = new FormData();
    data.append("file", file);
    try {
      const response = await fetch("/api/dataset/upload", { method: "POST", body: data });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || "Upload failed.");
      setUploadStatus(`${result.name} · ${result.rows} rows. Saved locally; not used by the demo scoring rules.`);
    } catch (uploadError) {
      setUploadStatus(uploadError.message);
    }
    event.target.value = "";
  }

  return (
    <div className="min-h-screen bg-canvas text-ink-900">
      <aside className="sidebar fixed inset-y-0 left-0 z-20 hidden w-[250px] flex-col border-r border-white/10 bg-sidebar px-4 py-5 lg:flex">
        <div className="flex items-center gap-3 px-1">
          <div className="brand-mark"><span>e</span><i>+</i></div>
          <div>
            <div className="text-[15px] font-semibold tracking-tight text-white">E-XMAI</div>
            <div className="mt-0.5 text-[10px] uppercase tracking-[0.15em] text-slate-400">Research workspace</div>
          </div>
        </div>
        <div className="my-7 border-t border-white/10" />
        <p className="mb-2 px-2 text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">Workspace</p>
        <nav className="space-y-1">
          {NAV_ITEMS.map((item) => (
            <button key={item.id} type="button" onClick={() => setPage(item.id)} className={`nav-item ${page === item.id ? "nav-item-active" : ""}`}>
              <Icon className="w-5 text-[17px]">{item.icon}</Icon>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>
        <div className="mt-auto rounded-xl border border-white/10 bg-white/[0.04] p-3.5">
          <div className="flex items-center gap-2 text-[11px] font-medium text-slate-200">
            <span className={`status-dot ${service}`} />
            API {service === "checking" ? "checking" : service}
          </div>
          <p className="mt-2 text-[10px] leading-relaxed text-slate-500">Local prototype · no patient data leaves this machine.</p>
        </div>
      </aside>

      <div className="lg:pl-[250px]">
        <header className="sticky top-0 z-10 flex h-[72px] items-center justify-between border-b border-ink-100 bg-white/90 px-5 backdrop-blur md:px-8">
          <div>
            <div className="flex items-center gap-2 text-[11px] font-medium text-ink-400">
              <span>Workspace</span><span>/</span><span className="text-ink-600">{NAV_ITEMS.find((item) => item.id === page)?.label}</span>
            </div>
            <h1 className="mt-1 text-[15px] font-semibold tracking-tight text-ink-900">Multimodal health research</h1>
          </div>
          <div className="hidden items-center gap-2 rounded-full border border-amber-200 bg-amber-50 px-3 py-1.5 text-[10px] font-semibold text-amber-800 sm:flex">
            <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
            RESEARCH DEMO — NOT FOR CLINICAL USE
          </div>
          <nav className="flex gap-1 lg:hidden">
            {NAV_ITEMS.map((item) => <button key={item.id} type="button" className={`mobile-nav ${page === item.id ? "mobile-nav-active" : ""}`} onClick={() => setPage(item.id)}>{item.label}</button>)}
          </nav>
        </header>

        <main className="mx-auto max-w-[1420px] px-4 py-6 md:px-8 md:py-8">
          {error && <div role="alert" className="mb-5 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</div>}
          {page === "overview" && (
            <>
              <section className="mb-7 flex flex-wrap items-end justify-between gap-4">
                <div>
                  <p className="eyebrow">Expandable explainable AI framework</p>
                  <h2 className="mt-2 text-[26px] font-semibold tracking-[-0.04em] text-ink-950 md:text-[32px]">Four conditions. One clear view.</h2>
                  <p className="mt-2 max-w-2xl text-[13px] leading-relaxed text-ink-500">Explore an illustrative fusion of structured clinical measures and note-text cues, with a visible explanation for each output.</p>
                </div>
                <button type="button" className="button-primary" onClick={() => { setForm(EXAMPLE); requestPrediction(EXAMPLE); }}>Load example patient <span aria-hidden="true">↗</span></button>
              </section>

              <div className="alert-banner mb-6">
                <span className="alert-icon">i</span>
                <p><strong>Research prototype, not a diagnostic tool.</strong> Scores are uncalibrated demonstrations, not probabilities or validated predictions. Do not use them for care decisions.</p>
              </div>

              <section aria-label="Illustrative disease scores" className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                {(prediction?.results ?? []).map((item) => (
                  <RiskCard key={item.key} item={item} selected={selectedKey === item.key} onSelect={() => setSelectedKey(item.key)} />
                ))}
                {!prediction && [1, 2, 3, 4].map((item) => <div key={item} className="h-[166px] animate-pulse rounded-xl bg-white" />)}
              </section>

              <div className="mt-6 grid gap-5 xl:grid-cols-[minmax(0,1.45fr)_minmax(330px,0.85fr)]">
                <section className="panel p-5 md:p-6">
                  <div className="flex flex-wrap items-start justify-between gap-3 border-b border-ink-100 pb-4">
                    <div>
                      <p className="eyebrow">Local explanation</p>
                      <h3 className="mt-1.5 text-[18px] font-semibold text-ink-900">{selected?.name ?? "Waiting for assessment"} <span className="text-ink-300">·</span> contributing signals</h3>
                    </div>
                    <span className="rounded-md bg-mint-50 px-2.5 py-1.5 text-[10px] font-semibold text-mint-800">Illustrative additive cues</span>
                  </div>
                  {selected ? (
                    <div className="pt-4">
                      {selected.contributions.length ? selected.contributions.map((item, index) => (
                        <div key={`${item.feature}-${index}`} className="contribution-row">
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center justify-between gap-3">
                              <span className="truncate text-[12px] font-medium text-ink-700">{item.feature}</span>
                              <span className="shrink-0 text-[11px] font-semibold tabular-nums text-ink-600">{item.contribution > 0 ? "+" : ""}{item.contribution} pts</span>
                            </div>
                            <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-ink-50">
                              <div className={`h-full rounded-full ${item.contribution < 0 ? "bg-teal-500" : "bg-coral-400"}`} style={{ width: `${Math.min(100, Math.max(5, Math.abs(item.contribution) * 2.7))}%` }} />
                            </div>
                          </div>
                          <span className="ml-3 w-[58px] rounded bg-ink-50 px-1.5 py-1 text-center text-[9px] font-semibold uppercase tracking-wide text-ink-500">{item.modality}</span>
                        </div>
                      )) : <p className="py-8 text-center text-[12px] text-ink-400">No explanatory cues returned.</p>}
                      <div className="mt-4 grid grid-cols-2 gap-3 rounded-lg bg-canvas p-3.5">
                        <div><p className="text-[10px] font-medium uppercase tracking-wide text-ink-400">Clinical modality</p><p className="mt-1 text-[19px] font-semibold text-ink-800">{selected.clinical_score}<span className="ml-1 text-[11px] font-normal text-ink-400">index</span></p></div>
                        <div><p className="text-[10px] font-medium uppercase tracking-wide text-ink-400">Note-text modality</p><p className="mt-1 text-[19px] font-semibold text-ink-800">{selected.text_score}<span className="ml-1 text-[11px] font-normal text-ink-400">index</span></p></div>
                      </div>
                    </div>
                  ) : <p className="py-10 text-center text-sm text-ink-400">Submit the assessment to view an explanation.</p>}
                </section>

                <AssessmentPanel form={form} updateField={updateField} onSubmit={submitAssessment} busy={busy} setPage={setPage} />
              </div>
              <p className="mt-5 text-center text-[10px] leading-relaxed text-ink-400">Rule-based demonstration only · no trained or clinically validated model · explanation cues are not SHAP/LIME values.</p>
            </>
          )}
          {page === "assessment" && <FullAssessment form={form} updateField={updateField} onSubmit={submitAssessment} busy={busy} />}
          {page === "data" && <DataPage dataset={dataset} onUpload={uploadCsv} uploadStatus={uploadStatus} />}
        </main>
      </div>
    </div>
  );
}

function AssessmentPanel({ form, updateField, onSubmit, busy, setPage }) {
  return (
    <section className="panel overflow-hidden">
      <div className="border-b border-ink-100 px-5 py-4">
        <p className="eyebrow">Assessment input</p>
        <h3 className="mt-1 text-[17px] font-semibold text-ink-900">Patient snapshot</h3>
      </div>
      <form onSubmit={onSubmit} className="space-y-4 p-5">
        <div className="grid grid-cols-2 gap-3">
          <Field label="Age" name="age" unit="years" min={18} max={110} value={form.age} onChange={updateField} />
          <Field label="BMI" name="bmi" unit="kg/m²" min={10} max={80} step={0.1} value={form.bmi} onChange={updateField} />
          <Field label="Glucose" name="glucose" unit="mg/dL" min={30} max={600} value={form.glucose} onChange={updateField} />
          <Field label="Systolic BP" name="systolic_bp" unit="mmHg" min={60} max={260} value={form.systolic_bp} onChange={updateField} />
        </div>
        <label className="block">
          <span className="mb-1.5 flex justify-between text-[12px] font-semibold text-ink-700"><span>Clinical note</span><span className="font-normal text-ink-400">text modality</span></span>
          <textarea className="field min-h-[72px] resize-y" name="clinical_note" maxLength={2000} value={form.clinical_note} onChange={updateField} placeholder="Enter a de-identified research note..." />
        </label>
        <div>
          <div className="mb-2 flex items-center justify-between"><span className="text-[12px] font-semibold text-ink-700">Modality fusion</span><span className="text-[10px] text-ink-400">normalized on submit</span></div>
          <WeightSlider label="Clinical" name="clinical_weight" value={form.clinical_weight} onChange={updateField} color="bg-teal-600" />
          <WeightSlider label="Note text" name="text_weight" value={form.text_weight} onChange={updateField} color="bg-coral-400" />
        </div>
        <button type="submit" disabled={busy} className="button-primary w-full justify-center">{busy ? "Calculating…" : "Update illustrative scores"} <span aria-hidden="true">→</span></button>
        <button type="button" onClick={() => setPage("assessment")} className="w-full py-1 text-center text-[11px] font-medium text-ink-500 hover:text-ink-800">Edit all clinical features</button>
      </form>
    </section>
  );
}

function WeightSlider({ label, name, value, onChange, color }) {
  return (
    <label className="mb-2 grid grid-cols-[66px_1fr_38px] items-center gap-2">
      <span className="text-[10px] text-ink-500">{label}</span>
      <input className={`weight-slider ${color}`} type="range" min="0" max="100" step="5" name={name} value={value} onChange={onChange} aria-label={`${label} modality weight`} />
      <span className="text-right text-[10px] tabular-nums text-ink-500">{value}%</span>
    </label>
  );
}

function FullAssessment({ form, updateField, onSubmit, busy }) {
  const groups = [
    { title: "Demographic", fields: [["age", "Age", "years", 18, 110, 1]] },
    { title: "Anthropometric", fields: [["bmi", "Body mass index", "kg/m²", 10, 80, 0.1]] },
    { title: "Clinical & cardiovascular", fields: [["glucose", "Blood glucose", "mg/dL", 30, 600, 1], ["systolic_bp", "Systolic blood pressure", "mmHg", 60, 260, 1], ["cholesterol", "Total cholesterol", "mg/dL", 50, 600, 1]] },
    { title: "Renal & hepatic biomarkers", fields: [["creatinine", "Creatinine", "mg/dL", 0.1, 30, 0.1], ["egfr", "eGFR", "mL/min/1.73m²", 1, 160, 1], ["alt", "ALT", "U/L", 1, 3000, 1], ["ast", "AST", "U/L", 1, 3000, 1]] },
  ];
  return (
    <section>
      <p className="eyebrow">Research input</p>
      <h2 className="mt-2 text-[27px] font-semibold tracking-tight text-ink-950">Patient assessment</h2>
      <p className="mt-1 text-sm text-ink-500">All fields are local, illustrative signals. Use synthetic or de-identified values only.</p>
      <form onSubmit={onSubmit} className="mt-6 grid gap-5 xl:grid-cols-[minmax(0,1fr)_340px]">
        <div className="grid gap-4 sm:grid-cols-2">
          {groups.map((group) => <div key={group.title} className="panel p-5"><h3 className="mb-4 text-sm font-semibold text-ink-800">{group.title}</h3><div className="grid gap-3">{group.fields.map(([name, label, unit, min, max, step]) => <Field key={name} {...{ name, label, unit, min, max, step }} value={form[name]} onChange={updateField} />)}</div></div>)}
          <div className="panel p-5 sm:col-span-2">
            <h3 className="mb-4 text-sm font-semibold text-ink-800">Lifestyle & narrative</h3>
            <div className="mb-4 grid gap-4 sm:grid-cols-2">
              <ToggleField label="Smoking recorded" name="smoking" checked={Number(form.smoking) === 1} onChange={updateField} />
              <ToggleField label="Alcohol use recorded" name="alcohol_use" checked={Number(form.alcohol_use) === 1} onChange={updateField} />
            </div>
            <label className="block"><span className="mb-1.5 block text-xs font-semibold text-ink-700">De-identified clinical note <span className="font-normal text-ink-400">(text modality)</span></span><textarea className="field min-h-28" name="clinical_note" maxLength={2000} value={form.clinical_note} onChange={updateField} placeholder="Describe relevant findings or symptoms for the demonstration..." /></label>
            <div className="mt-5 grid gap-4 sm:grid-cols-2"><WeightSlider label="Clinical" name="clinical_weight" value={form.clinical_weight} onChange={updateField} color="bg-teal-600" /><WeightSlider label="Note text" name="text_weight" value={form.text_weight} onChange={updateField} color="bg-coral-400" /></div>
          </div>
        </div>
        <aside className="panel h-fit p-5 xl:sticky xl:top-24">
          <div className="eyebrow">Before you run</div><h3 className="mt-2 text-base font-semibold text-ink-900">Demo scoring only</h3>
          <p className="mt-2 text-xs leading-relaxed text-ink-500">Four transparent, handcrafted scoring rules combine bounded clinical values with keyword matches. No model training, calibration, clinical validation, or protected health information handling is implemented.</p>
          <button type="submit" disabled={busy} className="button-primary mt-5 w-full justify-center">{busy ? "Calculating…" : "Calculate demonstration" } <span aria-hidden="true">→</span></button>
        </aside>
      </form>
    </section>
  );
}

function ToggleField({ label, name, checked, onChange }) {
  return <label className="flex cursor-pointer items-center justify-between rounded-lg border border-ink-100 px-3 py-2.5 text-xs font-medium text-ink-700"><span>{label}</span><input type="checkbox" name={name} checked={checked} onChange={onChange} className="h-4 w-4 accent-teal-700" /></label>;
}

function DataPage({ dataset, onUpload, uploadStatus }) {
  const info = [
    ["Source", "Project-provided research proposal"],
    ["Modalities", "Structured clinical values + note text"],
    ["Disease modules", "Diabetes · Cardiovascular · Renal · Liver"],
    ["Explanation", "Transparent handcrafted score contributions"],
    ["Validation", "No clinical validation or performance results"],
    ["Extendability", "Incremental learning is future research scope"],
  ];
  return (
    <section>
      <p className="eyebrow">Research transparency</p>
      <h2 className="mt-2 text-[27px] font-semibold tracking-tight text-ink-950">Data & methodology</h2>
      <p className="mt-1 max-w-2xl text-sm leading-relaxed text-ink-500">A reproducible demonstration scaffold, not a reproduction of a trained or evaluated clinical framework.</p>
      <div className="mt-6 grid gap-5 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="panel p-5 md:p-6">
          <div className="eyebrow">Example dataset</div><h3 className="mt-1.5 text-lg font-semibold text-ink-900">Synthetic patient records</h3>
          <p className="mt-2 text-xs leading-relaxed text-ink-500">{dataset?.use ?? "Example records are bundled locally and are not used for training."}</p>
          <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3">
            <Stat label="Rows" value={dataset?.rows ?? "—"} />
            <Stat label="Fields" value={dataset?.columns?.length ?? "—"} />
            <Stat label="Record type" value="Synthetic" />
          </div>
          <h4 className="mb-2 mt-6 text-xs font-semibold text-ink-700">Included measures</h4>
          <div className="flex flex-wrap gap-2">{(dataset?.columns ?? []).filter((column) => column !== "record_id").map((column) => <span key={column} className="rounded-md bg-canvas px-2 py-1 text-[10px] text-ink-500">{column.replaceAll("_", " ")}</span>)}</div>
          <div className="mt-6 border-t border-ink-100 pt-5">
            <label className="button-secondary inline-flex cursor-pointer items-center gap-2">Upload research CSV <span aria-hidden="true">↑</span><input className="sr-only" type="file" accept=".csv,text/csv" onChange={onUpload} /></label>
            <p className="mt-2 text-[10px] leading-relaxed text-ink-400">Max 5 MB · expected columns: age, bmi, glucose, systolic_bp. Stored locally only. Upload does not change demonstration scoring.</p>
            {uploadStatus && <p role="status" className="mt-3 break-words rounded bg-canvas px-3 py-2 text-[11px] text-ink-600">{uploadStatus}</p>}
          </div>
        </div>
        <div className="panel p-5 md:p-6">
          <div className="eyebrow">Framework mapping</div><h3 className="mt-1.5 text-lg font-semibold text-ink-900">What this prototype implements</h3>
          <div className="mt-5 space-y-4">
            {info.map(([label, value], index) => <div key={label} className="flex gap-3 border-b border-ink-50 pb-3 last:border-0"><span className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-mint-50 text-[10px] font-semibold text-mint-800">{String(index + 1).padStart(2, "0")}</span><div><p className="text-[11px] font-semibold text-ink-700">{label}</p><p className="mt-0.5 text-[11px] leading-relaxed text-ink-500">{value}</p></div></div>)}
          </div>
        </div>
      </div>
      <div className="mt-5 rounded-xl border border-ink-100 bg-white p-5">
        <h3 className="text-sm font-semibold text-ink-800">Research limitations surfaced by design</h3>
        <ul className="mt-3 grid gap-2 text-[11px] leading-relaxed text-ink-500 md:grid-cols-2">
          <li>• Scores are handcrafted indices; no model was fitted to patient records.</li>
          <li>• No AUROC, F1, calibration, generalization, or forgetting measurements are reported.</li>
          <li>• Cue contributions are not SHAP, LIME, or counterfactual explanations.</li>
          <li>• Continual learning and adding disease modules remain proposed future work.</li>
        </ul>
      </div>
    </section>
  );
}

function Stat({ label, value }) {
  return <div className="rounded-lg bg-canvas px-3 py-2.5"><p className="text-[9px] font-semibold uppercase tracking-wide text-ink-400">{label}</p><p className="mt-1 text-[17px] font-semibold text-ink-800">{value}</p></div>;
}

export default App;
