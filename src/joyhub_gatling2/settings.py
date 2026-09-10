"""Paths, translations, patterns, and UI constants."""

from __future__ import annotations
import base64
import json
import os
import socket
import re
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

VIDEO_DIR = Path(os.environ.get("JOYHUB_VIDEO_DIR", str(Path.home() / "Videos")))

SCRIPT_DIR = VIDEO_DIR / "RotaryScript"

PLAYER = Path.home() / ".cache/joyhub-gatling2-player/gatling2-ble-direct-engine.py"

APP_VERSION = "v1.3.5"

APP_NAME = f"JoyHub Gatling 2 Player {APP_VERSION}"

PYTHON = Path(sys.executable)

CONFIG = Path.home() / ".config/joyhub-gatling2-player/config.json"

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v"}

TRANSLATIONS = {'Vidéos': 'Videos', 'Tous les fichiers': 'All files', 'Aucun script sélectionné': 'No script selected', 'Choisis une vidéo pour commencer.': 'Choose a video to start.', 'MOUVEMENT FUNSCRIPT — clique ou glisse pour déplacer la vidéo': 'FUNSCRIPT MOVEMENT — click or drag to seek the video', 'Pause / Reprendre': 'Pause / Resume', 'Conversion directe en rotation — amplification adaptateur 0 à 100 %': 'Direct rotary conversion — adapter amplification 0 to 100%', 'Fichier': 'File', 'Vidéo': 'Video', 'Parcourir': 'Browse', 'Script': 'Script', 'Réglages': 'Settings', 'Puissance maximale': 'Maximum power', 'Passage à zéro': 'Zero hold', 'Lissage': 'Smoothing', 'Vitesse minimale': 'Minimum speed', 'Amplification adaptateur': 'Adapter amplification', 'Ouvrir MPV en plein écran sur l’écran de droite': 'Open MPV fullscreen on the right display', 'Pompage Gatling 2 au début de chaque cycle': 'Gatling 2 pumping at the start of each cycle', 'Durée du pompage': 'Pump duration', 'Pause entre pompages': 'Pause between pumps', 'Niveau de pompe (max 7)': 'Pump level (max 7)', 'Supprimer la vidéo et ses funscripts à la fin ou en passant à la suivante': 'Delete video and its funscripts at the end or when moving to the next', 'Passer automatiquement à la vidéo suivante': 'Automatically play the next video', 'Patterns de pompage — sélection libre': 'Pump patterns — free selection', 'Chaque pattern est joué au complet, puis un autre est choisi parmi les sélections. Niveau toujours limité à 7.': 'Each pattern is played in full, then another is chosen from the selection. Level is always limited to 7.', '▶  Lancer la vidéo': '▶  Play video', '⏭  Lire le dossier': '⏭  Play folder', '⏩  Vidéo suivante': '⏩  Next video', '🧪  Test pompage continu 10 s': '🧪  Continuous pump test 10 s', '■  Arrêter': '■  Stop', 'Choisis une vidéo avec son funscript': 'Choose a video with its funscript', 'sélectionné(s)': 'selected'}

VIDEO_TYPES = (
    ("Vidéos", "*.mp4 *.mkv *.avi *.mov *.webm *.m4v"),
    ("Tous les fichiers", "*"),
)

