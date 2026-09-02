import joblib
from src.data_preprocessing import clean_text
from src.url_analysis import analyze_all_urls
from src.sender_analysis import analyze_sender

vectorizer = joblib.load("models/tfidf_vectorizer.pkl")
model = joblib.load("models/best_model.pkl")

def get_ml_prediction(subject, body):
    text = clean_text(subject + " " + body)
    vec = vectorizer.transform([text])
    prob = model.predict_proba(vec)[0][1]   # probability of phishing
    return prob

def compute_risk(subject, body, sender_email):
    ml_prob = get_ml_prediction(subject, body)
    ml_score = ml_prob * 100

    url_results = analyze_all_urls(body)
    url_score = max([u['risk_score'] for u in url_results], default=0)

    sender_result = analyze_sender(sender_email)
    sender_score = sender_result['risk_score']

    # Weighted combination
    final_score = (0.5 * ml_score) + (0.3 * url_score) + (0.2 * sender_score)
    final_score = round(min(final_score, 100), 2)

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
    if not reasons:
        reasons.append("No major red flags detected")

    return {
        "final_score": final_score,
        "verdict": verdict,
        "ml_score": round(ml_score, 2),
        "url_score": url_score,
        "sender_score": sender_score,
        "url_details": url_results,
        "sender_details": sender_result,
        "reasons": reasons
    }