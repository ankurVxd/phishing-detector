import re
import tldextract

TRUSTED_DOMAINS = ['gmail.com', 'outlook.com', 'yahoo.com', 'company.com']

FREE_EMAIL_PROVIDERS = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']

def analyze_sender(sender_email, claimed_org=None):
    result = {
        "sender": sender_email,
        "domain": None,
        "is_free_provider": False,
        "domain_mismatch": False,
        "suspicious_pattern": False,
        "risk_score": 0
    }

    if not sender_email or '@' not in sender_email:
        result["suspicious_pattern"] = True
        result["risk_score"] = 40
        return result

    domain = sender_email.split('@')[-1].lower()
    result["domain"] = domain
    ext = tldextract.extract(domain)

    result["is_free_provider"] = domain in FREE_EMAIL_PROVIDERS

    # numeric/random-looking domain check
    if re.search(r'\d{3,}', ext.domain):
        result["suspicious_pattern"] = True

    # lookalike domain check (e.g., paypa1.com, micros0ft.com)
    lookalike_targets = ['paypal', 'microsoft', 'google', 'apple', 'amazon', 'bank']
    for target in lookalike_targets:
        if target in ext.domain and ext.domain != target:
            result["domain_mismatch"] = True

    # claimed organization vs actual domain mismatch
    if claimed_org and claimed_org.lower() not in domain:
        result["domain_mismatch"] = True

    score = 0
    if result["suspicious_pattern"]: score += 30
    if result["domain_mismatch"]: score += 40
    if result["is_free_provider"] and claimed_org: score += 15

    result["risk_score"] = min(score, 100)
    return result