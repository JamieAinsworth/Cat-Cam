# Cat Cam — Acceptance Criteria

Testable criteria that define "done" for each feature of the cat monitoring
system. Each item should be verifiable by a concrete action and observed result.
Format: **Given / When / Then** plus a checkbox to tick when it passes.

Legend: 🟢 MVP (must-have for v1) · 🔵 Later (post-MVP)

---

## 1. Base Setup & Devices 🟢

- [x] **AC1.1 — Pi reachable**
  *Given* the Pi is powered and on the network,
  *when* I SSH to it from my laptop,
  *then* I get a shell prompt without using a password (key-based auth).

- [x] **AC1.2 — Camera detected**
  *Given* the webcam is plugged in,
  *when* I run `v4l2-ctl --list-devices`,
  *then* the camera appears with a `/dev/video*` node.

- [x] **AC1.3 — Mic detected**
  *Given* the webcam mic is connected,
  *when* I run `arecord -l`,
  *then* the capture device is listed and a 5-second test recording plays back
  with audible sound.

- [ ] **AC1.4 — Speaker works**
  *Given* the speaker is connected,
  *when* I run `speaker-test`,
  *then* sound is clearly audible in the room.

---

## 2. Live Video 🟢

- [x] **AC2.1 — Local live view**
  *Given* MediaMTX and FFmpeg are running,
  *when* I open `http://<pi-ip>:8889/cam` on a device on the same Wi-Fi,
  *then* I see live video of the room within ~2 seconds of latency.

- [x] **AC2.2 — Acceptable quality**
  *Given* the stream is live,
  *when* I watch for 60 seconds,
  *then* the video is at least 720p (or a chosen resolution) and does not stall
  or drop the connection.

- [x] **AC2.3 — Auto-recovery**
  *Given* the stream is interrupted (e.g. camera unplugged/replugged),
  *when* the device returns,
  *then* the stream resumes automatically without manual restart
  (`runOnInitRestart`).

---

## 3. Audio — Listen In 🟢

- [x] **AC3.1 — Hear the flat**
  *Given* the stream is live,
  *when* I view the feed on my phone,
  *then* I can hear ambient audio from the room in sync with the video.

---

## 4. Two-Way Talk 🟢

- [ ] **AC4.1 — Talk to the cat**
  *Given* I open the publish/talk control in the app,
  *when* I speak into my phone,
  *then* my voice plays clearly through the Pi speaker in the flat within a
  couple of seconds.

- [x] **AC4.2 — Push-to-talk control**
  *Given* the talk feature exists,
  *when* I am not actively holding/enabling talk,
  *then* my phone mic is **not** transmitting to the Pi.

- [ ] **AC4.3 — No persistent echo/feedback**
  *Given* two-way audio is active,
  *when* I talk while listening,
  *then* there is no runaway echo/feedback loop that makes it unusable.

---

## 5. Remote Access 🟢

- [x] **AC5.1 — Works away from home**
  *Given* Tailscale is installed on the Pi and my phone,
  *when* I am on mobile data (off home Wi-Fi) and open
  `http://<pi-tailscale-ip>:8889/cam`,
  *then* live video + audio work as they do at home.

- [x] **AC5.2 — Not publicly exposed**
  *Given* the system is deployed,
  *when* I scan the Pi's public IP / router for open camera ports,
  *then* no camera or MediaMTX port is reachable from the public internet.

---

## 6. Security 🟢

- [x] **AC6.1 — No default credentials**
  *Given* the Pi is configured,
  *when* I attempt to log in with `pi`/`raspberry`,
  *then* it fails.

- [x] **AC6.2 — SSH hardened**
  *Given* `sshd_config` is set,
  *when* I attempt password-based SSH login,
  *then* it is rejected (keys only), and root login is disabled.

- [ ] **AC6.3 — Firewall active**
  *Given* `ufw` is enabled,
  *when* I check allowed ports,
  *then* only SSH and the Tailscale interface are permitted inbound.

- [x] **AC6.4 — Stream requires auth**
  *Given* MediaMTX auth is configured,
  *when* an unauthenticated client tries to view or publish,
  *then* access is denied.

- [x] **AC6.5 — Encrypted transport**
  *Given* the app connects to the stream,
  *when* traffic is inspected,
  *then* media is encrypted (WebRTC DTLS-SRTP) and the web layer is HTTPS or
  Tailscale-only.

- [ ] **AC6.6 — Talk path protected**
  *Given* the two-way audio publish endpoint,
  *when* an unauthorised party attempts to publish audio,
  *then* they cannot transmit to the Pi speaker.

---

## 7. Companion App (Android PWA) 🟢

- [x] **AC7.1 — Installable**
  *Given* the PWA is served over HTTPS,
  *when* I open it in Chrome on Android,
  *then* I can install it to the home screen and it launches fullscreen.

- [x] **AC7.2 — Core controls**
  *Given* the app is open,
  *when* I use it,
  *then* I can see live video, hear audio, toggle push-to-talk, and go
  fullscreen.

- [x] **AC7.3 — No secrets in client**
  *Given* the app's client-side code,
  *when* I inspect it,
  *then* no credentials are hardcoded in the JavaScript.

- [x] **AC7.4 — Remote-capable**
  *Given* the app is installed,
  *when* I am off home Wi-Fi (with Tailscale up),
  *then* the app connects to the camera successfully.

---

## 8. "Being Viewed" Indicator 🟢

- [ ] **AC8.1 — Chime on view**
  *Given* `runOnRead` is configured,
  *when* the companion app opens the stream,
  *then* the Pi plays an audible chime through the speaker in the flat.

- [ ] **AC8.2 — Stop signal (optional)**
  *Given* `runOnUnread` is configured,
  *when* the viewer disconnects,
  *then* the Pi plays the stop chime.

- [ ] **AC8.3 — Non-disruptive**
  *Given* the chime plays,
  *when* two-way talk is in use shortly after,
  *then* the chime is short enough not to interfere with the conversation.

---

## 9. Alerts 🔵 (Later)

- [ ] **AC9.1 — Motion detected**
  *Given* the motion-detection script is running against the RTSP stream,
  *when* significant movement occurs in frame,
  *then* it is detected above the configured threshold.

- [ ] **AC9.2 — Phone notification**
  *Given* motion is detected,
  *when* the event fires,
  *then* I receive a push notification on my phone (e.g. via ntfy) within a few
  seconds.

- [ ] **AC9.3 — No false-alert flood**
  *Given* normal conditions (lighting changes, minor noise),
  *when* the detector runs over an hour,
  *then* it does not produce an unreasonable number of false alerts.

---

## 10. Reliability & Operations 🔵

- [x] **AC10.1 — Starts on boot**
  *Given* MediaMTX is a systemd service,
  *when* the Pi reboots,
  *then* streaming comes back up automatically without manual intervention.

- [x] **AC10.2 — Survives crashes**
  *Given* the service fails,
  *when* the process dies,
  *then* systemd restarts it automatically.

- [ ] **AC10.3 — Config versioned**
  *Given* the project files,
  *when* I check the repo,
  *then* `mediamtx.yml` and scripts are committed to git.

---

## Definition of Done (v1 / MVP)

The MVP is complete when **all 🟢 criteria in sections 1–8 pass**:
live video + audio, two-way talk, secure remote access via the Android PWA, and
the "being viewed" chime — with the security criteria satisfied.

Sections 9–10 (alerts, reliability hardening) are tracked separately as
post-MVP work.
