import streamlit as st
from faster_whisper import WhisperModel
import tempfile
import time
import plotly.graph_objects as go
import numpy as np

# ---------- PAGE ----------
st.set_page_config(
    page_title="Pro Subtitle Generator",
    page_icon="🎬",
    layout="wide"
)

# ---------- SESSION ----------

if "segments" not in st.session_state:
    st.session_state.segments=None

if "history" not in st.session_state:
    st.session_state.history=[]

# ---------- PREMIUM CSS ----------

st.markdown("""

<style>

.stApp{
background:linear-gradient(140deg,#020617,#0f172a);
color:white;
}

/* Cards */

.card{
background:#111827;
padding:22px;
border-radius:18px;
margin-bottom:18px;
box-shadow:0px 10px 35px rgba(0,0,0,.7);
}

/* Subtitle */

.subtitleCard{
background:#1f2937;
padding:14px;
border-radius:14px;
margin-bottom:10px;
font-size:18px;
}

.activeCard{
background:linear-gradient(90deg,#2563eb,#1d4ed8);
font-weight:bold;
}


/* Upload zone */

.stFileUploader>div{
border:2px dashed #2563eb;
border-radius:20px;
padding:70px;
font-size:18px;
}


/* Buttons */

.stButton>button{
border-radius:50px;
height:55px;
font-size:20px;
background:linear-gradient(90deg,#2563eb,#1d4ed8);
border:none;
}

/* Banner */

.banner{
text-align:center;
padding:20px;
border-radius:18px;
background:#111827;
margin-top:30px;
}

</style>

""",unsafe_allow_html=True)

# ---------- HEADER ----------

st.markdown(
"<h1 style='text-align:center;font-size:44px'>🎬 Pro Subtitle Generator</h1>",
unsafe_allow_html=True)

st.markdown(
"<p style='text-align:center;color:#94a3b8'>Premium AI Subtitle Editor</p>",
unsafe_allow_html=True)

# ---------- MODEL ----------

@st.cache_resource
def load():

    return WhisperModel("base",compute_type="int8")

model=load()

# ---------- LAYOUT ----------

left,center,right=st.columns([1.2,4,1.2])

# ---------- LEFT PANEL ----------

with left:

    st.markdown("""
    <div class='card'>
    <b>💡 Tips</b><br><br>
    Drag audio file<br>
    Generate subtitles<br>
    Download instantly
    </div>
    """,unsafe_allow_html=True)


    st.markdown("""
    <div class='card'>
    <b>🔥 Sponsored</b><br><br>

    <a href="#">
    <img src="https://via.placeholder.com/250x250.png?text=Advertise+Here" width="100%">
    </a>

    <br><br>
    Advertise Here
    </div>
    """,unsafe_allow_html=True)


    if st.session_state.history:

        st.markdown("<div class='card'><b>History</b><br>"+
        "<br>".join(st.session_state.history[-5:])
        +"</div>",unsafe_allow_html=True)


# ---------- RIGHT PANEL ----------

with right:

    st.markdown("""
    <div class='card'>
    <b>🚀 Features</b><br><br>

    ✔ CapCut Style<br>
    ✔ Offline AI<br>
    ✔ Whisper Engine<br>
    ✔ Fast Export
    </div>
    """,unsafe_allow_html=True)


    st.markdown("""
    <div class='card'>
    <b>⭐ Partner</b><br><br>

    <a href="#">
    <img src="https://via.placeholder.com/250x400.png?text=Ad+Space" width="100%">
    </a>

    <br><br>
    Premium Ads
    </div>
    """,unsafe_allow_html=True)



# ---------- CENTER ----------

with center:

    uploaded=st.file_uploader(
    "🎵 Drag & Drop Audio",
    type=["mp3","wav","m4a","mp4"]
    )


    if uploaded:

        st.audio(uploaded)

        if st.button("Generate Subtitles"):

            progress=st.progress(0)

            with tempfile.NamedTemporaryFile(delete=False) as tmp:

                tmp.write(uploaded.read())
                audio=tmp.name

            progress.progress(20)

            segments,_=model.transcribe(audio)

            segments=list(segments)

            st.session_state.segments=segments

            st.session_state.history.append(uploaded.name)

            progress.progress(100)

            st.success("Subtitles Generated")


# ---------- LIVE SUBTITLE PLAYER ----------

if st.session_state.segments:

    st.markdown("## 🎬 Live Subtitle Player")

    play=st.button("▶ Play with Highlight")

    container=st.empty()

    if play:

        start=time.time()

        for seg in st.session_state.segments:

            while time.time()-start < seg.start:
                time.sleep(0.05)

            html=""

            for s in st.session_state.segments:

                if s==seg:

                    html+=f"<div class='subtitleCard activeCard'>{s.text}</div>"

                else:

                    html+=f"<div class='subtitleCard'>{s.text}</div>"

            container.markdown(html,unsafe_allow_html=True)


# ---------- EXPORT ----------

if st.session_state.segments:

    output=""

    for i,s in enumerate(st.session_state.segments,1):

        output+=f"{i}\n"
        output+=f"{s.start:.2f} --> {s.end:.2f}\n"
        output+=s.text+"\n\n"


    st.download_button(
    "⬇ Download SRT",
    output,
    "subtitles.srt"
    )


# ---------- BIG BANNER ----------

st.markdown("""

<div class='banner'>

<b>Advertise Your Business Here</b>

<br><br>

<a href="#">

<img src="https://via.placeholder.com/900x120.png?text=Premium+Banner"
width="100%">

</a>

</div>

""",unsafe_allow_html=True)