PUMP_PATTERNS = {'01 Escalier montant': [1, 2, 3, 4, 5, 6, 7], '02 Escalier descendant': [7, 6, 5, 4, 3, 2, 1], '03 Vague complète': [1, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 2], '04 Vague courte': [1, 3, 5, 7, 5, 3], '05 Montée rapide': [1, 3, 5, 7], '06 Descente rapide': [7, 5, 3, 1], '07 Alternance extrême': [1, 7, 1, 7, 1, 7], '08 Alternance douce': [2, 5, 2, 5, 2, 5], '09 Double maximum': [2, 4, 7, 7, 4, 2], '10 Triple maximum': [3, 5, 7, 7, 7, 5, 3], '11 Double bas': [1, 1, 3, 5, 7], '12 Double haut': [1, 3, 5, 7, 7], '13 Marche paire': [2, 4, 6, 7, 6, 4, 2], '14 Marche impaire': [1, 3, 5, 7, 5, 3, 1], '15 Pic central': [1, 2, 4, 7, 4, 2, 1], '16 Pic double': [1, 3, 7, 3, 1, 3, 7, 3], '17 Pulsation 3-7': [3, 7, 3, 7, 3, 7], '18 Pulsation 4-7': [4, 7, 4, 7, 4, 7], '19 Pulsation 5-7': [5, 7, 5, 7, 5, 7], '20 Pulsation 1-5': [1, 5, 1, 5, 1, 5], '21 Dent de scie montante': [1, 2, 4, 6, 7, 2, 4, 6, 7], '22 Dent de scie descendante': [7, 6, 4, 2, 1, 6, 4, 2, 1], '23 Deux marches': [1, 2, 3, 7, 1, 2, 3, 7], '24 Trois marches': [1, 2, 4, 7, 2, 4, 7], '25 Plateau moyen': [1, 3, 5, 5, 5, 7], '26 Plateau haut': [2, 4, 6, 7, 7, 7, 6, 4], '27 Plateau bas': [1, 1, 1, 3, 5, 7], '28 Accélération niveau': [1, 2, 3, 5, 7, 7, 7], '29 Décélération niveau': [7, 7, 7, 5, 3, 2, 1], '30 Battement court': [2, 7, 2, 4, 2, 7], '31 Battement long': [1, 4, 7, 4, 1, 4, 7, 4], '32 Battement asymétrique': [1, 6, 2, 7, 3, 5], '33 Haut dominant': [4, 5, 6, 7, 6, 7, 5, 7], '34 Bas dominant': [1, 2, 1, 3, 1, 4, 1, 5], '35 Escalier double': [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7], '36 Escalier saut 2': [1, 3, 5, 7, 6, 4, 2], '37 Triangle serré': [3, 4, 5, 6, 7, 6, 5, 4], '38 Triangle large': [1, 2, 4, 6, 7, 6, 4, 2], '39 Maximum intermittent': [7, 2, 3, 7, 3, 4, 7, 4, 5], '40 Maximum fréquent': [7, 5, 7, 4, 7, 3, 7, 2], '41 Maximum progressif': [2, 3, 4, 5, 6, 7, 7, 7], '42 Relance basse': [1, 7, 1, 2, 7, 2, 3, 7], '43 Relance moyenne': [3, 7, 3, 4, 7, 4, 5, 7], '44 Groupes de deux': [2, 2, 5, 5, 7, 7, 4, 4], '45 Groupes de trois': [2, 2, 2, 5, 5, 5, 7, 7, 7], '46 Syncopé A': [1, 4, 2, 6, 3, 7, 2, 5], '47 Syncopé B': [7, 3, 6, 2, 5, 1, 4, 2], '48 Cascade': [1, 4, 7, 2, 5, 7, 3, 6, 7], '49 Cascade inverse': [7, 6, 3, 7, 5, 2, 7, 4, 1], '50 Chaos contrôlé': [1, 6, 3, 7, 2, 5, 4, 7, 3, 6]}

