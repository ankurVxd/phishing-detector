import streamlit as st
from datetime import datetime
from src.risk_engine import compute_risk
from src.gmail_integration import authenticate_gmail, fetch_recent_emails

st.set_page_config(page_title="PhishGuard | AI Email Security", layout="wide", initial_sidebar_state="expanded")

# ===========================================================
# SESSION STATE INITIALIZATION
# ===========================================================
if "history" not in st.session_state:
    st.session_state.history = []          # list of analyzed email records
if "gmail_connected" not in st.session_state:
    st.session_state.gmail_connected = False
if "gmail_emails" not in st.session_state:
    st.session_state.gmail_emails = []
if "selected_record_id" not in st.session_state:
    st.session_state.selected_record_id = None
if "nav" not in st.session_state:
    st.session_state.nav = "Dashboard"

# ===========================================================
# STYLING — Beige/cream background, navy text, glass cards
# ===========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Poppins:wght@600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(180deg, #F4EEE2 0%, #EFE7D8 100%);
    color: #10203D;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #FBF7EE;
    border-right: 1px solid #E3D9C4;
}
section[data-testid="stSidebar"] * {
    color: #10203D !important;
}
.sidebar-logo {
    font-family: 'Poppins', sans-serif;
    font-size: 24px;
    font-weight: 800;
    color: #1B2A4A;
    margin-top: 6px;
    margin-bottom: 0px;
}
.sidebar-sub {
    font-size: 12px;
    color: #5A6B8C;
    margin-bottom: 24px;
    letter-spacing: 0.3px;
}
.privacy-card {
    background: #EEF3FB;
    border: 1px solid #D6E1F5;
    border-radius: 12px;
    padding: 14px;
    font-size: 12px;
    color: #33456B;
    margin-top: 30px;
    line-height: 1.5;
}

/* Nav radio styled as sidebar list */
div[role="radiogroup"] > label {
    background: transparent;
    border-radius: 10px;
    padding: 10px 14px !important;
    margin-bottom: 4px;
    font-weight: 600;
    color: #33456B !important;
    width: 100%;
}
div[role="radiogroup"] > label:hover {
    background: #EEF3FB;
}
div[role="radiogroup"] input:checked + div {
    color: white !important;
}

/* Glass card base */
.glass-card {
    background: rgba(255,255,255,0.72);
    backdrop-filter: blur(6px);
    border-radius: 16px;
    border: 1px solid rgba(200,190,165,0.5);
    box-shadow: 0 4px 18px rgba(30,40,70,0.06);
    padding: 22px 26px;
    margin-bottom: 20px;
}

/* Welcome banner */
.banner {
    background: rgba(255,255,255,0.65);
    border-radius: 20px;
    border: 1px solid rgba(200,190,165,0.5);
    padding: 34px 38px;
    margin-bottom: 26px;
    box-shadow: 0 6px 24px rgba(30,40,70,0.07);
}
.banner-heading {
    font-family: 'Poppins', sans-serif;
    font-size: 36px;
    font-weight: 800;
    color: #14213D;
    margin-bottom: 8px;
    text-shadow: 0 0 22px rgba(47,111,237,0.18);
}
.banner-desc {
    font-size: 15px;
    color: #4C5A78;
    max-width: 640px;
    line-height: 1.6;
}

