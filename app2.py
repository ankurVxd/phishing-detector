import streamlit as st
from src.risk_engine import compute_risk
from src.gmail_integration import authenticate_gmail, fetch_recent_emails

st.set_page_config(page_title="Phishing Email Detector", layout="wide")

# ---------------------------------------------------------
# CUSTOM STYLING — Silver background, black text, clean fonts
# ---------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
}

.stApp {
    background-color: #C7CBCF;
    color: #111111;
}

section[data-testid="stSidebar"] {
    background-color: #B5B9BD;
    border-right: 1px solid #999999;
}
section[data-testid="stSidebar"] * {
    color: #111111 !important;
}

.main-title {
    font-size: 34px;
    font-weight: 700;
    color: #0D0D0D;
    letter-spacing: -0.5px;
    margin-bottom: 0px;
}
.sub-title {
    font-size: 15px;
    font-weight: 400;
    color: #333333;
    margin-top: 4px;
    margin-bottom: 28px;
}

.section-header {
    font-size: 16px;
    font-weight: 600;
    color: #0D0D0D;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 24px;
    margin-bottom: 12px;
    border-bottom: 1px solid #9A9EA2;
    padding-bottom: 6px;
}

label, .stTextInput label, .stTextArea label {
    color: #111111 !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.stTextInput input, .stTextArea textarea {
    background-color: #E4E6E8 !important;
    color: #0D0D0D !important;
    border: 1px solid #9A9EA2 !important;
    border-radius: 4px !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border: 1px solid #0D0D0D !important;
    box-shadow: none !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #0D0D0D !important;
    opacity: 0.65 !important;
    font-style: italic;
}

.stButton button {
    background-color: #0D0D0D;
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    padding: 10px 28px;
    font-weight: 600;
    font-size: 14px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    transition: background-color 0.2s ease;
}
.stButton button:hover {
    background-color: #333333;
    color: #FFFFFF;
    border: none;
}

.verdict-card {
    background-color: #DCDFE2;
    border-left: 6px solid #0D0D0D;
    border-radius: 4px;
    padding: 20px 24px;
    margin-top: 10px;
    margin-bottom: 20px;
}
.verdict-label {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #444444;
    margin-bottom: 4px;
}
.verdict-value {
    font-size: 28px;
    font-weight: 700;
    color: #0D0D0D;
}

.score-card {
    border-radius: 6px;
    padding: 18px 20px;
    text-align: left;
    border: 2px solid #0D0D0D;
    box-shadow: 2px 2px 0px rgba(0,0,0,0.15);
}
.score-label {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #1A1A1A;
    margin-bottom: 8px;
}
.score-value {
    font-size: 32px;
    font-weight: 800;
    color: #0D0D0D;
}
.score-value .suffix {
    font-size: 15px;
    font-weight: 500;
    color: #333333;
}

.score-low {
    background-color: #BFE3C9;
    border-color: #1E5631;
}
.score-medium {
    background-color: #F5D98B;
    border-color: #8A5A00;
}
.score-high {
    background-color: #EFA9A9;
    border-color: #7A1A1A;
}

.stProgress > div > div {
    background-color: #0D0D0D !important;
}
.stProgress {
    background-color: #B5B9BD !important;
}

.reason-box {
    background-color: #DCDFE2;
    border: 1px solid #9A9EA2;
    border-left: 4px solid #0D0D0D;
    border-radius: 4px;
    padding: 14px 18px;
    margin-bottom: 8px;
    font-size: 14px;
    font-weight: 500;
    color: #1A1A1A;
}

.streamlit-expanderHeader {
    background-color: #B5B9BD !important;
    color: #0D0D0D !important;
    font-weight: 600 !important;
    border-radius: 4px !important;
}

.stTable, .stDataFrame {
    background-color: #E4E6E8 !important;
}

