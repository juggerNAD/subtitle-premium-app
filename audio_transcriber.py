import streamlit as st
from faster_whisper import WhisperModel
import tempfile
import requests
import streamlit.components.v1 as components
import json
import random
import string
import os

st.set_page_config(
    page_title="Pro Subtitle Generator",
    page_icon="🎬",
    layout="wide"
)

FREE_LIMIT=3
USER_DB="users.json"


# ======================
# DATABASE
# ======================

def load_users():

    if os.path.exists(USER_DB):

        with open(USER_DB,"r") as f:
            return json.load(f)

    return {}

def save_users(data):

    with open(USER_DB,"w") as f:
        json.dump(data,f)

users=load_users()


# ======================
# SESSION
# ======================

if "premium" not in st.session_state:
    st.session_state.premium=False

if "usage" not in st.session_state:
    st.session_state.usage=0

if "user" not in st.session_state:
    st.session_state.user=None

if "history" not in st.session_state:
    st.session_state.history=[]


# ======================
# PLAN
# ======================

if st.session_state.premium:

    allowed_models=["tiny","base","small","medium"]
    MAX_MB=500

else:

    allowed_models=["tiny","base"]
    MAX_MB=25


# ======================
# PREMIUM CSS
# ======================

st.markdown("""
<style>

body,.stApp{
background:linear-gradient(135deg,#0f172a,#1e293b);
color:white;
}

.card{
background:#1f2937;
padding:20px;
border-radius:20px;
margin-bottom:20px;
box-shadow:0 10px 25px rgba(0,0,0,0.6);
}

.subtitle-card{
background:#0f172a;
padding:15px;
border-radius:10px;
margin-bottom:10px;
border-left:5px solid #2563eb;
}

.badge{
background:#22c55e;
padding:6px 15px;
border-radius:20px;
font-size:12px;
}

.freebadge{
background:#2563eb;
padding:6px 15px;
border-radius:20px;
font-size:12px;
}

</style>
""",unsafe_allow_html=True)


# ======================
# HEADER
# ======================

badge='<span class="badge">PREMIUM</span>' if st.session_state.premium else '<span class="freebadge">FREE</span>'

st.markdown(f"""

<div style='text-align:center'>

<h1>🎬 Pro Subtitle Generator</h1>

<p>AI Subtitle SaaS</p>

{badge}

</div>

""",unsafe_allow_html=True)


# ======================
# PAYPAL VERIFY
# ======================

def paypal_token():

    try:

        r=requests.post(
        "https://api-m.paypal.com/v1/oauth2/token",
        headers={"Accept":"application/json"},
        data={"grant_type":"client_credentials"},
        auth=(
        st.secrets["PAYPAL_CLIENT_ID"],
        st.secrets["PAYPAL_SECRET"]
        )
        )

        data=r.json()
        return data.get("access_token")

    except:
        return None


def verify_payment(txn):

    token=paypal_token()

    if not token:
        return False

    try:

        r=requests.get(
        f"https://api-m.paypal.com/v2/checkout/orders/{txn}",
        headers={"Authorization":f"Bearer {token}"}
        )

        if r.status_code==200:

            if r.json().get("status")=="COMPLETED":
                return True

    except:
        return False

    return False


# ======================
# PASSWORD GENERATOR
# ======================

def temp_password():
    return ''.join(random.choices(string.ascii_letters+string.digits,k=8))


# ======================
# SUBTITLE FORMATTERS
# ======================

