# Cat Cam — Test Plan

Concrete, repeatable test procedures that verify the acceptance criteria in
[ACCEPTANCE-CRITERIA.md](ACCEPTANCE-CRITERIA.md). Each test lists preconditions,
exact steps, and the expected result. Record the outcome in the results log at
the bottom.

Status values: **Pass** · **Fail** · **Blocked** · **N/A** · **Not run**

---

## How to use this plan

1. Work top-down; earlier suites are prerequisites for later ones.
2. Run each test, compare actual vs. expected, and mark status + date + notes in
   the [Results Log](#results-log).
3. Any **Fail** should be logged as a defect (see [Defect Log](#defect-log)) and
   re-tested after a fix.
4. A test run is "green" when all MVP (🟢) tests Pass.

**Test environment to record for each run:**
- Pi OS version / kernel:
- MediaMTX version:
- Webcam model / speaker model:
- Test client (phone/laptop) + browser version:
- Network (home Wi-Fi / mobile data / Tailscale):

---

## Suite 1 — Base Setup & Devices 🟢

### T1.1 — SSH key login (AC1.1)
- **Pre:** Pi powered, on network, SSH key added.
- **Steps:** From laptop run `ssh <user>@<pi-host>`.
- **Expected:** Shell prompt appears without a password prompt.

### T1.2 — Camera enumeration (AC1.2)
- **Pre:** Webcam plugged in.
- **Steps:** Run `v4l2-ctl --list-devices`.
- **Expected:** Camera listed with a `/dev/video*` node. Record the node.

### T1.3 — Mic capture round-trip (AC1.3)
- **Pre:** Webcam mic connected; speaker working.
- **Steps:** `arecord -l`; then
  `arecord -d 5 -f cd test.wav && aplay test.wav` while making noise.
- **Expected:** Capture device listed; playback contains the recorded sound.

### T1.4 — Speaker output (AC1.4)
- **Pre:** Speaker connected.
- **Steps:** Run `speaker-test -t wav -c 2`; stop with Ctrl-C.
- **Expected:** Clear sound audible in the room from expected channels.

---

## Suite 2 — Live Video 🟢

### T2.1 — Local live view + latency (AC2.1)
- **Pre:** MediaMTX + FFmpeg running; client on same Wi-Fi.
- **Steps:** Open `http://<pi-ip>:8889/cam`. Wave hand in front of camera and
  compare to on-screen motion.
- **Expected:** Live video shown; end-to-end latency roughly ≤ 2 s.

### T2.2 — Quality & stability (AC2.2)
- **Pre:** Stream live.
- **Steps:** Watch continuously for 60 s.
- **Expected:** Resolution ≥ target (e.g. 720p); no stalls, freezes, or drops.

### T2.3 — Auto-recovery (AC2.3)
- **Pre:** Stream live.
- **Steps:** Unplug the webcam, wait 10 s, replug. Observe the stream.
- **Expected:** Stream resumes automatically within a short time, no manual
  restart needed.

---

## Suite 3 — Listen-In Audio 🟢

### T3.1 — Ambient audio + sync (AC3.1)
- **Pre:** Stream live on phone.
- **Steps:** Make a distinct sound in the room (clap) while watching.
- **Expected:** Clap is heard through the app, reasonably in sync with video.

---

## Suite 4 — Two-Way Talk 🟢

### T4.1 — Talk to speaker (AC4.1)
- **Pre:** Publish/talk control available in app; someone listening near Pi.
- **Steps:** Enable talk, speak a test phrase into the phone.
- **Expected:** Phrase plays clearly from the Pi speaker within a couple of
  seconds.

### T4.2 — Push-to-talk gating (AC4.2)
- **Pre:** Talk feature present.
- **Steps:** With talk **off/released**, speak into the phone.
- **Expected:** Nothing is transmitted to the Pi speaker.

### T4.3 — No feedback loop (AC4.3)
- **Pre:** Two-way audio active.
- **Steps:** Listen and talk simultaneously for 30 s near the Pi.
- **Expected:** No runaway echo/howl that makes it unusable.

---

## Suite 5 — Remote Access 🟢

### T5.1 — Off-network access (AC5.1)
- **Pre:** Tailscale up on Pi + phone.
- **Steps:** Disable Wi-Fi on phone (mobile data only), open
  `http://<pi-tailscale-ip>:8889/cam`.
- **Expected:** Video + audio work as on the home network.

### T5.2 — No public exposure (AC5.2)
- **Pre:** System deployed.
- **Steps:** From an external network, attempt to reach the router's public IP
  on the MediaMTX ports (e.g. 8889, 8554); optionally run an external port scan.
- **Expected:** No camera/MediaMTX ports reachable from the public internet.

---

## Suite 6 — Security 🟢

### T6.1 — Default creds rejected (AC6.1)
- **Steps:** Attempt SSH login as `pi` / password `raspberry`.
- **Expected:** Login fails.

### T6.2 — SSH hardening (AC6.2)
- **Steps:** Attempt password-based SSH (`ssh -o PubkeyAuthentication=no ...`);
  attempt `ssh root@<pi>`.
- **Expected:** Password auth rejected; root login disabled.

### T6.3 — Firewall rules (AC6.3)
- **Steps:** Run `sudo ufw status verbose`.
- **Expected:** Only SSH + Tailscale interface allowed inbound; default deny.

### T6.4 — Stream auth required (AC6.4)
- **Steps:** From an authorised network but with no/invalid credentials, try to
  view and to publish to the `cam` path.
- **Expected:** Both are denied without valid credentials.

### T6.5 — Encrypted transport (AC6.5)
- **Steps:** Inspect a live session (browser devtools/WebRTC internals); confirm
  web layer is HTTPS or Tailscale-only.
- **Expected:** Media uses DTLS-SRTP; signaling/web is encrypted or Tailscale-only.

### T6.6 — Talk path protected (AC6.6)
- **Steps:** Without valid credentials, attempt to publish audio to the speaker
  path.
- **Expected:** Publishing is rejected; no audio reaches the Pi speaker.

---

## Suite 7 — Companion App (Android PWA) 🟢

### T7.1 — Install to home screen (AC7.1)
- **Pre:** PWA served over HTTPS.
- **Steps:** Open in Chrome on Android → "Install app" / "Add to Home Screen";
  launch from the icon.
- **Expected:** Installs and launches fullscreen (no browser chrome).

### T7.2 — Core controls (AC7.2)
- **Steps:** In the app, verify live video, audio, push-to-talk toggle, and
  fullscreen each work.
- **Expected:** All four controls function.

### T7.3 — No client-side secrets (AC7.3)
- **Steps:** View page source / bundled JS in the browser.
- **Expected:** No hardcoded credentials present.

### T7.4 — Remote via app (AC7.4)
- **Pre:** App installed, Tailscale up.
- **Steps:** On mobile data, open the app.
- **Expected:** Connects to the camera successfully.

---

## Suite 8 — "Being Viewed" Indicator 🟢

### T8.1 — Chime on connect (AC8.1)
- **Pre:** `runOnRead` configured with a chime file.
- **Steps:** Open the stream from the app while listening near the Pi.
- **Expected:** Pi plays the chime through the speaker when viewing starts.

### T8.2 — Stop chime (AC8.2, optional)
- **Pre:** `runOnUnread` configured.
- **Steps:** Close the stream/app.
- **Expected:** Pi plays the stop chime on disconnect.

### T8.3 — Chime non-disruptive (AC8.3)
- **Steps:** Trigger the chime, then immediately use two-way talk.
- **Expected:** Chime is short and does not interfere with the conversation.

---

## Suite 9 — Alerts 🔵 (Later)

### T9.1 — Motion detection (AC9.1)
- **Pre:** Motion script running against RTSP stream.
- **Steps:** Walk through / move an object in frame.
- **Expected:** Motion event fires above threshold.

### T9.2 — Push notification (AC9.2)
- **Steps:** Trigger motion; watch the phone.
- **Expected:** Push notification received within a few seconds.

### T9.3 — False-alert rate (AC9.3)
- **Steps:** Leave the detector running for 1 hour under normal conditions
  (lighting changes, minor noise, no real intrusion).
- **Expected:** Number of false alerts stays within an acceptable, low bound.

---

## Suite 10 — Reliability & Operations 🔵 (Later)

### T10.1 — Start on boot (AC10.1)
- **Pre:** MediaMTX installed as a systemd service.
- **Steps:** `sudo reboot`; after boot, open the stream.
- **Expected:** Streaming resumes automatically, no manual start.

### T10.2 — Crash recovery (AC10.2)
- **Steps:** Kill the MediaMTX process (`sudo systemctl kill mediamtx` or
  `kill <pid>`); observe.
- **Expected:** systemd restarts the service automatically.

### T10.3 — Config in git (AC10.3)
- **Steps:** In the repo run `git status` / `git log`.
- **Expected:** `mediamtx.yml` and scripts are committed and tracked.

---

## Regression Checklist (run before calling a build "done")

- [ ] Suite 1 — devices detected
- [ ] Suite 2 — live video
- [ ] Suite 3 — listen-in audio
- [ ] Suite 4 — two-way talk
- [ ] Suite 5 — remote access
- [ ] Suite 6 — security
- [ ] Suite 7 — companion app
- [ ] Suite 8 — viewing indicator

MVP sign-off requires all of the above green.

---

## Results Log

| Test | Date | Env | Status | Notes |
|------|------|-----|--------|-------|
| T1.1 |      |     | Not run |       |
| T1.2 |      |     | Not run |       |
| T1.3 |      |     | Not run |       |
| T1.4 |      |     | Not run |       |
| T2.1 |      |     | Not run |       |
| T2.2 |      |     | Not run |       |
| T2.3 |      |     | Not run |       |
| T3.1 |      |     | Not run |       |
| T4.1 |      |     | Not run |       |
| T4.2 |      |     | Not run |       |
| T4.3 |      |     | Not run |       |
| T5.1 |      |     | Not run |       |
| T5.2 |      |     | Not run |       |
| T6.1 |      |     | Not run |       |
| T6.2 |      |     | Not run |       |
| T6.3 |      |     | Not run |       |
| T6.4 |      |     | Not run |       |
| T6.5 |      |     | Not run |       |
| T6.6 |      |     | Not run |       |
| T7.1 |      |     | Not run |       |
| T7.2 |      |     | Not run |       |
| T7.3 |      |     | Not run |       |
| T7.4 |      |     | Not run |       |
| T8.1 |      |     | Not run |       |
| T8.2 |      |     | Not run |       |
| T8.3 |      |     | Not run |       |
| T9.1 |      |     | Not run |       |
| T9.2 |      |     | Not run |       |
| T9.3 |      |     | Not run |       |
| T10.1 |     |     | Not run |       |
| T10.2 |     |     | Not run |       |
| T10.3 |     |     | Not run |       |

---

## Defect Log

| ID | Related test | Description | Severity | Status | Fixed in / notes |
|----|--------------|-------------|----------|--------|------------------|
|    |              |             |          |        |                  |
