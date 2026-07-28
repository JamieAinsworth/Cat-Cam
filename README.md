# Cat Cam — Raspberry Pi Surveillance Setup Guide

A two-way audio/video monitor for keeping an eye (and ear) on the cat, viewable
from your phone. Live video, hear the flat, and talk to the cat — with secure
remote access and room to add motion alerts later.

---

## 1. Project Overview

**Goal:** One webcam streaming live video + audio to your phone, plus two-way
talk so you can speak to the cat and hear noises in the flat. Live viewing first;
motion alerts as a later add-on.

**Chosen stack:**

| Component   | Role                                                                 |
|-------------|----------------------------------------------------------------------|
| MediaMTX    | WebRTC streaming server — serves a browser page, handles 2-way audio |
| FFmpeg      | Captures webcam video + mic audio, feeds it to MediaMTX              |
| Tailscale   | Secure remote phone access (no port forwarding)                      |
| OpenCV + ntfy | *(Later)* motion detection + push alerts to phone                  |

**Why WebRTC / MediaMTX:** browsers natively support sending the phone's mic
*back* to the Pi speaker, so two-way talk works with no custom app — just a
browser tab. Low latency, and a built-in publish/view web page.

---

## 2. Hardware

### Already have
- Raspberry Pi 5, 8GB
- 64GB microSD card

### Still to buy
- [ ] **USB webcam with built-in mic** — confirm it's **UVC-compatible** (most
      are) so Linux detects it without drivers. Check reviews mention Linux/`v4l2`.
- [ ] **Speaker** — a **USB speaker** is the least painful option (shows up as
      its own audio device). Alternatively a small amp + speaker, or a USB DAC.
- [ ] **Official Pi 5 power supply** — undervoltage causes camera/USB dropouts.
- [ ] **Case** (optional) and a small **tripod or mount** to aim at the cat's
      favourite spot.

### Nice to have
- Small heatsink/fan for the Pi 5 (video encoding generates heat).

---

## 3. Phase 1 — Base OS + Verify Devices

Get the OS ready and confirm every device is detected **before** touching
streaming. This saves hours of debugging later.

### 3.1 Flash and boot
1. Flash **Raspberry Pi OS (Lite, 64-bit)** with Raspberry Pi Imager.
2. In the Imager settings, pre-configure: hostname, **enable SSH**, Wi-Fi
   credentials, and your locale.
3. Boot the Pi headless and SSH in:
   ```bash
   ssh <user>@<pi-hostname>.local
   ```
4. Update:
   ```bash
   sudo apt update && sudo apt full-upgrade -y
   sudo apt install -y ffmpeg v4l-utils alsa-utils fswebcam
   ```

### 3.2 Verify the devices
```bash
# Video device — note the /dev/videoN path
v4l2-ctl --list-devices

# Audio capture (mic) — note the card,device numbers e.g. card 2, device 0
arecord -l

# Audio playback (speaker) — note the card,device numbers
aplay -l
```

### 3.3 Quick round-trip tests
```bash
fswebcam test.jpg                                 # video capture works?
arecord -d 5 -f cd test.wav && aplay test.wav     # mic + speaker round-trip
speaker-test -t wav -c 2                           # speaker only
```

> **Write down** the device addresses now, you'll need them for FFmpeg:
> - Video: `/dev/video____`
> - Mic (capture): `hw:____,____`
> - Speaker (playback): `hw:____,____`

---

## 4. Phase 2 — Install & Run MediaMTX

```bash
# Get the latest ARM64 (arm64v8) release from:
# https://github.com/bluenviron/mediamtx/releases
wget https://github.com/bluenviron/mediamtx/releases/latest/download/mediamtx_linux_arm64v8.tar.gz
tar -xzf mediamtx_*.tar.gz
./mediamtx
```

- MediaMTX serves a WebRTC page at `http://<pi-ip>:8889/cam` once something is
  publishing to a path named `cam`.
- Leave it running in one terminal for now; we'll make it a service later.

---

## 5. Phase 3 — Publish Camera + Mic

Configure MediaMTX to auto-launch FFmpeg. Edit `mediamtx.yml`:

```yaml
paths:
  cam:
    runOnInit: >
      ffmpeg -f v4l2 -framerate 30 -video_size 1280x720 -i /dev/video0
      -f alsa -i hw:2,0
      -c:v libx264 -preset ultrafast -tune zerolatency -pix_fmt yuv420p
      -c:a libopus -b:a 64k
      -f rtsp rtsp://localhost:8554/cam
    runOnInitRestart: yes
```

- Replace `/dev/video0` and `hw:2,0` with the values from Phase 1.
- Restart MediaMTX, then on your phone (same Wi-Fi) open:
  `http://<pi-ip>:8889/cam`
- You should see **live video** and hear the **flat's audio**.

**Tuning tips:**
- Drop to `640x480` or `15` fps if the stream stutters.
- `ultrafast` + `zerolatency` keeps latency low at the cost of file size (fine
  for live streaming).

---

## 6. Phase 4 — Two-Way Talk (Speaker Out)

1. On your phone, open the publisher page: `http://<pi-ip>:8889/cam/publish`
   and **enable the microphone** — this streams your phone's mic *to* the Pi.
2. On the Pi, run a reader that pulls that incoming audio stream and routes it
   to the speaker (exact command depends on your speaker's `hw:` address —
   tune once hardware is in hand). General shape:
   ```bash
   ffmpeg -i rtsp://localhost:8554/cam -f alsa hw:X,Y
   ```
3. Result: speak on the phone → cat hears you through the Pi speaker.

> This phase usually needs a little trial and error with device routing and
> echo. Get one-way audio solid first, then enable the return path.

---

## 7. Phase 5 — Secure Remote Access (Tailscale)

**Do not** port-forward the Pi to the internet. Use a VPN mesh instead:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

- Install the **Tailscale app on your phone** and sign in with the same account.
- Access from anywhere, encrypted:
  `http://<pi-tailscale-ip>:8889/cam`

---

## 8. Phase 6 — Alerts (Later)

Once live viewing is rock-solid, add motion detection without disturbing the
streaming layer:

1. A small **Python + OpenCV** script reads the same RTSP stream
   (`rtsp://localhost:8554/cam`), compares consecutive frames, and detects
   motion above a threshold.
2. On motion, push a phone notification via **[ntfy.sh](https://ntfy.sh)** —
   dead simple, just an HTTP POST to a topic your phone subscribes to.

---

## 9. Make It Permanent (Recommended once working)

- Turn MediaMTX into a **systemd service** so it starts on boot and restarts on
  failure.
- Keep `mediamtx.yml` and any scripts in a git repo so config is versioned.

---

## 10. Build Order Checklist

- [ ] **Phase 1** — OS installed, SSH works, all 3 devices detected, `hw:`
      addresses recorded.
- [ ] **Phase 2** — MediaMTX running and reachable on local Wi-Fi.
- [ ] **Phase 3** — Live video + mic audio on phone browser.
- [ ] **Phase 4** — Two-way talk working.
- [ ] **Phase 5** — Tailscale remote access.
- [ ] **Phase 6** — Motion alerts.
- [ ] **Hardening** — systemd service, config in git.

---

## 11. Handy References

- MediaMTX: https://github.com/bluenviron/mediamtx
- FFmpeg V4L2/ALSA capture: https://trac.ffmpeg.org/wiki/Capture/Webcam
- Tailscale: https://tailscale.com/download
- ntfy push notifications: https://ntfy.sh

---

*Guide created 2026-07-28. Update the `hw:` / `/dev/video*` placeholders once the
webcam and speaker arrive.*