def format_timestamp(seconds):
    h=int(seconds//3600)
    m=int((seconds%3600)//60)
    s=seconds%60
    return f"{h:02}:{m:02}:{s:06.3f}".replace(".",",")


def generate_srt(segments):

    lines=[]
    for i,seg in enumerate(segments,1):

        start=format_timestamp(seg.start)
        end=format_timestamp(seg.end)

        lines.append(f"{i}")
        lines.append(f"{start} --> {end}")
        lines.append(seg.text.strip())
        lines.append("")

    return "\n".join(lines)


def generate_lrc(segments):

    lines=[]
    for seg in segments:

        m=int(seg.start//60)
        s=seg.start%60

        lines.append(f"[{m:02}:{s:05.2f}]{seg.text.strip()}")

    return "\n".join(lines)


def generate_ass(segments):

    header="""[Script Info]
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, Alignment
Style: Default,Arial,20,&H00FFFFFF,2

[Events]
Format: Layer, Start, End, Style, Text
"""

    lines=[header]

    for seg in segments:

        start=format_timestamp(seg.start).replace(",",".")
        end=format_timestamp(seg.end).replace(",", ".")

        lines.append(f"Dialogue: 0,{start},{end},Default,{seg.text.strip()}")

    return "\n".join(lines)


# ======================
# PANELS
# ======================

left,center,right=st.columns([1,3,1])


# ======================
# LEFT PANEL
# ======================

with left:

    st.markdown("<div class='card'>",unsafe_allow_html=True)
    st.subheader("Account")

    if st.session_state.user:

        st.write("Logged as:",st.session_state.user)

        if st.button("Logout"):
            st.session_state.user=None
            st.session_state.premium=False
            st.rerun()

    else:

        login_email=st.text_input("Email")
        login_pass=st.text_input("Password",type="password")

        if st.button("Login"):

            if login_email in users:

                if users[login_email]["password"]==login_pass:

                    st.session_state.user=login_email
                    st.session_state.premium=users[login_email]["premium"]

                    st.success("Logged in")
                    st.rerun()

            st.error("Invalid login")

    st.markdown("</div>",unsafe_allow_html=True)


    if not st.session_state.premium:

        st.markdown("""
<div class="card">
<h4>Upgrade Premium</h4>
Unlimited Subtitles<br>
Long Audio<br>
Better Models
</div>
""",unsafe_allow_html=True)

        st.link_button(
        "Pay ₱699",
        "https://paypal.me/DonnaldBariso791/699"
        )

        email=st.text_input("Email for Premium")
        txn=st.text_input("Transaction ID")

        if st.button("Verify Payment"):

            if verify_payment(txn):

                password=temp_password()

                users[email]={
                "password":password,
                "premium":True
                }

                save_users(users)

                st.success("Account Created")
                st.write("Email:",email)
                st.write("Temp Password:",password)

            else:
                st.error("Payment not verified")


    st.markdown(f"""
<div class="card">
Usage:
{st.session_state.usage}/{FREE_LIMIT}
</div>
""",unsafe_allow_html=True)


# ======================
# CENTER
# ======================

with center:

    uploaded_file=st.file_uploader(
    "Upload Audio",
    type=["mp3","wav","m4a","mp4"]
    )

    if uploaded_file:

        size=uploaded_file.size/1024/1024

        if size>MAX_MB:
            st.error("File too large")
            st.stop()

        st.audio(uploaded_file)

        if not st.session_state.premium:
            if st.session_state.usage>=FREE_LIMIT:
                st.error("Free limit reached")
                st.stop()

        model_size=st.selectbox(
        "Whisper Model",
        allowed_models
        )

        @st.cache_resource
        def load_model(size):
            return WhisperModel(size,compute_type="int8")

        model=load_model(model_size)

        if st.button("Generate Subtitles"):

            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(uploaded_file.read())
                path=tmp.name

            segments,_=model.transcribe(path)
            segments=list(segments)

            st.session_state.usage+=1

            for seg in segments:

                st.markdown(f"""
<div class="subtitle-card">
{seg.text}
</div>
""",unsafe_allow_html=True)


            # ======================
            # DOWNLOAD SUBTITLES
            # ======================

            srt_file=generate_srt(segments)
            lrc_file=generate_lrc(segments)
            ass_file=generate_ass(segments)

            st.markdown("### Download Subtitles")

            col1,col2,col3=st.columns(3)

            with col1:
                st.download_button(
                    "Download SRT",
                    srt_file,
                    file_name="subtitles.srt"
                )

            with col2:
                st.download_button(
                    "Download LRC",
                    lrc_file,
                    file_name="subtitles.lrc"
                )

            with col3:
                st.download_button(
                    "Download ASS",
                    ass_file,
                    file_name="subtitles.ass"
                )


# ======================
# RIGHT PANEL
# ======================

with right:

    st.markdown("""
<div class="card">
<h4>🤝 Sponsored</h4>
Advertise your service here.
</div>
""",unsafe_allow_html=True)

    st.markdown("""
<div class="card">
<h4>📢 Advertisement</h4>
</div>
""",unsafe_allow_html=True)

    components.html("""
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4128082001934890"
crossorigin="anonymous"></script>

<ins class="adsbygoogle"
style="display:block;min-height:250px"
data-ad-client="ca-pub-4128082001934890"
data-ad-slot="7666553518"
data-ad-format="auto"
data-full-width-responsive="true"></ins>

<script>
(adsbygoogle = window.adsbygoogle || []).push({});
</script>
""",height=350)