PUMP_PATTERN_LABELS = {'01 Escalier montant': '01 Escalier montant — 1 → 2 → 3 → 4 → 5 → 6 → 7', '02 Escalier descendant': '02 Escalier descendant — 7 → 6 → 5 → 4 → 3 → 2 → 1', '03 Vague complète': '03 Vague complète — 1 → 2 → 3 → 4 → 5 → 6 → 7 → 6 → 5 → 4 → 3 → 2', '04 Vague courte': '04 Vague courte — 1 → 3 → 5 → 7 → 5 → 3', '05 Montée rapide': '05 Montée rapide — 1 → 3 → 5 → 7', '06 Descente rapide': '06 Descente rapide — 7 → 5 → 3 → 1', '07 Alternance extrême': '07 Alternance extrême — 1 → 7 → 1 → 7 → 1 → 7', '08 Alternance douce': '08 Alternance douce — 2 → 5 → 2 → 5 → 2 → 5', '09 Double maximum': '09 Double maximum — 2 → 4 → 7 → 7 → 4 → 2', '10 Triple maximum': '10 Triple maximum — 3 → 5 → 7 → 7 → 7 → 5 → 3', '11 Double bas': '11 Double bas — 1 → 1 → 3 → 5 → 7', '12 Double haut': '12 Double haut — 1 → 3 → 5 → 7 → 7', '13 Marche paire': '13 Marche paire — 2 → 4 → 6 → 7 → 6 → 4 → 2', '14 Marche impaire': '14 Marche impaire — 1 → 3 → 5 → 7 → 5 → 3 → 1', '15 Pic central': '15 Pic central — 1 → 2 → 4 → 7 → 4 → 2 → 1', '16 Pic double': '16 Pic double — 1 → 3 → 7 → 3 → 1 → 3 → 7 → 3', '17 Pulsation 3-7': '17 Pulsation 3-7 — 3 → 7 → 3 → 7 → 3 → 7', '18 Pulsation 4-7': '18 Pulsation 4-7 — 4 → 7 → 4 → 7 → 4 → 7', '19 Pulsation 5-7': '19 Pulsation 5-7 — 5 → 7 → 5 → 7 → 5 → 7', '20 Pulsation 1-5': '20 Pulsation 1-5 — 1 → 5 → 1 → 5 → 1 → 5', '21 Dent de scie montante': '21 Dent de scie montante — 1 → 2 → 4 → 6 → 7 → 2 → 4 → 6 → 7', '22 Dent de scie descendante': '22 Dent de scie descendante — 7 → 6 → 4 → 2 → 1 → 6 → 4 → 2 → 1', '23 Deux marches': '23 Deux marches — 1 → 2 → 3 → 7 → 1 → 2 → 3 → 7', '24 Trois marches': '24 Trois marches — 1 → 2 → 4 → 7 → 2 → 4 → 7', '25 Plateau moyen': '25 Plateau moyen — 1 → 3 → 5 → 5 → 5 → 7', '26 Plateau haut': '26 Plateau haut — 2 → 4 → 6 → 7 → 7 → 7 → 6 → 4', '27 Plateau bas': '27 Plateau bas — 1 → 1 → 1 → 3 → 5 → 7', '28 Accélération niveau': '28 Accélération niveau — 1 → 2 → 3 → 5 → 7 → 7 → 7', '29 Décélération niveau': '29 Décélération niveau — 7 → 7 → 7 → 5 → 3 → 2 → 1', '30 Battement court': '30 Battement court — 2 → 7 → 2 → 4 → 2 → 7', '31 Battement long': '31 Battement long — 1 → 4 → 7 → 4 → 1 → 4 → 7 → 4', '32 Battement asymétrique': '32 Battement asymétrique — 1 → 6 → 2 → 7 → 3 → 5', '33 Haut dominant': '33 Haut dominant — 4 → 5 → 6 → 7 → 6 → 7 → 5 → 7', '34 Bas dominant': '34 Bas dominant — 1 → 2 → 1 → 3 → 1 → 4 → 1 → 5', '35 Escalier double': '35 Escalier double — 1 → 1 → 2 → 2 → 3 → 3 → 4 → 4 → 5 → 5 → 6 → 6 → 7 → 7', '36 Escalier saut 2': '36 Escalier saut 2 — 1 → 3 → 5 → 7 → 6 → 4 → 2', '37 Triangle serré': '37 Triangle serré — 3 → 4 → 5 → 6 → 7 → 6 → 5 → 4', '38 Triangle large': '38 Triangle large — 1 → 2 → 4 → 6 → 7 → 6 → 4 → 2', '39 Maximum intermittent': '39 Maximum intermittent — 7 → 2 → 3 → 7 → 3 → 4 → 7 → 4 → 5', '40 Maximum fréquent': '40 Maximum fréquent — 7 → 5 → 7 → 4 → 7 → 3 → 7 → 2', '41 Maximum progressif': '41 Maximum progressif — 2 → 3 → 4 → 5 → 6 → 7 → 7 → 7', '42 Relance basse': '42 Relance basse — 1 → 7 → 1 → 2 → 7 → 2 → 3 → 7', '43 Relance moyenne': '43 Relance moyenne — 3 → 7 → 3 → 4 → 7 → 4 → 5 → 7', '44 Groupes de deux': '44 Groupes de deux — 2 → 2 → 5 → 5 → 7 → 7 → 4 → 4', '45 Groupes de trois': '45 Groupes de trois — 2 → 2 → 2 → 5 → 5 → 5 → 7 → 7 → 7', '46 Syncopé A': '46 Syncopé A — 1 → 4 → 2 → 6 → 3 → 7 → 2 → 5', '47 Syncopé B': '47 Syncopé B — 7 → 3 → 6 → 2 → 5 → 1 → 4 → 2', '48 Cascade': '48 Cascade — 1 → 4 → 7 → 2 → 5 → 7 → 3 → 6 → 7', '49 Cascade inverse': '49 Cascade inverse — 7 → 6 → 3 → 7 → 5 → 2 → 7 → 4 → 1', '50 Chaos contrôlé': '50 Chaos contrôlé — 1 → 6 → 3 → 7 → 2 → 5 → 4 → 7 → 3 → 6'}

