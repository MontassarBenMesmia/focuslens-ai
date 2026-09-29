import { createSignalTracker, updateSignalTracker } from "/static/camera-signals.js";

const fields = [
  { key: "eye_openness", label: "Eye openness", min: 0, max: 1, step: 0.01, value: 0.72 },
  { key: "gaze_stability", label: "Gaze stability", min: 0, max: 1, step: 0.01, value: 0.81 },
  { key: "head_alignment", label: "Head alignment", min: 0, max: 1, step: 0.01, value: 0.76 },
  { key: "blink_rate", label: "Blink rate / min", min: 0, max: 60, step: 1, value: 16 },
  { key: "mouth_activity", label: "Mouth activity", min: 0, max: 1, step: 0.01, value: 0.18 },
  { key: "face_presence", label: "Face presence", min: 0, max: 1, step: 0.01, value: 1 },
  { key: "movement_level", label: "Movement level", min: 0, max: 1, step: 0.01, value: 0.24 },
  { key: "framing_stability", label: "Framing stability", min: 0, max: 1, step: 0.01, value: 0.79 },
];

const CAMERA_DURATION_MS = 10_000;
const MEDIAPIPE_MODULE = "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@1.0.1/vision_bundle.mjs";
const MEDIAPIPE_WASM = "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@1.0.1/wasm";
const FACE_MODEL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task";

const sliderHost = document.querySelector("#sliders");
const cameraButton = document.querySelector("#camera-start");
const stopButton = document.querySelector("#camera-stop");
const cameraStatus = document.querySelector("#camera-status");
const cameraProgress = document.querySelector("#camera-progress");
const video = document.querySelector("#camera-preview");
let faceLandmarker;
let cameraStream;
let animationFrame;
let cameraRunning = false;
let nextManualSource = "manual";

function displayValue(field, value) {
  return field.key === "blink_rate" ? String(Math.round(value)) : Number(value).toFixed(2);
}

function setFieldValue(field, value) {
  const bounded = Math.min(field.max, Math.max(field.min, Number(value)));
  const input = document.querySelector(`#${field.key}`);
  input.value = bounded;
  document.querySelector(`#${field.key}-value`).value = displayValue(field, bounded);
}

function applySignals(signals) {
  for (const field of fields) setFieldValue(field, signals[field.key]);
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
    nextManualSource = "manual";
  });
}

document.querySelector("#randomize").addEventListener("click", () => {
  for (const field of fields) {
    const value = field.key === "blink_rate"
      ? Math.round(8 + Math.random() * 28)
      : field.min + Math.random() * (field.max - field.min);
    setFieldValue(field, value);
  }
  nextManualSource = "synthetic";
  cameraStatus.textContent = "Synthetic sample ready. Review the sliders, then analyze.";
});

function requirementsConfirmed() {
  return document.querySelector("#consent").checked
    && document.querySelector("#adult-self-use").checked;
}

async function loadLandmarker() {
  if (faceLandmarker) return faceLandmarker;
  cameraStatus.textContent = "Loading the on-device vision model…";
  const { FaceLandmarker, FilesetResolver } = await import(MEDIAPIPE_MODULE);
  const fileset = await FilesetResolver.forVisionTasks(MEDIAPIPE_WASM);
  const options = {
    baseOptions: { modelAssetPath: FACE_MODEL, delegate: "GPU" },
    runningMode: "VIDEO",
    numFaces: 1,
    outputFaceBlendshapes: true,
    outputFacialTransformationMatrixes: false,
    minFaceDetectionConfidence: 0.6,
    minFacePresenceConfidence: 0.6,
    minTrackingConfidence: 0.6,
  };
  try {
    faceLandmarker = await FaceLandmarker.createFromOptions(fileset, options);
  } catch {
    options.baseOptions.delegate = "CPU";
    faceLandmarker = await FaceLandmarker.createFromOptions(fileset, options);
  }
  return faceLandmarker;
}

function stopCamera(message = "Camera stopped. No frame was uploaded or stored.") {
  cameraRunning = false;
  if (animationFrame) cancelAnimationFrame(animationFrame);
  animationFrame = undefined;
  cameraStream?.getTracks().forEach((track) => track.stop());
  cameraStream = undefined;
  video.srcObject = null;
  video.classList.remove("active");
  cameraButton.disabled = false;
  stopButton.disabled = true;
  cameraProgress.style.width = "0%";
  cameraStatus.textContent = message;
}

