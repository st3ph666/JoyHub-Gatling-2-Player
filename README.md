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

## uv deployment

The recommended deployment method is [`uv`](https://docs.astral.sh/uv/). The project is configured to use the system Python so Tkinter remains provided by the Linux distribution.

### Debian / Ubuntu

```bash
sudo apt update
sudo apt install -y python3 python3-tk mpv bluetooth bluez
```

Install `uv` using its official installation method, then:

```bash
git clone https://github.com/st3ph666/JoyHub-Gatling-2-Player.git
cd JoyHub-Gatling-2-Player
uv sync
uv run python JoyHub-Gatling-2-Player-v1.3.5.py
```

Python dependencies are installed automatically by `uv sync`. Do not run `uv sync` with `sudo`.

### Update

```bash
git pull
uv sync
uv run python JoyHub-Gatling-2-Player-v1.3.5.py
```

## Source architecture

```text
JoyHub-Gatling-2-Player-v1.3.5.py  # Compatibility launcher
src/joyhub_gatling2/
├── __init__.py                   # Version metadata
├── settings.py                   # Paths, translations, patterns and UI constants
├── app.py                        # BLE engine bundle, helpers and Tkinter application
└── main.py                       # Application entry point
```

Source-code comments are maintained in **English only**. French and English user-interface strings are preserved.