PUMP_PATTERN_NAMES_EN = {'01 Escalier montant': '01 Rising staircase', '02 Escalier descendant': '02 Falling staircase', '03 Vague complète': '03 Full wave', '04 Vague courte': '04 Short wave', '05 Montée rapide': '05 Fast rise', '06 Descente rapide': '06 Fast fall', '07 Alternance extrême': '07 Extreme alternation', '08 Alternance douce': '08 Gentle alternation', '09 Double maximum': '09 Double maximum', '10 Triple maximum': '10 Triple maximum', '11 Double bas': '11 Double low', '12 Double haut': '12 Double high', '13 Marche paire': '13 Even steps', '14 Marche impaire': '14 Odd steps', '15 Pic central': '15 Central peak', '16 Pic double': '16 Double peak', '17 Pulsation 3-7': '17 Pulse 3-7', '18 Pulsation 4-7': '18 Pulse 4-7', '19 Pulsation 5-7': '19 Pulse 5-7', '20 Pulsation 1-5': '20 Pulse 1-5', '21 Dent de scie montante': '21 Rising sawtooth', '22 Dent de scie descendante': '22 Falling sawtooth', '23 Deux marches': '23 Two steps', '24 Trois marches': '24 Three steps', '25 Plateau moyen': '25 Medium plateau', '26 Plateau haut': '26 High plateau', '27 Plateau bas': '27 Low plateau', '28 Accélération niveau': '28 Level acceleration', '29 Décélération niveau': '29 Level deceleration', '30 Battement court': '30 Short beat', '31 Battement long': '31 Long beat', '32 Battement asymétrique': '32 Asymmetric beat', '33 Haut dominant': '33 High dominant', '34 Bas dominant': '34 Low dominant', '35 Escalier double': '35 Double staircase', '36 Escalier saut 2': '36 Staircase step 2', '37 Triangle serré': '37 Tight triangle', '38 Triangle large': '38 Wide triangle', '39 Maximum intermittent': '39 Intermittent maximum', '40 Maximum fréquent': '40 Frequent maximum', '41 Maximum progressif': '41 Progressive maximum', '42 Relance basse': '42 Low restart', '43 Relance moyenne': '43 Medium restart', '44 Groupes de deux': '44 Groups of two', '45 Groupes de trois': '45 Groups of three', '46 Syncopé A': '46 Syncopated A', '47 Syncopé B': '47 Syncopated B', '48 Cascade': '48 Cascade', '49 Cascade inverse': '49 Reverse cascade', '50 Chaos contrôlé': '50 Controlled chaos'}

MAX_SELECTED_PUMP_PATTERNS = 50

COLORS = {
    "bg": "#111318",
    "panel": "#191c22",
    "panel_alt": "#20242c",
    "border": "#2c313b",
    "text": "#f2f4f8",
    "muted": "#9aa3b2",
    "accent": "#7c5cff",
    "accent_hover": "#9278ff",
    "danger": "#ff5c72",
    "warning": "#ffb84d",
    "success": "#39d98a",
    "track": "#343a46",
}
