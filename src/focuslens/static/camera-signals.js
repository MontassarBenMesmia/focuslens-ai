const clamp = (value, minimum = 0, maximum = 1) => Math.min(maximum, Math.max(minimum, value));

const average = (values) => values.length
  ? values.reduce((total, value) => total + value, 0) / values.length
  : 0;

const variance = (values) => {
  if (values.length < 2) return 0;
  const center = average(values);
  return average(values.map((value) => (value - center) ** 2));
};

const pointAverage = (landmarks, indexes) => ({
  x: average(indexes.map((index) => landmarks[index]?.x ?? 0)),
  y: average(indexes.map((index) => landmarks[index]?.y ?? 0)),
});

const distance = (first, second) => Math.hypot(first.x - second.x, first.y - second.y);

const blendshapeScore = (categories, name) =>
  categories.find((category) => category.categoryName === name)?.score ?? 0;

export function createSignalTracker(startedAt = performance.now()) {
  return {
    startedAt,
    framesSeen: 0,
    framesWithFace: 0,
    blinkCount: 0,
    eyesClosed: false,
    lastNose: null,
    sums: {
      eye_openness: 0,
      gaze_stability: 0,
      head_alignment: 0,
      mouth_activity: 0,
      movement_level: 0,
      framing_stability: 0,
    },
    gazeX: [],
    gazeY: [],
    frameX: [],
    frameY: [],
    frameSize: [],
  };
}

function keepRecent(values, value, limit = 90) {
  values.push(value);
  if (values.length > limit) values.shift();
}

export function updateSignalTracker(result, tracker, timestamp = performance.now()) {
  tracker.framesSeen += 1;
  const landmarks = result?.faceLandmarks?.[0];
  if (!landmarks || landmarks.length < 478) return summarizeSignals(tracker, timestamp);

  tracker.framesWithFace += 1;
  const categories = result?.faceBlendshapes?.[0]?.categories ?? [];
  const blinkLeft = blendshapeScore(categories, "eyeBlinkLeft");
  const blinkRight = blendshapeScore(categories, "eyeBlinkRight");
  const eyeOpenness = clamp(1 - average([blinkLeft, blinkRight]));
  const currentlyClosed = eyeOpenness < 0.38;
  if (currentlyClosed && !tracker.eyesClosed) tracker.blinkCount += 1;
  tracker.eyesClosed = currentlyClosed;

  const leftEye = pointAverage(landmarks, [33, 133, 159, 145]);
  const rightEye = pointAverage(landmarks, [263, 362, 386, 374]);
  const eyeCenter = {
    x: average([leftEye.x, rightEye.x]),
    y: average([leftEye.y, rightEye.y]),
  };
  const eyeDistance = Math.max(distance(leftEye, rightEye), 0.001);
  const nose = landmarks[1];
  const leftIris = pointAverage(landmarks, [468, 469, 470, 471, 472]);
  const rightIris = pointAverage(landmarks, [473, 474, 475, 476, 477]);
  const irisCenter = {
    x: average([leftIris.x, rightIris.x]),
    y: average([leftIris.y, rightIris.y]),
  };

  keepRecent(tracker.gazeX, (irisCenter.x - eyeCenter.x) / eyeDistance);
  keepRecent(tracker.gazeY, (irisCenter.y - eyeCenter.y) / eyeDistance);
  keepRecent(tracker.frameX, eyeCenter.x);
  keepRecent(tracker.frameY, eyeCenter.y);
  keepRecent(tracker.frameSize, eyeDistance);

  const gazeVariation = Math.sqrt(variance(tracker.gazeX) + variance(tracker.gazeY));
  const gazeStability = clamp(1 - gazeVariation * 10);
  const headAlignment = clamp(1 - Math.abs(nose.x - eyeCenter.x) / (eyeDistance * 0.55));
  const frameVariation = Math.sqrt(variance(tracker.frameX) + variance(tracker.frameY))
    + Math.sqrt(variance(tracker.frameSize));
  const framingStability = clamp(1 - frameVariation * 9);
  const movementLevel = tracker.lastNose
    ? clamp(distance(nose, tracker.lastNose) / eyeDistance * 5)
    : 0;
  tracker.lastNose = { x: nose.x, y: nose.y };
  const mouthActivity = clamp(blendshapeScore(categories, "jawOpen"));

  const frameSignals = {
    eye_openness: eyeOpenness,
    gaze_stability: gazeStability,
    head_alignment: headAlignment,
    mouth_activity: mouthActivity,
    movement_level: movementLevel,
    framing_stability: framingStability,
  };
  for (const [key, value] of Object.entries(frameSignals)) tracker.sums[key] += value;
  return summarizeSignals(tracker, timestamp);
}

export function summarizeSignals(tracker, timestamp = performance.now()) {
  const detected = Math.max(tracker.framesWithFace, 1);
  const elapsedMinutes = Math.max((timestamp - tracker.startedAt) / 60_000, 1 / 60);
  return {
    eye_openness: clamp(tracker.sums.eye_openness / detected),
    gaze_stability: clamp(tracker.sums.gaze_stability / detected),
    head_alignment: clamp(tracker.sums.head_alignment / detected),
    blink_rate: clamp(tracker.blinkCount / elapsedMinutes, 0, 60),
    mouth_activity: clamp(tracker.sums.mouth_activity / detected),
    face_presence: clamp(tracker.framesWithFace / Math.max(tracker.framesSeen, 1)),
    movement_level: clamp(tracker.sums.movement_level / detected),
    framing_stability: clamp(tracker.sums.framing_stability / detected),
  };
}

export { clamp };