hr {
    border-top: 1px solid #9A9EA2;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    background-color: #B5B9BD;
    border-radius: 4px 4px 0px 0px;
    color: #111111;
    font-weight: 600;
    padding: 10px 20px;
}
.stTabs [aria-selected="true"] {
    background-color: #0D0D0D !important;
    color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown('<div class="main-title">Phishing Email Detection</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Analyze email content, sender authenticity, and embedded links to determine risk level.</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def score_class(score):
    if score >= 70:
        return "score-high"
    elif score >= 35:
        return "score-medium"
    else:
        return "score-low"


def render_result(result):
    verdict = result['verdict']

    st.markdown(f"""
    <div class="verdict-card">
        <div class="verdict-label">Overall Verdict</div>
        <div class="verdict-value">{verdict}</div>
    </div>
    """, unsafe_allow_html=True)

    st.progress(int(result['final_score']) / 100)
    st.markdown(
        f"<div style='text-align:right; font-size:13px; color:#333333; margin-top:-8px;'>Overall Risk Score: {result['final_score']} / 100</div>",
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        cls = score_class(result['ml_score'])
        st.markdown(f"""
        <div class="score-card {cls}">
            <div class="score-label">Text Analysis Score</div>
            <div class="score-value">{result['ml_score']}<span class="suffix"> / 100</span></div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        cls = score_class(result['url_score'])
        st.markdown(f"""
        <div class="score-card {cls}">
            <div class="score-label">URL Risk Score</div>
            <div class="score-value">{result['url_score']}<span class="suffix"> / 100</span></div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        cls = score_class(result['sender_score'])
        st.markdown(f"""
        <div class="score-card {cls}">
            <div class="score-label">Sender Risk Score</div>
            <div class="score-value">{result['sender_score']}<span class="suffix"> / 100</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">Analysis Summary</div>', unsafe_allow_html=True)
    for r in result['reasons']:
        st.markdown(f'<div class="reason-box">{r}</div>', unsafe_allow_html=True)

    with st.expander("URL Analysis Details"):
        if result['url_details']:
            st.table(result['url_details'])
        else:
            st.write("No URLs were found in this email.")

    with st.expander("Sender Analysis Details"):
        st.json(result['sender_details'])


# ---------------------------------------------------------
# TABS
# ---------------------------------------------------------
tab1, tab2 = st.tabs(["Manual Email Check", "Recent Gmail Inbox"])

# ---------------------------------------------------------
# TAB 1 — MANUAL PASTE
# ---------------------------------------------------------
with tab1:
    st.markdown('<div class="section-header">Email Details</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        sender = st.text_input("Sender Email Address", placeholder="e.g. support@paypa1-secure-verify.com")
        subject = st.text_input("Subject", placeholder="e.g. Urgent: Your account will be suspended")
    with col2:
        body = st.text_area(
            "Email Body",
            height=180,
            placeholder="e.g. Dear user, we detected unusual activity on your account. Click the link below within 24 hours to verify your identity or your account will be permanently locked. http://secure-login-update.com/verify"
        )

    analyze_clicked = st.button("Analyze Email", key="manual_analyze")

    if analyze_clicked:
        if not body.strip():
            st.warning("Please paste the email body before analyzing.")
        else:
            with st.spinner("Analyzing email..."):
                result = compute_risk(subject, body, sender)
            st.markdown('<div class="section-header">Result</div>', unsafe_allow_html=True)
            render_result(result)

# ---------------------------------------------------------
# TAB 2 — GMAIL INBOX
# ---------------------------------------------------------
with tab2:
    st.markdown('<div class="section-header">Connect Your Gmail Account</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:14px; color:#1A1A1A; margin-bottom:16px;">
    This will open a Google sign-in window in your browser. Only read access to your 
    inbox is requested — the app cannot send, delete, or modify any emails.
    </div>
    """, unsafe_allow_html=True)

    num_emails = st.slider("Number of recent emails to fetch", min_value=5, max_value=30, value=10)

    if st.button("Connect Gmail and Fetch Emails", key="gmail_connect"):
        try:
            with st.spinner("Connecting to Gmail..."):
                service = authenticate_gmail()
                emails = fetch_recent_emails(service, max_results=num_emails)
                st.session_state['gmail_emails'] = emails
            st.success(f"Fetched {len(emails)} recent emails.")
        except FileNotFoundError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Failed to connect to Gmail: {e}")

    if 'gmail_emails' in st.session_state and st.session_state['gmail_emails']:
        st.markdown('<div class="section-header">Inbox Analysis</div>', unsafe_allow_html=True)

        for idx, email in enumerate(st.session_state['gmail_emails']):
            with st.spinner("Scoring..."):
                result = compute_risk(email['subject'], email['body'], email['sender_email'])

            verdict = result['verdict']

            with st.expander(f"{email['subject']}  —  {verdict}  ({result['final_score']}/100)"):
                st.markdown(f"""
                <div style="font-size:13px; color:#333333; margin-bottom:10px;">
                <b>From:</b> {email['sender_display']}<br>
                <b>Date:</b> {email['date']}
                </div>
                """, unsafe_allow_html=True)
                render_result(result)

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
st.sidebar.markdown('<div class="section-header" style="margin-top:0;">About</div>', unsafe_allow_html=True)
st.sidebar.markdown("""
<div style="font-size:14px; line-height:1.6; color:#111111;">
This dashboard combines a machine learning text classifier, URL heuristics, 
and sender domain checks into a single, transparent risk score for any 
given email.
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div class="section-header">Risk Levels</div>', unsafe_allow_html=True)
st.sidebar.markdown("""
<div style="font-size:13px; line-height:1.8; color:#111111;">
<b>Low Risk / Safe</b> — Score below 35<br>
<b>Suspicious</b> — Score between 35 and 70<br>
<b>High-Risk Phishing</b> — Score above 70
</div>
""", unsafe_allow_html=True)