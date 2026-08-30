# JoyHub Gatling 2 Player

A Linux desktop media player for controlling the JoyHub Gatling 2 while playing local videos and matching Funscript files.

## Highlights

- Direct Bluetooth Low Energy (BLE) control
- Local playback through MPV
- Runtime conversion of linear Funscript movement to rotary commands
- Adjustable rotation power, smoothing and amplification
- Gatling 2 pump control
- 50 selectable pump patterns
- Folder playback and next-video controls
- Remembers the last video folder used
- Optional automatic deletion after playback
- French and English interface
- Readable dark theme

## Requirements

- Linux
- Python 3
- Bluetooth Low Energy adapter
- MPV
- JoyHub Gatling 2
- Python packages from `requirements.txt`

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Install MPV with your distribution package manager.

## Running

```bash
python3 src/JoyHub-Gatling-2-Player.py
```

The default video folder is `~/Videos`.

You can override it with:

```bash
JOYHUB_VIDEO_DIR=/path/to/videos python3 src/JoyHub-Gatling-2-Player.py
```

## Disclaimer

This is an independent open-source project and is not affiliated with or endorsed by JoyHub.
