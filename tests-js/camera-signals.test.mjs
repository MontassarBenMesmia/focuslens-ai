import test from "node:test";
import assert from "node:assert/strict";

import {
  clamp,
  createSignalTracker,
  summarizeSignals,
  updateSignalTracker,
} from "../src/focuslens/static/camera-signals.js";

function fakeResult({ blink = 0.1, jawOpen = 0.15, noseX = 0.5 } = {}) {
  const landmarks = Array.from({ length: 478 }, () => ({ x: 0.5, y: 0.5 }));
  landmarks[1] = { x: noseX, y: 0.58 };
  for (const index of [33, 133, 159, 145]) landmarks[index] = { x: 0.42, y: 0.42 };
  for (const index of [263, 362, 386, 374]) landmarks[index] = { x: 0.58, y: 0.42 };
  for (const index of [468, 469, 470, 471, 472, 473, 474, 475, 476, 477]) {
    landmarks[index] = { x: 0.5, y: 0.42 };
  }
  return {
    faceLandmarks: [landmarks],
    faceBlendshapes: [{ categories: [
      { categoryName: "eyeBlinkLeft", score: blink },
      { categoryName: "eyeBlinkRight", score: blink },
      { categoryName: "jawOpen", score: jawOpen },
    ] }],
  };
}

test("clamp enforces metric boundaries", () => {
  assert.equal(clamp(-0.2), 0);
  assert.equal(clamp(1.2), 1);
});

test("missing faces lower face presence without inventing a frame", () => {
  const tracker = createSignalTracker(0);
  updateSignalTracker({}, tracker, 1_000);
  assert.equal(summarizeSignals(tracker, 1_000).face_presence, 0);
});

test("landmarks become a bounded numeric-only summary", () => {
  const tracker = createSignalTracker(0);
  updateSignalTracker(fakeResult(), tracker, 1_000);
  updateSignalTracker(fakeResult({ blink: 0.9 }), tracker, 2_000);
  const signals = updateSignalTracker(fakeResult(), tracker, 10_000);

  assert.deepEqual(Object.keys(signals), [
    "eye_openness", "gaze_stability", "head_alignment", "blink_rate",
    "mouth_activity", "face_presence", "movement_level", "framing_stability",
  ]);
  assert.equal(signals.face_presence, 1);
  assert.ok(signals.blink_rate > 0);
  for (const [key, value] of Object.entries(signals)) {
    assert.ok(value >= 0, `${key} should be non-negative`);
    assert.ok(value <= (key === "blink_rate" ? 60 : 1), `${key} should be bounded`);
  }
});
