import re

# ---------------------------------------------------------
# Keyword categories commonly seen in lottery/prize/advance-fee scams
# ---------------------------------------------------------

PRIZE_KEYWORDS = [
    'winner', 'you have won', 'you have been selected', 'prize', 'lottery',
    'cash prize', 'jackpot', 'reward', 'congratulations', 'lucky winner',
    'grand prize', 'sweepstake', 'giveaway', 'selected automatically',
    'winning reference', 'claim your prize'
]

URGENCY_KEYWORDS = [
    'act now', 'immediately', 'within 24 hours', 'within 60 minutes',
    'do not delay', 'expire', 'expires', 'urgent', 'action required',
    'limited time', 'before it is too late', 'time-sensitive',
    'will be cancelled', 'will be forfeited', 'reassigned', 'on hold'
]

FINANCIAL_INFO_REQUEST_KEYWORDS = [
    'bank account', 'account number', 'government id', 'government identification',
    'passport number', 'date of birth', 'ifsc', 'otp', 'pin number',
    'social security', 'aadhaar', 'card number', 'cvv', 'routing number',
    'full name, phone number', 'personal identification'
]

ADVANCE_FEE_KEYWORDS = [
    'processing fee', 'processing charge', 'refundable fee', 'handling fee',
    'courier fee', 'clearance fee', 'administrative fee', 'tax payment required',
    'advance payment', 'pay before', 'small fee', 'nominal fee', 'release your payment'
]

TOO_GOOD_TO_BE_TRUE_KEYWORDS = [
    'no registration required', 'no cost', 'free of charge', 'automatically selected',
    'randomly selected', 'no previous entry', 'guaranteed winner'
]

STEP_INSTRUCTION_PATTERN = re.compile(r'step\s*\d', re.IGNORECASE)


def _count_matches(text, keywords):
    text_lower = text.lower()
    matched = [kw for kw in keywords if kw in text_lower]
    return matched


def analyze_fraud_patterns(text):
    """
    Scans email text for classic scam-email patterns (lottery/prize scams,
    advance-fee fraud, urgency pressure, personal info harvesting).
    Returns a score (0-100) and the specific categories that matched.
    """
    if not text:
        return {"score": 0, "matched_categories": [], "matched_keywords": []}

    text = str(text)

    prize_hits = _count_matches(text, PRIZE_KEYWORDS)
    urgency_hits = _count_matches(text, URGENCY_KEYWORDS)
    financial_hits = _count_matches(text, FINANCIAL_INFO_REQUEST_KEYWORDS)
    fee_hits = _count_matches(text, ADVANCE_FEE_KEYWORDS)
    too_good_hits = _count_matches(text, TOO_GOOD_TO_BE_TRUE_KEYWORDS)
    has_step_pattern = bool(STEP_INSTRUCTION_PATTERN.search(text))

    categories_matched = []
    score = 0

    if prize_hits:
        categories_matched.append("prize_or_lottery_language")
        score += 30
    if urgency_hits:
        categories_matched.append("urgency_or_pressure_tactics")
        score += 25
    if financial_hits:
        categories_matched.append("requests_personal_or_financial_info")
        score += 30
    if fee_hits:
        categories_matched.append("advance_fee_request")
        score += 35
    if too_good_hits:
        categories_matched.append("too_good_to_be_true_claims")
        score += 15
    if has_step_pattern and (prize_hits or fee_hits):
        categories_matched.append("multi_step_verification_process")
        score += 15

    score = min(score, 100)

    all_matched_keywords = prize_hits + urgency_hits + financial_hits + fee_hits + too_good_hits

    return {
        "score": score,
        "matched_categories": categories_matched,
        "matched_keywords": all_matched_keywords,
        "category_count": len(categories_matched)
    }