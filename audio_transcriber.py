import streamlit as st
from faster_whisper import WhisperModel
import tempfile
import pandas as pd
import plotly.graph_objects as go

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Pro Subtitle Generator",
    page_icon="🎬",
    layout="wide"
)

# ---------- SESSION STATE ----------
if "show_sidebar" not in st.session_state:
    st.session_state.show_sidebar = False
if "history" not in st.session_state:
    st.session_state.history = []
if "premium" not in st.session_state:
    st.session_state.premium = False
if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0  # Free users limit
if "screen_width" not in st.session_state:
    st.session_state.screen_width = 1200

# ---------- PREMIUM CSS ----------
st.markdown("""
<style>
body,.stApp{background:linear-gradient(135deg,#0f172a,#1e293b);color:white;transition:background 0.5s;}
.card{background:#1f2937;padding:22px;border-radius:20px;margin-bottom:18px;box-shadow:0 10px 30px rgba(0,0,0,0.6);}
.stButton button{border-radius:40px;padding:16px 45px;font-size:18px;background:linear-gradient(90deg,#2563eb,#1d4ed8);color:white;border:none;box-shadow:0 6px 20px rgba(0,0,0,0.6);}
.stButton button:hover{transform:scale(1.05);}
.stFileUploader>div{border:2px dashed #2563eb;border-radius:20px;padding:70px;background:linear-gradient(135deg,#020617,#0f172a);font-size:18px;}
.subtitle-card{background:#0f172a;padding:16px;border-radius:14px;margin-bottom:10px;border-left:5px solid #2563eb;}
.active-sub{border-left:5px solid #22c55e;background:#020617;}
</style>
""", unsafe_allow_html=True)

# ---------- BRANDING ----------
st.markdown(f"""
<div style='text-align:center'>
<h1>🎬 Pro Subtitle Generator</h1>
<p style='color:#94a3b8'>Premium AI Subtitle Studio</p>
<p style='font-size:13px;color:#64748b'>Powered By Faster-Whisper • Streamlit Cloud • AI Engine</p>
<span style="background:#2563eb;padding:6px 18px;border-radius:20px;font-size:14px">
{'Premium User' if st.session_state.premium else 'Free User'}
</span>
</div>
""", unsafe_allow_html=True)

# ---------- SETTINGS BUTTON ----------
if st.button("⚙"):
    st.session_state.show_sidebar = not st.session_state.show_sidebar

# ---------- PLAN LIMITS ----------
if st.session_state.premium:
    allowed_models = ["tiny","base","small","medium"]
    MAX_MB = 9999
    PLAN_NAME = "Premium Plan"
else:
    allowed_models = ["tiny","base"]
    MAX_MB = 25
    PLAN_NAME = "Free Plan (3 conversions/day)"

# ---------- SIDEBAR ----------
if st.session_state.show_sidebar:
    with st.sidebar:
        st.header("Settings")
        model_size = st.selectbox("Whisper Model", allowed_models)
        format_choice = st.selectbox("Format", ["srt","lrc","ass"])
else:
    model_size="base"
    format_choice="srt"

# ---------- LOAD MODEL ----------
@st.cache_resource
def load_model(size):
    return WhisperModel(size, compute_type="int8")
model = load_model(model_size)

# ---------- RESPONSIVE PANELS ----------
def panels():
    width = 1200
    try:
        if "screen_width" in st.query_params:
            width = int(st.query_params["screen_width"])
    except:
        width = 1200
    if width > 1000:
        left, center, right = st.columns([1,3,1])
    else:
        left = None
        right = None
        center = st.container()
    return left, center, right
left_panel, center_panel, right_panel = panels()

# ---------- LEFT PANEL ----------
def render_left():
    if not st.session_state.premium:
        st.markdown(f"""
<div class="card">
<h4>💎 Upgrade to Premium</h4>
<ul>
<li>Unlimited Transcriptions</li>
<li>Access Small/Medium Whisper Models</li>
<li>Long Audio Support</li>
<li>Priority Processing</li>
</ul>
<a href="https://paypal.me/DonnaldBariso791/9.99?currency=USD" target="_blank">
<button style="width:100%;padding:12px;border-radius:12px;border:none;background:#2563eb;color:white;">Upgrade 🚀</button>
</a>
</div>
""", unsafe_allow_html=True)
    st.markdown("""
<div class="card">
<h4>📢 Ads</h4>
Place Adsense Here
</div>
""", unsafe_allow_html=True)

