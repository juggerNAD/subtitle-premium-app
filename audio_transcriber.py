import streamlit as st
from faster_whisper import WhisperModel
import tempfile
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
    PLAN_NAME="Premium"

else:

    allowed_models=["tiny","base"]
    MAX_MB=25
    PLAN_NAME="Free"

# =========================
# PREMIUM CSS
# =========================

st.markdown("""
<style>

body,.stApp{
background:linear-gradient(135deg,#0f172a,#1e293b);
color:white;
}

.card{
background:#1f2937;
padding:22px;
border-radius:20px;
margin-bottom:20px;
box-shadow:0 10px 25px rgba(0,0,0,0.6);
}

.subtitle-card{
background:#0f172a;
padding:15px;
border-radius:12px;
margin-bottom:10px;
border-left:5px solid #2563eb;
}

.badge{
background:#22c55e;
padding:6px 18px;
border-radius:20px;
font-size:13px;
}

.freebadge{
background:#2563eb;
padding:6px 18px;
border-radius:20px;
font-size:13px;
}

.stButton button{
border-radius:40px;
padding:14px 35px;
font-size:18px;
background:linear-gradient(90deg,#2563eb,#1d4ed8);
color:white;
border:none;
}

</style>
""",unsafe_allow_html=True)

# =========================
# HEADER
# =========================

badge = '<span class="badge">PREMIUM</span>' if st.session_state.premium else '<span class="freebadge">FREE</span>'

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
# PAYPAL SAFE VERIFY
# =========================

def paypal_token():

    try:

        r=requests.post(
        "https://api-m.paypal.com/v1/oauth2/token",
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

        return None

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

✔ Unlimited Subtitles<br>
✔ Long Audio Support<br>
✔ Faster Models<br>
✔ Priority Processing<br><br>

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

""",height=300)

# =========================
# CENTER PANEL
# =========================

with center:

    # Upload Card

    st.markdown('<div class="card">',unsafe_allow_html=True)

    uploaded_file=st.file_uploader(
    "🎵 Upload Audio",
    type=["mp3","wav","m4a","mp4"]
    )

    st.markdown('</div>',unsafe_allow_html=True)

    if uploaded_file:

        size=uploaded_file.size/1024/1024

        if size>MAX_MB:

            st.error("File too large for your plan")
            st.stop()

        # Preview Card

        st.markdown('<div class="card">',unsafe_allow_html=True)

        st.audio(uploaded_file)

        st.markdown('</div>',unsafe_allow_html=True)

        # Settings Card

        st.markdown('<div class="card">',unsafe_allow_html=True)

        col1,col2=st.columns(2)

        with col1:

            model_size=st.selectbox(
            "Whisper Model",
            allowed_models
            )

        with col2:

            format_choice=st.selectbox(
            "Subtitle Format",
            ["srt","lrc","ass"]
            )

        st.markdown('</div>',unsafe_allow_html=True)

        # FREE LIMIT CHECK

        if not st.session_state.premium:

            if st.session_state.usage>=FREE_LIMIT:

                st.error("Free limit reached")
                st.warning("Upgrade to continue")
                st.stop()

        # LOAD MODEL

        @st.cache_resource
        def load_model(size):

            return WhisperModel(size,compute_type="int8")

        model=load_model(model_size)

        # GENERATE

        if st.button("Generate Subtitles"):

            progress=st.progress(0)

            with tempfile.NamedTemporaryFile(delete=False) as tmp:

                tmp.write(uploaded_file.read())
                path=tmp.name

            progress.progress(40)

            segments,_=model.transcribe(path)

            segments=list(segments)

            progress.progress(100)

            st.session_state.usage+=1
            st.session_state.history.append(uploaded_file.name)

            st.markdown("### Subtitles")

            for seg in segments:

                st.markdown(f"""

<div class="subtitle-card">

{seg.text}

</div>

""",unsafe_allow_html=True)

# =========================
# RIGHT PANEL
# =========================

with right:

    st.markdown("""
<div class="card">

<h4>Sponsored</h4>

Your Ad Here

</div>
""",unsafe_allow_html=True)

    if st.session_state.history:

        st.markdown("<div class='card'><h4>History</h4>",unsafe_allow_html=True)

        for h in st.session_state.history[-5:]:

            st.write(h)

        st.markdown("</div>",unsafe_allow_html=True)
