import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const cameraApp = await readFile("src/focuslens/static/app.js", "utf8");

test("camera flow performs local landmark extraction", () => {
  assert.match(cameraApp, /getUserMedia/);
  assert.match(cameraApp, /detectForVideo/);
  assert.match(cameraApp, /\/api\/v1\/analyze/);
});

test("camera flow contains no recording or frame-upload primitive", () => {
  for (const forbidden of ["MediaRecorder", "toDataURL", "FormData", "captureStream", "image/jpeg"] ) {
    assert.equal(cameraApp.includes(forbidden), false, `${forbidden} must not enter the camera pipeline`);
  }
});
