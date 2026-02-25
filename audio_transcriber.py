import streamlit as st
from faster_whisper import WhisperModel
import tempfile
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit.components.v1 as components

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="Pro Subtitle Generator",
    page_icon="🎬",
    layout="wide"
)

# =========================
# SESSION STATE
# =========================

if "premium" not in st.session_state:
    st.session_state.premium=False

if "usage" not in st.session_state:
    st.session_state.usage=0

if "history" not in st.session_state:
    st.session_state.history=[]


# =========================
# PLAN SYSTEM
# =========================

FREE_LIMIT=3

if st.session_state.premium:

    allowed_models=["tiny","base","small","medium"]
    MAX_MB=500
    PLAN_NAME="Premium Plan"

else:

    allowed_models=["tiny","base"]
    MAX_MB=25
    PLAN_NAME="Free Plan"



# =========================
# CSS
# =========================

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
padding:5px 15px;
border-radius:20px;
font-size:12px;
}

.freebadge{
background:#2563eb;
padding:5px 15px;
border-radius:20px;
font-size:12px;
}

</style>
""",unsafe_allow_html=True)



# =========================
# BRANDING
# =========================

if st.session_state.premium:
    badge='<span class="badge">PREMIUM</span>'
else:
    badge='<span class="freebadge">FREE</span>'

st.markdown(f"""

<div style='text-align:center'>

<h1>🎬 Pro Subtitle Generator</h1>

<p style='color:#94a3b8'>
AI Subtitle SaaS Platform
</p>

<p style='font-size:13px;color:#64748b'>
Powered By Faster-Whisper • Streamlit Cloud
</p>

{badge}

</div>

""",unsafe_allow_html=True)



# =========================
# PAYPAL API
# =========================

# =========================
# PAYPAL API (SAFE VERSION)
# =========================

def paypal_token():

    try:

        url="https://api-m.paypal.com/v1/oauth2/token"

        r=requests.post(
            url,
            headers={
                "Accept":"application/json",
                "Accept-Language":"en_US"
            },
            data={"grant_type":"client_credentials"},
            auth=(
                st.secrets["PAYPAL_CLIENT_ID"],
                st.secrets["PAYPAL_SECRET"]
            )
        )

        data=r.json()

        if "access_token" in data:

            return data["access_token"]

        else:

            st.error("PayPal authentication failed.")
            st.write(data)

            return None

    except Exception as e:

        st.error("PayPal connection error")
        st.write(e)

        return None



def verify_payment(txn):

    token=paypal_token()

    if token is None:
        return False

    try:

        url=f"https://api-m.paypal.com/v2/checkout/orders/{txn}"

        r=requests.get(
            url,
            headers={
                "Authorization":f"Bearer {token}"
            }
        )

        if r.status_code==200:

            data=r.json()

            if data.get("status")=="COMPLETED":

                return True

    except Exception as e:

        st.write(e)

    return False

# =========================
# WHISPER MODEL
# =========================

@st.cache_resource
def load_model(size):

    return WhisperModel(size,compute_type="int8")


model_size=st.selectbox(
"Whisper Model",
allowed_models
)

model=load_model(model_size)



# =========================
# PANELS
# =========================

left,center,right=st.columns([1,3,1])



# =========================
# LEFT PANEL
# =========================

with left:

    if not st.session_state.premium:

        st.markdown("""
<div class="card">

<h4>💎 Upgrade to Premium</h4>

Unlimited Transcriptions<br>
Long Audio Support<br>
Faster AI<br><br>

</div>
""",unsafe_allow_html=True)


        st.link_button(
        "Pay ₱699 with PayPal",
        "https://paypal.me/DonnaldBariso791/699"
        )


        txn=st.text_input("Transaction ID")


        if st.button("Verify Payment"):

            if verify_payment(txn):

                st.session_state.premium=True

                st.success("Premium Activated")

            else:

                st.error("Payment not verified")


    st.markdown(f"""
<div class="card">

<h4>Usage</h4>

Used:

{st.session_state.usage} / {FREE_LIMIT}

</div>
""",unsafe_allow_html=True)


    # ADSENSE

    components.html("""

<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4128082001934890"
crossorigin="anonymous"></script>

<ins class="adsbygoogle"
style="display:block"
data-ad-client="ca-pub-4128082001934890"
data-ad-slot="7666553518"
data-ad-format="auto"
data-full-width-responsive="true"></ins>

<script>
(adsbygoogle = window.adsbygoogle || []).push({});
</script>

""",height=250)



# =========================
# CENTER PANEL
# =========================

with center:


    uploaded_file=st.file_uploader(
    "Upload Audio",
    type=["mp3","wav","m4a","mp4"]
    )


    if uploaded_file:

        size=uploaded_file.size/1024/1024

        if size>MAX_MB:

            st.error("File too large for your plan")
            st.stop()


        st.audio(uploaded_file)


        # FREE LIMIT

        if not st.session_state.premium:

            if st.session_state.usage>=FREE_LIMIT:

                st.error("Free limit reached")

                st.warning("Upgrade to continue")

                st.stop()


        if st.button("Generate Subtitles"):

            progress=st.progress(0)


            with tempfile.NamedTemporaryFile(delete=False) as tmp:

                tmp.write(uploaded_file.read())

                path=tmp.name


            progress.progress(30)


            segments,_=model.transcribe(path)

            segments=list(segments)


            progress.progress(80)


            subtitles=[

            [seg.start,seg.end,seg.text]

            for seg in segments

            ]


            progress.progress(100)


            st.session_state.usage+=1

            st.session_state.history.append(uploaded_file.name)


            st.markdown("### Subtitles")


            for row in subtitles:

                st.markdown(f"""

<div class="subtitle-card">

{row[2]}

</div>

""",unsafe_allow_html=True)



# =========================
# RIGHT PANEL
# =========================

with right:


    st.markdown("""
<div class="card">

<h4>Sponsored</h4>

Adsense Ready

</div>
""",unsafe_allow_html=True)



    if st.session_state.history:

        st.markdown("<div class='card'><h4>History</h4>",unsafe_allow_html=True)

        for h in st.session_state.history[-5:]:

            st.write(h)

        st.markdown("</div>",unsafe_allow_html=True)

