const fields = [
  { key: "eye_openness", label: "Eye openness", min: 0, max: 1, step: 0.01, value: 0.72 },
  { key: "gaze_stability", label: "Gaze stability", min: 0, max: 1, step: 0.01, value: 0.81 },
  { key: "head_alignment", label: "Head alignment", min: 0, max: 1, step: 0.01, value: 0.76 },
  { key: "blink_rate", label: "Blink rate / min", min: 0, max: 60, step: 1, value: 16 },
  { key: "mouth_activity", label: "Mouth activity", min: 0, max: 1, step: 0.01, value: 0.18 },
  { key: "face_presence", label: "Face presence", min: 0, max: 1, step: 0.01, value: 1 },
  { key: "hand_activity", label: "Hand activity", min: 0, max: 1, step: 0.01, value: 0.24 },
  { key: "posture_stability", label: "Posture stability", min: 0, max: 1, step: 0.01, value: 0.79 },
];

const sliderHost = document.querySelector("#sliders");

function displayValue(field, value) {
  return field.key === "blink_rate" ? String(Math.round(value)) : Number(value).toFixed(2);
}

for (const field of fields) {
  const row = document.createElement("div");
  row.className = "slider-row";
  row.innerHTML = `
    <label class="slider-label" for="${field.key}">
      <span>${field.label}</span><output id="${field.key}-value">${displayValue(field, field.value)}</output>
    </label>
    <input id="${field.key}" name="${field.key}" type="range" min="${field.min}" max="${field.max}" step="${field.step}" value="${field.value}" />`;
  sliderHost.appendChild(row);
  row.querySelector("input").addEventListener("input", (event) => {
    row.querySelector("output").value = displayValue(field, event.target.value);
  });
}

document.querySelector("#randomize").addEventListener("click", () => {
  for (const field of fields) {
    const input = document.querySelector(`#${field.key}`);
    const value = field.key === "blink_rate"
      ? Math.round(8 + Math.random() * 28)
      : field.min + Math.random() * (field.max - field.min);
    input.value = value;
    document.querySelector(`#${field.key}-value`).value = displayValue(field, value);
  }
});

document.querySelector("#signal-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = event.currentTarget.querySelector("button[type='submit']");
  button.disabled = true;
  button.textContent = "Analyzing…";
  const payload = Object.fromEntries(fields.map((field) => [field.key, Number(document.querySelector(`#${field.key}`).value)]));
  payload.consent_confirmed = document.querySelector("#consent").checked;
  payload.persist = document.querySelector("#persist").checked;

  try {
    const response = await fetch("/api/v1/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail?.[0]?.msg || data.detail || "Analysis failed");
    renderResult(data);
  } catch (error) {
    document.querySelector("#label").textContent = "Input rejected";
    document.querySelector("#confidence").textContent = error.message;
  } finally {
    button.disabled = false;
    button.innerHTML = "Analyze signals <span>→</span>";
  }
});

function renderResult(data) {
  const percent = Math.round(data.attention_score * 100);
  document.querySelector("#score").textContent = `${percent}%`;
  document.querySelector("#score-ring").style.setProperty("--score-deg", `${percent * 3.6}deg`);
  document.querySelector("#label").textContent = data.attention_label;
  document.querySelector("#confidence").textContent = `${Math.round(data.confidence * 100)}% model confidence`;
  document.querySelector("#energy").textContent = data.energy_signal;
  document.querySelector("#fatigue").textContent = `${Math.round(data.fatigue_signal * 100)}%`;
  document.querySelector("#factors").innerHTML = data.factors
    .map((factor) => `<li><span>${factor.feature.replaceAll("_", " ")}</span><b>${factor.influence}</b></li>`)
    .join("");
}
