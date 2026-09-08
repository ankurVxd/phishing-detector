import joblib
from src.data_preprocessing import clean_text
from src.url_analysis import analyze_all_urls
from src.sender_analysis import analyze_sender
from src.fraud_pattern_analysis import analyze_fraud_patterns

vectorizer = joblib.load("models/tfidf_vectorizer.pkl")
model = joblib.load("models/best_model.pkl")


def get_ml_prediction(subject, body):
    text = clean_text(subject + " " + body)
    vec = vectorizer.transform([text])
    prob = model.predict_proba(vec)[0][1]
    return prob


def compute_risk(subject, body, sender_email):
    ml_prob = get_ml_prediction(subject, body)
    ml_score = ml_prob * 100

    url_results = analyze_all_urls(body)
    url_score = max([u['risk_score'] for u in url_results], default=0)

    sender_result = analyze_sender(sender_email)
    sender_score = sender_result['risk_score']

    full_text = (subject or "") + " " + (body or "")
    fraud_pattern_result = analyze_fraud_patterns(full_text)
    fraud_score = fraud_pattern_result['score']

    # Weighted combination — fraud pattern signal now included
    final_score = (
        (0.35 * ml_score) +
        (0.20 * url_score) +
        (0.15 * sender_score) +
        (0.30 * fraud_score)
    )
    final_score = round(min(final_score, 100), 2)

    # Override: if multiple strong scam-pattern categories are present together
    # (e.g. prize claim + urgency + fee request), force a high-risk verdict
    # even if the ML/URL/sender scores alone were lower.
    forced_high_risk = fraud_pattern_result['category_count'] >= 3

    if forced_high_risk:
        final_score = max(final_score, 85)

    if final_score >= 70:
        verdict = "High-Risk Phishing"
    elif final_score >= 35:
        verdict = "Suspicious"
    else:
        verdict = "Low Risk / Safe"

    reasons = []
    if ml_score > 60:
        reasons.append(f"ML model detected phishing-like language (confidence: {ml_score:.1f}%)")
    if url_score > 50:
        reasons.append("Suspicious URL patterns detected (shortener, IP address, or keywords)")
    if sender_result['domain_mismatch']:
        reasons.append("Sender domain does not match claimed organization")
    if sender_result['suspicious_pattern']:
        reasons.append("Sender address has suspicious/random pattern")

    if "prize_or_lottery_language" in fraud_pattern_result['matched_categories']:
        reasons.append("Email claims the recipient won a prize, lottery, or reward")
    if "urgency_or_pressure_tactics" in fraud_pattern_result['matched_categories']:
        reasons.append("Email uses urgency or time-pressure tactics to rush a decision")
    if "requests_personal_or_financial_info" in fraud_pattern_result['matched_categories']:
        reasons.append("Email requests sensitive personal or financial information")
    if "advance_fee_request" in fraud_pattern_result['matched_categories']:
        reasons.append("Email requests an upfront payment or processing fee — classic advance-fee scam pattern")
    if "too_good_to_be_true_claims" in fraud_pattern_result['matched_categories']:
        reasons.append("Email makes unrealistic no-effort, guaranteed-reward claims")
    if "multi_step_verification_process" in fraud_pattern_result['matched_categories']:
        reasons.append("Email instructs a multi-step 'verification' process typical of scam workflows")

    if forced_high_risk:
        reasons.insert(0, "Multiple classic scam indicators detected together (prize claim, urgency, and fee/info request) — strongly indicates fraud")

    if not reasons:
        reasons.append("No major red flags detected")

    return {
        "final_score": final_score,
        "verdict": verdict,
        "ml_score": round(ml_score, 2),
        "url_score": url_score,
        "sender_score": sender_score,
        "fraud_pattern_score": fraud_score,
        "url_details": url_results,
        "sender_details": sender_result,
        "fraud_pattern_details": fraud_pattern_result,
        "reasons": reasons
    }