cameraButton.addEventListener("click", async () => {
  if (!requirementsConfirmed()) {
    cameraStatus.textContent = "Confirm consent and adult self-use before starting the camera.";
    return;
  }
  if (!navigator.mediaDevices?.getUserMedia) {
    cameraStatus.textContent = "Camera access requires localhost or an HTTPS deployment in a supported browser.";
    return;
  }

  cameraButton.disabled = true;
  try {
    const landmarker = await loadLandmarker();
    cameraStream = await navigator.mediaDevices.getUserMedia({
      audio: false,
      video: { facingMode: "user", width: { ideal: 960 }, height: { ideal: 540 } },
    });
    video.srcObject = cameraStream;
    await video.play();
    video.classList.add("active");
    stopButton.disabled = false;
    cameraRunning = true;

    const startedAt = performance.now();
    const tracker = createSignalTracker(startedAt);
    let lastVideoTime = -1;
    cameraStatus.textContent = "Measuring locally for 10 seconds. Look naturally at your screen.";

    const processFrame = async () => {
      if (!cameraRunning) return;
      const now = performance.now();
      if (video.currentTime !== lastVideoTime) {
        lastVideoTime = video.currentTime;
        const result = landmarker.detectForVideo(video, now);
        applySignals(updateSignalTracker(result, tracker, now));
      }
      const elapsed = now - startedAt;
      cameraProgress.style.width = `${Math.min(100, elapsed / CAMERA_DURATION_MS * 100)}%`;
      if (elapsed >= CAMERA_DURATION_MS) {
        stopCamera("Local measurement complete. Sending only the numeric summary for analysis.");
        await analyzeSignals("camera", CAMERA_DURATION_MS / 1000);
        return;
      }
      animationFrame = requestAnimationFrame(processFrame);
    };
    animationFrame = requestAnimationFrame(processFrame);
  } catch (error) {
    stopCamera(`Camera unavailable: ${error.message}`);
  }
});

stopButton.addEventListener("click", () => stopCamera());
window.addEventListener("pagehide", () => stopCamera("Camera stopped."));

document.querySelector("#signal-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  await analyzeSignals(nextManualSource, 10);
});

async function analyzeSignals(source, observationWindowSeconds) {
  const button = document.querySelector("#analyze-button");
  button.disabled = true;
  button.textContent = "Analyzing…";
  const payload = Object.fromEntries(
    fields.map((field) => [field.key, Number(document.querySelector(`#${field.key}`).value)]),
  );
  payload.source = source;
  payload.observation_window_seconds = observationWindowSeconds;
  payload.consent_confirmed = document.querySelector("#consent").checked;
  payload.adult_self_use_confirmed = document.querySelector("#adult-self-use").checked;
  payload.persist = document.querySelector("#persist").checked;

  try {
    const response = await fetch("/api/v1/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail?.[0]?.msg || data.detail || "Analysis failed");
    renderResult(data, source);
  } catch (error) {
    document.querySelector("#label").textContent = "Input rejected";
    document.querySelector("#confidence").textContent = error.message;
  } finally {
    button.disabled = false;
    button.innerHTML = "Analyze numeric signals <span>→</span>";
  }
}

function renderResult(data, source) {
  const percent = Math.round(data.stability_score * 100);
  document.querySelector("#score").textContent = `${percent}%`;
  document.querySelector("#score-ring").style.setProperty("--score-deg", `${percent * 3.6}deg`);
  document.querySelector("#label").textContent = data.session_label;
  document.querySelector("#confidence").textContent = `${Math.round(data.confidence * 100)}% model confidence · ${source}`;
  document.querySelector("#quality").textContent = `${Math.round(data.signal_quality * 100)}%`;
  document.querySelector("#source").textContent = source;
  document.querySelector("#factors").innerHTML = data.factors
    .map((factor) => `<li><span>${factor.feature.replaceAll("_", " ")}</span><b>${factor.influence}</b></li>`)
    .join("");
}
