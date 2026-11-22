

import os, re, json, functools, html, time, inspect, hmac, hashlib, secrets, urllib.parse, urllib.request
from pathlib import Path
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta, timezone
import numpy as np, pandas as pd, streamlit as st
import plotly.express as px, plotly.graph_objects as go
import plotly.io as pio

st.set_page_config(page_title="ArthaAgent", page_icon="💰", layout="wide", initial_sidebar_state="collapsed")


def _w(f):
    """Newer Streamlit wants width='stretch'; older wants use_container_width=True."""
    try:
        return {"width": "stretch"} if "width" in inspect.signature(f).parameters else {"use_container_width": True}
    except Exception:
        return {"use_container_width": True}


WB, WP, WD, WDF = _w(st.button), _w(st.plotly_chart), _w(st.data_editor), _w(st.dataframe)
PAL = ["#FFB703", "#2EC4B6", "#8E7DFF", "#F25F8C", "#4ADE80", "#5EC8F2", "#FFD166", "#9AA9B8"]
LANGS = {"English": "English", "Hinglish": "Hinglish (Hindi in Roman script)", "हिन्दी": "Hindi", "मराठी": "Marathi"}
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@500;700&family=Sora:wght@700;800&display=swap');
.stApp{background:radial-gradient(1000px 500px at 80% -10%,#1d3b6b66,transparent),#080F1F;color:#EEF3FA}
header[data-testid=stHeader]{background:#080F1Fcc;backdrop-filter:blur(8px)}
header[data-testid=stHeader] *{color:#EEF3FA}
.stApp,.stApp p,.stApp li,.stApp label,.stApp button,.stApp input,.stApp textarea{font-family:'DM Sans',system-ui,sans-serif}
.stApp p,.stApp li,.stMarkdown{color:#EEF3FA;font-weight:500;font-size:1.04rem}
.stApp h1,.stApp h2,.stApp h3,.stApp h4{font-family:'Sora',sans-serif;font-weight:800;color:#fff;letter-spacing:-.02em}
[data-testid=stWidgetLabel],[data-testid=stWidgetLabel] p,label{color:#F4F7FB!important;font-weight:700!important;font-size:.98rem!important}
[data-testid=stCaptionContainer],[data-testid=stCaptionContainer] p{color:#A9BDD2!important;font-weight:600;font-size:.98rem}
button[data-baseweb=tab]{padding:10px 16px}
button[data-baseweb=tab] p{font-weight:700;font-size:1.08rem;color:#B9C9DB}
button[data-baseweb=tab][aria-selected=true] p{color:#FFB703;font-weight:800}
[data-baseweb=tab-highlight]{background:#FFB703;height:3px}
[data-baseweb=tab-border]{background:#ffffff22}
[data-testid=stMetric]{background:#ffffff10;border:1px solid #ffffff22;border-radius:16px;padding:14px 18px}
[data-testid=stMetricLabel] p{color:#A9BDD2!important;font-weight:700;font-size:.95rem}
[data-testid=stMetricValue]{color:#fff;font-family:'Sora',sans-serif;font-weight:800}
input,textarea,[data-baseweb=input],[data-baseweb=textarea],[data-baseweb=select]>div{
background:#0F1C33!important;color:#fff!important;border-color:#ffffff30!important;font-weight:600}
input::placeholder,textarea::placeholder{color:#7F94AB!important}
[data-testid=stNumberInput] button{background:#16294a;color:#fff}
.stButton>button,.stDownloadButton>button,[data-testid=stFormSubmitButton]>button{font-weight:700;font-size:1rem;border-radius:12px;
border:1.5px solid #FFB703;background:#FFB70318;color:#FFB703;padding:.55rem 1rem}
.stButton>button:hover,.stDownloadButton>button:hover,[data-testid=stFormSubmitButton]>button:hover{background:#FFB703;color:#1a1100;border-color:#FFB703}
.stButton>button *,.stDownloadButton>button *,[data-testid=stFormSubmitButton]>button *{color:inherit!important}
.stButton>button[kind=primary],[data-testid=stFormSubmitButton]>button[kind=primary],[data-testid=stFormSubmitButton]>button[kind=primaryFormSubmit]{background:#FFB703;color:#1a1100;font-weight:800}
.stSlider [role=slider]{background:#FFB703!important}
.stSlider [data-testid=stTickBarMin],.stSlider [data-testid=stTickBarMax],.stSlider [data-testid=stSliderThumbValue]{color:#FFB703;font-weight:700}
[data-testid=stSidebar]{background:#0B1730;border-right:1px solid #ffffff1a}
[data-testid=stFileUploaderDropzone]{background:#0F1C33;border:1.5px dashed #ffffff44}
[data-testid=stFileUploaderDropzone] *{color:#EEF3FA!important}
[data-testid=stFileUploaderDropzone] button{background:#FFB703!important;border:none!important}
[data-testid=stFileUploaderDropzone] button *{color:#1a1100!important;font-weight:800}
[data-testid=stChatMessage]{background:#ffffff0d;border:1px solid #ffffff1a;border-radius:16px}
[data-testid=stDataFrame],[data-testid=stDataEditor]{filter:invert(.92) hue-rotate(180deg);border-radius:12px}
[data-testid=stAlert]{background:#ffffff14!important;border:1px solid #ffffff30;border-radius:12px}
[data-testid=stAlert] *{color:#EEF3FA!important}
[data-testid=stExpander],[data-testid=stForm]{border:1px solid #ffffff22;border-radius:12px}
[data-testid=stExpander] summary p{font-weight:700}
.hero h1{font-family:'Sora',sans-serif;font-size:3.4rem;font-weight:800;line-height:1.05;margin:0 0 8px;
background:linear-gradient(90deg,#FFB703,#2EC4B6,#8E7DFF,#FFB703);background-size:300% 100%;
-webkit-background-clip:text;color:transparent;animation:g 8s linear infinite}
@keyframes g{to{background-position:300% 0}}
.hero p{color:#C3D2E2!important;font-weight:600;font-size:1.15rem;max-width:70ch}
.chip{display:inline-block;background:#FFB70322;color:#FFB703;border:1px solid #FFB70366;border-radius:99px;
padding:3px 13px;margin:2px 4px 2px 0;font-size:.9rem;font-weight:700}
.box{border-left:5px solid #2EC4B6;background:#ffffff10;padding:12px 16px;border-radius:0 12px 12px 0;margin:8px 0;
font-weight:600;color:#fff}
.bad{border-color:#FF5C5C}.warn{border-color:#FFB703}
::selection{background:#FFB70366;color:#fff}
::-webkit-scrollbar{width:10px}::-webkit-scrollbar-thumb{background:#2a4066;border-radius:9px}
.sec{margin:6px 0 16px}
.sec h2{font-family:'Sora',sans-serif;font-size:2.1rem;font-weight:800;margin:0;color:#fff}
.sec h2:after{content:"";display:block;width:70px;height:5px;border-radius:9px;margin-top:9px;
background:linear-gradient(90deg,#FFB703,#2EC4B6)}
.sec p{color:#B6C7DA!important;font-weight:600;font-size:1.08rem;margin:10px 0 0}
.pills{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0 6px}
.pill{background:#ffffff12;border:1px solid #ffffff2a;border-radius:99px;padding:6px 14px;font-weight:700;
font-size:.92rem;color:#EEF3FA}
[data-testid=stMetricValue]{text-shadow:0 0 18px #FFB70344}
[data-testid=stMetric]:hover{border-color:#FFB70388;box-shadow:0 0 24px #FFB70326}
.stApp h3{font-size:1.35rem}
@media (prefers-reduced-motion:reduce){.hero h1{animation:none}}
[data-testid=stSidebar],[data-testid=stSidebarCollapsedControl],[data-testid=collapsedControl],[data-testid=stSidebarNav]{display:none!important}

[data-testid=stAlert],[data-testid=stAlertContainer]{background:linear-gradient(145deg,#1a2c4d,#101e38)!important;
border:1px solid #ffffff33!important;border-radius:14px!important}
[data-testid=stAlert] *,[data-testid=stAlertContainer] *{color:#F4F7FB!important;font-weight:600}
[data-testid^=stAlertContent]{background:transparent!important}
.info{border-color:#5EC8F2}
[data-testid=stMetric],.box,[data-testid=stChatMessage],[data-testid=stExpander],[data-testid=stForm]{
background-image:linear-gradient(145deg,#ffffff1f,#ffffff08);box-shadow:0 1px 0 #ffffff30 inset,0 8px 16px #00000055}
.stButton>button,.stDownloadButton>button,[data-testid=stFormSubmitButton]>button{box-shadow:0 4px 0 #8a6200,0 8px 12px #00000055}
.stButton>button:active,.stDownloadButton>button:active,[data-testid=stFormSubmitButton]>button:active{transform:translateY(4px);box-shadow:0 0 0 #8a6200}
.pill,.chip{box-shadow:0 3px 0 #00000055}
.coin3d{display:none}
.hero h1{animation:none!important}
</style>""", unsafe_allow_html=True)
_t = pio.templates["plotly_dark"]
_t.layout.paper_bgcolor = "rgba(0,0,0,0)"
_t.layout.plot_bgcolor = "rgba(0,0,0,0)"
_t.layout.font = dict(family="DM Sans, sans-serif", color="#EEF3FA", size=14)
pio.templates.default = "plotly_dark"

_COIN_LAYERS = "".join(f'<i style="transform:translateZ({z}px)"></i>' for z in range(-8, 9, 2))
def _cube(s, x, y, t, c1, c2, d):
    faces = "".join("<i>₹</i>" for _ in range(6))
    return (f'<div class="fl" style="--x:{x}px;--y:{y}px;--d:{d}s"><div class="cube" '
            f'style="--s:{s}px;--t:{t}s;--c1:{c1};--c2:{c2}">{faces}</div></div>')


CUBES = ('<div class="cubes">' + _cube(46, -78, 4, 11, "#2EC4B6bb", "#1B2A5Ebb", 5) + _cube(30, -138, 88, 8, "#FFB703bb", "#8a5a00bb", 6)
         + _cube(36, -44, 116, 13, "#8E7DFFbb", "#2a1f66bb", 7) + '</div>')
COIN = ('<div class="coin3d"><div class="disc">' + _COIN_LAYERS +
        '<span class="f">₹</span><span class="b">₹</span></div><div class="coin-shadow"></div>' + CUBES + '</div>')

CSS_3D = """
.stApp::after{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
background:radial-gradient(420px 320px at 12% 18%,#8E7DFF2e,transparent 70%),
radial-gradient(520px 380px at 88% 30%,#2EC4B62b,transparent 70%),
radial-gradient(480px 300px at 50% 105%,#FFB7032e,transparent 70%)}
.stApp::before{content:"";position:fixed;left:-60%;right:-60%;bottom:-6vh;height:62vh;pointer-events:none;z-index:0;
background-image:linear-gradient(#2EC4B640 1.5px,transparent 1.5px),linear-gradient(90deg,#2EC4B640 1.5px,transparent 1.5px);
background-size:64px 64px;transform:perspective(520px) rotateX(64deg);transform-origin:50% 100%;
-webkit-mask-image:linear-gradient(to top,#000 5%,transparent 80%);mask-image:linear-gradient(to top,#000 5%,transparent 80%);
animation:gridmove 7s linear infinite}
@keyframes gridmove{to{background-position:0 64px}}
[data-testid=stMain],[data-testid=stAppViewContainer]>section{position:relative;z-index:1}

.hero{position:relative;padding:6px 0 10px}
.hero h1{filter:drop-shadow(0 1px 0 #b57f00) drop-shadow(0 2px 0 #9a6b00) drop-shadow(0 3px 0 #7d5600)
drop-shadow(0 4px 0 #5f4100) drop-shadow(0 14px 16px #000c)}
.coin3d{display:block!important;position:absolute;right:3%;top:-4px;width:150px;height:150px;perspective:760px;pointer-events:none}
.coin3d .disc{position:relative;width:100%;height:100%;transform-style:preserve-3d;transform:rotateX(-14deg) rotateY(25deg);
animation:coinspin 8s linear infinite}
.coin3d .disc i{position:absolute;inset:0;border-radius:50%;background:linear-gradient(135deg,#e0a000,#a96f00)}
.coin3d .disc .f,.coin3d .disc .b{position:absolute;inset:0;border-radius:50%;display:grid;place-items:center;
font:800 84px 'Sora',sans-serif;color:#7a4e00;text-shadow:0 2px 0 #ffe9a8,0 -1px 0 #5b3a00;
background:radial-gradient(circle at 32% 28%,#fff1b8,#FFD166 38%,#FFB703 70%,#d48c00);
box-shadow:inset 0 0 0 7px #f3b21a,inset 0 0 0 9px #ffe08a,inset 0 0 22px #8a5a00;backface-visibility:hidden}
.coin3d .disc .f{transform:translateZ(9px)}
.coin3d .disc .b{transform:rotateY(180deg) translateZ(9px)}
.coin3d .coin-shadow{position:absolute;left:14%;right:14%;bottom:-22px;height:22px;border-radius:50%;
background:radial-gradient(#000a,transparent 70%);filter:blur(3px)}
@keyframes coinspin{from{transform:rotateX(-14deg) rotateY(0)}to{transform:rotateX(-14deg) rotateY(360deg)}}
@media (max-width:900px){.coin3d{display:none!important}}

[data-testid=stMetric],.box,[data-testid=stChatMessage],[data-testid=stExpander],[data-testid=stForm],
[data-testid=stPlotlyChart],[data-testid=stDataFrame]{
transform-style:preserve-3d;will-change:transform;
transition:transform .22s cubic-bezier(.2,.8,.2,1),box-shadow .22s ease,border-color .22s ease}
[data-testid=stMetric]{position:relative;border-radius:18px;border:1px solid #ffffff2e;border-top-color:#ffffff55;
background-image:linear-gradient(150deg,#ffffff26,#ffffff08 55%,#00000022);
box-shadow:0 1px 0 #ffffff40 inset,0 5px 0 #0b1a33,0 6px 0 #ffffff12,0 22px 28px -8px #000c,0 0 0 1px #00000040;
transform:perspective(900px) rotateX(4deg)}
[data-testid=stMetric]:hover{transform:perspective(900px) rotateX(0) translateY(-7px) scale(1.02);
border-color:#FFB703aa;box-shadow:0 1px 0 #ffffff55 inset,0 8px 0 #0b1a33,0 30px 36px -8px #000d,0 0 30px #FFB70340}
[data-testid=stMetricValue]{transform:translateZ(30px);text-shadow:0 2px 0 #00000088,0 0 20px #FFB70355}
.box{border-radius:0 14px 14px 0;box-shadow:0 1px 0 #ffffff30 inset,0 4px 0 #0b1a33,0 14px 22px -6px #000b,-4px 0 18px -4px #2EC4B655}
.box.bad{box-shadow:0 1px 0 #ffffff30 inset,0 4px 0 #0b1a33,0 14px 22px -6px #000b,-4px 0 18px -4px #FF5C5C66}
.box.warn{box-shadow:0 1px 0 #ffffff30 inset,0 4px 0 #0b1a33,0 14px 22px -6px #000b,-4px 0 18px -4px #FFB70366}
.box:hover{transform:translateY(-3px) translateX(3px)}
[data-testid=stChatMessage],[data-testid=stExpander],[data-testid=stForm]{
box-shadow:0 1px 0 #ffffff33 inset,0 6px 0 #0b1a33,0 20px 30px -10px #000c}
[data-testid=stPlotlyChart]{background:linear-gradient(150deg,#ffffff18,#ffffff05 60%,#00000025);border:1px solid #ffffff26;
border-top-color:#ffffff4d;border-radius:20px;padding:10px 8px 4px;
box-shadow:0 1px 0 #ffffff33 inset,0 6px 0 #0b1a33,0 26px 36px -12px #000d}
[data-testid=stPlotlyChart]:hover{transform:translateY(-4px);border-color:#2EC4B688;
box-shadow:0 1px 0 #ffffff44 inset,0 8px 0 #0b1a33,0 34px 44px -12px #000e,0 0 34px #2EC4B62e}

[data-baseweb=tab-list]{gap:6px;padding:8px 6px 0}
button[data-baseweb=tab]{border-radius:14px 14px 0 0;border:1px solid #ffffff1f;border-bottom:none;
background:linear-gradient(180deg,#ffffff22,#ffffff08);box-shadow:0 1px 0 #ffffff38 inset,0 -6px 10px -4px #0008;
transition:transform .18s ease,background .18s ease}
button[data-baseweb=tab]:hover{transform:translateY(-3px);background:linear-gradient(180deg,#ffffff30,#ffffff10)}
button[data-baseweb=tab][aria-selected=true]{transform:translateY(-5px);
background:linear-gradient(180deg,#FFB70340,#FFB70310);border-color:#FFB70388;
box-shadow:0 1px 0 #ffe29a88 inset,0 -10px 22px -6px #FFB70355}
[data-baseweb=tab-highlight]{box-shadow:0 0 14px #FFB703}

.stButton>button,.stDownloadButton>button,[data-testid=stFormSubmitButton]>button{
border-radius:14px;transition:transform .12s ease,box-shadow .12s ease,background .12s ease;
background:linear-gradient(180deg,#FFB70330,#FFB70310);
box-shadow:0 1px 0 #ffffff44 inset,0 5px 0 #8a6200,0 12px 16px -2px #000a}
.stButton>button:hover,.stDownloadButton>button:hover,[data-testid=stFormSubmitButton]>button:hover{
transform:translateY(-3px);background:linear-gradient(180deg,#FFD166,#FFB703);color:#1a1100;
box-shadow:0 1px 0 #fff8 inset,0 8px 0 #8a6200,0 18px 24px -4px #000b,0 0 22px #FFB70355}
.stButton>button:active,.stDownloadButton>button:active,[data-testid=stFormSubmitButton]>button:active{
transform:translateY(5px);box-shadow:0 1px 0 #fff6 inset,0 0 0 #8a6200,0 4px 8px #000a}
.stButton>button[kind=primary],[data-testid=stFormSubmitButton]>button[kind=primary],
[data-testid=stFormSubmitButton]>button[kind=primaryFormSubmit]{
background:linear-gradient(180deg,#FFE08A,#FFB703 55%,#e59e00);color:#1a1100;
box-shadow:0 1px 0 #fffb inset,0 6px 0 #8a6200,0 14px 20px -2px #000b,0 0 18px #FFB70344}
.stButton>button[kind=primary]:hover,[data-testid=stFormSubmitButton]>button[kind=primary]:hover,
[data-testid=stFormSubmitButton]>button[kind=primaryFormSubmit]:hover{
transform:translateY(-3px);box-shadow:0 1px 0 #fffb inset,0 9px 0 #8a6200,0 20px 28px -4px #000c,0 0 30px #FFB70380}
.stButton>button[kind=primary]:active,[data-testid=stFormSubmitButton]>button[kind=primary]:active,
[data-testid=stFormSubmitButton]>button[kind=primaryFormSubmit]:active{transform:translateY(6px);box-shadow:0 0 0 #8a6200,0 3px 6px #000a}

[data-baseweb=input],[data-baseweb=textarea],[data-baseweb=select]>div{border-radius:12px!important;
box-shadow:inset 0 4px 10px #000b,0 1px 0 #ffffff26!important}
[data-baseweb=input] input,[data-baseweb=textarea] textarea{box-shadow:none!important}
[data-baseweb=input]:focus-within,[data-baseweb=textarea]:focus-within{border-color:#FFB703!important;
box-shadow:inset 0 4px 10px #000b,0 0 0 3px #FFB70344!important}

.pill,.chip{background-image:linear-gradient(180deg,#ffffff26,#ffffff08);box-shadow:0 1px 0 #ffffff40 inset,0 4px 0 #0b1a33,0 8px 10px -3px #000a;
transition:transform .15s ease}
.pill:hover,.chip:hover{transform:translateY(-3px) rotateX(10deg)}
.sec h2:after{box-shadow:0 3px 0 #8a6200,0 6px 14px #FFB70366}

[data-testid=stForm]{border-radius:20px;padding:6px 10px}

[data-testid=stElementContainer]:has(iframe[height="0"]),[data-testid=element-container]:has(iframe[height="0"]){
position:absolute;height:0;margin:0;overflow:hidden}

@media (prefers-reduced-motion:reduce){
.stApp::before,.coin3d .disc{animation:none}
[data-testid=stMetric],.box,[data-testid=stPlotlyChart],button[data-baseweb=tab]{transition:none}}
"""

CSS_V7 = """
.cubes{position:absolute;left:0;top:0;width:0;height:0;perspective:700px;pointer-events:none}
.cubes .fl{position:absolute;left:var(--x);top:var(--y);animation:bob var(--d) ease-in-out infinite alternate}
.cubes .cube{position:relative;width:var(--s);height:var(--s);transform-style:preserve-3d;animation:cubespin var(--t) linear infinite}
.cubes .cube i{position:absolute;inset:0;display:grid;place-items:center;font:800 16px 'Sora',sans-serif;color:#ffffffdd;
border:1.5px solid #ffffff88;background:linear-gradient(135deg,var(--c1),var(--c2));box-shadow:inset 0 0 14px #ffffff44}
.cubes .cube i:nth-child(1){transform:translateZ(calc(var(--s)/2))}
.cubes .cube i:nth-child(2){transform:rotateY(90deg) translateZ(calc(var(--s)/2))}
.cubes .cube i:nth-child(3){transform:rotateY(180deg) translateZ(calc(var(--s)/2))}
.cubes .cube i:nth-child(4){transform:rotateY(-90deg) translateZ(calc(var(--s)/2))}
.cubes .cube i:nth-child(5){transform:rotateX(90deg) translateZ(calc(var(--s)/2))}
.cubes .cube i:nth-child(6){transform:rotateX(-90deg) translateZ(calc(var(--s)/2))}
@keyframes cubespin{from{transform:rotateX(20deg) rotateY(0)}to{transform:rotateX(380deg) rotateY(360deg)}}
@keyframes bob{to{transform:translateY(-14px)}}
@media (max-width:1250px){.cubes{display:none}}

[data-baseweb=tab-panel]{transform-origin:50% 0;animation:panelin .5s cubic-bezier(.2,.8,.2,1) both}
@keyframes panelin{from{opacity:0;transform:perspective(1200px) rotateX(-8deg) translateY(22px)}to{opacity:1;transform:none}}

[data-testid=stMetric]{background-image:radial-gradient(240px circle at var(--mx,50%) var(--my,-60%),#ffffff33,transparent 65%),
linear-gradient(150deg,#ffffff26,#ffffff08 55%,#00000022)}
.box,[data-testid=stChatMessage]{background-image:radial-gradient(300px circle at var(--mx,30%) var(--my,-80%),#ffffff2a,transparent 65%),
linear-gradient(145deg,#ffffff1f,#ffffff08)}

.sec h2{text-shadow:0 1px 0 #b9c8da,0 2px 0 #8ea3bc,0 3px 0 #667b95,0 4px 0 #44566e,0 12px 16px #000c}
.stApp h3{text-shadow:0 2px 0 #00000099,0 0 16px #2EC4B633}

.stSlider [role=slider]{background:radial-gradient(circle at 32% 28%,#fff1b8,#FFB703 55%,#b57f00)!important;
box-shadow:0 3px 0 #7d5600,0 9px 12px #000b,0 0 14px #FFB70366!important;border:none!important}
div[role=progressbar]{box-shadow:inset 0 3px 7px #000c,0 1px 0 #ffffff2a;border-radius:99px}
div[role=progressbar]>div>div{background:linear-gradient(180deg,#FFE08A,#FFB703 55%,#c98400)!important;
box-shadow:0 0 16px #FFB70399,inset 0 1px 0 #fff9}
[data-testid=stFileUploaderDropzone]{border-radius:18px;box-shadow:inset 0 4px 12px #000b,0 1px 0 #ffffff26}
::-webkit-scrollbar-thumb{background:linear-gradient(90deg,#3a5486,#1f3157);box-shadow:inset 0 1px 0 #ffffff44}

[data-testid=stMetricDelta]{background:#0F1C33!important;border:1px solid #ffffff33!important;border-radius:99px!important}
[data-testid=stMetricDelta],[data-testid=stMetricDelta] *{color:#FFFFFF!important;font-weight:800!important}
[data-testid=stMetricDelta]:has([data-testid=stMetricDeltaIcon-Up]),[data-testid=stMetricDelta]:has([data-testid=stMetricDeltaIcon-Up]) *{color:#4ADE80!important}
[data-testid=stMetricDelta]:has([data-testid=stMetricDeltaIcon-Down]),[data-testid=stMetricDelta]:has([data-testid=stMetricDeltaIcon-Down]) *{color:#FF7A7A!important}
#artha-bg{mix-blend-mode:screen}
@media (prefers-reduced-motion:reduce){.cubes .fl,.cubes .cube,[data-baseweb=tab-panel]{animation:none}}
"""
CSS_3D += CSS_V7

TILT_JS = """<script>
(function(){
  var W, d; try{W=window.parent; d=W.document}catch(e){return}
  if(d.__artha3d)return; d.__artha3d=true;
  var calm=W.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var hover=W.matchMedia('(hover: hover)').matches;

  if(hover&&!calm){
    var SEL='[data-testid=stMetric],.box,[data-testid=stChatMessage]', cur=null;
    var reset=function(){if(cur){cur.style.transform='';cur=null}};
    d.addEventListener('mousemove',function(e){
      var el=e.target&&e.target.closest?e.target.closest(SEL):null;
      if(el!==cur)reset();
      if(!el)return;
      cur=el;
      var r=el.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;
      el.style.setProperty('--mx',(e.clientX-r.left)+'px');el.style.setProperty('--my',(e.clientY-r.top)+'px');
      el.style.transform='perspective(900px) rotateX('+(-y*9).toFixed(2)+'deg) rotateY('+(x*11).toFixed(2)+'deg) translateY(-6px) scale(1.02)';
    },{passive:true});
    d.documentElement.addEventListener('mouseleave',reset);
  }

  if(calm)return;
  var cv=d.getElementById('artha-bg');
  if(!cv){cv=d.createElement('canvas');cv.id='artha-bg';
    cv.style.cssText='position:fixed;inset:0;width:100%;height:100%;z-index:0;pointer-events:none;opacity:.55';
    d.body.appendChild(cv);}
  var ctx=cv.getContext('2d'),w=0,h=0,dpr=Math.min(W.devicePixelRatio||1,1.5);
  function size(){w=W.innerWidth;h=W.innerHeight;cv.width=w*dpr;cv.height=h*dpr;ctx.setTransform(dpr,0,0,dpr,0,0)}
  size();W.addEventListener('resize',size);
  var N=62,P=[],i;
  for(i=0;i<N;i++)P.push({x:Math.random()*2-1,y:Math.random()*2-1,z:Math.random()*2-1,g:i%7===0,c:i%3});
  var ry=0,tx=0,ty=0,sx=0,sy=0,COL=['255,183,3','46,196,182','142,125,255'];
  d.addEventListener('mousemove',function(e){tx=(e.clientX/w-.5)*.9;ty=(e.clientY/h-.5)*.6},{passive:true});
  function frame(){
    if(!d.hidden){
      ry+=.0016;sx+=(tx-sx)*.04;sy+=(ty-sy)*.04;
      var a=ry+sx,ca=Math.cos(a),sa=Math.sin(a),b=sy,cb=Math.cos(b),sb=Math.sin(b),S=Math.min(w,h)*.85,Q=[],k,j;
      ctx.clearRect(0,0,w,h);
      for(k=0;k<N;k++){
        var p=P[k],x=p.x*ca+p.z*sa,z=-p.x*sa+p.z*ca,y=p.y*cb-z*sb;z=p.y*sb+z*cb;
        var f=3/(3+z);Q.push({X:w/2+x*S*f*1.15,Y:h/2+y*S*f*.75,f:f,x:x,y:y,z:z,g:p.g,c:p.c});
      }
      ctx.lineWidth=1;
      for(k=0;k<N;k++)for(j=k+1;j<N;j++){
        var A=Q[k],B=Q[j],dx=A.x-B.x,dy=A.y-B.y,dz=A.z-B.z,dd=Math.sqrt(dx*dx+dy*dy+dz*dz);
        if(dd<.62){ctx.strokeStyle='rgba(46,196,182,'+((1-dd/.62)*.4*Math.min(A.f,B.f)).toFixed(3)+')';
          ctx.beginPath();ctx.moveTo(A.X,A.Y);ctx.lineTo(B.X,B.Y);ctx.stroke();}
      }
      for(k=0;k<N;k++){
        var q=Q[k];
        if(q.g){ctx.font='800 '+(15*q.f*1.4).toFixed(1)+'px Sora,sans-serif';ctx.fillStyle='rgba(255,183,3,'+(.35+.5*q.f/1.5).toFixed(2)+')';
          ctx.fillText('\u20B9',q.X,q.Y);}
        else{ctx.fillStyle='rgba('+COL[q.c]+','+(.35+.4*q.f/1.5).toFixed(2)+')';
          ctx.beginPath();ctx.arc(q.X,q.Y,1.2+2.6*q.f,0,6.2832);ctx.fill();}
      }
    }
    W.requestAnimationFrame(frame);
  }
  frame();
})();
</script>"""


def light3d(fig):
    """Add lighting to 3D surfaces and outlines to bars and pies."""
    lit = dict(lighting=dict(ambient=.52, diffuse=.92, specular=.75, roughness=.32, fresnel=.45),
               lightposition=dict(x=2500, y=2500, z=5000))
    fig.update_traces(selector=dict(type="surface"), **lit)
    fig.update_traces(selector=dict(type="mesh3d"), **lit)
    fig.update_traces(selector=dict(type="pie"), marker_line_color="#080F1F", marker_line_width=3, pull=.04)
    fig.update_traces(selector=dict(type="bar"), marker_line_color="rgba(255,255,255,0.4)", marker_line_width=1.5, opacity=.95)
    if any(getattr(t, "type", "") == "scatterpolar" for t in fig.data):
        fig.update_layout(polar=dict(bgcolor="rgba(255,255,255,0.05)"))
    return fig


def apply_3d():
    """Inject the 3D styles and the mouse-tilt script."""
    st.markdown(f"<style>{CSS_3D}</style>", unsafe_allow_html=True)
    try:
        import streamlit.components.v1 as components
        components.html(TILT_JS, height=0)
    except Exception:
        pass


apply_3d()


def pchart(target, fig, **kw):
    """Draw a Plotly chart with our dark template (theme=None keeps our colours)."""
    fig.update_xaxes(rangemode="nonnegative")
    fig.update_yaxes(rangemode="nonnegative")
    light3d(fig)
    target.plotly_chart(fig, theme=None, **WP)


def rs(x):
    x = int(round(x)); s = str(abs(x))
    if len(s) > 3:
        h, t, p = s[:-3], s[-3:], []
        while len(h) > 2: p.insert(0, h[-2:]); h = h[:-2]
        s = ",".join(([h] if h else []) + p + [t])
    return ("-" if x < 0 else "") + "₹" + s


def box(t, kind=""): st.markdown(f'<div class="box {kind}">{t}</div>', unsafe_allow_html=True)


def section(title, sub=""):
    st.markdown(f'<div class="sec"><h2>{title}</h2><p>{sub}</p></div>', unsafe_allow_html=True)


def iv(x, lo, hi=None):
    """Clamp to int so Streamlit number_input never sees mismatched types/ranges."""
    x = int(round(float(x or 0)))
    return max(lo, x) if hi is None else max(lo, min(hi, x))


def K(n): return f"{n}_{st.session_state.get('pv', 0)}"


# ---------------- violence word detector ----------------
VIOLENCE_RE = re.compile(
    r"\b(kill(?:ing|ed|er|s)?|murder\w*|shoot(?:ing|er|s)?|stab(?:bing|bed|s)?|bomb(?:ing|s)?|blow\s?up|behead\w*|"
    r"lynch\w*|rap(?:e|es|ed|ing)|kidnap\w*|abduct\w*|assault\w*|acid\s+attack|strangle\w*|slaughter\w*|massacre\w*|"
    r"terroris[mt]s?|torture\w*|gun\s?down|hang\s+you|burn\s+(?:you|him|her|them|alive)|"
    r"beat\s+(?:you|him|her|them)\s+up|break\s+your\s+(?:legs|bones)|hurt\s+you|"
    r"(?:i|we)(?:'ll|\s+will)\s+(?:destroy|finish|get)\s+you|threaten\w*|death\s+threat)\b", re.I)


def violence_scan(text):
    """Return the unique violent / threatening words found in `text` (empty list if clean)."""
    seen, out = set(), []
    for m in VIOLENCE_RE.finditer(text or ""):
        w = re.sub(r"\s+", " ", m.group(0).lower())
        if w not in seen: seen.add(w); out.append(w)
    return out


# ---------------- accounts & profile ----------------
DB = Path(os.getenv("ARTHA_DB", str(Path(__file__).with_name("artha_users.json"))))
GENDERS = ["Prefer not to say", "Female", "Male", "Other"]
MARITAL = ["Single", "Married", "Divorced", "Widowed"]
EMPLOY = ["Salaried", "Self-employed", "Business owner", "Freelancer", "Student", "Homemaker", "Retired"]
RISKS = ["Conservative", "Moderate", "Aggressive"]
GOALS = ["Build wealth", "Retire early", "Buy a home", "Child's education", "Marriage", "Emergency fund",
         "Pay off debt", "Save tax"]
REGIMES = ["Not sure", "New regime", "Old regime"]
STATES = ("Andhra Pradesh,Arunachal Pradesh,Assam,Bihar,Chhattisgarh,Goa,Gujarat,Haryana,Himachal Pradesh,Jharkhand,"
          "Karnataka,Kerala,Madhya Pradesh,Maharashtra,Manipur,Meghalaya,Mizoram,Nagaland,Odisha,Punjab,Rajasthan,Sikkim,"
          "Tamil Nadu,Telangana,Tripura,Uttar Pradesh,Uttarakhand,West Bengal,Delhi,Jammu & Kashmir,Ladakh,Chandigarh,"
          "Puducherry,Andaman & Nicobar,Lakshadweep,Dadra & Nagar Haveli and Daman & Diu").split(",")
PD = dict(name="", email="", phone="", age=28, gender=GENDERS[0], marital="Single", dependents=0, city="",
          state="Maharashtra", employment="Salaried", occupation="", salary=60000, other_income=0, rent=0, emi=0,
          expenses=20000, savings=150000, investments=0, sip=0, risk="Moderate", goal="Build wealth",
          goal_amount=10000000, goal_years=15, retire_age=55, regime="Not sure", health_ins=False, term_ins=False,
          lang="English")


def _load():
    try: return json.loads(DB.read_text("utf-8"))
    except Exception: return {}


def _save(d):
    tmp = DB.with_suffix(".tmp"); tmp.write_text(json.dumps(d, indent=1), "utf-8"); os.replace(tmp, DB)


def hash_pw(pw, salt=None):
    salt = salt or secrets.token_hex(16)
    return salt, hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 200_000).hex()


def verify(pw, salt, h): return hmac.compare_digest(hash_pw(pw, salt)[1], h)


EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}")


def valid_email(e): return EMAIL_RE.fullmatch((e or "").strip()) is not None


def pw_problem(p):
    if len(p) < 8: return "Password needs at least 8 characters."
    if not re.search(r"[A-Za-z]", p) or not re.search(r"\d", p): return "Password needs letters and at least one number."
    return None


def check_profile(o):
    if not o["name"].strip(): return "Please enter your full name."
    if not valid_email(o["email"]): return "Please enter a valid email address (like name@example.com)."
    if o["phone"] and not re.fullmatch(r"\+?\d[\d \-]{8,13}", o["phone"].strip()): return "Mobile number looks invalid."
    bad = violence_scan(" ".join(str(o.get(k, "")) for k in ("name", "city", "occupation")))
    if bad: return "Violent or threatening words aren't allowed in profile text: " + ", ".join(bad)
    return None


def find_user(db, ident):
    """Look an account up by email or by username key."""
    i = (ident or "").strip().lower()
    if not i: return None
    if i in db: return i
    return next((k for k, r in db.items() if r.get("profile", {}).get("email", "").strip().lower() == i), None)


def register(pw, o):
    """Create an account whose ID is the user's email. Returns (error, key)."""
    email = o["email"].strip().lower()
    if (e := check_profile(o)): return e, None
    if (e := pw_problem(pw)): return e, None
    db = _load()
    if find_user(db, email): return "That email is already registered. Please log in instead.", None
    salt, h = hash_pw(pw)
    db[email] = dict(salt=salt, hash=h, profile={**o, "email": email}, created=time.time(), fails=0, lock=0)
    _save(db)
    return None, email


def login(ident, pw):
    """Email + password login. Returns (error, key)."""
    db = _load(); u = find_user(db, ident); r = db.get(u) if u else None
    bad = "Invalid email or password."
    if not r:
        hash_pw(pw); return bad, None
    if r.get("lock", 0) > time.time():
        return f"Too many attempts. Try again in {int((r['lock'] - time.time()) // 60) + 1} min.", None
    if verify(pw, r["salt"], r["hash"]):
        r["fails"], r["lock"] = 0, 0; _save(db); return None, u
    r["fails"] = r.get("fails", 0) + 1
    if r["fails"] >= 5: r["fails"], r["lock"] = 0, time.time() + 300
    _save(db)
    return bad, None


def prof(): return st.session_state.get("profile") or dict(PD)
def pf(k): return prof().get(k, PD[k])
def income(): return pf("salary") + pf("other_income")
def outgo(): return pf("rent") + pf("emi") + pf("expenses")


def profile_txns(p):
    inc = p["salary"] + p["other_income"]
    if inc <= 0: return parse_sms(DEMO)
    t = [dict(merchant="Income", amount=float(inc), kind="credit", category="Income", type="in")]

    def d(m, a, c, ty):
        if a > 0: t.append(dict(merchant=m, amount=float(a), kind="debit", category=c, type=ty))
    d("Rent", p["rent"], "Rent & EMI", "need"); d("EMI", p["emi"], "Rent & EMI", "need")
    for m, ty, s in [("Groceries", "need", .25), ("Bills", "need", .10), ("Transport", "need", .10),
                     ("Health", "need", .05), ("Subscriptions", "want", .05), ("Food delivery", "want", .15),
                     ("Shopping", "want", .15), ("Entertainment", "want", .15)]:
        d(m, round(p["expenses"] * s), m, ty)
    return t


def start_session(u):
    db = _load()
    p = {**PD, **db[u]["profile"]}
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.session_state.update(user=u, profile=p, pv=0, txns=profile_txns(p), txn_src="profile", sms_text="",
                            last_txt="", msgs=[], lang="English",
                            flash=f"Welcome, {p['name'].split()[0] if p['name'] else u}!")


def logout():
    for k in list(st.session_state.keys()): del st.session_state[k]


def save_profile(o):
    u = st.session_state.user; db = _load()
    db[u]["profile"] = o; _save(db)
    st.session_state.profile = {**PD, **o}
    st.session_state.pv = st.session_state.get("pv", 0) + 1
    if st.session_state.get("txn_src") == "profile": st.session_state.txns = profile_txns(st.session_state.profile)
    st.session_state.flash = "Profile saved ✅"


def ix(opts, v): return opts.index(v) if v in opts else 0


def profile_fields(d, pre):
    """Shared registration / update form body. Returns dict of values."""
    o = {}
    st.markdown("**👤 About you**")
    c = st.columns(3)
    o["name"] = c[0].text_input("Full name *", d["name"], key=pre + "name")
    o["email"] = c[1].text_input("Email *", d["email"], key=pre + "email")
    o["phone"] = c[2].text_input("Mobile (optional)", d["phone"], key=pre + "phone", max_chars=15)
    c = st.columns(4)
    o["age"] = c[0].number_input("Age *", 18, 90, iv(d["age"], 18, 90), key=pre + "age")
    o["gender"] = c[1].selectbox("Gender", GENDERS, ix(GENDERS, d["gender"]), key=pre + "gender")
    o["marital"] = c[2].selectbox("Marital status", MARITAL, ix(MARITAL, d["marital"]), key=pre + "marital")
    o["dependents"] = c[3].number_input("Dependents", 0, 10, iv(d["dependents"], 0, 10), key=pre + "dep")
    c = st.columns(3)
    o["city"] = c[0].text_input("City", d["city"], key=pre + "city")
    o["state"] = c[1].selectbox("State", STATES, ix(STATES, d["state"]), key=pre + "state")
    o["employment"] = c[2].selectbox("Employment", EMPLOY, ix(EMPLOY, d["employment"]), key=pre + "emp")
    o["occupation"] = st.text_input("Occupation / job title", d["occupation"], key=pre + "occ")
    st.markdown("**💵 Monthly money**")
    c = st.columns(3)
    o["salary"] = c[0].number_input("Gross monthly salary / income ₹", 0, value=iv(d["salary"], 0), step=5000, key=pre + "sal")
    o["other_income"] = c[1].number_input("Other monthly income ₹", 0, value=iv(d["other_income"], 0), step=1000, key=pre + "oi")
    o["expenses"] = c[2].number_input("Living expenses ₹ (excl. rent & EMI)", 0, value=iv(d["expenses"], 0), step=1000, key=pre + "exp")
    c = st.columns(3)
    o["rent"] = c[0].number_input("Rent ₹", 0, value=iv(d["rent"], 0), step=1000, key=pre + "rent")
    o["emi"] = c[1].number_input("Total loan EMIs ₹", 0, value=iv(d["emi"], 0), step=1000, key=pre + "emi")
    o["sip"] = c[2].number_input("Monthly SIP / investing ₹", 0, value=iv(d["sip"], 0), step=1000, key=pre + "sip")
    c = st.columns(2)
    o["savings"] = c[0].number_input("Savings / bank balance ₹", 0, value=iv(d["savings"], 0), step=10000, key=pre + "sav")
    o["investments"] = c[1].number_input("Existing investments ₹ (MF, stocks, PPF, NPS, FD)", 0, value=iv(d["investments"], 0), step=10000, key=pre + "inv")
    st.markdown("**🎯 Goals & preferences**")
    c = st.columns(3)
    o["risk"] = c[0].selectbox("Risk appetite", RISKS, ix(RISKS, d["risk"]), key=pre + "risk")
    o["goal"] = c[1].selectbox("Main goal", GOALS, ix(GOALS, d["goal"]), key=pre + "goal")
    o["regime"] = c[2].selectbox("Tax regime you use", REGIMES, ix(REGIMES, d["regime"]), key=pre + "reg")
    c = st.columns(3)
    o["goal_amount"] = c[0].number_input("Goal amount ₹", 0, value=iv(d["goal_amount"], 0), step=500000, key=pre + "ga")
    o["goal_years"] = c[1].number_input("Years to goal", 1, 40, iv(d["goal_years"], 1, 40), key=pre + "gy")
    o["retire_age"] = c[2].number_input("Target retirement age", 30, 75, iv(d["retire_age"], 30, 75), key=pre + "ra")
    o["lang"] = "English"
    c = st.columns(2)
    o["health_ins"] = c[0].checkbox("I have health insurance", d["health_ins"], key=pre + "hi")
    o["term_ins"] = c[1].checkbox("I have term life insurance", d["term_ins"], key=pre + "ti")
    return o


def _go(view): st.session_state["auth_view"] = view


def auth_page():
    """Login (email + password) and Register windows."""
    st.markdown("<style>[data-testid=stSidebar],[data-testid=stSidebarCollapsedControl]{display:none}</style>", unsafe_allow_html=True)
    st.markdown('<div class="hero">' + COIN + '<h1>ArthaAgent</h1><p>Sign in with your email and password so your salary, goals and '
                'spending shape every plan, simulation and tip.</p></div>', unsafe_allow_html=True)
    view = st.session_state.setdefault("auth_view", "login")
    if view == "login":
        section("Welcome back", "Log in with the email and password you registered with.")
        with st.form("login_form"):
            em = st.text_input("Email", key="l_email", placeholder="you@example.com")
            pw = st.text_input("Password", type="password", key="l_pw")
            sub = st.form_submit_button("Login", type="primary")
        if sub:
            if not em.strip() or not pw: st.error("Enter your email and password.")
            else:
                err, u = login(em, pw)
                if err: st.error(err)
                else: start_session(u); st.rerun()
        st.caption("Passwords are salted and hashed (PBKDF2). 5 wrong attempts lock the account for 5 minutes.")
        st.button("📝 New here? Create an account", key="go_reg", on_click=_go, args=("register",))
    else:
        section("Create your account", "Your email is your login ID. Fill the details once; every tab will use them.")
        with st.form("reg_form"):
            o = profile_fields(dict(PD), "r_")
            st.markdown("**🔐 Set your password**")
            c = st.columns(2)
            rp = c[0].text_input("Password *", type="password", key="r_pw", help="8+ characters with letters and a number")
            rp2 = c[1].text_input("Confirm password *", type="password", key="r_pw2")
            agree = st.checkbox("I understand ArthaAgent is educational and not SEBI-registered advice.", key="r_agree")
            sub = st.form_submit_button("Create account", type="primary")
        if sub:
            if rp != rp2: st.error("Passwords don't match.")
            elif not agree: st.error("Please tick the acknowledgement box.")
            else:
                o["email"] = o["email"].strip().lower(); o["name"] = o["name"].strip()
                err, u = register(rp, o)
                if err: st.error(err)
                else: start_session(u); st.rerun()
        st.button("← Back to login", key="go_login", on_click=_go, args=("login",))


# ---------------- Gemini layer ----------------
def key():
    k = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not k:
        try: k = st.secrets.get("GEMINI_API_KEY")
        except Exception: k = None
    return k


@st.cache_resource
def client(k):
    from google import genai
    from google.genai import types
    try:  # the "-latest" model aliases are served on v1beta, not v1
        return genai.Client(api_key=k, http_options=types.HttpOptions(api_version="v1beta"))
    except Exception:
        return genai.Client(api_key=k)


DEFAULT_MODEL = "gemini-2.5-flash-lite"
MODEL_PREFS = ["gemini-flash-lite-latest", "gemini-2.5-flash-lite", "gemini-3.1-flash-lite", "gemini-2.0-flash-lite",
               "gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-latest"]


@st.cache_resource(show_spinner=False)
def listed_models(k):
    """Names of the models this API key can call with generateContent (empty list if the lookup fails)."""
    try:
        out = []
        for m in client(k).models.list():
            acts = getattr(m, "supported_actions", None)
            if not acts or "generateContent" in acts: out.append(m.name.split("/")[-1])
        return out
    except Exception:
        return []


def model_candidates():
    """Models to try, best first: forced one, last one that worked, stable listed ones, other listed Flash models,
    '-latest' aliases, then the preference list. A model that 404s is simply skipped at call time."""
    out = []
    if os.getenv("GEMINI_MODEL"): out.append(os.getenv("GEMINI_MODEL"))
    if st.session_state.get("good_model"): out.append(st.session_state["good_model"])
    k = key()
    listed = listed_models(k) if k else []
    stable = [p for p in MODEL_PREFS if p in listed and "latest" not in p]
    others = [m for m in listed if "flash" in m and m not in stable
              and not re.search(r"image|tts|live|embed|audio|vision|exp|preview|thinking|latest", m)]
    latest = [p for p in MODEL_PREFS if p in listed and "latest" in p]
    others.sort(key=lambda m: "lite" not in m)
    out += ["gemini-flash-lite-latest"] + stable + others + latest + [p for p in MODEL_PREFS if p not in listed] + [DEFAULT_MODEL]
    seen = set()
    return [m for m in out if m and not (m in seen or seen.add(m))]


def model(): return model_candidates()[0]


def _model_missing(e):
    s = str(e).lower()
    return "not_found" in s or "404" in s or "not found" in s or "not supported" in s


def profile_brief():
    if "user" not in st.session_state: return ""
    p = prof()
    return (f" The user is {p['name'].split()[0] if p['name'] else 'a user'}, age {p['age']}, {p['employment']}, "
            f"monthly income {rs(income())}, rent {rs(p['rent'])}, EMIs {rs(p['emi'])}, expenses {rs(p['expenses'])}, "
            f"SIP {rs(p['sip'])}, savings {rs(p['savings'])}, investments {rs(p['investments'])}, {p['dependents']} dependents, "
            f"risk {p['risk']}, goal {p['goal']} of {rs(p['goal_amount'])} in {p['goal_years']} years, "
            f"retire at {p['retire_age']}, health insurance {p['health_ins']}, term insurance {p['term_ins']}.")


def system():
    tone = ("Playfully roast their spending like a witty friend, then give one genuinely useful tip."
            if st.session_state.get("mode") == "Roast" else "Be warm, practical and specific.")
    return ("You are ArthaAgent, an AI money agent for Indian users (UPI, SIP, FD, PPF, NPS, old/new tax regime). "
            f"Reply in {LANGS.get(st.session_state.get('lang', 'English'))}. {tone} Use your tools for every number; "
            "never invent figures. Keep answers under 150 words. Educational only: not a SEBI-registered adviser."
            + profile_brief())


def fast_cfg(m, js=False, tools=None, think=True):
    """Speed-tuned config: thinking switched off on 2.5 Flash models, short capped answers, low temperature."""
    from google.genai import types
    kw = dict(system_instruction=system(), temperature=.4, max_output_tokens=2048 if js else 900)
    if js: kw["response_mime_type"] = "application/json"
    if think and re.match(r"gemini-2\.5-flash", m): kw["thinking_config"] = types.ThinkingConfig(thinking_budget=0)
    if tools:
        kw["tools"] = tools
        kw["automatic_function_calling"] = types.AutomaticFunctionCallingConfig(maximum_remote_calls=8)
    return types.GenerateContentConfig(**kw)


def gen(prompt, parts=None, js=False):
    """One-shot Gemini call (text + optional image parts). Tries each candidate model until one works."""
    if not key(): return None
    last = None
    for m_ in model_candidates():
        for think in (True, False):  # second pass drops the thinking setting if a model rejects it
            try:
                r = client(key()).models.generate_content(model=m_, contents=[prompt] + (parts or []),
                                                          config=fast_cfg(m_, js, think=think)).text
                st.session_state["good_model"] = m_
                return r
            except Exception as e:
                last = e
                if think and "thinking" in str(e).lower(): continue
                break
        if not _model_missing(last): break
    return f"⚠️ Gemini error: {last}"


NOKEY = "Gemini key missing. Add GEMINI_API_KEY to Streamlit secrets (.streamlit/secrets.toml), then restart the app."


def ai_show(prompt, parts=None, spin="Gemini is thinking…"):
    """Button handler helper: streams the answer; falls back to a normal call."""
    if not key(): st.warning(NOKEY); return
    if hasattr(st, "write_stream"):
        for m_ in model_candidates():
            try:
                it = iter(client(key()).models.generate_content_stream(model=m_, contents=[prompt] + (parts or []), config=fast_cfg(m_)))
                first = next(it)  # a wrong model name fails here, before anything is shown
            except StopIteration:
                break
            except Exception as e:
                if _model_missing(e) or "thinking" in str(e).lower(): continue
                st.error(f"⚠️ Gemini error: {e}"); return

            def chunks(first=first, it=it):
                yield first.text or ""
                for c in it: yield c.text or ""
            try:
                st.write_stream(chunks())
                st.session_state["good_model"] = m_
                return
            except Exception as e:
                st.error(f"⚠️ Gemini error: {e}"); return
    with st.spinner(spin): out = gen(prompt, parts)
    (st.error if (out or "").startswith("⚠️") else st.markdown)(out or "Gemini returned nothing. Try again.")


def img_part(f):
    from google.genai import types
    return types.Part.from_bytes(data=f.getvalue(), mime_type=f.type or "image/png")


def jload(t):
    try: return json.loads(re.sub(r"^```(?:json)?|```$", "", (t or "").strip(), flags=re.M).strip())
    except Exception: return None


# ---------------- finance engine ----------------
CATS = [("Rent & EMI", "need", r"rent|emi|loan|landlord"), ("Groceries", "need", r"bigbasket|blinkit|zepto|grocer|dmart"),
        ("Bills", "need", r"electric|bbps|recharge|jio|airtel|broadband|gas|bills"), ("Transport", "need",
        r"uber|ola|rapido|metro|fuel|petrol|irctc|transport"),
        ("Health", "need", r"pharma|apollo|hospital|clinic|health"), ("Subscriptions", "want", r"netflix|spotify|prime|hotstar|youtube|subscri"),
        ("Food delivery", "want", r"swiggy|zomato|restaurant|cafe|dominos|food"), ("Shopping", "want", r"amazon|flipkart|myntra|ajio|shopping"),
        ("Entertainment", "want", r"pvr|inox|bookmyshow|movie|entertain")]
DEMO = """Rs.60,000.00 credited to A/c XX1234 by ACME SALARY
Rs.18,000.00 debited to VPA landlord@oksbi rent
Rs.12,500.00 debited EMI HDFC LOAN
Rs.1,250.00 debited to VPA swiggy@ybl
Rs.1,840.00 debited to VPA zomato@icici
Rs.349.00 debited to VPA netflix@icici
Rs.349.00 debited to VPA netflix@icici
Rs.899.00 debited to VPA spotify@ybl
Rs.2,340.00 debited at BigBasket
Rs.620.00 debited to VPA uber@axis
Rs.3,200.00 debited at Amazon
Rs.1,150.00 debited to VPA electricity@bbps
Rs.2,100.00 debited at PVR Cinemas
Rs.4,500.00 debited to VPA zomato@icici"""


def cat_of(s):
    s = s.lower()
    return next(((c, t) for c, t, p in CATS if re.search(p, s)), ("Other", "want"))


def parse_sms(text):
    out = []
    for l in filter(str.strip, (text or "").splitlines()):
        m = re.search(r"(?:rs\.?|inr|₹)\s*([\d,]+(?:\.\d+)?)", l, re.I)
        if not m: continue
        a = float(m.group(1).replace(",", ""))
        mm = re.search(r"([\w.\-]+)@\w+", l) or re.search(r"(?:at|to|by)\s+([A-Za-z][\w &]+?)(?:\s+on|\.|$)", l, re.I)
        mer = mm.group(1) if mm else "Unknown"
        if re.search(r"credited|received", l, re.I): out.append(dict(merchant=mer, amount=a, kind="credit", category="Income", type="in"))
        elif re.search(r"debited|paid|sent|spent|withdrawn", l, re.I):
            c, t = cat_of(l); out.append(dict(merchant=mer, amount=a, kind="debit", category=c, type=t))
    return out


def clean_vision(d):
    """Turn Gemini's JSON list into our transaction dicts, tolerating messy values."""
    out = []
    for x in d:
        if not isinstance(x, dict): continue
        try: a = float(re.sub(r"[^\d.]", "", str(x.get("amount", 0))) or 0)
        except ValueError: continue
        if a <= 0: continue
        mer = str(x.get("merchant") or "Unknown")
        if str(x.get("type", "debit")).lower().startswith("c"):
            out.append(dict(merchant=mer, amount=a, kind="credit", category="Income", type="in"))
        else:
            c, t = cat_of(mer); out.append(dict(merchant=mer, amount=a, kind="debit", category=c, type=t))
    return out


def sim(start, monthly, years, mu, sigma, step=0, events=None, n=2000):
    m, ev, rng = int(years * 12), events or {}, np.random.default_rng(7)
    r = rng.normal(mu / 1200, sigma / 100 / np.sqrt(12), (n, m)); v = np.full(n, float(start)); P = np.empty((n, m + 1)); P[:, 0] = v
    for t in range(m):
        v = np.maximum(v * (1 + r[:, t]) + monthly * (1 + step / 100) ** (t // 12) + ev.get(t, 0), 0); P[:, t + 1] = v
    return P


def emi_of(P, rate, months):
    r = rate / 1200
    return P / months if r == 0 else P * r * (1 + r) ** months / ((1 + r) ** months - 1)


def slab(t, S):
    tax = prev = 0
    for lim, rt in S:
        if t > prev: tax += (min(t, lim) - prev) * rt
        prev = lim
    return tax


# ---- New tax regime slabs (verify against the Income Tax portal before use) ----
NEW_SLABS = [(4e5, 0), (8e5, .05), (12e5, .10), (16e5, .15), (2e6, .20), (24e5, .25), (1e12, .30)]
NEW_STD, REBATE_MAX, REBATE_LIMIT, CESS = 75000, 60000, 12e5, .04
SURCHARGE = [(2e7, .25), (1e7, .15), (5e6, .10)]  # >2cr, >1cr, >50L (new-regime cap is 25%)


def _lakh(x): return "∞" if x >= 1e11 else f"₹{x / 1e5:g}L"


def new_regime_breakdown(gross, salaried=True):
    """Slab-by-slab new-regime tax: std deduction, slabs, 87A rebate + marginal relief, surcharge, 4% cess."""
    std = NEW_STD if salaried else 0
    taxable = max(0.0, gross - std)
    rows, prev, base = [], 0, 0.0
    for lim, rt in NEW_SLABS:
        amt = max(0.0, min(taxable, lim) - prev); tx = amt * rt; base += tx
        rows.append(dict(Slab=f"{_lakh(prev)} to {_lakh(lim)}" if lim < 1e11 else f"Above {_lakh(prev)}",
                         Rate=f"{rt * 100:.0f}%", **{"Income in slab": round(amt), "Tax": round(tx)}))
        prev = lim
    after = base
    relief = ""
    if taxable <= REBATE_LIMIT:
        rebate = min(base, REBATE_MAX); after = base - rebate
    else:  # marginal relief: tax can't exceed the income above ₹12 lakh
        after = min(base, taxable - REBATE_LIMIT); rebate = base - after
        if rebate > 0: relief = "Marginal relief applied: your tax is capped at the income above ₹12 lakh."
    sur_rt = next((r for lim, r in SURCHARGE if taxable > lim), 0)
    sur = after * sur_rt
    cess = (after + sur) * CESS
    total = after + sur + cess
    return dict(std=std, taxable=taxable, rows=rows, slab_tax=base, rebate=rebate, surcharge=sur, cess=cess,
                total=round(total), eff_pct=round(total / gross * 100, 2) if gross else 0, note=relief,
                tax_free_gross=REBATE_LIMIT + std)


def tax_calc(g, c80=0, d80=0, hra=0):
    n = new_regime_breakdown(g)["total"]
    ot = max(0, g - 50000 - min(c80, 15e4) - min(d80, 5e4) - hra)
    o = 0 if ot <= 5e5 else slab(ot, [(25e4, 0), (5e5, .05), (1e6, .2), (1e12, .3)])
    return dict(new_regime_tax=round(n), old_regime_tax=round(o * 1.04),
                better="new" if n <= o * 1.04 else "old", saving=round(abs(n - o * 1.04)))


RULES = [(r"otp|pin\b|cvv|password", 30, "Asks for OTP/PIN/password"), (r"collect|receive.*money", 25, "Collect-request trick"),
         (r"blocked|suspend|deactivat|expire|freeze", 18, "Account-block threat"),
         (r"kyc|pan.*update|aadhaar.*link", 18, "Fake KYC pretext"),
         (r"bit\.ly|tinyurl|cutt\.ly|\.xyz|\.top|\.click", 25, "Shortened or odd link"),
         (r"lottery|won\b|prize|cashback|gift|kbc", 20, "Too-good prize"),
         (r"anydesk|teamviewer|quicksupport", 35, "Remote-access app"),
         (r"urgent|immediately|today|act now|within \d+", 12, "Artificial urgency"),
         (r"part.?time|work from home|earn.*daily|task", 18, "Task/job scam"),
         (r"customs|parcel|courier|police|cbi|arrest", 25, "Impersonates authority/courier")]


def scam_rules(t):
    h = [(w, r) for p, w, r in RULES if re.search(p, t, re.I)]
    v = violence_scan(t)
    if v: h.append((25, "Violent / threatening language: " + ", ".join(v)))
    s = min(100, sum(w for w, _ in h))
    return s, [r for _, r in h]


# ---------------- agent tools (Gemini calls these itself) ----------------
def traced(f):
    @functools.wraps(f)
    def w(*a, **k):
        r = f(*a, **k); st.session_state.setdefault("trace", []).append((f.__name__, k or list(a), r)); return r
    return w


@traced
def spending_summary() -> dict:
    """Summarise the user's loaded transactions: income, spent, saved, savings rate, top categories, repeat subscriptions."""
    allt = st.session_state.get("txns", [])
    tx = [t for t in allt if t["kind"] == "debit"]; inc = sum(t["amount"] for t in allt if t["kind"] == "credit")
    spent = sum(t["amount"] for t in tx); cats = {}
    for t in tx: cats[t["category"]] = cats.get(t["category"], 0.0) + t["amount"]
    seen = pd.Series([f"{t['merchant']}@{t['amount']}" for t in tx], dtype=object).value_counts()
    return dict(income=inc, spent=spent, saved=inc - spent, savings_rate_pct=round((inc - spent) / inc * 100, 1) if inc else 0,
                needs=sum(t["amount"] for t in tx if t["type"] == "need"),
                top_categories={k: round(v) for k, v in sorted(cats.items(), key=lambda x: -x[1])[:5]},
                repeat_charges=[k for k, v in seen.items() if v > 1])


@traced
def my_profile() -> dict:
    """Get the signed-in user's profile: age, income, expenses, EMIs, SIP, savings, goals, risk appetite, insurance."""
    p = dict(prof())
    for k in ("name", "email", "phone"): p.pop(k, None)
    return p


@traced
def scam_score(message: str) -> dict:
    """Score a suspicious SMS/WhatsApp/UPI message 0-100 and list red flags."""
    s, f = scam_rules(message); return dict(score=s, flags=f, level="high" if s >= 60 else "medium" if s >= 30 else "low")


@traced
def tax_compare(gross: float, deductions_80c: float = 0, health_80d: float = 0, hra_exempt: float = 0) -> dict:
    """Compare Indian income tax under old vs new regime (FY 2026-27) for an annual gross salary."""
    return tax_calc(gross, deductions_80c, health_80d, hra_exempt)


@traced
def sip_projection(monthly: float, years: int, annual_return_pct: float = 12, stepup_pct: float = 0) -> dict:
    """Deterministic SIP projection with optional yearly step-up."""
    v = inv = 0; m = monthly
    for _ in range(int(years)):
        for _ in range(12): v = (v + m) * (1 + annual_return_pct / 1200); inv += m
        m *= 1 + stepup_pct / 100
    return dict(invested=round(inv), projected_value=round(v), gain=round(v - inv))


@traced
def goal_probability(goal: float, monthly: float, years: int, current_savings: float = 0,
                     annual_return_pct: float = 11, volatility_pct: float = 16) -> dict:
    """Monte Carlo (2,000 market paths): probability of reaching a goal corpus and the p10/median/p90 outcomes."""
    f = sim(current_savings, monthly, years, annual_return_pct, volatility_pct)[:, -1]
    return dict(probability_pct=float(round((f >= goal).mean() * 100, 1)), worst_10pct=int(np.percentile(f, 10)),
                median=int(np.median(f)), best_10pct=int(np.percentile(f, 90)))


@traced
def emi_calculator(loan: float, annual_rate_pct: float, years: int) -> dict:
    """EMI, total interest and total payable for a loan."""
    e = emi_of(loan, annual_rate_pct, int(years * 12))
    return dict(emi=round(e), total_interest=round(e * years * 12 - loan), total_payable=round(e * years * 12))


@traced
def can_i_afford(price: float, monthly_income: float, emi_months: int = 12, rate_pct: float = 14) -> dict:
    """Check whether buying something on EMI is affordable: EMI-to-income ratio, interest cost, and what the money could grow to if invested instead."""
    e = emi_of(price, rate_pct, emi_months)
    return dict(emi=round(e), emi_pct_of_income=round(e / monthly_income * 100, 1), interest_cost=round(e * emi_months - price),
                if_invested_12pct=round(price * (1 + .12 / 12) ** emi_months),
                verdict="comfortable" if e / monthly_income < .1 else "okay" if e / monthly_income < .2 else "risky")


def health_parts(S, balance=150000):
    inc = S["income"] or 1
    needs = S["needs"]
    wants = S["spent"] - needs

    def clip(v): return int(max(0, min(100, v)))
    return {
        "Savings": clip(S["savings_rate_pct"] / 20 * 100),
        "Needs load": clip(100 - max(0, needs / inc - .5) * 250),
        "Wants control": clip(100 - max(0, wants / inc - .3) * 300),
        "Subscriptions": clip(100 - 25 * len(S["repeat_charges"])),
        "Emergency fund": clip(balance / (6 * needs) * 100) if needs else 100,
    }


def anomalies(txns):
    d = [t for t in txns if t["kind"] == "debit"]
    out = []
    if len(d) >= 5:
        a = np.array([t["amount"] for t in d])
        lim = a.mean() + 2 * a.std()
        out += [f"Unusually large payment: {t['merchant']} {rs(t['amount'])}" for t in d if t["amount"] > lim and t["type"] == "want"]
    seen = {}
    for t in d:
        k = (t["merchant"], t["amount"])
        seen[k] = seen.get(k, 0) + 1
    out += [f"Repeated charge: {m} {rs(a)} x{n} (duplicate or subscription?)" for (m, a), n in seen.items() if n > 1]
    fd = [t for t in d if t["category"] == "Food delivery"]
    if len(fd) >= 3:
        out.append(f"{len(fd)} food-delivery orders cost {rs(sum(t['amount'] for t in fd))} this period")
    return out


def fire_calc(exp, bal, monthly, ret, inf, wr=4.0, max_years=50):
    r, v, rows = ret / 1200, float(bal), []
    need = exp * 12 / (wr / 100)
    for m in range(max_years * 12 + 1):
        need = exp * 12 * (1 + inf / 100) ** (m / 12) / (wr / 100)
        if m % 12 == 0 or v >= need:
            rows.append((m / 12, v, need))
        if v >= need:
            return dict(years=m / 12, corpus=need, rows=rows)
        v = v * (1 + r) + monthly
    return dict(years=None, corpus=need, rows=rows)


def build_report(S, parts, overall, alerts, narrative):
    p = prof()
    L = ["# ArthaAgent Money Report", f"_Prepared for {p['name'] or 'you'} on {pd.Timestamp.today():%d %b %Y}_", "",
         f"## Money health score: {overall}/100", "", "| Area | Score |", "|---|---|"]
    L += [f"| {k} | {v}/100 |" for k, v in parts.items()]
    L += ["", "## Snapshot", f"- Income: {rs(S['income'])}", f"- Spent: {rs(S['spent'])}",
          f"- Saved: {rs(S['saved'])} ({S['savings_rate_pct']}%)", "", "## Top categories"]
    L += [f"- {k}: {rs(v)}" for k, v in S["top_categories"].items()]
    L += ["", "## Alerts"] + ([f"- {a}" for a in alerts] or ["- None"])
    L += ["", "## AI summary", narrative, "", "_Educational only, not financial advice._"]
    return "\n".join(L)


@traced
def financial_health(balance: float = 150000) -> dict:
    """Score the user's money health 0-100 (savings, needs, wants, subscriptions, emergency fund) and list unusual transactions."""
    S = spending_summary.__wrapped__()
    p = health_parts(S, balance)
    return dict(overall=int(np.mean(list(p.values()))), parts=p, alerts=anomalies(st.session_state.get("txns", [])))


@traced
def fire_plan(monthly_expenses: float, current_savings: float, monthly_investment: float,
              annual_return_pct: float = 11, inflation_pct: float = 6) -> dict:
    """Years until financial independence (corpus = 25x yearly expenses, 4% rule), adjusted for inflation."""
    r = fire_calc(monthly_expenses, current_savings, monthly_investment, annual_return_pct, inflation_pct)
    return dict(years_to_fi=None if r["years"] is None else round(r["years"], 1), corpus_needed=round(r["corpus"]))


@traced
def prepay_vs_invest(loan_balance: float, loan_rate_pct: float, remaining_years: int,
                     extra_monthly: float, invest_return_pct: float = 12) -> dict:
    """Compare using extra monthly money to prepay a loan versus investing it in equity (after 12.5% LTCG)."""
    n = int(remaining_years * 12)
    e = emi_of(loan_balance, loan_rate_pct, n)
    bal, paid, m = float(loan_balance), 0.0, 0
    while bal > 1 and m < n:
        i = bal * loan_rate_pct / 1200
        bal -= min(e - i + extra_monthly, bal)
        paid += i
        m += 1
    r = invest_return_pct / 1200
    fv_ = extra_monthly * (((1 + r) ** n - 1) / r) * (1 + r) if r else extra_monthly * n
    gain = (fv_ - extra_monthly * n) * (1 - .125)
    saved = e * n - loan_balance - paid
    return dict(months_saved=n - m, interest_saved=round(saved), invest_gain_after_tax=round(gain),
                winner="prepay" if saved >= gain else "invest")


TOOLS = [my_profile, spending_summary, scam_score, tax_compare, sip_projection, goal_probability, emi_calculator,
         can_i_afford, financial_health, fire_plan, prepay_vs_invest]

# ================= NEWS + 3D SIP LAB MODULES =================
UA = {"User-Agent": "Mozilla/5.0 (ArthaAgent)"}
CS = [[0, "#1B2A5E"], [.35, "#2EC4B6"], [.7, "#FFB703"], [1, "#F25F8C"]]

FEEDS = {
    "ET Markets": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "ET Stocks": "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms",
    "ET Mutual Funds": "https://economictimes.indiatimes.com/mf/rssfeeds/359241701.cms",
    "Mint Markets": "https://www.livemint.com/rss/markets",
    "Moneycontrol": "https://www.moneycontrol.com/rss/marketreports.xml",
    "Business Standard": "https://www.business-standard.com/rss/markets-106.rss",
    "Google News Markets": "https://news.google.com/rss/search?q=sensex+OR+nifty+OR+RBI+when:1d&hl=en-IN&gl=IN&ceid=IN:en",
    "Google News Business": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-IN&gl=IN&ceid=IN:en",
}
TICKERS = {"Nifty 50": "^NSEI", "Sensex": "^BSESN", "Bank Nifty": "^NSEBANK", "Nifty IT": "^CNXIT",
           "USD/INR": "INR=X", "Gold (USD)": "GC=F", "Brent crude": "BZ=F"}
POS = r"rally|surge|gain|jump|record high|bull|rise|climb|soar|upbeat|rebound|strong|boost|outperform"
NEG = r"fall|slump|crash|drop|sell-?off|plunge|bear|tumble|decline|lose|weak|slide|worry|fear|rout|cut"


@st.cache_data(ttl=45, show_spinner=False)
def fetch_feed(url, limit=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=8) as r:
        root = ET.fromstring(r.read())
    out = []
    for it in root.iter("item"):
        g = lambda t: (it.findtext(t) or "").strip()
        try: ts = parsedate_to_datetime(g("pubDate")).timestamp()
        except Exception: ts = 0
        out.append(dict(title=html.unescape(g("title")), link=g("link"), ts=ts,
                        summary=re.sub(r"<[^>]+>", "", html.unescape(g("description")))[:200]))
    return out[:limit]


def load_news(sources):
    rows, errs = [], []
    for s in sources:
        try: rows += [dict(x, source=s) for x in fetch_feed(FEEDS[s])]
        except Exception: errs.append(s)
    seen, uniq = set(), []
    for r in sorted(rows, key=lambda r: r["ts"], reverse=True):
        k = r["title"].lower()[:60]
        if k and k not in seen:
            seen.add(k); uniq.append(r)
    return uniq, errs


def mood(title):
    p, n = len(re.findall(POS, title, re.I)), len(re.findall(NEG, title, re.I))
    return ("bull", "🟢 Bullish") if p > n else ("bear", "🔴 Bearish") if n > p else ("neu", "⚪ Neutral")


def ago(ts):
    if not ts: return ""
    s = max(0, int(time.time() - ts))
    return f"{s // 60}m ago" if s < 3600 else f"{s // 3600}h ago" if s < 86400 else f"{s // 86400}d ago"


IST = timezone(timedelta(hours=5, minutes=30))
# st.fragment lets one panel re-run on a timer without re-running the whole app (needs Streamlit 1.37+)
_FRAG = getattr(st, "fragment", None) or getattr(st, "experimental_fragment", None)


def ist_now(): return datetime.now(IST)


def market_open():
    """Rough NSE session check (Mon-Fri, 9:15-15:30 IST). Exchange holidays are not modelled."""
    n = ist_now()
    return n.weekday() < 5 and (9, 15) <= (n.hour, n.minute) <= (15, 30)


@st.cache_data(ttl=20, show_spinner=False)
def yahoo_chart(sym, rng="1d", itv="5m"):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}?range={rng}&interval={itv}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=8) as r:
        d = json.loads(r.read())["chart"]["result"][0]
    q = d["indicators"]["quote"][0]
    rows = [(t, o, h, l, c) for t, o, h, l, c in zip(d["timestamp"], q["open"], q["high"], q["low"], q["close"])
            if None not in (o, h, l, c)]
    df = pd.DataFrame(rows, columns=["t", "o", "h", "l", "c"])
    df["t"] = pd.to_datetime(df["t"], unit="s") + pd.Timedelta(hours=5, minutes=30)  # show IST on the axis
    return dict(df=df, meta=d.get("meta", {}))


def _one_quote(item):
    name, sym = item
    try:
        c = yahoo_chart(sym, "1d", "5m"); df, meta = c["df"], c["meta"]
        price = float(meta.get("regularMarketPrice") or df["c"].iloc[-1])
        prev = float(meta.get("chartPreviousClose") or meta.get("previousClose") or df["o"].iloc[0])
        return name, dict(price=price, chg=price - prev, pct=(price - prev) / prev * 100, df=df, asof=meta.get("regularMarketTime"))
    except Exception:
        return name, None


@st.cache_data(ttl=20, show_spinner=False)
def quotes_all():
    with ThreadPoolExecutor(max_workers=7) as ex:
        return dict(ex.map(_one_quote, TICKERS.items()))


def _live_wrap(fn, secs):
    """Wrap fn in a self-refreshing fragment when Streamlit supports it; otherwise run it once."""
    if _FRAG is None: return fn
    try: return _FRAG(run_every=secs)(fn) if secs else _FRAG(fn)
    except TypeError: return _FRAG(fn)


def news_tab():
    section("Market News & Pulse", "Index levels and headlines that refresh by themselves, with an AI brief.")
    st.markdown("""<style>
.livebar{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin:4px 0 12px;font-weight:700;color:#C3D2E2}
.live{display:inline-flex;align-items:center;gap:7px;padding:4px 12px;border-radius:99px;font-weight:800;font-size:.9rem;
background:linear-gradient(180deg,#ffffff26,#ffffff08);box-shadow:0 1px 0 #ffffff40 inset,0 4px 0 #0b1a33,0 8px 10px -3px #000a}
.live i{width:10px;height:10px;border-radius:50%;background:#FF5C5C;box-shadow:0 0 10px #FF5C5C}
.live.on i{animation:livepulse 1.4s ease-out infinite}
.live.off i{background:#9AA9B8;box-shadow:none}
@keyframes livepulse{0%{box-shadow:0 0 0 0 #FF5C5Caa}100%{box-shadow:0 0 0 12px #FF5C5C00}}
.newtag{background:#4ADE80;color:#062b12;border-radius:6px;padding:1px 7px;font-size:.75rem;font-weight:800;margin-right:6px}
@media (prefers-reduced-motion:reduce){.live.on i{animation:none}}
</style>""", unsafe_allow_html=True)
    top = st.columns([4, 1.2, 1.2, 1.4])
    srcs = top[0].multiselect("News sources", list(FEEDS), default=["ET Markets", "Mint Markets", "Google News Markets"], key="nw_src")
    live = top[1].toggle("🔴 Live updates", value=True, key="nw_live")
    secs = top[2].selectbox("Refresh every", [30, 60, 120, 300], 0, format_func=lambda s: f"{s} sec" if s < 60 else f"{s // 60} min", key="nw_every")
    top[3].markdown("<div style='height:1.9rem'></div>", unsafe_allow_html=True)
    if top[3].button("🔄 Refresh now", key="nw_ref", **WB):
        fetch_feed.clear(); quotes_all.clear(); yahoo_chart.clear(); st.rerun()
    if live and _FRAG is None:
        st.caption("Auto-refresh needs Streamlit 1.37 or newer. Use 'Refresh now' until you upgrade (pip install -U streamlit).")

    def ai_run(prompt, spin):
        if not key(): st.warning(NOKEY); return
        with st.spinner(spin): st.session_state.nw_ai = gen(prompt)

    def panel():
        Q = quotes_all()
        lq = {k: v for k, v in Q.items() if v}
        now = ist_now()
        asof = [v["asof"] for v in lq.values() if v.get("asof")]
        qtime = datetime.fromtimestamp(max(asof), IST).strftime("%H:%M:%S") if asof else "n/a"
        st.markdown(f'<div class="livebar"><span class="live {"on" if live else "off"}"><i></i>{"LIVE" if live else "PAUSED"}</span>'
                    f'<span>Page updated {now:%H:%M:%S} IST</span><span>·</span><span>Last quote {qtime} IST</span><span>·</span>'
                    f'<span>NSE {"open" if market_open() else "closed"} (approx.)</span>'
                    f'{"<span>·</span><span>next refresh in about " + str(secs) + "s</span>" if live and _FRAG else ""}</div>',
                    unsafe_allow_html=True)
        if lq:
            cols = st.columns(len(lq))
            for c, (k, v) in zip(cols, lq.items()):
                c.metric(k, f"{v['price']:,.2f}", f"{v['pct']:+.2f}%")
            cc = st.columns([3, 2])
            pick = cc[0].radio("Chart", list(lq), horizontal=True, key="nw_pick")
            rng = cc[1].radio("Range", ["Today (live)", "3 months"], horizontal=True, key="nw_rng")
            try:
                df = lq[pick]["df"] if rng.startswith("Today") else yahoo_chart(TICKERS[pick], "3mo", "1d")["df"]
                fig = go.Figure(go.Candlestick(x=df["t"], open=df["o"], high=df["h"], low=df["l"], close=df["c"],
                                               increasing_line_color="#4ADE80", decreasing_line_color="#FF5C5C"))
                if rng.startswith("Today"): fig.add_hline(y=lq[pick]["price"], line_dash="dot", line_color="#FFB703")
                fig.update_layout(title=f"{pick}: {'today, 5-minute candles (IST)' if rng.startswith('Today') else 'last 3 months'}",
                                  height=360, xaxis_rangeslider_visible=False, margin=dict(t=50, b=10))
                pchart(st, fig)
            except Exception:
                box("Couldn't load that chart right now. It will retry on the next refresh.", "warn")
        else:
            box("Couldn't reach the market-data service (needs internet). Headlines below may still load.", "warn")

        news, errs = load_news(srcs or ["ET Markets"])
        if errs: st.caption("Could not load: " + ", ".join(errs))
        # flag headlines that appeared since the page was opened
        first = "nw_seen" not in st.session_state
        seen = st.session_state.setdefault("nw_seen", {})
        t_now, added = time.time(), 0
        for n in news:
            k = n["title"].lower()[:60]
            if k and k not in seen:
                seen[k] = 0 if first else t_now
                added += 0 if first else 1
        if added: st.toast(f"🆕 {added} new headline{'s' if added > 1 else ''}")
        q = st.text_input("🔎 Filter headlines", placeholder="e.g. RBI, HDFC, gold, IPO", key="nw_q")
        if q: news = [n for n in news if q.lower() in (n["title"] + n["summary"]).lower()]
        if news:
            moods = [mood(n["title"])[0] for n in news]
            b, r = moods.count("bull"), moods.count("bear")
            score = int(50 + 50 * (b - r) / max(1, b + r)) if b + r else 50
            m = st.columns(3)
            m[0].metric("Headline mood", f"{score}/100", "bullish" if score > 55 else "bearish" if score < 45 else "mixed")
            m[1].metric("Bullish / Bearish", f"{b} / {r}")
            m[2].metric("Headlines", len(news))
            a1, a2 = st.columns(2)
            heads = "\n".join(f"- {n['title']}" for n in news[:14])
            if a1.button("🤖 AI market brief", type="primary", key="nw_brief", **WB):
                ai_run("Today's Indian market headlines:\n" + heads +
                       "\nWrite a 5-bullet market brief: what moved, why, and what a long-term SIP investor should do (usually: stay calm). "
                       "Use only these headlines.", "Gemini is reading the headlines…")
            if a2.button("📈 What does this mean for my SIP?", key="nw_sip", **WB):
                ai_run("Headlines:\n" + heads + "\nExplain in simple words how this affects a monthly equity SIP investor "
                       "and whether to pause, continue or step up. Do not predict prices.", "Gemini is thinking…")
            ai = st.session_state.get("nw_ai")  # kept in session so the next auto-refresh doesn't wipe it
            if ai: (st.error if ai.startswith("⚠️") else st.markdown)(ai)
            st.subheader("🗞️ Latest headlines")
            for n in news[:30]:
                kind, label = mood(n["title"])
                css = {"bull": "", "bear": "bad", "neu": "warn"}[kind]
                fresh = 0 < t_now - seen.get(n["title"].lower()[:60], 0) < 300
                box(f'{"<span class=newtag>NEW</span>" if fresh else ""}'
                    f'<a href="{html.escape(n["link"])}" target="_blank" style="color:#FFB703;text-decoration:none">'
                    f'{html.escape(n["title"])}</a><br><span style="font-size:.85rem;color:#A9BDD2;font-weight:600">'
                    f'{html.escape(n["source"])} · {ago(n["ts"])} · {label}</span>', css)
        else:
            box("No headlines loaded. Check your internet connection or pick other sources.", "warn")
        st.caption("Headlines come from public RSS feeds and quotes from Yahoo Finance; they can be delayed by a few minutes. "
                   "Educational only, not investment advice.")

    _live_wrap(panel, secs if live else None)()


# ---------------- 3D SIP LAB ----------------
AX = dict(showbackground=False, gridcolor="rgba(255,255,255,0.15)", zerolinecolor="rgba(255,255,255,0.25)", color="#EEF3FA",
          rangemode="nonnegative")


def sip_path(monthly, years, ret, step=0.0, lump=0.0):
    """Deterministic SIP with yearly step-up. Returns list of (year, invested, value)."""
    r, v, inv, m = ret / 1200, float(lump), float(lump), float(monthly)
    out = [(0, inv, v)]
    for y in range(int(years)):
        for _ in range(12):
            v = (v + m) * (1 + r); inv += m
        m *= 1 + step / 100
        out.append((y + 1, inv, v))
    return out


def fv(monthly, years, ret, step=0.0, lump=0.0):
    return sip_path(monthly, years, ret, step, lump)[-1][2]


def boxes(items):
    """Many cuboids -> one Mesh3d. items = (x0, x1, y0, y1, z0, z1)."""
    X, Y, Z, I, J, K_ = [], [], [], [], [], []
    tri = [(0, 1, 2), (0, 2, 3), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4),
           (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    for x0, x1, y0, y1, z0, z1 in items:
        base = len(X)
        for x, y, z in [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]:
            X.append(x); Y.append(y); Z.append(z)
        for a, b, c in tri:
            I.append(base + a); J.append(base + b); K_.append(base + c)
    return dict(x=X, y=Y, z=Z, i=I, j=J, k=K_)


def style3d(fig, title, xt, yt, zt, h=580, spin=True):
    fig.update_layout(
        title=title, height=h, margin=dict(l=0, r=0, t=50, b=0), paper_bgcolor="rgba(0,0,0,0)",
        scene=dict(xaxis=dict(title=xt, **AX), yaxis=dict(title=yt, **AX), zaxis=dict(title=zt, **AX),
                   camera=dict(eye=dict(x=1.7, y=1.7, z=0.9)), aspectmode="manual", aspectratio=dict(x=1.3, y=1.3, z=.8)))
    if spin:
        ang = np.linspace(0, 2 * np.pi, 72)
        fig.frames = [go.Frame(layout=dict(scene=dict(camera=dict(eye=dict(x=2.3 * np.cos(a), y=2.3 * np.sin(a), z=.9)))))
                      for a in ang]
        fig.update_layout(updatemenus=[dict(
            type="buttons", showactive=False, x=0.02, y=0.02, xanchor="left", yanchor="bottom",
            bgcolor="#16294a", font=dict(color="#FFB703"),
            buttons=[dict(label="▶ Auto-rotate", method="animate",
                          args=[None, dict(frame=dict(duration=60, redraw=True), transition=dict(duration=0),
                                           fromcurrent=True, mode="immediate")]),
                     dict(label="⏸ Pause", method="animate",
                          args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate",
                                             transition=dict(duration=0))])])])
    return fig


def surf(x, y, z, cbar="₹ lakh", **kw):
    return go.Surface(x=x, y=y, z=z, colorscale=CS, colorbar=dict(title=cbar, len=.6), opacity=.95,
                      contours=dict(z=dict(show=True, usecolormap=True, project_z=True, highlightcolor="#fff")), **kw)


@st.cache_data(show_spinner="Simulating 3D terrain…")
def terrain(lump, mu, sg, step, goal, sips, yrs_list):
    out = np.zeros((len(yrs_list), len(sips)))
    for i, y in enumerate(yrs_list):
        for j, s in enumerate(sips):
            out[i, j] = (sim(lump, s, y, mu, sg, step, None, 300)[:, -1] >= goal).mean() * 100
    return out


def towers3d(labels, values, title, ztitle, colors=None, fmt=None, h=470):
    """Reusable 3D bar chart."""
    fmt = fmt or (lambda v: f"{v:,.0f}")
    colors = colors or PAL
    vals = [max(float(v), 0.0) for v in values]
    vmax = max(max(vals), 1.0)
    n = len(vals)
    tr = [go.Mesh3d(**boxes([(i + .12, i + .88, .08, .92, 0, max(v, vmax * 1e-4))]), color=colors[i % len(colors)],
                    flatshading=True, name=str(lab), showlegend=False,
                    hovertemplate=f"{lab}<br>{fmt(v)}<extra></extra>")
          for i, (lab, v) in enumerate(zip(labels, vals))]
    tr.append(go.Scatter3d(x=[i + .5 for i in range(n)], y=[.5] * n, z=[v + vmax * .07 for v in vals], mode="text",
                           text=[fmt(v) for v in vals], textfont=dict(color="#FFFFFF", size=12), showlegend=False,
                           hoverinfo="skip"))
    f = go.Figure(tr)
    style3d(f, title, "", "", ztitle, h=h)
    f.update_layout(scene=dict(
        xaxis=dict(tickvals=[i + .5 for i in range(n)], ticktext=[str(x)[:14] for x in labels], title="", tickfont=dict(size=10)),
        yaxis=dict(showticklabels=False, title="", range=[0, 1]),
        aspectratio=dict(x=min(2.4, .55 + .3 * n), y=.7, z=.75)))
    return f


def sip3d_tab():
    section("SIP 3D Lab", "Rotate, zoom and spin. Eight interactive 3D views of what your SIP can become.")
    a = st.columns(4)
    lump = a[0].number_input("Lump sum now ₹", 0, value=iv(pf("investments") or 100000, 0), step=25000, key=K("s3_l"))
    mo = a[1].number_input("Monthly SIP ₹", 500, value=iv(pf("sip") or 15000, 500), step=1000, key=K("s3_m"))
    yrs = a[2].number_input("Years", 1, 40, iv(pf("goal_years"), 1, 40), key=K("s3_y"))
    ret = a[3].number_input("Expected return %", 1.0, 25.0, 12.0, key="s3_r")
    b = st.columns(3)
    step = b[0].slider("Yearly step-up %", 0, 20, 8, key="s3_s")
    sg = b[1].slider("Volatility %", 5, 30, 16, key="s3_v")
    goal = b[2].number_input("Goal ₹", 100000, value=iv(pf("goal_amount") or 10000000, 100000), step=500000, key=K("s3_g"))

    path = sip_path(mo, yrs, ret, step, lump)
    inv, val = path[-1][1], path[-1][2]
    m = st.columns(4)
    m[0].metric("You invest", rs(inv)); m[1].metric("Projected value", rs(val))
    m[2].metric("Wealth gained", rs(val - inv)); m[3].metric("Money multiple", f"{val / max(inv, 1):.2f}x")

    P = sim(lump, mo, yrs, ret, sg, step, None, 1500)
    prob = (P[:, -1] >= goal).mean() * 100
    yv = np.arange(P.shape[1]) / 12
    T = st.tabs(["⛰️ Wealth Mountain", "⏳ Return × Time", "🪜 Step-up Landscape", "🏙️ Growth Towers",
                 "🎲 Probability Sheet", "🌲 Path Forest", "🌊 Future Density", "🧭 Goal Terrain"])
    L = 1e5

    with T[0]:
        xs = np.unique(np.linspace(1000, max(mo * 3, 20000), 16).round(-2))
        ys = np.arange(1, 41, 2)
        Z = np.array([[fv(x, y, ret, step, lump) for x in xs] for y in ys]) / L
        f = go.Figure([surf(xs, ys, Z, hovertemplate="SIP ₹%{x:,.0f}<br>%{y} yrs<br>₹%{z:,.1f} L<extra></extra>"),
                       go.Scatter3d(x=[mo], y=[yrs], z=[val / L], mode="markers+text", text=["You"], textfont=dict(color="#fff"),
                                    marker=dict(size=8, color="#fff", symbol="diamond"), showlegend=False)])
        pchart(st, style3d(f, "Wealth mountain: SIP × years → corpus", "Monthly SIP ₹", "Years", "Corpus (₹ lakh)"))
        st.caption("The white diamond is your plan. Time (the Y axis) climbs faster than SIP size, so start early.")

    with T[1]:
        xs = np.arange(4, 20.1, 1.0)
        ys = np.arange(1, 41, 2)
        Z = np.array([[fv(mo, y, x, step, lump) for x in xs] for y in ys]) / L
        f = go.Figure([surf(xs, ys, Z, hovertemplate="%{x}% return<br>%{y} yrs<br>₹%{z:,.1f} L<extra></extra>"),
                       go.Scatter3d(x=[ret], y=[yrs], z=[val / L], mode="markers", marker=dict(size=8, color="#fff", symbol="diamond"),
                                    showlegend=False)])
        pchart(st, style3d(f, "Return × time at your SIP", "Return %", "Years", "Corpus (₹ lakh)"))

    with T[2]:
        xs = np.arange(0, 21, 2)
        ys = np.unique(np.linspace(1000, max(mo * 3, 20000), 14).round(-2))
        Z = np.array([[fv(y, yrs, ret, x, lump) for x in xs] for y in ys]) / L
        f = go.Figure([surf(xs, ys, Z, hovertemplate="Step-up %{x}%<br>SIP ₹%{y:,.0f}<br>₹%{z:,.1f} L<extra></extra>"),
                       go.Scatter3d(x=[step], y=[mo], z=[val / L], mode="markers", marker=dict(size=8, color="#fff", symbol="diamond"),
                                    showlegend=False)])
        pchart(st, style3d(f, f"Step-up landscape over {yrs} years", "Yearly step-up %", "Monthly SIP ₹", "Corpus (₹ lakh)"))

    with T[3]:
        sc = [("Cautious", max(1.0, ret - 4)), ("Your plan", ret), ("Bullish", ret + 4)]
        gap = max(1, int(yrs) // 20)
        yl = list(range(1, int(yrs) + 1, gap))
        ib, gb = [], []
        for j, (_, r_) in enumerate(sc):
            pr = sip_path(mo, yrs, r_, step, lump)
            for y in yl:
                _, i_, v_ = pr[y]
                ib.append((y - .35, y + .35, j + .1, j + .8, 0, i_ / L))
                gb.append((y - .35, y + .35, j + .1, j + .8, i_ / L, max(v_, i_) / L))
        f = go.Figure([go.Mesh3d(**boxes(ib), color="#2EC4B6", flatshading=True, name="Invested", showlegend=True, hoverinfo="name"),
                       go.Mesh3d(**boxes(gb), color="#FFB703", flatshading=True, name="Growth", showlegend=True, hoverinfo="name")])
        style3d(f, "Growth towers: invested (teal) + market growth (amber)", "Year", "Scenario", "Corpus (₹ lakh)")
        f.update_layout(scene=dict(yaxis=dict(tickvals=[.45, 1.45, 2.45], ticktext=[f"{n} {r_:.0f}%" for n, r_ in sc])))
        pchart(st, f)
        st.caption("Notice how the amber growth part overtakes the teal part in the later years: that is compounding.")

    with T[4]:
        pc = np.arange(5, 96, 5)
        Z = np.percentile(P, pc, axis=0) / L
        gz = goal / L
        f = go.Figure([surf(yv, pc, Z, hovertemplate="Year %{x:.1f}<br>Percentile %{y}<br>₹%{z:,.1f} L<extra></extra>"),
                       go.Surface(x=[0, yrs], y=[5, 95], z=[[gz, gz], [gz, gz]], showscale=False, opacity=.3,
                                  colorscale=[[0, "#FFFFFF"], [1, "#FFFFFF"]], hoverinfo="skip")])
        pchart(st, style3d(f, f"Probability sheet. Chance of hitting goal: {prob:.0f}%", "Years", "Percentile of luck", "Corpus (₹ lakh)"))
        st.caption("Low percentiles = bad market luck, high = good luck. The white plane is your goal: where the sheet rises above it, you win.")

    with T[5]:
        idx = np.argsort(P[:, -1])[np.linspace(0, len(P) - 1, 40).astype(int)]
        fin = P[idx, -1] / L
        lines = [go.Scatter3d(x=yv, y=[k] * len(yv), z=P[i] / L, mode="lines", showlegend=False,
                              line=dict(width=4, color=[fin[k]] * len(yv), colorscale=CS, cmin=fin.min(), cmax=fin.max()),
                              hovertemplate=f"Path {k + 1}<br>Year %{{x:.1f}}<br>₹%{{z:,.1f}} L<extra></extra>")
                 for k, i in enumerate(idx)]
        pchart(st, style3d(go.Figure(lines), "Path forest: 40 possible futures, ranked worst → best", "Years", "Path rank", "Value (₹ lakh)"))

    with T[6]:
        tix = np.arange(0, P.shape[1], 12)
        top = max(np.percentile(P[:, -1], 98) * 1.05, 1)
        edges = np.linspace(0, top, 41)
        cen = (edges[:-1] + edges[1:]) / 2 / L
        Z = np.column_stack([np.histogram(np.clip(P[:, t], 0, top), bins=edges)[0] / len(P) * 100 for t in tix])
        f = go.Figure(surf(yv[tix], cen, Z, cbar="% of paths",
                           hovertemplate="Year %{x:.0f}<br>₹%{y:,.1f} L<br>%{z:.1f}% of futures<extra></extra>"))
        pchart(st, style3d(f, "Future density: where your wealth is most likely to sit", "Years", "Value (₹ lakh)", "% of futures"))
        st.caption("A tall ridge = many futures land there. The ridge widens with time: the longer you wait, the wider the range of outcomes.")

    with T[7]:
        sips = tuple(int(x) for x in np.linspace(max(1000, mo * .25), mo * 2.5, 9))
        yl = tuple(range(3, 31, 3))
        Z = terrain(lump, ret, sg, step, goal, sips, yl)
        f = go.Figure([go.Surface(x=list(sips), y=list(yl), z=Z, colorscale=CS, cmin=0, cmax=100,
                                  colorbar=dict(title="% chance", len=.6),
                                  contours=dict(z=dict(show=True, usecolormap=True, project_z=True)),
                                  hovertemplate="SIP ₹%{x:,.0f}<br>%{y} yrs<br>%{z:.0f}% chance<extra></extra>")])
        pchart(st, style3d(f, f"Goal terrain: chance of reaching {rs(goal)}", "Monthly SIP ₹", "Years", "Success %"))
        st.caption("Find the green-to-pink plateau: those SIP and time combinations make your goal very likely.")

    if st.button("🤖 Explain my SIP in simple words", key="s3_ai"):
        ai_show(f"SIP ₹{mo}/month, {yrs} years, {ret}% return, {step}% step-up, lump sum ₹{lump}. Invested {rs(inv)}, "
                f"projected {rs(val)}. Chance of reaching goal {rs(goal)} is {prob:.0f}%. Explain simply and give one move to improve the odds.")
    st.caption("Projections assume constant returns; the probability views use simulated markets. Not a guarantee. Educational only.")


# ===================== AUTH GATE =====================
if "user" not in st.session_state:
    auth_page()
    st.stop()

# ===================== UI =====================
st.session_state.setdefault("txns", profile_txns(prof())); st.session_state.setdefault("msgs", [])
st.session_state.setdefault("sms_text", ""); st.session_state.setdefault("last_txt", "")
if st.session_state.get("flash"): st.toast(st.session_state.pop("flash"))

hdr = st.columns([6, 1])
hdr[0].markdown(f"💰 **ArthaAgent** · {prof()['name'] or st.session_state.user} · {prof()['email'] or st.session_state.user}")
if hdr[1].button("🚪 Log out", key="logout", **WB): logout(); st.rerun()
with st.expander("⚙️ Settings"):
    st.radio("Agent personality", ["Coach", "Roast"], key="mode", horizontal=True)
    if key(): st.success(f"Gemini connected · model {model()}")
    else: st.warning("Gemini key not found. Add GEMINI_API_KEY to Streamlit secrets.")
    st.caption("Educational only. Market tools use simulated paths, never real money.")

st.markdown('<div class="hero">' + COIN + '<h1>Your money, run by an AI agent.</h1>'
            '<p>Gemini reads your payment screenshots, calls real finance tools, simulates thousands of versions '
            'of your future and explains everything in plain words.</p>'
            '<div class="pills"><span class="pill">🤖 Tool-calling agent</span><span class="pill">📸 Screenshot vision</span>'
            '<span class="pill">🔮 Monte Carlo twin</span><span class="pill">🔥 FIRE planner</span>'
            '<span class="pill">📰 Live market news</span><span class="pill">🧊 3D SIP lab</span>'
            '<span class="pill">🛡️ Scam shield</span></div></div>',
            unsafe_allow_html=True)
T = st.tabs(["🏠 Dashboard", "🤖 Agent", "📸 Snap & Budget", "🔮 Money Twin", "⚖️ Decision Lab",
             "🛡️ Scam Shield", "🧾 Tax", "🔥 FIRE & Loans", "📰 Market News", "📈 SIP 3D Lab", "👤 Profile"])

# ---- Dashboard ----
with T[0]:
    section("Your money at a glance", "Health score, smart alerts and badges, computed from your own transactions.")
    S = spending_summary.__wrapped__()
    bal = st.number_input("Savings balance ₹ (used for the emergency-fund score)", 0, value=iv(pf("savings"), 0), step=10000, key=K("bal"))
    parts = health_parts(S, bal)
    overall = int(np.mean(list(parts.values())))
    col = "#2EC4B6" if overall >= 70 else "#FFB703" if overall >= 45 else "#FF5C5C"
    d1, d2 = st.columns(2)
    gg = go.Figure(go.Indicator(mode="gauge+number", value=overall, title={"text": "Money health score"},
                                gauge={"axis": {"range": [0, 100]}, "bar": {"color": col}}))
    gg.update_layout(height=320, margin=dict(t=60, b=10))
    pchart(d1, gg)
    names, vals = list(parts), list(parts.values())
    rd = go.Figure(go.Scatterpolar(r=vals + vals[:1], theta=names + names[:1], fill="toself", line=dict(color="#FFB703")))
    rd.update_layout(height=320, margin=dict(t=60, b=10), polar=dict(radialaxis=dict(range=[0, 100], rangemode="nonnegative")),
                     title="Where you are strong and weak")
    pchart(d2, rd)
    t1, t2 = st.columns(2)
    pchart(t1, towers3d(list(parts), list(parts.values()), "Health score towers", "Score / 100", fmt=lambda v: f"{v:.0f}"))
    pchart(t2, towers3d(["Income", "Spent", "Saved"], [S["income"], S["spent"], max(S["saved"], 0)], "Cash-flow towers",
                        "₹", colors=["#2EC4B6", "#F25F8C", "#FFB703"], fmt=rs))
    kc = st.columns(4)
    kc[0].metric("Income", rs(S["income"])); kc[1].metric("Spent", rs(S["spent"]))
    kc[2].metric("Saved", rs(S["saved"])); kc[3].metric("Savings rate", f"{S['savings_rate_pct']}%")
    st.subheader("🚨 Smart alerts")
    al = anomalies(st.session_state.get("txns", []))
    for x_ in al: box(x_, "warn")
    if not al: box("No unusual activity found. Clean and clear.")
    st.subheader("🏅 Your badges")
    bd = []
    if S["savings_rate_pct"] >= 20: bd.append("💎 Super Saver")
    if not S["repeat_charges"]: bd.append("🧘 Subscription Slayer")
    if parts["Emergency fund"] >= 100: bd.append("🛟 Safety Net Ready")
    if parts["Needs load"] >= 80 and parts["Wants control"] >= 80: bd.append("⚖️ Balanced Budget")
    st.markdown("".join(f'<span class="chip">{b_}</span>' for b_ in (bd or ["🚀 Just Getting Started"])), unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    if b1.button("✨ Build my 30-day money plan", type="primary", key="plan30", **WB):
        with b1: ai_show(f"Summary {S}, health scores {parts}, alerts {al}.{profile_brief()} "
                         "Write a 30-day money plan in 4 weekly steps with specific rupee targets.", spin="Gemini is planning your month…")
    if b2.button("📄 Create my money report", key="mkrep", **WB):
        with st.spinner("Writing your report…"):
            nar = gen(f"Write a 120-word executive summary of this person's finances: {S}, scores {parts}, alerts {al}.")
            if nar and nar.startswith("⚠️"): st.error(nar); nar = None
            st.session_state.report = build_report(S, parts, overall, al, nar or "(Add a Gemini key for an AI summary.)")
    if st.session_state.get("report"):
        st.download_button("⬇️ Download your report (Markdown)", st.session_state.report, "artha_money_report.md", key="dlrep")

# ---- Agent ----
with T[1]:
    section("Meet your money agent", "Ask in plain words. Gemini picks the right tools, runs the numbers and shows its work.")
    if not key(): st.info("Add GEMINI_API_KEY to Streamlit secrets to chat. Other tabs work without it.")
    c = st.columns(3) + st.columns(3)
    asks = ["Review my spending and tell me what to fix",
            "Will I reach ₹1 crore in 15 years with ₹10,000 SIP and ₹2 lakh saved?",
            "Can I afford an ₹80,000 phone on 12-month EMI? Use my income from my profile",
            "Compare tax for ₹18 lakh salary with ₹1.5 lakh 80C",
            "Using my profile, when can I retire early?",
            "Score my financial health and flag anything unusual"]
    pend = next((a for i, a in enumerate(asks) if c[i].button(a, key=f"a{i}", **WB)), None)
    q = st.chat_input("Ask anything about your money…", key="agent_in") or pend
    if q:
        vw = violence_scan(q)
        if vw:  # violence word detector: block before anything reaches Gemini
            st.error("🚫 Message blocked: it contains violent or threatening words (" + ", ".join(vw) + "). "
                     "ArthaAgent only helps with money questions. If anyone is in danger, call 112 (India emergency number).")
            q = None
    if q and not key(): st.warning(NOKEY)
    elif q:
        from google.genai import types
        sig = (key(), model(), st.session_state.get("lang"), st.session_state.get("mode"), st.session_state.get("pv", 0))
        st.session_state.trace = []
        with st.spinner("Agent is thinking and calling tools…"):
            ans = None
            for m_ in model_candidates():
                try:
                    if st.session_state.get("sig") != sig or st.session_state.get("chat_model") != m_:
                        st.session_state.chat = client(key()).chats.create(model=m_, config=fast_cfg(m_, tools=TOOLS))
                        st.session_state.sig, st.session_state.chat_model = sig, m_
                    ans = st.session_state.chat.send_message(q).text or "(no answer)"
                    st.session_state["good_model"] = m_
                    break
                except Exception as e:
                    ans = f"⚠️ {e}"
                    st.session_state.pop("sig", None)
                    if not _model_missing(e): break
        st.session_state.msgs += [dict(role="user", content=q), dict(role="assistant", content=ans, trace=list(st.session_state.trace))]
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]):
            if m.get("trace"):
                st.markdown("".join(f'<span class="chip">🔧 {n}</span>' for n, _, _ in m["trace"]), unsafe_allow_html=True)
                with st.expander("See the agent's tool calls"):
                    for n, a, r in m["trace"]: st.code(f"{n}({json.dumps(a, default=str)})\n→ {json.dumps(r, default=str)}", language="python")
            st.write(m["content"])
    if st.session_state.msgs and st.button("🧹 Clear chat", key="clrchat"):
        st.session_state.msgs = []; st.session_state.pop("sig", None); st.rerun()

# ---- Snap & Budget ----
with T[2]:
    section("Snap, paste, understand", "Drop a screenshot or paste SMS alerts and see where every rupee went.")


    def _use_profile():
        st.session_state.txns = profile_txns(prof()); st.session_state.txn_src = "profile"
        st.session_state.sms_text = ""; st.session_state.last_txt = ""


    def _use_demo():
        st.session_state.sms_text = DEMO


    a, b = st.columns([3, 2])
    txt = a.text_area("Paste UPI / bank SMS (one per line)", height=170, key="sms_text",
                      placeholder="Rs.1,250.00 debited to VPA swiggy@ybl")
    a1, a2 = a.columns(2)
    a1.button("🧾 Use my profile budget", on_click=_use_profile, key="useprof", **WB)
    a2.button("🧪 Load demo SMS", on_click=_use_demo, key="usedemo", **WB)
    shot = b.file_uploader("📸 Or upload a screenshot (UPI history, bank statement, bill)", type=["png", "jpg", "jpeg"], key="shot")
    if shot: b.image(shot, caption="Preview", width=240)
    if b.button("🔍 Read screenshot with Gemini Vision", key="vis", type="primary", **WB):
        if not key(): b.warning(NOKEY)
        elif not shot: b.warning("Upload a screenshot first, then press the button.")
        else:
            with st.spinner("Gemini is reading your screenshot…"):
                raw = gen('Extract every transaction visible. Return ONLY a JSON array of '
                          '{"merchant": str, "amount": number, "type": "debit"|"credit"}.', [img_part(shot)], js=True)
            d = jload(raw)
            if isinstance(d, dict): d = next((v for v in d.values() if isinstance(v, list)), None)
            tx = clean_vision(d) if isinstance(d, list) else []
            if tx:
                st.session_state.txns = tx; st.session_state.txn_src = "vision"
                st.session_state.last_txt = txt
                st.session_state.flash = f"Loaded {len(tx)} transactions from your screenshot ✅"; st.rerun()
            else:
                b.error(raw if (raw or "").startswith("⚠️") else "Couldn't read any transactions. Try a clearer, cropped screenshot.")
    if txt != st.session_state.get("last_txt"):
        st.session_state.last_txt = txt
        new = parse_sms(txt)
        if new: st.session_state.txns = new; st.session_state.txn_src = "sms"
    st.caption(f"Data source: **{st.session_state.get('txn_src', 'profile')}** · {len(st.session_state.txns)} transactions")
    S = spending_summary.__wrapped__()
    m = st.columns(4)
    m[0].metric("Income", rs(S["income"])); m[1].metric("Spent", rs(S["spent"]))
    m[2].metric("Saved", rs(S["saved"])); m[3].metric("Savings rate", f"{S['savings_rate_pct']}%")
    cats = {}
    for t in st.session_state.txns:
        if t["kind"] == "debit": cats[t["category"]] = cats.get(t["category"], 0) + t["amount"]
    g1, g2 = st.columns(2)
    if cats:
        pchart(g1, px.pie(names=list(cats), values=list(cats.values()), hole=.55, color_discrete_sequence=PAL, title="Where it went"))
        wants = S["spent"] - S["needs"]; inc = S["income"] or 1
        pchart(g2, px.bar(x=["Needs", "Wants", "Savings"] * 2, y=[S["needs"], max(wants, 0), max(S["saved"], 0)] + [inc * .5, inc * .3, inc * .2],
                          color=["You"] * 3 + ["50/30/20 ideal"] * 3, barmode="group",
                          color_discrete_sequence=PAL, labels={"x": "", "y": "₹", "color": ""}))
        pchart(st, towers3d(list(cats), list(cats.values()), "Spending towers by category", "₹", fmt=rs))
    with st.expander("📋 View parsed transactions"):
        st.dataframe(pd.DataFrame(st.session_state.txns), **WDF)
    for r in S["repeat_charges"]: box(f"Repeat charge spotted: {r}", "warn")
    if st.button("🧬 Generate my Spending DNA", type="primary", key="dna"):
        if not key(): st.warning(NOKEY)
        else:
            with st.spinner("Sequencing your spending…"):
                o = jload(gen(f'Using this data {S}, invent a fun "Spending DNA" persona. Return ONLY JSON: '
                              '{"name": str, "emoji": str, "one_liner": str, "superpower": str, '
                              '"money_leak": str, "next_move": str}', js=True))
            if isinstance(o, dict):
                st.markdown("## " + str(o.get("emoji", "🧬")) + " " + str(o.get("name")))
                st.write(o.get("one_liner"))
                box("🦸 <b>Superpower:</b> " + html.escape(str(o.get("superpower"))))
                box("💧 <b>Money leak:</b> " + html.escape(str(o.get("money_leak"))), "warn")
                box("🚀 <b>Next move:</b> " + html.escape(str(o.get("next_move"))), "info")
            else:
                st.error("Gemini didn't return a persona. Try again.")

# ---- Money Twin ----
with T[3]:
    section("Your Money Twin", "Thousands of possible futures, with life events built in.")
    st.caption("Simulates thousands of possible market futures for you, including life events.")
    a = st.columns(6)
    s0 = a[0].number_input("Savings now ₹", 0, value=iv(pf("savings") + pf("investments"), 0), step=50000, key=K("mt_s0"))
    mo = a[1].number_input("Monthly SIP ₹", 0, value=iv(pf("sip") or 10000, 0), step=1000, key=K("mt_mo"))
    yrs = a[2].number_input("Years", 1, 40, iv(pf("goal_years"), 1, 40), key=K("mt_y"))
    goal = a[3].number_input("Goal ₹", 0, value=iv(pf("goal_amount"), 0), step=500000, key=K("mt_g"))
    mu = a[4].number_input("Return %", 1.0, 25.0, 11.0, key="mt_mu")
    sg = a[5].number_input("Volatility %", 1.0, 40.0, 16.0, key="mt_sg")
    step = st.slider("Yearly SIP step-up %", 0, 20, 8, key="mt_step")
    ev = st.data_editor(pd.DataFrame([dict(Label="Wedding", Year=4, Amount=-500000), dict(Label="Bonus", Year=2, Amount=200000),
                                      dict(Label="Career break", Year=7, Amount=-300000)]),
                        num_rows="dynamic", key="mt_ev", **WD)
    E = {}
    for _, r in ev.dropna().iterrows():
        try:
            mth = int(min(max(int(r.Year * 12) - 1, 0), int(yrs * 12) - 1)); E[mth] = E.get(mth, 0) + float(r.Amount)
        except Exception: pass
    P = sim(s0, mo, yrs, mu, sg, step, E, 3000); fin_ = P[:, -1]; prob = (fin_ >= goal).mean() * 100
    x = st.columns(4)
    x[0].metric("Chance of hitting goal", f"{prob:.0f}%"); x[1].metric("Median outcome", rs(np.median(fin_)))
    x[2].metric("Bad luck (worst 10%)", rs(np.percentile(fin_, 10))); x[3].metric("Good luck (best 10%)", rs(np.percentile(fin_, 90)))
    yv = np.arange(P.shape[1]) / 12; lo, md, hi = (np.percentile(P, q, axis=0) for q in (10, 50, 90))
    fig = go.Figure([go.Scatter(x=yv, y=hi, line=dict(width=0), showlegend=False),
                     go.Scatter(x=yv, y=lo, fill="tonexty", fillcolor="rgba(255,183,3,.18)", line=dict(width=0), name="10-90% range"),
                     go.Scatter(x=yv, y=md, name="Median", line=dict(color="#FFB703", width=3)),
                     go.Scatter(x=[0, yrs], y=[goal, goal], name="Goal", line=dict(color="#2EC4B6", dash="dash"))])
    fig.update_layout(title="Your possible futures", xaxis_title="Years")
    pchart(st, fig)
    lev = {"Today's plan": prob,
           "SIP +25%": (sim(s0, mo * 1.25, yrs, mu, sg, step, E, 1500)[:, -1] >= goal).mean() * 100,
           "+2 more years": (sim(s0, mo, yrs + 2, mu, sg, step, E, 1500)[:, -1] >= goal).mean() * 100,
           "Goal -20%": (fin_ >= goal * .8).mean() * 100,
           "Step-up 15%": (sim(s0, mo, yrs, mu, sg, 15, E, 1500)[:, -1] >= goal).mean() * 100}
    pchart(st, px.bar(x=list(lev), y=list(lev.values()), color=list(lev), color_discrete_sequence=PAL,
                      title="Which lever moves your odds most?", labels={"x": "", "y": "Success %"}))
    pchart(st, towers3d(list(lev), list(lev.values()), "3D lever towers: chance of success", "Success %", fmt=lambda v: f"{v:.0f}%"))
    if st.button("Ask Gemini to read my twin", key="twin_ai"):
        ai_show(f"My Monte Carlo result: goal {goal}, success {prob:.0f}%, levers {lev}. Explain what it means and the single best move.")

# ---- Decision Lab ----
with T[4]:
    section("Decision Lab", "Buy now, take an EMI, or invest instead? See the true cost before you commit.")
    d = st.columns(5)
    pr = d[0].number_input("Price ₹", 1000, value=80000, step=5000, key="dl_p")
    inc_ = d[1].number_input("Monthly income ₹", 1000, value=iv(income() or 60000, 1000), step=5000, key=K("dl_i"))
    mn = d[2].selectbox("EMI months", [3, 6, 9, 12, 18, 24], 3, key="dl_m")
    rt = d[3].number_input("EMI interest %", 0.0, 40.0, 14.0, key="dl_r")
    rr = d[4].number_input("Invest return %", 1.0, 20.0, 12.0, key="dl_rr")
    R = can_i_afford.__wrapped__(pr, inc_, mn, rt)
    m = st.columns(4)
    m[0].metric("EMI", rs(R["emi"])); m[1].metric("EMI vs income", f"{R['emi_pct_of_income']}%")
    m[2].metric("Interest you pay", rs(R["interest_cost"])); m[3].metric("If invested instead", rs(pr * (1 + rr / 1200) ** mn))
    box(f"Verdict: <b>{R['verdict']}</b>. " + {"comfortable": "Fits easily. Still try the 30-day wait rule.",
                                               "okay": "Affordable but it will squeeze savings.",
                                               "risky": "Too heavy. Save first or buy cheaper."}[R["verdict"]],
        "" if R["verdict"] == "comfortable" else "warn" if R["verdict"] == "okay" else "bad")
    pchart(st, px.bar(x=["Pay cash", f"EMI ({mn}m)", "Invest instead (value)"], y=[pr, pr + R["interest_cost"], pr * (1 + rr / 1200) ** mn],
                      color_discrete_sequence=PAL, labels={"x": "", "y": "₹"}))
    pchart(st, towers3d(["Pay cash", f"EMI ({mn}m)", "Invest instead"], [pr, pr + R["interest_cost"], pr * (1 + rr / 1200) ** mn],
                        "True cost in 3D", "₹", fmt=rs))
    if st.button("Ask Gemini: should I buy it?", key="dl_ai"):
        ai_show(f"Decision: {R}, price {pr}, income {inc_}. Give a clear buy/wait/skip recommendation with one trick to pay less.")

# ---- Scam Shield ----
with T[5]:
    section("Scam Shield", "Paste or snap a suspicious message and know in seconds whether to trust it.")
    msg = st.text_area("Paste a suspicious message",
                       "Dear customer, your SBI account will be blocked today. Update KYC immediately: bit.ly/sbi-kyc9 and share the OTP.",
                       height=100, key="scam_msg")
    ss = st.file_uploader("…or upload a screenshot of the message/payment request", type=["png", "jpg", "jpeg"], key="ss")
    sc, fl = scam_rules(msg); lvl = "high" if sc >= 60 else "medium" if sc >= 30 else "low"
    vwords = violence_scan(msg)
    g = go.Figure(go.Indicator(mode="gauge+number", value=sc, title={"text": "Rule-based risk"},
                               gauge={"axis": {"range": [0, 100]}, "bar": {"color": {"high": "#FF5C5C", "medium": "#FFB703", "low": "#2EC4B6"}[lvl]}}))
    g.update_layout(height=250, margin=dict(t=50, b=0))
    c1, c2 = st.columns([1, 2]); pchart(c1, g)
    with c2:
        if vwords:
            box("🚫 <b>Violence word detector:</b> threatening words found: " + html.escape(", ".join(vwords)), "bad")
        for f in fl:
            if not f.startswith("Violent / threatening"): box("⚠ " + f, "bad" if lvl == "high" else "warn")
        if sc >= 30 or vwords:
            st.error("Don't click, reply or pay. Call your bank on the number on your card. "
                     "Lost money? Call 1930 or report at cybercrime.gov.in within an hour."
                     + (" If you feel physically threatened, call 112." if vwords else ""))
    if st.button("Get Gemini's verdict", key="scam_ai"):
        ai_show(f"Is this a scam? Rule flags: {fl}. Message: {msg!r}. Say yes/no/maybe, why, and exactly what to do (mention 1930 if risky).",
                [img_part(ss)] if ss else None, spin="Analysing…")

# ---- Tax ----
with T[6]:
    section("Tax, in plain words", "Old vs new regime, with the numbers to back it up.")
    t = st.columns(4)
    gross0 = iv(pf("salary") * 12 or 1800000, 0)
    g_ = t[0].number_input("Gross salary/yr", 0, value=gross0, step=50000, key=K("tx_g"))
    c8 = t[1].number_input("80C", 0, value=150000, step=10000, key=K("tx_c"))
    d8 = t[2].number_input("80D", 0, value=25000 if pf("health_ins") else 0, step=5000, key=K("tx_d"))
    hr = t[3].number_input("HRA exemption", 0, value=iv(min(pf("rent") * 12 * .5, gross0 * .2), 0), step=10000, key=K("tx_h"))
    X = tax_calc(g_, c8, d8, hr)
    m = st.columns(3)
    m[0].metric("New regime", rs(X["new_regime_tax"])); m[1].metric("Old regime", rs(X["old_regime_tax"]))
    m[2].metric(f"Better: {X['better']}", rs(X["saving"]))
    if pf("regime") != "Not sure": st.caption(f"You told us you use the **{pf('regime')}**.")
    pchart(st, px.bar(x=["New", "Old"], y=[X["new_regime_tax"], X["old_regime_tax"]], color=["New", "Old"],
                      color_discrete_sequence=PAL, labels={"x": "", "y": "Tax ₹"}))
    st.subheader("🆕 New regime in detail (FY 2026-27)")
    NB = new_regime_breakdown(g_)
    nm = st.columns(4)
    nm[0].metric("Standard deduction", rs(NB["std"])); nm[1].metric("Taxable income", rs(NB["taxable"]))
    nm[2].metric("87A rebate", rs(NB["rebate"])); nm[3].metric("Effective tax rate", f"{NB['eff_pct']}%")
    nm = st.columns(3)
    nm[0].metric("Tax before rebate", rs(NB["slab_tax"])); nm[1].metric("Cess (4%)", rs(NB["cess"]))
    nm[2].metric("Final new-regime tax", rs(NB["total"]))
    if NB["surcharge"] > 0: box(f"Surcharge added: {rs(NB['surcharge'])} (no marginal relief on surcharge is modelled).", "warn")
    box(f"Salary up to <b>{rs(NB['tax_free_gross'])}</b> pays zero tax under the new regime "
        f"(₹75,000 standard deduction + ₹60,000 rebate on income up to ₹12 lakh)."
        + (" " + NB["note"] if NB["note"] else ""), "" if NB["total"] == 0 else "warn")
    st.dataframe(pd.DataFrame(NB["rows"]), hide_index=True, **WDF)
    pchart(st, px.bar(pd.DataFrame(NB["rows"]), x="Slab", y="Tax", color="Rate", color_discrete_sequence=PAL,
                      title="Where your new-regime tax comes from", labels={"Tax": "Tax ₹"}))
    pchart(st, towers3d([r_["Slab"] for r_ in NB["rows"]], [r_["Tax"] for r_ in NB["rows"]], "Tax staircase: tax paid in each slab",
                        "Tax ₹", fmt=rs))
    st.caption("New regime: no 80C/80D/HRA. Verify slabs on the Income Tax portal before filing. Educational only.")
    if st.button("Explain in simple words", key="tax_ai"):
        ai_show(f"Tax result {X}. Explain simply why the {X['better']} regime wins and one way to cut tax.")

# ---- FIRE & Loans ----
with T[7]:
    section("Freedom & loans", "When could you stop working, and should you prepay that loan or invest instead?")
    fc = st.columns(5)
    age = fc[0].number_input("Your age", 18, 70, iv(pf("age"), 18, 70), key=K("fage"))
    ex = fc[1].number_input("Monthly expenses ₹", 1000, value=iv(outgo() or 40000, 1000), step=5000, key=K("fex"))
    sv = fc[2].number_input("Invested so far ₹", 0, value=iv(pf("investments") or 500000, 0), step=50000, key=K("fsv"))
    mi = fc[3].number_input("Invest per month ₹", 0, value=iv(pf("sip") or 30000, 0), step=5000, key=K("fmi"))
    fr = fc[4].number_input("Return %", 1.0, 20.0, 11.0, key="fr")
    fg = st.columns(2)
    fi_ = fg[0].slider("Inflation %", 3, 10, 6, key="fi")
    wr = fg[1].slider("Safe withdrawal rate %", 2.5, 5.0, 4.0, .1, key="fwr")
    R0 = fire_calc(ex, sv, mi, fr, fi_, wr)
    ok_ = R0["years"] is not None
    fm = st.columns(3)
    fm[0].metric("Years to freedom", f"{R0['years']:.1f}" if ok_ else "50+")
    fm[1].metric("Freedom age", f"{age + R0['years']:.0f}" if ok_ else "n/a")
    fm[2].metric("Corpus needed then", rs(R0["corpus"]))
    if ok_ and age + R0["years"] > pf("retire_age"):
        box(f"At this pace you reach freedom after your target retirement age of {pf('retire_age')}. Try raising your monthly investment.", "warn")
    vr = {"Lean (spend 70%)": .7, "Regular": 1.0, "Fat (spend 160%)": 1.6}
    ys = {k_: fire_calc(ex * v_, sv, mi, fr, fi_, wr)["years"] for k_, v_ in vr.items()}
    pchart(st, px.bar(x=list(ys), y=[v_ if v_ is not None else 50 for v_ in ys.values()], color=list(ys),
                      color_discrete_sequence=PAL, title="Years to freedom by lifestyle", labels={"x": "", "y": "Years"}))
    pchart(st, towers3d(list(ys), [v_ if v_ is not None else 50 for v_ in ys.values()], "Lifestyle towers: years to freedom",
                        "Years", fmt=lambda v: f"{v:.1f}y"))
    rows = pd.DataFrame(R0["rows"], columns=["Year", "Your portfolio", "Corpus needed"])
    pchart(st, px.line(rows, x="Year", y=["Your portfolio", "Corpus needed"], color_discrete_sequence=PAL,
                       title="When the lines cross, you are free"))
    st.divider()
    st.subheader("🏦 Prepay your loan or invest?")
    lc = st.columns(5)
    lb = lc[0].number_input("Loan balance ₹", 10000, value=2500000, step=100000, key="lb")
    lr = lc[1].number_input("Loan rate %", 1.0, 20.0, 9.0, key="lr")
    ly = lc[2].number_input("Years left", 1, 30, 12, key="ly")
    lx = lc[3].number_input("Extra per month ₹", 0, value=10000, step=1000, key="lx")
    li = lc[4].number_input("Invest return %", 1.0, 20.0, 12.0, key="li")
    PV = prepay_vs_invest.__wrapped__(lb, lr, ly, lx, li)
    pm = st.columns(3)
    pm[0].metric("Interest saved if you prepay", rs(PV["interest_saved"]))
    pm[1].metric("Months cut from loan", PV["months_saved"])
    pm[2].metric("Invest gain (after tax)", rs(PV["invest_gain_after_tax"]))
    box(f"Numbers favour: <b>{PV['winner']}</b>. Prepaying is a guaranteed return equal to your loan rate; "
        "investing can earn more but is not guaranteed.", "" if PV["winner"] == "prepay" else "warn")

# ---- Market News (live) ----
with T[8]:
    news_tab()

# ---- SIP 3D Lab ----
with T[9]:
    sip3d_tab()

# ---- Profile ----
with T[10]:
    section("Your profile", "Keep this up to date: every tab and the AI agent use it to personalise numbers.")
    p = prof()
    filled = [bool(p["name"]), bool(p["email"]), bool(p["phone"]), bool(p["city"]), bool(p["occupation"]),
              p["salary"] > 0, p["expenses"] > 0, p["savings"] > 0, p["investments"] > 0 or p["sip"] > 0,
              p["goal_amount"] > 0, p["health_ins"], p["term_ins"]]
    st.progress(sum(filled) / len(filled), text=f"Profile completeness {sum(filled) * 100 // len(filled)}%")
    inc, out = income(), outgo()
    free = inc - out - p["sip"]
    pm = st.columns(4)
    pm[0].metric("Monthly income", rs(inc)); pm[1].metric("Rent + EMI + expenses", rs(out))
    pm[2].metric("Free cash after SIP", rs(free)); pm[3].metric("Savings rate", f"{(inc - out) / inc * 100:.0f}%" if inc else "n/a")
    pchart(st, towers3d(["Income", "Rent", "EMI", "Living", "SIP", "Free cash"],
                        [inc, p["rent"], p["emi"], p["expenses"], p["sip"], max(free, 0)], "Your monthly budget in 3D", "₹", fmt=rs))
    st.subheader("💡 Personal insights")
    tips = []
    if inc and p["emi"] / inc > .4: tips.append(("EMIs take over 40% of your income. Avoid new loans and consider prepaying the costliest one.", "bad"))
    if free < 0: tips.append(("You spend more than you earn after SIP. Trim expenses or lower the SIP until it's positive.", "bad"))
    ef = 6 * out
    tips.append((f"Emergency fund target is {rs(ef)} (6 months). You have {rs(p['savings'])}: "
                 + ("on track." if p["savings"] >= ef else f"build {rs(ef - p['savings'])} more."), "" if p["savings"] >= ef else "warn"))
    if inc and p["sip"] < .2 * (inc - out): tips.append((f"You could invest more: 20% of income is {rs(inc * .2)}/month versus your SIP of {rs(p['sip'])}.", "warn"))
    if not p["health_ins"]: tips.append(("No health insurance listed. A ₹10 lakh+ family floater is the first protection to add.", "warn"))
    if not p["term_ins"] and (p["dependents"] > 0 or p["marital"] == "Married"):
        tips.append((f"With dependents, term cover of about {rs(inc * 12 * 12)} (12x yearly income) is a common rule of thumb.", "warn"))
    for t_, k_ in tips: box(t_, k_)

    st.subheader("✏️ Update profile")
    with st.form(f"upd_{st.session_state.pv}"):
        vals = profile_fields(p, f"u{st.session_state.pv}_")
        sub = st.form_submit_button("💾 Save profile", type="primary")
    if sub:
        err = check_profile(vals)
        if err:
            st.error(err)
        else:
            others = [r["profile"].get("email", "").lower() for u_, r in _load().items() if u_ != st.session_state.user]
            if vals["email"].strip().lower() in others: st.error("That email belongs to another account.")
            else:
                vals["name"], vals["email"] = vals["name"].strip(), vals["email"].strip().lower()
                save_profile(vals); st.rerun()

    with st.expander("🔑 Change password"):
        with st.form("pw_form"):
            cp = st.text_input("Current password", type="password")
            np1 = st.text_input("New password", type="password")
            np2 = st.text_input("Confirm new password", type="password")
            sub = st.form_submit_button("Update password")
        if sub:
            db = _load(); r = db.get(st.session_state.user)
            if not r or not verify(cp, r["salt"], r["hash"]): st.error("Current password is wrong.")
            elif np1 != np2: st.error("New passwords don't match.")
            elif (e := pw_problem(np1)): st.error(e)
            else:
                r["salt"], r["hash"] = hash_pw(np1); _save(db); st.success("Password updated.")

    with st.expander("⚠️ Delete my account"):
        with st.form("del_form"):
            dp = st.text_input("Confirm with your password", type="password")
            sure = st.checkbox("Yes, permanently delete my account and profile")
            sub = st.form_submit_button("Delete account")
        if sub:
            db = _load(); r = db.get(st.session_state.user)
            if not sure: st.error("Tick the box to confirm.")
            elif not r or not verify(dp, r["salt"], r["hash"]): st.error("Password is wrong.")
            else:
                del db[st.session_state.user]; _save(db); logout(); st.rerun()