/* Stat cards */
.stat-card {
    border-radius: 16px;
    padding: 20px;
    background: rgba(255,255,255,0.75);
    border: 1px solid rgba(200,190,165,0.5);
    box-shadow: 0 4px 14px rgba(30,40,70,0.06);
}
.stat-label {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: #5A6B8C;
    margin-bottom: 6px;
}
.stat-value {
    font-size: 30px;
    font-weight: 800;
    font-family: 'Poppins', sans-serif;
}
.stat-blue   { color: #2F6FED; text-shadow: 0 0 14px rgba(47,111,237,0.25); }
.stat-green  { color: #1E8A5F; text-shadow: 0 0 14px rgba(30,138,95,0.25); }
.stat-red    { color: #D64545; text-shadow: 0 0 14px rgba(214,69,69,0.25); }
.stat-amber  { color: #C7861A; text-shadow: 0 0 14px rgba(199,134,26,0.25); }

/* Section heading */
.section-title {
    font-family: 'Poppins', sans-serif;
    font-size: 20px;
    font-weight: 700;
    color: #14213D;
    margin-bottom: 4px;
}
.section-subtitle {
    font-size: 13px;
    color: #5A6B8C;
    margin-bottom: 18px;
}

/* Inputs */
.stTextInput input, .stTextArea textarea {
    background-color: #FFFFFF !important;
    color: #10203D !important;
    border: 1px solid #D9CFB8 !important;
    border-radius: 10px !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: #10203D !important;
    opacity: 0.55 !important;
}
label { color: #14213D !important; font-weight: 600 !important; font-size: 13px !important; }

/* Buttons */
.stButton button {
    background: linear-gradient(135deg, #2F6FED, #1B4FD1);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 26px;
    font-weight: 700;
    box-shadow: 0 4px 14px rgba(47,111,237,0.35);
}
.stButton button:hover {
    background: linear-gradient(135deg, #1B4FD1, #123a9c);
    color: white;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.3px;
}
.badge-safe { background: #E1F6EB; color: #1E8A5F; border: 1px solid #B7E7CC; }
.badge-suspicious { background: #FBF0DC; color: #C7861A; border: 1px solid #F0DBA5; }
.badge-phishing { background: #FBE4E4; color: #D64545; border: 1px solid #F3BDBD; }

/* Table row card */
.table-row {
    background: rgba(255,255,255,0.75);
    border: 1px solid rgba(200,190,165,0.5);
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 8px;
}

/* Risk bar */
.stProgress > div > div { background-color: #2F6FED !important; }

hr { border-top: 1px solid #E3D9C4; }
</style>
""", unsafe_allow_html=True)

# ===========================================================
# HELPERS
# ===========================================================
def verdict_to_badge(verdict):
    if "Phishing" in verdict:
        return '<span class="badge badge-phishing">Phishing</span>'
    elif "Suspicious" in verdict:
        return '<span class="badge badge-suspicious">Suspicious</span>'
    else:
        return '<span class="badge badge-safe">Safe</span>'


def log_record(subject, sender, body, result, source):
    record = {
        "id": len(st.session_state.history) + 1,
        "subject": subject if subject else "(No subject)",
        "sender": sender if sender else "Unknown",
        "body": body,
        "result": result,
        "source": source,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    st.session_state.history.append(record)
    return record


def render_stats():
    total = len(st.session_state.history)
    phishing_count = sum(1 for r in st.session_state.history if "Phishing" in r["result"]["verdict"])
    safe_count = sum(1 for r in st.session_state.history if "Safe" in r["result"]["verdict"])
    last_time = st.session_state.history[-1]["timestamp"] if total > 0 else "—"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Total Emails Analyzed</div>
            <div class="stat-value stat-blue">{total}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Phishing Detected</div>
            <div class="stat-value stat-red">{phishing_count}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Safe Emails</div>
            <div class="stat-value stat-green">{safe_count}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Last Analysis</div>
            <div class="stat-value stat-amber" style="font-size:18px;">{last_time}</div>
        </div>""", unsafe_allow_html=True)


def render_detail_view(record):
    result = record["result"]
    st.markdown(f'<div class="section-title">Detailed Security Analysis</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="glass-card">
        <b>Sender:</b> {record['sender']}<br>
        <b>Subject:</b> {record['subject']}<br>
        <b>Analyzed:</b> {record['timestamp']}<br><br>
        <b>Verdict:</b> {verdict_to_badge(result['verdict'])}
    </div>
    """, unsafe_allow_html=True)

    st.progress(int(result['final_score']) / 100)
    st.markdown(f"<div style='font-size:13px; color:#4C5A78;'>Overall Risk Score: <b>{result['final_score']} / 100</b></div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="stat-card"><div class="stat-label">Text Analysis</div><div class="stat-value stat-blue">{result["ml_score"]}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-card"><div class="stat-label">URL Risk</div><div class="stat-value stat-amber">{result["url_score"]}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-card"><div class="stat-label">Sender Risk</div><div class="stat-value stat-red">{result["sender_score"]}</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="stat-card"><div class="stat-label">Scam Pattern</div><div class="stat-value stat-green">{result.get("fraud_pattern_score", 0)}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="margin-top:20px;">Why This Result</div>', unsafe_allow_html=True)
    for r in result['reasons']:
        st.markdown(f'<div class="table-row">{r}</div>', unsafe_allow_html=True)

    with st.expander("Full Email Body"):
        st.write(record['body'])

    with st.expander("URL Details"):
        if result['url_details']:
            st.table(result['url_details'])
        else:
            st.write("No URLs found in this email.")

    with st.expander("Sender Details"):
        st.json(result['sender_details'])

    if st.button("Back to List"):
        st.session_state.selected_record_id = None
        st.rerun()


def render_results_table(records, key_prefix, newest_first=True):
    if not records:
        st.info("No emails analyzed yet.")
        return

    # `records` from st.session_state.history grows oldest -> newest as you analyze,
    # so reverse it to show newest first. Gmail results already arrive newest-first
    # from the Gmail API, so they should NOT be reversed again.
    display_records = list(reversed(records)) if newest_first else records

    for r in display_records:
        badge = verdict_to_badge(r["result"]["verdict"])
        col1, col2, col3, col4, col5, col6 = st.columns([2.5, 1.5, 1.3, 1.3, 1, 1])
        with col1:
            st.markdown(f"**{r['subject']}**<br><span style='font-size:12px;color:#5A6B8C;'>{r['sender']}</span>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<span style='font-size:12px;color:#5A6B8C;'>{r['timestamp']}</span>", unsafe_allow_html=True)
        with col3:
            st.markdown(badge, unsafe_allow_html=True)
        with col4:
            st.markdown(f"<b>{r['result']['final_score']}</b> / 100", unsafe_allow_html=True)
        with col5:
            st.markdown(f"<span style='font-size:12px;'>{r['source']}</span>", unsafe_allow_html=True)
        with col6:
            if st.button("View", key=f"{key_prefix}_{r['id']}"):
                st.session_state.selected_record_id = r["id"]
                st.rerun()
        st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)


def get_record_by_id(rid):
    for r in st.session_state.history:
        if r["id"] == rid:
            return r
    return None

# ===========================================================
# SIDEBAR NAVIGATION
# ===========================================================
with st.sidebar:
    st.markdown('<div class="sidebar-logo">PhishGuard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">AI-Powered Email Protection</div>', unsafe_allow_html=True)

    nav = st.radio(
        "Navigation",
        ["Dashboard", "Manual Check", "Gmail Inbox", "Analysis History", "About"],
        index=["Dashboard", "Manual Check", "Gmail Inbox", "Analysis History", "About"].index(st.session_state.nav),
        label_visibility="collapsed"
    )
    st.session_state.nav = nav

    st.markdown("""
    <div class="privacy-card">
        <b>Privacy Notice</b><br>
        Email data is analyzed locally in this session only. 
        Gmail access is read-only and no messages are sent, 
        modified, or stored permanently.
    </div>
    """, unsafe_allow_html=True)

# ===========================================================
# PAGE: DASHBOARD
# ===========================================================
if st.session_state.nav == "Dashboard" and st.session_state.selected_record_id is None:
    st.markdown("""
    <div class="banner">
        <div class="banner-heading">Smarter Email Security</div>
        <div class="banner-desc">
            PhishGuard uses artificial intelligence and cybersecurity heuristics to detect phishing 
            emails, analyze suspicious links and sender behavior, and help you stay protected from 
            evolving cyber threats — all explained transparently, not as a black box.
        </div>
    </div>
    """, unsafe_allow_html=True)

    render_stats()

    st.markdown('<div class="section-title" style="margin-top:26px;">Recent Email Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">A quick overview of the latest scanned emails.</div>', unsafe_allow_html=True)

    recent = st.session_state.history[-5:]
    render_results_table(recent, key_prefix="dash")

    if len(st.session_state.history) > 5:
        if st.button("View All \u2192 Analysis History"):
            st.session_state.nav = "Analysis History"
            st.rerun()

# ===========================================================
# PAGE: MANUAL CHECK
# ===========================================================
elif st.session_state.nav == "Manual Check" and st.session_state.selected_record_id is None:
    st.markdown('<div class="section-title">Manual Phishing Check</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Paste any email\'s details below to run it through the AI risk engine.</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        sender = st.text_input("Sender Email Address", placeholder="e.g. support@paypa1-secure-verify.com")
        subject = st.text_input("Subject", placeholder="e.g. Urgent: Verify your account")
    with col2:
        body = st.text_area(
            "Email Body", height=180,
            placeholder="e.g. Dear user, we detected unusual activity on your account. Click the link below within 24 hours to verify your identity. http://secure-login-update.com/verify"
        )
    analyze_clicked = st.button("Analyze Email")
    st.markdown('</div>', unsafe_allow_html=True)

    if analyze_clicked:
        if not body.strip():
            st.warning("Please paste the email body before analyzing.")
        else:
            with st.spinner("Analyzing email..."):
                result = compute_risk(subject, body, sender)
            record = log_record(subject, sender, body, result, source="Manual")
            st.session_state.selected_record_id = record["id"]
            st.rerun()

# ===========================================================
# PAGE: GMAIL INBOX
# ===========================================================
elif st.session_state.nav == "Gmail Inbox" and st.session_state.selected_record_id is None:
    st.markdown('<div class="section-title">Gmail Inbox Integration</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Securely connect your Gmail account to automatically scan recent emails.</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    status_col1, status_col2 = st.columns([3, 1])
    with status_col1:
        status_text = "Connected" if st.session_state.gmail_connected else "Not Connected"
        status_color = "#1E8A5F" if st.session_state.gmail_connected else "#D64545"
        st.markdown(f"<b>Connection Status:</b> <span style='color:{status_color}; font-weight:700;'>{status_text}</span>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:13px; color:#5A6B8C; margin-top:6px;'>Only read-only access is requested — PhishGuard cannot send, delete, or modify your emails.</div>", unsafe_allow_html=True)

    num_emails = st.slider("Number of recent emails to scan", min_value=5, max_value=30, value=10)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Connect with Gmail"):
            try:
                with st.spinner("Connecting to Gmail..."):
                    authenticate_gmail()
                st.session_state.gmail_connected = True
                st.success("Gmail connected successfully.")
            except FileNotFoundError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Connection failed: {e}")
    with c2:
        if st.session_state.gmail_connected:
            if st.button("Scan Inbox"):
                with st.spinner("Fetching and analyzing emails..."):
                    service = authenticate_gmail()
                    emails = fetch_recent_emails(service, max_results=num_emails)
                    for email in emails:
                        result = compute_risk(email["subject"], email["body"], email["sender_email"])
                        log_record(email["subject"], email["sender_display"], email["body"], result, source="Gmail")
                st.success(f"Scanned {len(emails)} emails.")
    with c3:
        gmail_count = len([r for r in st.session_state.history if r["source"] == "Gmail"])
        if gmail_count > 0:
            if st.button("Clear Scan History"):
                st.session_state.history = [r for r in st.session_state.history if r["source"] != "Gmail"]
                st.session_state.selected_record_id = None
                st.success("Gmail scan history cleared.")
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    gmail_records = [r for r in st.session_state.history if r["source"] == "Gmail"]
    if gmail_records:
        scanned = len(gmail_records)
        phishing = sum(1 for r in gmail_records if "Phishing" in r["result"]["verdict"])

        s1, s2 = st.columns(2)
        s1.markdown(f'<div class="stat-card"><div class="stat-label">Emails Scanned</div><div class="stat-value stat-blue">{scanned}</div></div>', unsafe_allow_html=True)
        s2.markdown(f'<div class="stat-card"><div class="stat-label">Phishing Detected</div><div class="stat-value stat-red">{phishing}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title" style="margin-top:22px;">Inbox Scan Results</div>', unsafe_allow_html=True)
        render_results_table(gmail_records, key_prefix="gmail", newest_first=False)

# ===========================================================
# PAGE: ANALYSIS HISTORY
# ===========================================================
elif st.session_state.nav == "Analysis History" and st.session_state.selected_record_id is None:
    st.markdown('<div class="section-title">Analysis History</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Complete record of every email analyzed this session.</div>', unsafe_allow_html=True)
    render_results_table(st.session_state.history, key_prefix="history")

# ===========================================================
# PAGE: ABOUT
# ===========================================================
elif st.session_state.nav == "About" and st.session_state.selected_record_id is None:
    st.markdown('<div class="section-title">About PhishGuard</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="glass-card">
        PhishGuard combines a machine learning text classifier (TF-IDF + Logistic Regression / 
        Naive Bayes), URL heuristic analysis, sender domain verification, and rule-based scam 
        pattern detection into a single, transparent phishing risk score.<br><br>
        <b>Risk Levels</b><br>
        <span class="badge badge-safe">Safe</span> — Score below 35<br><br>
        <span class="badge badge-suspicious">Suspicious</span> — Score between 35 and 70<br><br>
        <span class="badge badge-phishing">Phishing</span> — Score above 70
    </div>
    """, unsafe_allow_html=True)

# ===========================================================
# DETAIL VIEW (overrides whichever page is active)
# ===========================================================
if st.session_state.selected_record_id is not None:
    record = get_record_by_id(st.session_state.selected_record_id)
    if record:
        render_detail_view(record)
    else:
        st.session_state.selected_record_id = None

# ===========================================================
# FOOTER
# ===========================================================
st.markdown("""
<hr>
<div style="text-align:center; font-size:12px; color:#8A93A8; padding: 10px 0 20px 0;">
    <b>PhishGuard</b> — AI-Powered Phishing Email Detection System<br>
    Built with Python and Streamlit
</div>
""", unsafe_allow_html=True)