# ---------- RIGHT PANEL ----------
def render_right():
    st.markdown("""
<div class="card">
<h4>📢 Sponsored</h4>
Adsense Ready Block
</div>
""", unsafe_allow_html=True)
    if st.session_state.history:
        st.markdown(
            "<div class='card'><h4>History</h4>"
            +"<br>".join(st.session_state.history[-5:])
            +"</div>", unsafe_allow_html=True
        )

# ---------- TIME FUNCTIONS ----------
def srt_time(s):
    h=int(s//3600)
    m=int((s%3600)//60)
    sec=int(s%60)
    ms=int((s-int(s))*1000)
    return f"{h:02}:{m:02}:{sec:02},{ms:03}"
def lrc_time(seconds):
    m=int(seconds//60)
    s=int(seconds%60)
    ms=int((seconds-int(seconds))*100)
    return f"[{m:02}:{s:02}.{ms:02}]"
def ass_time(seconds):
    h=int(seconds//3600)
    m=int((seconds%3600)//60)
    s=int(seconds%60)
    cs=int((seconds-int(seconds))*100)
    return f"{h}:{m:02}:{s:02}.{cs:02}"
def clean_text(text):
    text=text.strip()
    return text[0].upper()+text[1:] if len(text)>1 else text

# ---------- CENTER PANEL ----------
with center_panel:
    uploaded_file = st.file_uploader(
        "🎵 Drag & Drop Audio Here (mp3, wav, m4a, mp4)",
        type=["mp3","wav","m4a","mp4"]
    )
    if uploaded_file:
        size = uploaded_file.size / 1024 / 1024
        if size > MAX_MB:
            st.error("File too large for your plan. Upgrade to Premium for bigger files.")
            st.stop()
        st.audio(uploaded_file)

        if not st.session_state.premium and st.session_state.usage_count >= 3:
            st.warning("You reached the Free Plan limit (3 subtitle generations). Upgrade to Premium for unlimited usage!")
            st.markdown(f"""
<a href="https://paypal.me/DonnaldBariso791/9.99?currency=USD" target="_blank">
<button style="width:100%;padding:12px;border-radius:12px;border:none;background:#2563eb;color:white;">Upgrade 🚀</button>
</a>
""", unsafe_allow_html=True)
        else:
            if st.button("🎯 Generate Subtitles", key="genbtn"):
                st.session_state.usage_count += 1
                progress = st.progress(0)
                status = st.empty()
                status.text("Preparing audio...")
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp.write(uploaded_file.read())
                    path = tmp.name
                progress.progress(20)
                status.text("Transcribing audio...")
                segments,_ = model.transcribe(path)
                segments = list(segments)
                progress.progress(60)
                subtitles = [[seg.start, seg.end, clean_text(seg.text)] for seg in segments]
                progress.progress(100)
                st.session_state.history.append(uploaded_file.name)
                st.markdown("### Subtitles")
                for i,row in enumerate(subtitles):
                    st.markdown(f"""
<div class="subtitle-card">
{row[2]}
</div>
""", unsafe_allow_html=True)
                # Export
                output = ""
                if format_choice=="srt":
                    for i,row in enumerate(subtitles):
                        output += f"{i+1}\n{srt_time(row[0])} --> {srt_time(row[1])}\n{row[2]}\n\n"
                    filename="subtitles.srt"
                elif format_choice=="lrc":
                    for row in subtitles:
                        output += f"{lrc_time(row[0])}{row[2]}\n"
                    filename="subtitles.lrc"
                elif format_choice=="ass":
                    output += "[Script Info]\nScriptType: v4.00+\n\n[V4+ Styles]\n"
                    output += "Format: Name,Fontname,Fontsize,PrimaryColour,OutlineColour,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV\n"
                    output += "Style: Default,Arial,40,&H00FFFFFF,&H00000000,1,2,0,2,10,10,10\n\n[Events]\nFormat: Layer,Start,End,Style,Text\n"
                    for row in subtitles:
                        output += f"Dialogue: 0,{ass_time(row[0])},{ass_time(row[1])},Default,{row[2]}\n"
                    filename="subtitles.ass"
                st.download_button("⬇ Download Subtitles", output, file_name=filename)

# ---------- SIDE PANELS ----------
if left_panel:
    with left_panel:
        render_left()
if right_panel:
    with right_panel:
        render_right()
if not left_panel:
    render_left()
    render_right()
