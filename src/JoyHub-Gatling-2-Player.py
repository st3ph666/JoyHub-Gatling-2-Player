#!/usr/bin/env python3
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
APP_VERSION = "v1.3.4"
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



ENGINE_BUNDLE = 'c-qZ8+iv5?a_{<zK3p7_nw4luvg{dUy@A$a?|L)#7`At@fR8~?VoT-@Me^{XvEw*6ugP;h;2;k{d|vXBmmrV&lk+91>KmIkUuKaYh9OgARdsdUx~jVAuYR|kr^)ur54UN!Ch=W%6NRJBB8gVSaTa-&C)9C>zlx(IBW@T*nVb1hn07kyUb2kcB&G6u;)Y(dQcu&naPCL)>&#E-Jd@vkO`}j=uiWfLUPr0CO8sT%2I^Zh|3npbn$O}Sn$uK4XLJ=W{6Mji`76q&5(D+XpUHWg;b81Rb{G5MQr@42cb!g_+)X+Jei*<kpzbI6{5$+|5co9Adi=}99ArY14!xbzI3vdl?l4KBgwse|m@&DyOM$n;TR$_|UHmalA}<f97{HySK-40~VVb!?K>P5-bHkLt-!*DxLW~0SAGc?Dmc>E7?8kw7N0UCnFfGP@Ongp+ljdmMPUq-oIw1SRu;FL1a0h+7=nwGYEq>VcTYJ2CHyiCNW=7{=dho*`fTO6an`lMNF4-oAHIKrDzuaEBSpb3?%JE^S{@k74Pz#l6bUN=3kETC;xO6TKrl-!u;lan#_ZL8J*Rs{4vyUG>I45{_RNQ=jIDP-!^z=R4wJm$l>3DQO60|z%#4hUJjHAyqnUF;gxmlO=za_J~jHX=PUy-9I0b3$-HwN3?JQB}Oz~tx(#7jIH=Y9%8&isWtr(i+}`LTZzeO?Cs@iCDkrZ%xh#J0unFTarKR6K%fnr0+$$=VGlps(G;cW0<A%Gm_x*k1d<P)aR^1b{h(>8#vabI>CzKQxEqaSybVnMss~o(ak~*=+dKx?S>y0ElIG;fI?Mg~^0`qNZuzPVFACZ|xELw9B7tJp3}90(R&8<K^`7(7Cw$cm_-`3Km-S4ZSsu%1q&RIyJgX=5fA?ohXz-59pc(6J)wB@>73J-5ezlN2}Ofg2_ff6lN}np2<D%SAGV%*!-CcENhR;g;6ZaWsggRJ$Yv8d+c){C(Tgs%h3@|`s}BZGw1y9!{PMeuzA*d#gvbZ42g0!y}Ud;KSi6o-?9hfFrB;L?g?4pbi!<FLat!UVUK|5cX|ZWxZ5Lp*FCaj4-06IrgIv40%4B<jTyp-ArBbBi2Up>!8GO|v|#h^8Ev6nL1(x-3O7#_;)sFmvCk0$8<P`YeDesl>BhcS0c0S%<UQjy(_sV+$>|=M1{qC4Hw34lw^_3J%SzG$(BhLpzty3=D4#RXAtPCQGSGMAeUzj3fD!nsd?f&P7{NVu!R9-#$z|flWk5CEz0#xy14(q|rh>`xoCiY*apUG$Rd^g^L{8iU;u$O*V8sPrN+F819SI4GgoLdsLkMy(CTISfptKV=DAc{9CMyAV8KB3wEC}v#QtFz4?vb-RNLk<^qyC<d%$|n8XY^Ks+u?9(T=B`^-f3`S4yPuvR|s)vYjA`9Sa3OJ{E1Hn2kPLlm!xx_N>8Gt*>kBD*9>u3Ml76)7G5P}re8DM5#Z*xU@fSbwB%UaRELFRhC5(f5v&U}=pBtM4hjkkU@3xVw~Fp)Skm=a6V9%JlP0E5bWa%(1Kv}>C5tT^?GW5*KHoeBo5zF;J!E0GG`GSZ7z()8=CK8*<Tr)nMmG7*&BS`iqKjZ&31TRyj|Lhfg!`r7M43}@&A^8mIHZNE&107Mf6S#J>~hL{8Vq4XegN5l6Ts3SLTM!^YUViF0rF`Hcpz<KBzciGIT~xRTK6%I!ez;0@Q&2$u2LSOuv<__k;`G#?X?gw+QaDOhD(SzDNP_N5l-3=;~D(h0zQEJy2)2`^6wx5v8afvCrx0j&8S*>hFTy{s$o*tu@&9|cmh=@q_GwlI5rz;XP_`3^<E~B<oF9=AC>7yLG295IStrS0LGn`R}E!W(iL|`3Yz&>NK4_Y;9tV;knbUfifM{r!ULBV+zgdFN)#s9ov{v|q1P7(L*0wD8SFy-9?qi}5}0XW<3l#nk(>dS=w1Q(oe<?nn)X;)As6Laa^QjmsWn-}nz5X%41_!HBq->2O_NlMe<SGxL*;ddGPcRVjT@!l!LZb9{xjevH>mKesd)GLq0^ZMpdxY(X>4+Ll!xgY*4&I|d6*J9jvxA&<CrN87Clx}O;~}@ov7Nxb2AsRC#(W2NNK&)L@+C%uIFTsI+zsX<3Z`LZ{*pc|F#b$o*_~_{Bh^3yaW<g*XrgXN{9=SXVk4Fq@#v_GkO504Ua#nfYW~jyyeC*EFz|fS*Oj@P4~)hGvm73?GbSobJ2laJdUFjpLaDr@kbPWhwKkfua6poJgZZ)QYaD4f|9?0>@_sS(=Pdj49kRg4f!*s^{lcq4W%122na%88Bvbr9P^NE83lRNl~qVpT$LYVq0B_?UfI`$v<2*SM_B*}!pD1#D{Nqu7BvC<Eg1JP?Pk@!#s4^ozr4xJVmw3!JTg!?BGuP9zLI+CUSAEG7(st<WZ@+ZQ#@p>^?3C`MZwqubl01?p{H&Lr-G7l7DWM@3VTva<}306lMp6xY%)X%CVIrn$@f1Uvx1PNbiBd=-<!b4z6*i=FF<|_B@Y<WzGTu;WY?nlfkIc<9A2nWkWT_dGzJJPzuDiC<*dm!`^AjPX2YckC{+RDP-<K*9kBg%R|bHSczt|!@H)R|O2a2GC;U@>fSnt7a2kcQ{9u+Z&`=Dcd^@4A8l{=zd)NoyYG<t^#t#Iw5G+ctgT@r)nNTOd4^T=PXAsTsHo{queMVUn`g6?zKi~MU&{iLV*g57mYJ`$_LHKIU7QOY;EH%6J2+$ae7+b&+Z)jQkk14)QkDQ-QkALaOrxza&{tn9b^TX*$x0#Za(rgw0G=x?2$PH534CsD#ebth~FzO_E7y^<LL{V&Z86%F8E^v?~rkZ58WpquyX(I%;y4oWVJwIM(?XoB1XMGB3KxqtSJSbS>!Sa%8OoYn|CP;E}_A~gp=ch4f7;-+0k`>EBnLuU}(<HkS<`udth#eq_s<CS}`t`mZ#hB4nKsv>Y?r>QI2$QXmUcQP`^WK<8s};DgF}X5yCJfF1tm#HU%$UF!4_)##G5!!5U5hQLRI})pDLTb!DhN!a!Jg!<>Km6yPRk17_h&dh0hhtmLi%%ElOiX08CMCNuXUDo$K%m%-Soiya9kwaY&zT!4!AKx92K^JMzDY!dGl!0iK>tU3Ps8#fWQxFPmfyi(n{mN&rBu^$iK>DSLw2x4k4LtHIe`nPir(Kcgg-f8dH6GGK@<kWVLR~^B_tolcZ+3GHNl0g_0L#h*9|k8I;1aIOWD%sMVX9C$q*POYakB6|c=TWG)e3N@Tcmiq)ludkc_X1Q1)VzyW2RC({Jg|F_P-Swi#50Gglyqu&psJ}ZPmH-H;&kPeS#Y{c$02&)hjgaRkKHRr6aKPfl)dG~X|JBTbbD5S;hnWI^s6Iex^B~-Z1{Kid8?6ynv9<Yo-C#Cx$I(KS|nIk&tCM5bHxF+28QoYHovBigH?RHOJRrwtU1BQOPq)i6n)U$Nf@7L0FE!wMr3S5zcdmfg6Mio?YP=&|a0=PYO=7u6{Ri_8hQU4Bnf2Ikn(-3;@i>;Ag`x$oR(G%f%MT5w@6W4G*qzV6$xKLg4OPa?wQR2^e3i6<Fl3@D3Fb-VS-CKqcW_S~FuW|7}!Y$1IfNR{U`JOA03@xKUeoQ0fsZGi?4)#Y_R*&0gONxE*otIQMid8hGTWs`*Z4ct+1ycl~-U_Cg!ZgGr9>`z+^e+V41(2JrDY+LcJZz8t`lo+u2$6G`hh~Z<CsT(L&SA-HLgY~U1H0S8y;1Nfkbup#?{Z054ZMgzFn_WrgNTUt+GJ*I{t2kh`5<HhCIP^0(<$d218XdT?x!&N96C{U198oxYk$tFsYa{R?@8+{-IG?T-xSuW-%?h~?>=xwevR&K@)?8=8uALd^HS527IaQQ4y>L1-G@WXbYk9mCHJNHw0wX(_JtNy2!;z&-#@h=E1O49hABJIhY?b4m|#gyre~o`LWO6E$W+!Nios)D1kOoy5$5PD&hSeaVk}k&q@Vrl#stx8bGq(mHR8qQG2podNjLuu_2C4i3Q9slc4ujX`+!g&<{>P*E7qE!*sGLMwzP-=X)44`UX+*k^j<R!vu4MJSY`}Hpft-GERIuxz=Q-%l<k-LzEQ$x5z0A*<Ot-Dd)W7#;N(-92js`-?uUE^T%fP#*m;3$<X4yd0T?%q-GusqMv2}6rMa(K(}0FsXE0U1fxCUlTx|P<dDS+}=2oYYEf#Vuhl4!i9?Y$)Ci54_y(Ig3^mv6ywd2S{yCK??u&=8Yf$gR86qzaq^_W;PyfR8l{A|p<jZ?61J${7X6A5KH`x^p|=@us8t|9scTX~3k0mNvew=l})f{SpOyDR&e$?Bm_K#Lx1*=;rfp5Mr4K(5oUR-A1f6F<JePh>V#4j*D-VD!i{5vaO&wt&5K?c_NdItnD9t52}xoBT_<j};p(Wso{M(I@t`372QBEa59vqcXFbC=MZ2V(Ht2Pw}DB4Nyz5E^94VPnyIjl)BDSwY=aC38(>tS&!XZw1OXWgjV|cf<{Q6-1Afo)+UbpU}#3sytLZ_f|rr!d5B8jHDs|27t14zl|=a(Pl8xPT0gFYp@-I595S)=b38{-qtN0w3eCtGZEN9Eg7y_`$uP)zj8LoRkil8%L{Cvf1d#2SQ7k&hdM}n0JmMUWgs^xO#Gdo6rXxCcC8&k$GIL1v72qmc1g1ts$W5sDXW!dAMtr*HAlk?RqUdEafD$DQ>?HE25ZgpcOHj-_)n#c&C?u~P>cQJe!lxfkNuK!uroe_ye_@>EKEx&5dBW%-Ww3H@9d;;(ydeYIo>=zcf&5;cLa34ur(YP4_gmP)27PX!D@b~Hs)kUg0m&8!CY2yO4fpWC5-kR2M{s1SWes5DR2nX?I`t|KYF|gx!}@JMo|h^QY_(tt*4l;PSh$av<UD~cpbys=wYo(c-lN#Gf_2DEAOh(9Pn`nxCnXj-a_TS9eNBG4&$>AN{`mB=M~bhPhvz36ty;;0oMK>dIEr%vOa!n*!q;Afry`7q!r(N@j#qKOvIy!mbSsJiv|Kn#iHqo5Dchya%6V%!#*`WjJ))h=(!)`*L<M5gLlH&Y!hLO1hxbYr5d>Yo+E{1le!@gtAyDgJ!@W`_((n6WoM(Nontn<XNXYk%hNgCPct(ab!Hj*QH|XM4O%-RBz`9pj9!gZogJ``V8I?-VnpVM=p2d|1L($yv8du6LZm2A<Wz<)P8SkSML1N!CyAQ0_RZb^RH*yDY(Il*UZSc|}Q!`-=(8@y?{*zfV)y8I8VV-rbueR1oO*P(5({_(oWZ-)}rUqBFT7XlTh&Ce;mp{Pm9QVRDk1O2qdMs7y0_a?9eW|VlJBx}TZ&5j|sUmgL8B7bi-5sr<1WTX^Roj16M^FH<o2Rt;RAM>cYLG(k1E=l89TuzWV6!}P{+=e0vr21@=!Z_|qIiM;5n1!EK!y9%k?V5_kp+GnZ&AZykB~4R2Nh<}5N=#}#(<gtFe6Dq*14)|vDXY#bfT%}2&}Z+Ff1)n62w7(T6fz|*@<MZO|wq5$3k7VsbgGWHfE76W-W|5b1)8jR656beKi?hSKW%Ix<6igJbh1b<Aga`k6hlx{IXkhxK^Qwva$s646@O1s?;bb&hrElct^(rG=8Ywn%_iF?U^N_-8Nhde!48KnrL6wY{Q4O^Oo(psu%-_En6-j($G2e_%g`Nva(UcD^zXe_fsb=CkArIqX=A990dV3a@)2e8kUdtPN;Bo+{!nL09M-AGZ>K3u%U@bKID5vld6u3AbmU#(zqw3J2lLwc`m~HWz1?DNrD*78?SscPUK0^H3uAi%0N<h?ZK8W&|sm(mo!&Po4U%v!C(9^r=6-bsbC~dr8&6TzhW~!uGT&!Le28eR)`f_m^nFVzF7FTW^C~b+?urjz-UEnE4^E_XGq&L#IBI3j1{6H9(m}s<0?~{6na;-@H{&A7k)m*WM5jKAG$qKIpFn#2of3xF2=L&mmdzOT7nWvtM@fon^HU2F)rlWSnS!aFhE_N*tsifs7t=pPWtGueGvU<+_3spa|i6;)JA2hXxJYv@*#co*AZ2MF?r&oNTpuUU#e(U>JxcObFR*J$mKC8{hgSK0N*fu;E@NZs%Wu*l?9a5u%9H3PGOXj-33cKy4Hj<OY#im%-+SRBbAStHBVl^_DHRHP~4J7wTe6J^jTK#TGm+%qt86aL@8B|E4^tp*p=&xT?UyCwjP73FZZCyoZ)ccd|R7Er-u9$kxdZD=HtyHZhaKJy_BR>oJ5Q^|AlW+DN|()E|y_i4MaasadMr(LDX3Ao-5Q2*f2vMVY>pGKa)LdqhT8{3O0{nwD}K@HV_22+Waf-asdx9JI9PXgjvE*5z7~uQme^(^wf9Kwl?EJSQTaa+WZ2a{Efc(LLYr%x?rcXD5Xzxr&WD_2$3ryU&GRRawb0;S;(hr8SPv*mNgZ_ZbWX5H;p1^LA&ZK5VT9>*8eBHyhJDvE%~A|uzMw=by$wRc7yK!x$Z5!f^QhmWCfLyMYmNkwfR5I8;c>bGQv6vf;EN-9#(pUy%@@9@%IwlrJp@RkZ(TnVC0cBk7I~9Xw7&y*djmj%}h7%dk|l8_Qt`U^|Vq&4JKcWL{V0%wyRQ|cKx&hMa*n^$FgJ&{DsS2dHino_2yoAX_SxOeTCt(H0N1pt^e_2ldqp8cuE7j3ND@NY>Oc!46sbxZLKJ+`vSjdEx+4-eoL$1g*0E-Lik?_BF}>Htzi*rKAu*0eT4Pj^S=+<do8=mb&`lJMR4CV=LhR~QVo{Y+)1fs37w{#gQsBM?ALOz)&!*7ntZYu(bUQ0*=9TOmiFkk#AYE|B&+=j-ES2C?9NRTcyPO&t2rLjCi|`9eZjgfNj8;6?U+wCdYi~&7*d4*#w)SQCJF+k&u+_5t*vK9ywN`RuwWl{%W>!@yWPe7{Y4G*HAFdsFBfZ_Lc7~nVc#fQN@GerCtXERb^|hQrSP>7(;I?2{9v3d1e*2IeX7u|Fjv+QWGdm3S13&rtZ!rpZ*4k~g$1gD>(_BvuR%9FK6n!;-Yfmxer2Pi(>`f5G&PsTuApMA-D;lS41Kx%G}0>nyAUOq?h6E8D6$<`wwSrFI$yfrJ+sKc!j{}ux*(Hx)(B4lkbih$DO(u#ThsIN%|Bmm)f6I*9x!1ae>~lq4D9sbIckyuwiqU3b`Ih9Mtipqs{MWAiRX(TPjC1ErOpf1&DXT+Ixp1$mwmVTV%*S1%yR3EFJ>*<8eE>@1+`~S9;@2u5HgB9sh>6$Yz)Lv34DDaxGTN9Ax<H@?#+$YJKPu4vdvBW;ct3lwsl5I5~vBWIZeH%LWBTk=ZxiE_7`xb>jF2>TNR=0or||+I?a10ItgCvHtws`N6_KK%Ptvh*r6{DOHGPkz#A}l+URS3hHCSu4&Ad7oxNm>|JN&#n|Cok=)rDU(`1?B8gM2+I0QSB<BCV7!CKtx4Yp*N?i+t=G=r&j>+_&}anJ&fTGEA^2id;CUd*6gD+WIz+fH!qhJ8^S0@>^?ru*tmVLrsJWw&8Nme*$)T??vh?X=?Z4t9T~hGlOnE6g@Dw23yPk=-r@UM{rqX%E^^G3o7NrrtK{VB9(^ORV}Tv1%QC*e+o|?2Fv_8A;o3pQ6F@mM@q-Z_ooGe<gk2NHefECxZp7)u^!J@Oq4A%#gir@&vYQ>b0WVPolG?PosYKp2U+UF#7C2zZF<pEoU9J+NfnT&Avc#3hg=Z+3f-lNx~~tCiaN?xJTRyg$K;wyGEKHAk!pubzS;bXEBey*xAx!Z>)#fh;2QyTR2)O&uv29W1&Et^4^443JyM=UR<6ZA6#m0t%)P3khbZEY1#iCoa1RZf?Hph^BA=}#qMZ(9g(GWllj+0`5%aI=}`U_E(fKVcBmMS^!V~rg&06)6X5?QKjMu4+|9@TNPt}!$6;@zI1Y-+ag3IKxyS|C?fefZ<yH>'


