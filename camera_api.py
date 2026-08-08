#!/usr/bin/env python3
"""Minimal HTTPS API to get/set v4l2 camera controls."""
from flask import Flask, request, jsonify
import subprocess, re

app = Flask(__name__)

CERT = '/etc/mediamtx/certs/rhyho-pi.tailcceb24.ts.net.crt'
KEY  = '/etc/mediamtx/certs/rhyho-pi.tailcceb24.ts.net.key'
ORIGIN = 'https://jamieainsworth.github.io'

CONTROLS = {
    'brightness':                {'min': 0,    'max': 255,  'default': 128, 'label': 'Brightness'},
    'contrast':                  {'min': 0,    'max': 255,  'default': 128, 'label': 'Contrast'},
    'saturation':                {'min': 0,    'max': 255,  'default': 128, 'label': 'Saturation'},
    'sharpness':                 {'min': 0,    'max': 255,  'default': 128, 'label': 'Sharpness'},
    'gain':                      {'min': 0,    'max': 255,  'default': 0,   'label': 'Gain'},
    'auto_exposure':             {'min': 1,    'max': 3,    'default': 3,   'label': 'Auto Exposure'},
    'exposure_time_absolute':    {'min': 3,    'max': 2047, 'default': 250, 'label': 'Exposure Time'},
    'backlight_compensation':    {'min': 0,    'max': 1,    'default': 0,   'label': 'Backlight Comp'},
    'white_balance_automatic':   {'min': 0,    'max': 1,    'default': 1,   'label': 'Auto White Balance'},
    'white_balance_temperature': {'min': 2000, 'max': 7500, 'default': 4000,'label': 'White Balance Temp'},
    'zoom_absolute':             {'min': 100,  'max': 400,  'default': 100, 'label': 'Zoom'},
}

def cors(response):
    response.headers['Access-Control-Allow-Origin'] = ORIGIN
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.after_request
def add_cors(r): return cors(r)

@app.route('/camera', methods=['OPTIONS'])
def preflight(): return cors(jsonify({}))

@app.route('/camera', methods=['GET'])
def get_controls():
    names = ','.join(CONTROLS.keys())
    out = subprocess.run(['v4l2-ctl', f'--get-ctrl={names}'],
                         capture_output=True, text=True).stdout
    values = {}
    for line in out.splitlines():
        m = re.match(r'\s*(\w+):\s*(-?\d+)', line)
        if m and m.group(1) in CONTROLS:
            values[m.group(1)] = int(m.group(2))
    return jsonify({'controls': CONTROLS, 'values': values})

@app.route('/camera', methods=['POST'])
def set_controls():
    data = request.get_json(force=True) or {}
    for key, raw in data.items():
        if key not in CONTROLS:
            continue
        c = CONTROLS[key]
        val = max(c['min'], min(c['max'], int(raw)))
        subprocess.run(['v4l2-ctl', f'--set-ctrl={key}={val}'])
    return jsonify({'ok': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, ssl_context=(CERT, KEY))
