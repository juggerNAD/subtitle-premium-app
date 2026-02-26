# ======================
# RIGHT PANEL
# ======================

with right:

    # Sponsored Card
    st.markdown("""
<div class="card">

<h4>🤝 Sponsored</h4>

Advertise your service here.

</div>
""",unsafe_allow_html=True)



    # Adsense Card
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

""", height=350)