def ensure_internal_engine() -> None:
    """Installe automatiquement le moteur inclus dans cette application."""
    PLAYER.parent.mkdir(parents=True, exist_ok=True)
    engine_data = zlib.decompress(base64.b85decode(ENGINE_BUNDLE.encode("ascii")))

    try:
        current = PLAYER.read_bytes()
    except OSError:
        current = b""

    if current != engine_data:
        PLAYER.write_bytes(engine_data)
        PLAYER.chmod(0o755)


def find_script(video: Path) -> Path | None:
    # Priorité au funscript ORIGINAL placé dans le même dossier que la vidéo.
    candidates = [
        video.with_suffix(".funscript"),
        video.with_suffix(".rot.funscript"),
        SCRIPT_DIR / f"{video.stem}.funscript",
        SCRIPT_DIR / f"{video.stem}.rot.funscript",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def convertir_original_temporairement(
    script: Path,
    video: Path,
    amplification_percent: float = 0.0,
) -> Path:
    """
    Transforme le funscript linéaire en vitesse rotative par plateaux.

    Le fichier généré est temporaire et reste au-dessus de 50 :
      50 = arrêt, 51..100 = rotation.
    Il n'y a donc plus de faux va-et-vient dans la piste rotative.

    Amplification :
      0 %   = calcul normal (x1)
      50 %  = environ x2
      100 % = environ x3
    """
    amplification_percent = max(0.0, min(100.0, float(amplification_percent)))
    amplification_factor = 1.0 + 2.0 * (amplification_percent / 100.0)

    donnees = json.loads(script.read_text(encoding="utf-8-sig"))
    actions_source = donnees.get("actions", [])
    actions = []

    for action in actions_source:
        try:
            at = max(0, int(action["at"]))
            pos = max(0, min(100, int(action["pos"])))
        except (KeyError, TypeError, ValueError):
            continue
        actions.append((at, pos))

    actions.sort(key=lambda item: item[0])
    if len(actions) < 2:
        raise ValueError("Le funscript original contient moins de deux actions valides.")

    # Éliminer les doublons de temps.
    uniques = []
    for action in actions:
        if uniques and uniques[-1][0] == action[0]:
            uniques[-1] = action
        else:
            uniques.append(action)

    sortie = [{"at": 0, "pos": 50}]

    def ajouter(at: int, pos: int) -> None:
        element = {"at": max(0, int(at)), "pos": max(0, min(100, int(pos)))}
        if sortie and sortie[-1]["at"] == element["at"]:
            sortie[-1] = element
        elif not sortie or sortie[-1] != element:
            sortie.append(element)

    for index in range(1, len(uniques)):
        debut, pos_debut = uniques[index - 1]
        fin, pos_fin = uniques[index]
        duree = fin - debut
        amplitude = abs(pos_fin - pos_debut)

        if duree <= 0:
            continue

        # Une longue section presque immobile devient un arrêt réel.
        if amplitude < 2 or (duree >= 2500 and amplitude < 8):
            commande = 50
        else:
            vitesse = amplitude * 1000.0 / duree
            vitesse_amplifiee = vitesse * amplification_factor
            # Minimum suffisamment élevé pour démarrer réellement le Mowgli.
            # L'amplification augmente la commande sans dépasser 100 %.
            puissance = max(0.20, min(1.0, vitesse_amplifiee / 160.0))
            commande = 50 + int(round(puissance * 50.0))

        ajouter(debut, commande)
        ajouter(fin, commande)

    ajouter(uniques[-1][0], 50)

    resultat = dict(donnees)
    resultat["actions"] = sortie
    resultat["inverted"] = False
    resultat["range"] = 100
    resultat["runtime_rotary_conversion"] = True
    resultat["runtime_amplification_percent"] = amplification_percent
    resultat["runtime_amplification_factor"] = amplification_factor

    destination = Path(tempfile.gettempdir()) / (
        f"rotary-runtime-{os.getpid()}-{video.stem}.rot.funscript"
    )
    destination.write_text(
        json.dumps(resultat, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    return destination


def natural_key(path: Path) -> list[object]:
    return [
        int(part) if part.isdigit() else part.casefold()
        for part in re.split(r"(\d+)", path.name)
    ]


def script_candidates_for_deletion(video: Path, selected_script: Path | None) -> list[Path]:
    """Retourne tous les scripts portant exactement le nom de la vidéo."""
    folders = [
        video.parent,
        video.parent / "rotation",
        video.parent / "Rotation",
        video.parent / "RotaryScript",
        SCRIPT_DIR,
    ]
    candidates: list[Path] = []
    if selected_script is not None:
        candidates.append(selected_script)
    for folder in folders:
        candidates.extend([
            folder / f"{video.stem}.funscript",
            folder / f"{video.stem}.rot.funscript",
        ])

    unique: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            resolved = candidate.absolute()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(candidate)
    return unique


class RotaryPlayerGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1240x980")
        self.minsize(1100, 820)
        self.configure(bg=COLORS["bg"])

        # Démarrer maximisé sous KDE/X11. Repli sur la taille de l'écran
        # lorsque le gestionnaire de fenêtres ne prend pas -zoomed en charge.
        try:
            self.attributes("-zoomed", True)
        except tk.TclError:
            self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

        self.language = "fr"
        self.language_display = tk.StringVar(value="Français")

        self.video_path = tk.StringVar()
        self.last_video_dir = VIDEO_DIR if VIDEO_DIR.is_dir() else Path.home()
        self.script_path = tk.StringVar(value=self.tr("Aucun script sélectionné"))
        self.status = tk.StringVar(value=self.tr("Choisis une vidéo pour commencer."))
        self.max_power = tk.DoubleVar(value=0.80)
        self.zero_hold = tk.IntVar(value=150)
        self.smoothing = tk.DoubleVar(value=0.20)
        self.min_power = tk.DoubleVar(value=0.08)
        self.amplification = tk.DoubleVar(value=0.0)
        self.fullscreen = tk.BooleanVar(value=True)
        self.pump_enabled = tk.BooleanVar(value=False)
        self.pump_seconds = tk.DoubleVar(value=1.5)
        self.pump_interval = tk.DoubleVar(value=1.0)
        self.pump_level = tk.IntVar(value=7)
        self.selected_pump_patterns = ["01 Escalier montant"]
        self.delete_after_end_var = tk.BooleanVar(value=False)
        self.play_next_var = tk.BooleanVar(value=True)

        self.process: subprocess.Popen[str] | None = None
        self.playlist: list[Path] = []
        self.playlist_active = False
        self.delete_after_natural_end = False
        self.stop_requested = False
        self.manual_next_requested = False
        self.current_video: Path | None = None
        self.current_script: Path | None = None
        self.runtime_script: Path | None = None
        self.graph_actions: list[tuple[int, int]] = []
        self.graph_duration_ms = 0
        self.graph_position_ms = 0
        self.progress_file = Path(tempfile.gettempdir()) / f"rotary-player-progress-{os.getpid()}.json"
        self.mpv_socket = Path(tempfile.gettempdir()) / f"rotary-player-mpv-{os.getpid()}.sock"
        self.configure_styles()
        self.load_config()
        if not self.video_path.get():
            self.script_path.set(self.tr("Aucun script sélectionné"))
            self.status.set(self.tr("Choisis une vidéo pour commencer."))
        try:
            ensure_internal_engine()
        except OSError:
            pass
        self.build_ui()
        self.after(150, self.update_graph_position)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def tr(self, text: str) -> str:
        if self.language == "en":
            return TRANSLATIONS.get(text, text)
        return text

    def pump_pattern_display(self, key: str) -> str:
        label = PUMP_PATTERN_LABELS.get(key, key)
        if self.language != "en":
            return label
        english_name = PUMP_PATTERN_NAMES_EN.get(key, key)
        sequence = label.split(" — ", 1)[1] if " — " in label else ""
        return f"{english_name} — {sequence}" if sequence else english_name

    def change_language(self, _event=None) -> None:
        self.language = "en" if self.language_display.get() == "English" else "fr"
        self.save_config()
        for child in self.winfo_children():
            child.destroy()
        self.build_ui()

    def configure_styles(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "TButton",
            background=COLORS["panel_alt"],
            foreground=COLORS["accent"],
            bordercolor=COLORS["border"],
            focusthickness=1,
            focuscolor=COLORS["accent"],
            padding=(10, 6),
            font=("DejaVu Sans Mono", 9, "bold"),
        )
        style.map(
            "TButton",
            background=[("active", "#0A3A16"), ("pressed", "#0F5520")],
            foreground=[("active", "#B7FFBF"), ("pressed", "#FFFFFF")],
        )

        style.configure(
            "TCheckbutton",
            background=COLORS["panel"],
            foreground=COLORS["text"],
            font=("DejaVu Sans Mono", 9),
        )
        style.map(
            "TCheckbutton",
            foreground=[("active", COLORS["accent"])],
            background=[("active", COLORS["panel"])],
        )

        style.configure(
            "TLabel",
            background=COLORS["bg"],
            foreground=COLORS["text"],
            font=("DejaVu Sans Mono", 9),
        )
        style.theme_use("clam")

        style.configure(
            ".",
            background=COLORS["bg"],
            foreground=COLORS["text"],
            bordercolor=COLORS["border"],
            lightcolor=COLORS["border"],
            darkcolor=COLORS["border"],
            font=("DejaVu Sans Mono", 10, "bold"),
        )

        style.configure("Root.TFrame", background=COLORS["bg"])
        style.configure(
            "Card.TFrame",
            background=COLORS["panel"],
            borderwidth=1,
            relief="solid",
        )
        style.configure(
            "Header.TLabel",
            background=COLORS["bg"],
            foreground=COLORS["text"],
            font=("Noto Sans", 22, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background=COLORS["bg"],
            foreground=COLORS["muted"],
            font=("DejaVu Sans Mono", 10),
        )
        style.configure(
            "CardTitle.TLabel",
            background=COLORS["panel"],
            foreground=COLORS["text"],
            font=("Noto Sans", 12, "bold"),
        )
        style.configure(
            "CardText.TLabel",
            background=COLORS["panel"],
            foreground=COLORS["muted"],
        )
        style.configure(
            "Value.TLabel",
            background=COLORS["panel"],
            foreground=COLORS["accent_hover"],
            font=("DejaVu Sans Mono", 10, "bold"),
        )
        style.configure(
            "Status.TLabel",
            background=COLORS["panel_alt"],
            foreground=COLORS["muted"],
            padding=(12, 9),
        )

        style.configure(
            "Dark.TEntry",
            fieldbackground=COLORS["panel_alt"],
            foreground=COLORS["text"],
            insertcolor=COLORS["text"],
            bordercolor=COLORS["border"],
            padding=9,
        )
        style.map(
            "Dark.TEntry",
            fieldbackground=[("readonly", COLORS["panel_alt"])],
            foreground=[("readonly", COLORS["text"])],
        )

        style.configure(
            "TCombobox",
            fieldbackground=COLORS["panel_alt"],
            background=COLORS["panel_alt"],
            foreground=COLORS["text"],
            arrowcolor=COLORS["text"],
            bordercolor=COLORS["accent"],
            padding=6,
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", COLORS["panel_alt"])],
            foreground=[("readonly", COLORS["text"])],
            selectbackground=[("readonly", COLORS["accent"])],
            selectforeground=[("readonly", "#ffffff")],
        )

        style.configure(
            "Accent.TButton",
            background=COLORS["accent"],
            foreground="#D7FFDA",
            borderwidth=0,
            focusthickness=0,
            padding=(16, 11),
            font=("DejaVu Sans Mono", 10, "bold"),
        )
        style.map(
            "Accent.TButton",
            background=[
                ("active", COLORS["accent_hover"]),
                ("disabled", COLORS["panel_alt"]),
            ],
            foreground=[("disabled", "#6e7582")],
        )

        style.configure(
            "Secondary.TButton",
            background=COLORS["panel_alt"],
            foreground=COLORS["text"],
            borderwidth=1,
            padding=(14, 10),
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#2a2f39")],
        )

        style.configure(
            "Danger.TButton",
            background="#382028",
            foreground="#ff8797",
            borderwidth=0,
            padding=(14, 10),
            font=("DejaVu Sans Mono", 10, "bold"),
        )
        style.map(
            "Danger.TButton",
            background=[("active", "#4a2530")],
        )

        style.configure(
            "Dark.Horizontal.TScale",
            background=COLORS["panel"],
            troughcolor=COLORS["track"],
            bordercolor=COLORS["panel"],
            lightcolor=COLORS["accent"],
            darkcolor=COLORS["accent"],
        )

        style.configure(
            "Dark.TCheckbutton",
            background=COLORS["panel"],
            foreground=COLORS["text"],
            indicatorbackground=COLORS["panel_alt"],
            indicatorforeground=COLORS["accent"],
            padding=4,
        )
        style.map(
            "Dark.TCheckbutton",
            background=[("active", COLORS["panel"])],
            foreground=[("active", COLORS["text"])],
        )

    def build_ui(self) -> None:
        # Interface fixe : aucun scroll général.
        # Le seul scroll vertical reste celui de la liste des patterns.
        shell = ttk.Frame(self, style="Root.TFrame")
        shell.pack(fill="both", expand=True)

        graph_frame = tk.Frame(
            shell,
            bg="#010301",
            height=78,
            highlightbackground=COLORS["accent"],
            highlightthickness=1,
        )
        graph_frame.pack(side="bottom", fill="x")
        graph_frame.pack_propagate(False)

        graph_header = tk.Frame(graph_frame, bg="#010301", height=28)
        graph_header.pack(side="top", fill="x")
        graph_header.pack_propagate(False)

        graph_title = tk.Label(
            graph_header,
            text=self.tr("MOUVEMENT FUNSCRIPT — clique ou glisse pour déplacer la vidéo"),
            bg="#010301",
            fg=COLORS["accent_hover"],
            font=("DejaVu Sans Mono", 8, "bold"),
            anchor="w",
            padx=10,
        )
        graph_title.pack(side="left", fill="x", expand=True)

        for label, command in (
            ("−10 s", lambda: self.seek_relative(-10)),
            ("Pause / Reprendre", self.toggle_pause),
            ("+10 s", lambda: self.seek_relative(10)),
        ):
            tk.Button(
                graph_header,
                text=label,
                command=command,
                bg=COLORS["panel_alt"],
                fg=COLORS["text"],
                activebackground=COLORS["border"],
                activeforeground="#ffffff",
                relief="flat",
                borderwidth=0,
                padx=10,
                pady=2,
                cursor="hand2",
                font=("DejaVu Sans Mono", 8, "bold"),
            ).pack(side="left", padx=(0, 4), pady=3)

        self.graph_canvas = tk.Canvas(
            graph_frame,
            bg="#000000",
            highlightthickness=0,
            borderwidth=0,
            height=54,
        )
        self.graph_canvas.pack(side="bottom", fill="both", expand=True)
        self.graph_canvas.bind("<Configure>", lambda _event: self.draw_funscript_graph())
        self.graph_canvas.bind("<Button-1>", self.seek_from_graph)
        self.graph_canvas.bind("<B1-Motion>", self.seek_from_graph)
        self.graph_canvas.bind("<Button-3>", self.toggle_pause)
        self.graph_canvas.bind("<MouseWheel>", self.graph_mousewheel)
        self.graph_canvas.bind("<Button-4>", self.graph_mousewheel)
        self.graph_canvas.bind("<Button-5>", self.graph_mousewheel)

        root = ttk.Frame(shell, style="Root.TFrame", padding=(18, 10))
        root.pack(side="top", fill="both", expand=True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(3, weight=1)

        # F11 bascule l'application en plein écran; Échap revient maximisé.
        self.bind("<F11>", self.toggle_app_fullscreen)
        self.bind("<Escape>", self.leave_app_fullscreen)

        header = ttk.Frame(root, style="Root.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header, text="JoyHub Gatling 2 Player", style="Header.TLabel"
        ).grid(row=0, column=0, sticky="w")
        version_box = ttk.Frame(header, style="Root.TFrame")
        version_box.grid(row=0, column=1, rowspan=2, sticky="ne", padx=(20, 0))
        ttk.Label(
            version_box,
            text=APP_VERSION,
            style="Subtitle.TLabel",
        ).pack(side="left", padx=(0, 10))
        language_combo = ttk.Combobox(
            version_box,
            textvariable=self.language_display,
            values=("Français", "English"),
            state="readonly",
            width=10,
        )
        language_combo.pack(side="left")
        language_combo.bind("<<ComboboxSelected>>", self.change_language)
        ttk.Label(
            header,
            text=self.tr("Conversion directe en rotation — amplification adaptateur 0 à 100 %"),
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        file_card = ttk.Frame(root, style="Card.TFrame", padding=7)
        file_card.grid(row=1, column=0, sticky="ew", pady=(0, 4))
        file_card.columnconfigure(1, weight=1)

        ttk.Label(
            file_card, text=self.tr("Fichier"), style="CardTitle.TLabel"
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))

        ttk.Label(
            file_card, text=self.tr("Vidéo"), style="CardText.TLabel"
        ).grid(row=1, column=0, sticky="w", pady=2)

        ttk.Entry(
            file_card,
            textvariable=self.video_path,
            state="readonly",
            style="Dark.TEntry",
        ).grid(row=1, column=1, sticky="ew", padx=10, pady=2)

        ttk.Button(
            file_card,
            text=self.tr("Parcourir"),
            style="Secondary.TButton",
            command=self.choose_video,
        ).grid(row=1, column=2, pady=2)

        ttk.Label(
            file_card, text=self.tr("Script"), style="CardText.TLabel"
        ).grid(row=2, column=0, sticky="nw", pady=2)

        self.script_label = ttk.Label(
            file_card,
            textvariable=self.script_path,
            style="CardText.TLabel",
            wraplength=580,
        )
        self.script_label.grid(
            row=2, column=1, columnspan=2, sticky="w", padx=10, pady=2
        )

        settings = ttk.Frame(root, style="Card.TFrame", padding=7)
        settings.grid(row=2, column=0, sticky="ew", pady=(0, 4))
        settings.columnconfigure(1, weight=1)

        ttk.Label(
            settings, text=self.tr("Réglages"), style="CardTitle.TLabel"
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))

        self.add_scale(
            settings, 1, self.tr("Puissance maximale"), self.max_power, 0.10, 1.00,
            lambda v: f"{float(v) * 100:.0f} %"
        )
        self.add_scale(
            settings, 2, self.tr("Passage à zéro"), self.zero_hold, 0, 1000,
            lambda v: f"{int(float(v))} ms"
        )
        self.add_scale(
            settings, 3, self.tr("Lissage"), self.smoothing, 0.00, 0.95,
            lambda v: f"{float(v):.2f}"
        )
        self.add_scale(
            settings, 4, self.tr("Vitesse minimale"), self.min_power, 0.00, 0.50,
            lambda v: f"{float(v) * 100:.0f} %"
        )
        self.add_scale(
            settings, 5, self.tr("Amplification adaptateur"), self.amplification, 0, 100,
            lambda v: (
                f"{float(v):.0f} %  "
                f"(x{1.0 + 2.0 * float(v) / 100.0:.2f})"
            )
        )

        ttk.Checkbutton(
            settings,
            text=self.tr("Ouvrir MPV en plein écran sur l’écran de droite"),
            variable=self.fullscreen,
            style="Dark.TCheckbutton",
        ).grid(row=6, column=1, sticky="w", padx=10, pady=(10, 2))

        ttk.Checkbutton(
            settings,
            text=self.tr("Pompage Gatling 2 au début de chaque cycle"),
            variable=self.pump_enabled,
            style="Dark.TCheckbutton",
        ).grid(row=7, column=1, sticky="w", padx=10, pady=(8, 2))

        self.add_scale(
            settings, 8, self.tr("Durée du pompage"), self.pump_seconds, 0.2, 7.0,
            lambda v: f"{float(v):.1f} s"
        )
        self.add_scale(
            settings, 9, self.tr("Pause entre pompages"), self.pump_interval, 0.2, 7.0,
            lambda v: f"{float(v):.1f} s"
        )
        self.add_scale(
            settings, 10, self.tr("Niveau de pompe (max 7)"), self.pump_level, 1, 7,
            lambda v: f"{int(float(v))} / 7"
        )

        ttk.Checkbutton(
            settings,
            text=self.tr("Supprimer la vidéo et ses funscripts à la fin ou en passant à la suivante"),
            variable=self.delete_after_end_var,
            style="Dark.TCheckbutton",
        ).grid(row=11, column=1, sticky="w", padx=10, pady=(8, 2))

        ttk.Checkbutton(
            settings,
            text=self.tr("Passer automatiquement à la vidéo suivante"),
            variable=self.play_next_var,
            style="Dark.TCheckbutton",
        ).grid(row=12, column=1, sticky="w", padx=10, pady=(6, 2))

        pattern_card = ttk.Frame(root, style="Card.TFrame", padding=7)
        pattern_card.grid(row=3, column=0, sticky="nsew", pady=(0, 3))
        pattern_card.columnconfigure(0, weight=1)
        pattern_card.rowconfigure(1, weight=1)

        ttk.Label(
            pattern_card,
            text=self.tr("Patterns de pompage — sélection libre"),
            style="CardTitle.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        self.pattern_count_label = ttk.Label(
            pattern_card,
            text=("0 selected" if self.language == "en" else "0 sélectionné(s)"),
            style="Value.TLabel",
        )
        self.pattern_count_label.grid(row=0, column=1, sticky="e", padx=(12, 0))

        list_frame = tk.Frame(pattern_card, bg=COLORS["panel"])
        list_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.pump_pattern_listbox = tk.Listbox(
            list_frame,
            selectmode=tk.MULTIPLE,
            exportselection=False,
            height=20,
            bg=COLORS["panel_alt"],
            fg=COLORS["text"],
            selectbackground=COLORS["accent"],
            selectforeground="#ffffff",
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
            highlightthickness=1,
            borderwidth=0,
            activestyle="none",
            font=("DejaVu Sans Mono", 10),
        )
        pattern_scroll = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.pump_pattern_listbox.yview
        )
        self.pump_pattern_listbox.configure(yscrollcommand=pattern_scroll.set)
        self.pump_pattern_listbox.grid(row=0, column=0, sticky="nsew")
        pattern_scroll.grid(row=0, column=1, sticky="ns")

        for pattern_name in PUMP_PATTERNS:
            self.pump_pattern_listbox.insert(
                tk.END,
                self.pump_pattern_display(pattern_name),
            )

        for index, pattern_name in enumerate(PUMP_PATTERNS):
            if pattern_name in self.selected_pump_patterns:
                self.pump_pattern_listbox.selection_set(index)

        self.pump_pattern_listbox.bind("<<ListboxSelect>>", self.on_pump_pattern_select)
        self.update_pump_pattern_count()

        ttk.Label(
            pattern_card,
            text=self.tr("Chaque pattern est joué au complet, puis un autre est choisi parmi les sélections. Niveau toujours limité à 7."),
            style="CardText.TLabel",
            wraplength=1080,
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))

        actions = ttk.Frame(root, style="Root.TFrame")
        actions.grid(row=4, column=0, sticky="ew", pady=(0, 4))
        actions.columnconfigure(0, weight=1)

        self.launch_button = ttk.Button(
            actions,
            text=self.tr("▶  Lancer la vidéo"),
            command=self.launch,
            state="disabled",
            style="Accent.TButton",
        )
        self.launch_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.folder_button = ttk.Button(
            actions,
            text=self.tr("⏭  Lire le dossier"),
            command=self.launch_folder_playlist,
            state="disabled",
            style="Secondary.TButton",
        )
        self.folder_button.grid(row=0, column=1, padx=(0, 8))

        self.next_button = ttk.Button(
            actions,
            text=self.tr("⏩  Vidéo suivante"),
            command=self.next_video,
            state="disabled",
            style="Secondary.TButton",
        )
        self.next_button.grid(row=0, column=2, padx=(0, 8))

        ttk.Button(
            actions,
            text=self.tr("🧪  Test pompage continu 10 s"),
            command=self.test_pump,
            style="Secondary.TButton",
        ).grid(row=0, column=3, padx=(0, 8))

        ttk.Button(
            actions,
            text=self.tr("■  Arrêter"),
            command=self.stop,
            style="Danger.TButton",
        ).grid(row=0, column=4)

        self.status_label = ttk.Label(
            root,
            textvariable=self.status,
            style="Status.TLabel",
            anchor="w",
        )
        self.status_label.grid(row=5, column=0, sticky="ew")

        self.after(100, self.draw_funscript_graph)

    def get_selected_pump_patterns(self) -> list[str]:
        if not hasattr(self, "pump_pattern_listbox"):
            return list(self.selected_pump_patterns)

        pattern_names = list(PUMP_PATTERNS.keys())
        selected = []
        for i in self.pump_pattern_listbox.curselection():
            if 0 <= i < len(pattern_names):
                selected.append(pattern_names[i])
        return selected

    def update_pump_pattern_count(self) -> None:
        count = len(self.get_selected_pump_patterns())
        if hasattr(self, "pattern_count_label"):
            self.pattern_count_label.configure(text=(f"{count} selected" if self.language == "en" else f"{count} sélectionné(s)"))

    def on_pump_pattern_select(self, _event=None) -> None:
        indices = list(self.pump_pattern_listbox.curselection())
        selected = self.get_selected_pump_patterns()
        if selected:
            self.selected_pump_patterns = selected
        self.update_pump_pattern_count()

    def clear_funscript_graph(self) -> None:
        self.graph_actions = []
        self.graph_duration_ms = 0
        self.graph_position_ms = 0
        if hasattr(self, "graph_canvas"):
            self.draw_funscript_graph()

    def load_funscript_graph(self, script: Path) -> None:
        try:
            data = json.loads(script.read_text(encoding="utf-8-sig"))
            actions = data.get("actions", [])
            parsed = []
            for action in actions:
                at = int(action.get("at", 0))
                pos = max(0, min(100, int(action.get("pos", 50))))
                parsed.append((at, pos))
            parsed.sort()
            self.graph_actions = parsed
            self.graph_duration_ms = parsed[-1][0] if parsed else 0
            self.graph_position_ms = 0
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            self.graph_actions = []
            self.graph_duration_ms = 0
            self.graph_position_ms = 0
        if hasattr(self, "graph_canvas"):
            self.draw_funscript_graph()

    def draw_funscript_graph(self) -> None:
        if not hasattr(self, "graph_canvas"):
            return
        c = self.graph_canvas
        c.delete("all")
        w = max(c.winfo_width(), 2)
        h = max(c.winfo_height(), 2)
        # Grille très visible, même avant le chargement d'un script.
        for fraction in (0.25, 0.50, 0.75):
            y_grid = h * fraction
            c.create_line(
                0, y_grid, w, y_grid,
                fill="#262b36",
                width=1,
                dash=(3, 5),
            )
        for fraction in (0.25, 0.50, 0.75):
            x_grid = w * fraction
            c.create_line(
                x_grid, 0, x_grid, h,
                fill="#171b23",
                width=1,
            )

        duration = self.graph_duration_ms
        if self.graph_actions and duration > 0:
            points = []
            for at, pos in self.graph_actions:
                x = (at / duration) * w
                y = h - 5 - (pos / 100.0) * (h - 10)
                points.extend((x, y))
            if len(points) >= 4:
                c.create_line(
                    *points,
                    fill="#b39cff",
                    width=2,
                    smooth=False,
                )

            x_cursor = (
                min(max(self.graph_position_ms / duration, 0.0), 1.0) * w
            )
            c.create_line(
                x_cursor, 0, x_cursor, h,
                fill="#ff263f",
                width=4,
            )
        else:
            c.create_text(
                12,
                h / 2,
                text=self.tr("Choisis une vidéo avec son funscript"),
                fill="#c4cad6",
                anchor="w",
                font=("DejaVu Sans Mono", 10, "bold"),
            )
            c.create_line(
                3, 0, 3, h,
                fill="#ff263f",
                width=4,
            )

    def send_mpv_command(self, command: list) -> bool:
        """Envoie une commande JSON IPC au MPV actuellement lancé."""
        if self.process is None or self.process.poll() is not None:
            self.set_status("Aucune vidéo en lecture.", "warning")
            return False
        if not self.mpv_socket.exists():
            self.set_status("Contrôle MPV indisponible : socket IPC absent.", "danger")
            return False
        payload = json.dumps({"command": command}).encode("utf-8") + b"\n"
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                client.settimeout(0.5)
                client.connect(str(self.mpv_socket))
                client.sendall(payload)
            return True
        except OSError as exc:
            self.set_status(f"Erreur de contrôle MPV : {exc}", "danger")
            return False

    def seek_relative(self, seconds: float) -> None:
        self.send_mpv_command(["seek", float(seconds), "relative+exact"])

    def toggle_pause(self, _event=None):
        self.send_mpv_command(["cycle", "pause"])
        return "break"

    def seek_from_graph(self, event):
        duration_ms = self.graph_duration_ms
        width = max(self.graph_canvas.winfo_width(), 1)
        if duration_ms <= 0:
            self.set_status("Durée de la vidéo inconnue.", "warning")
            return "break"
        ratio = min(max(event.x / width, 0.0), 1.0)
        seconds = (duration_ms * ratio) / 1000.0
        if self.send_mpv_command(["seek", seconds, "absolute+exact"]):
            self.graph_position_ms = int(seconds * 1000)
            self.draw_funscript_graph()
        return "break"

    def graph_mousewheel(self, event):
        if getattr(event, "num", None) == 4 or getattr(event, "delta", 0) > 0:
            self.seek_relative(5)
        else:
            self.seek_relative(-5)
        return "break"

    def update_graph_position(self) -> None:
        if self.process is not None and self.process.poll() is None:
            try:
                data = json.loads(
                    self.progress_file.read_text(encoding="utf-8")
                )
                self.graph_position_ms = int(
                    float(data.get("time_pos", 0.0)) * 1000
                )
                duration_ms = int(
                    float(data.get("duration", 0.0)) * 1000
                )
                if duration_ms > 0:
                    self.graph_duration_ms = duration_ms
                self.draw_funscript_graph()
            except (OSError, ValueError, TypeError, json.JSONDecodeError):
                pass

        # La boucle continue même avant ou après une lecture.
        self.after(80, self.update_graph_position)

    def add_scale(
        self, parent, row, label, variable, minimum, maximum, formatter
    ) -> None:
        ttk.Label(
            parent, text=label, style="CardText.TLabel"
        ).grid(row=row, column=0, sticky="w", pady=3)

        scale = ttk.Scale(
            parent,
            variable=variable,
            from_=minimum,
            to=maximum,
            orient="horizontal",
            style="Dark.Horizontal.TScale",
        )
        scale.grid(row=row, column=1, sticky="ew", padx=10, pady=3)

        value_label = ttk.Label(
            parent, width=9, anchor="e", style="Value.TLabel"
        )
        value_label.grid(row=row, column=2, sticky="e")

        def update(*_) -> None:
            value_label.configure(text=formatter(variable.get()))

        variable.trace_add("write", update)
        update()

    def set_status(self, text: str, kind: str = "neutral") -> None:
        colors = {
            "neutral": COLORS["muted"],
            "success": COLORS["success"],
            "warning": COLORS["warning"],
            "danger": COLORS["danger"],
        }
        self.status.set(text)
        ttk.Style(self).configure(
            "Status.TLabel",
            background=COLORS["panel_alt"],
            foreground=colors.get(kind, COLORS["muted"]),
            padding=(12, 9),
        )

    def toggle_app_fullscreen(self, _event=None) -> None:
        enabled = bool(self.attributes("-fullscreen"))
        self.attributes("-fullscreen", not enabled)

    def leave_app_fullscreen(self, _event=None) -> None:
        if bool(self.attributes("-fullscreen")):
            self.attributes("-fullscreen", False)
        try:
            self.attributes("-zoomed", True)
        except tk.TclError:
            pass

    def choose_video(self) -> None:
        initial = self.last_video_dir if self.last_video_dir.is_dir() else (
            VIDEO_DIR if VIDEO_DIR.is_dir() else Path.home()
        )
        chosen = filedialog.askopenfilename(
            title=self.tr("Choisir une vidéo"),
            initialdir=str(initial),
            filetypes=(
                (self.tr("Vidéos"), "*.mp4 *.mkv *.avi *.mov *.webm *.m4v"),
                (self.tr("Tous les fichiers"), "*"),
            ),
        )
        if not chosen:
            return

        video = Path(chosen)
        self.last_video_dir = video.parent
        self.save_config()
        script = find_script(video)
        self.video_path.set(str(video))

        if script:
            self.load_funscript_graph(script)
            self.script_path.set(f"✓  {script}")
            self.script_label.configure(foreground=COLORS["success"])
            self.set_status("Funscript original trouvé. Conversion automatique prête.", "success")
            self.launch_button.configure(state="normal")
            self.folder_button.configure(state="normal")
            self.next_button.configure(state="normal")
        else:
            self.clear_funscript_graph()
            self.script_path.set(
                f"✕  Aucun script correspondant dans {SCRIPT_DIR}"
            )
            self.script_label.configure(foreground=COLORS["danger"])
            self.set_status("Aucun RotaryScript correspondant.", "danger")
            self.launch_button.configure(state="disabled")
            self.folder_button.configure(state="disabled")
            self.next_button.configure(state="disabled")
            messagebox.showwarning(
                "RotaryScript introuvable",
                "Aucun script portant le même nom que la vidéo n'a été trouvé.\n\n"
                f"Dossier recherché :\n{SCRIPT_DIR}\n\n"
                f"Noms recherchés :\n"
                f"{video.stem}.rot.funscript\n"
                f"{video.stem}.funscript",
            )


    def test_pump(self) -> None:
        """Lance un test direct sans vidéo et sans funscript."""
        if not PYTHON.is_file():
            messagebox.showerror(
                "Python introuvable",
                f"Environnement Python introuvable :\n{PYTHON}"
            )
            return

        try:
            ensure_internal_engine()
        except OSError as exc:
            messagebox.showerror(
                "Erreur du moteur intégré",
                f"Impossible de préparer le moteur de test :\n{exc}"
            )
            return

        self.stop()

        command = [
            str(PYTHON),
            str(PLAYER),
            "--test-pump",
            "--test-pump-seconds", "10",
            "--max-power", f"{self.max_power.get():.3f}",
            "--verbose",
            "--progress-file", str(self.progress_file),
        ]

        try:
            self.process = subprocess.Popen(command)
        except OSError as exc:
            messagebox.showerror("Erreur de lancement", str(exc))
            return

        self.set_status(
            f"Test Constrict en cours pendant 10 secondes — PID {self.process.pid}",
            "warning",
        )
        self.after(100, self.check_process)


    def launch(self, video: Path | None = None, script: Path | None = None) -> None:
        if video is None:
            video = Path(self.video_path.get())
        if script is None:
            script_text = self.script_path.get().removeprefix("✓  ")
            script = Path(script_text)

        if not video.is_file() or not script.is_file():
            messagebox.showerror(
                "Fichier introuvable",
                "La vidéo ou le RotaryScript n'existe plus."
            )
            return

        if not PYTHON.is_file():
            messagebox.showerror(
                "Python introuvable",
                f"Environnement Python introuvable :\n{PYTHON}"
            )
            return

        try:
            ensure_internal_engine()
        except OSError as exc:
            messagebox.showerror(
                "Erreur du moteur intégré",
                f"Impossible de préparer le moteur de lecture :\n{exc}"
            )
            return

        if not self.playlist_active:
            self.stop()
        self.stop_requested = False
        self.current_video = video
        self.current_script = script

        # Conversion automatique au lancement : le va-et-vient linéaire
        # devient une vitesse de rotation dans un seul sens.
        try:
            runtime_script = convertir_original_temporairement(
                script,
                video,
                self.amplification.get(),
            )
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            messagebox.showerror(
                "Erreur de conversion",
                f"Impossible de convertir le funscript original :\n{exc}",
            )
            return

        self.runtime_script = runtime_script
        self.load_funscript_graph(runtime_script)
        try:
            self.progress_file.unlink(missing_ok=True)
            self.mpv_socket.unlink(missing_ok=True)
        except OSError:
            pass
        self.save_config()

        command = [
            str(PYTHON),
            str(PLAYER),
            str(video),
            str(runtime_script),
            "--max-power", f"{self.max_power.get():.3f}",
            "--zero-hold-ms", str(int(self.zero_hold.get())),
            "--speed-smoothing", f"{self.smoothing.get():.3f}",
            "--min-running-power", f"{self.min_power.get():.3f}",
            "--min-change", "0.001",
            "--scan-seconds", "6.0",
            "--verbose",
            "--progress-file", str(self.progress_file),
            f"--mpv-arg=--input-ipc-server={self.mpv_socket}",
            "--mpv-arg=--screen=1",
            "--mpv-arg=--fs-screen=1",
        ]


        if self.pump_enabled.get():
            command.extend([
                "--pump",
                "--pump-seconds", f"{self.pump_seconds.get():.2f}",
                "--pump-interval", f"{self.pump_interval.get():.2f}",
                "--pump-level", str(max(1, min(7, int(self.pump_level.get())))),
                "--pump-patterns-json", json.dumps(
                    self.get_selected_pump_patterns() or ["01 Escalier montant"],
                    ensure_ascii=False,
                ),
            ])

        if self.fullscreen.get():
            command.append("--mpv-arg=--fs")

        try:
            self.process = subprocess.Popen(command)
        except OSError as exc:
            messagebox.showerror("Erreur de lancement", str(exc))
            return

        pump_text = (
            f" — Pompe {self.pump_seconds.get():.1f} s / pause {self.pump_interval.get():.1f} s / {len(self.get_selected_pump_patterns() or [1])} pattern(s) / max 7"
            if self.pump_enabled.get()
            else " — pompage désactivé"
        )
        amplification_factor = 1.0 + 2.0 * self.amplification.get() / 100.0
        amplification_text = (
            f" — amplification {self.amplification.get():.0f} % "
            f"(x{amplification_factor:.2f})"
        )
        self.set_status(
            f"Lecture en cours : {video.name}{pump_text}{amplification_text} "
            f"— PID {self.process.pid}",
            "success",
        )
        self.after(100, self.check_process)

    def next_video(self) -> None:
        video = self.current_video
        script = self.current_script

        if video is None:
            selected_text = self.video_path.get().strip()
            if selected_text:
                selected = Path(selected_text)
                if selected.is_file():
                    video = selected
                    script = find_script(selected)

        if video is None or not video.is_file():
            self.set_status("Aucune vidéo actuelle à passer.", "warning")
            return

        # Préparer les vidéos suivantes si aucune liste n'est active.
        if not self.playlist_active:
            videos = sorted(
                [
                    path for path in video.parent.iterdir()
                    if path.is_file()
                    and path.suffix.casefold() in VIDEO_EXTENSIONS
                ],
                key=natural_key,
            )
            try:
                current_index = videos.index(video)
            except ValueError:
                self.set_status(
                    "La vidéo actuelle n’est plus dans son dossier.",
                    "warning",
                )
                return

            self.playlist = [
                candidate
                for candidate in videos[current_index + 1:]
                if find_script(candidate)
            ]
            self.playlist_active = bool(self.playlist)

        deleted_count = 0
        if self.delete_after_end_var.get():
            deleted_count = len(self.delete_completed_files(video, script))

        if not self.playlist:
            self.playlist_active = False
            if self.process is not None and self.process.poll() is None:
                self.stop_requested = True
                self.process.terminate()

            if deleted_count:
                self.set_status(
                    f"{video.name} supprimée ({deleted_count} fichier(s)). "
                    "Aucune vidéo suivante.",
                    "success",
                )
            else:
                self.set_status("Aucune vidéo suivante disponible.", "warning")
            return

        self.manual_next_requested = True
        self.stop_requested = False

        if deleted_count:
            self.set_status(
                f"{video.name} supprimée ({deleted_count} fichier(s)). "
                "Passage à la suivante…",
                "success",
            )
        else:
            self.set_status("Passage à la vidéo suivante…", "neutral")

        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
        else:
            self.manual_next_requested = False
            self.current_video = None
            self.current_script = None
            self.after(50, self.play_next_in_playlist)

    def launch_folder_playlist(self) -> None:
        """Lit la vidéo choisie puis toutes les suivantes du même dossier."""
        selected = Path(self.video_path.get())
        if not selected.is_file():
            messagebox.showerror("Vidéo introuvable", "Choisis d’abord une vidéo valide.")
            return

        videos = sorted(
            [
                path for path in selected.parent.iterdir()
                if path.is_file() and path.suffix.casefold() in VIDEO_EXTENSIONS
            ],
            key=natural_key,
        )
        try:
            start_index = videos.index(selected)
        except ValueError:
            messagebox.showerror("Erreur", "La vidéo sélectionnée n’est plus dans le dossier.")
            return

        playlist = [video for video in videos[start_index:] if find_script(video)]
        if not playlist:
            messagebox.showwarning(
                "Aucune vidéo lisible",
                "Aucune vidéo à partir de la sélection ne possède un funscript correspondant.",
            )
            return

        self.stop()
        self.playlist = playlist
        self.playlist_active = True
        self.delete_after_natural_end = self.delete_after_end_var.get()
        self.stop_requested = False
        self.play_next_in_playlist()

    def play_next_in_playlist(self) -> None:
        while self.playlist:
            video = self.playlist.pop(0)
            script = find_script(video)
            if video.is_file() and script is not None and script.is_file():
                self.video_path.set(str(video))
                self.script_path.set(f"✓  {script}")
                self.script_label.configure(foreground=COLORS["success"])
                remaining = len(self.playlist) + 1
                self.set_status(
                    f"Lecture automatique : {video.name} — {remaining} restante(s)",
                    "success",
                )
                self.launch(video, script)
                return

        self.playlist_active = False
        self.delete_after_natural_end = False
        self.current_video = None
        self.current_script = None
        self.set_status("Toutes les vidéos du dossier ont été traitées.", "success")
        messagebox.showinfo("Terminé", "La lecture du dossier est terminée.")

    def delete_completed_files(self, video: Path, script: Path | None) -> list[str]:
        """Supprime uniquement les fichiers correspondant exactement à la vidéo terminée."""
        deleted: list[str] = []
        errors: list[str] = []

        targets = [video, *script_candidates_for_deletion(video, script)]
        seen: set[Path] = set()
        for target in targets:
            try:
                resolved = target.resolve()
            except OSError:
                resolved = target.absolute()
            if resolved in seen:
                continue
            seen.add(resolved)

            if not target.is_file():
                continue
            try:
                target.unlink()
                deleted.append(str(target))
            except OSError as exc:
                errors.append(f"{target}: {exc}")

        if errors:
            messagebox.showwarning(
                "Suppression partielle",
                "Certains fichiers n’ont pas pu être supprimés :\n\n" + "\n".join(errors),
            )
        return deleted

    def check_process(self) -> None:
        if self.process is None:
            return

        code = self.process.poll()
        if code is None:
            self.after(100, self.check_process)
            return

        finished_video = self.current_video
        finished_script = self.current_script
        self.process = None

        if self.manual_next_requested:
            self.manual_next_requested = False
            self.current_video = None
            self.current_script = None

            if self.playlist_active and self.playlist:
                self.after(50, self.play_next_in_playlist)
            else:
                self.playlist_active = False
                self.set_status("Aucune vidéo suivante disponible.", "warning")
            return

        # Le moteur retourne 20 uniquement lorsque MPV a atteint la vraie fin.
        if code == 20:
            deleted_count = 0

            if (
                self.playlist_active
                and self.delete_after_end_var.get()
                and not self.stop_requested
                and finished_video is not None
            ):
                deleted = self.delete_completed_files(finished_video, finished_script)
                deleted_count = len(deleted)

            if (
                self.playlist_active
                and self.play_next_var.get()
                and not self.stop_requested
            ):
                if deleted_count:
                    self.set_status(
                        f"Fin naturelle : {finished_video.name if finished_video else 'vidéo'} "
                        f"supprimée ({deleted_count} fichier(s)). Passage à la suivante…",
                        "success",
                    )
                else:
                    self.set_status(
                        "Fin naturelle. Passage à la vidéo suivante…",
                        "success",
                    )
                self.after(50, self.play_next_in_playlist)
            else:
                self.playlist_active = False
                self.playlist.clear()
                if deleted_count:
                    self.set_status(
                        f"Lecture terminée naturellement. "
                        f"{deleted_count} fichier(s) supprimé(s).",
                        "success",
                    )
                else:
                    self.set_status("Lecture terminée naturellement.", "neutral")
        elif code == 0:
            self.set_status(
                "Lecture fermée avant la fin : aucun fichier supprimé.",
                "warning",
            )
            if self.playlist_active:
                self.playlist_active = False
                self.playlist.clear()
        else:
            self.set_status(
                f"Le lecteur s'est arrêté avec le code {code}. Aucun fichier supprimé.",
                "danger",
            )
            if self.playlist_active:
                self.playlist_active = False
                self.playlist.clear()

        self.current_video = None
        self.current_script = None

    def stop(self) -> None:
        self.stop_requested = True
        self.manual_next_requested = False
        self.playlist_active = False
        self.delete_after_natural_end = False
        self.playlist.clear()
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            self.set_status("Arrêt demandé… aucun fichier ne sera supprimé.", "warning")
        self.process = None

    def load_config(self) -> None:
        try:
            data = json.loads(CONFIG.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        self.language = data.get("language", "fr") if data.get("language", "fr") in ("fr", "en") else "fr"
        self.language_display.set("English" if self.language == "en" else "Français")
        saved_video_dir = data.get("last_video_dir")
        if isinstance(saved_video_dir, str) and saved_video_dir:
            candidate = Path(saved_video_dir).expanduser()
            if candidate.is_dir():
                self.last_video_dir = candidate
        self.max_power.set(float(data.get("max_power", 0.80)))
        self.zero_hold.set(int(data.get("zero_hold", 150)))
        self.smoothing.set(float(data.get("smoothing", 0.20)))
        self.min_power.set(float(data.get("min_power", 0.08)))
        self.amplification.set(float(data.get("amplification", 0.0)))
        self.fullscreen.set(bool(data.get("fullscreen", True)))
        self.pump_enabled.set(bool(data.get("pump_enabled", False)))
        self.pump_seconds.set(float(data.get("pump_seconds", 1.5)))
        self.pump_interval.set(float(data.get("pump_interval", 1.0)))
        self.pump_level.set(max(1, min(7, int(data.get("pump_level", 7)))))
        saved_patterns = data.get("pump_patterns", ["01 Escalier montant"])
        if isinstance(saved_patterns, list):
            valid_patterns = [p for p in saved_patterns if p in PUMP_PATTERNS]
            self.selected_pump_patterns = valid_patterns or ["01 Escalier montant"]
        self.delete_after_end_var.set(
            bool(data.get("delete_after_end", False))
        )
        self.play_next_var.set(
            bool(data.get("play_next", True))
        )

    def save_config(self) -> None:
        CONFIG.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "language": self.language,
            "last_video_dir": str(self.last_video_dir),
            "max_power": self.max_power.get(),
            "zero_hold": int(self.zero_hold.get()),
            "smoothing": self.smoothing.get(),
            "min_power": self.min_power.get(),
            "amplification": self.amplification.get(),
            "fullscreen": self.fullscreen.get(),
            "pump_enabled": self.pump_enabled.get(),
            "pump_seconds": self.pump_seconds.get(),
            "pump_interval": self.pump_interval.get(),
            "pump_level": max(1, min(7, int(self.pump_level.get()))),
            "pump_patterns": self.get_selected_pump_patterns() or ["01 Escalier montant"],
            "delete_after_end": self.delete_after_end_var.get(),
            "play_next": self.play_next_var.get(),
        }
        CONFIG.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def on_close(self) -> None:
        self.save_config()
        self.stop()
        try:
            self.progress_file.unlink(missing_ok=True)
        except OSError:
            pass
        self.destroy()


def main() -> int:
    app = RotaryPlayerGUI()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
