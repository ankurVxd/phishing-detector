from src.risk_engine import compute_risk

subject = "IMPORTANT NOTICE — ACTION REQUIRED: You Have Won ₹50 CRORE"
body = """Dear Valued Customer,

IMPORTANT NOTICE — ACTION REQUIRED
Our automated international rewards system has selected your email address as the winner of a ₹50 CRORE CASH PRIZE, a luxury apartment, a Mercedes-Benz vehicle, and an iPhone 17 Pro Max.
You were selected automatically and no previous registration was required.
Your winning reference is GRW-IND-778291.
YOUR PRIZE IS CURRENTLY ON HOLD.
To prevent cancellation, you must complete the verification process within 60 minutes.
STEP 1 — VERIFY YOUR WINNING ACCOUNT
http://global-reward-verification.example/secure-login
STEP 2 — CONFIRM YOUR PRIZE
http://50crore-prize.example/claim-now
STEP 3 — RELEASE YOUR PAYMENT
http://international-reward.example/payment-verification
During verification, you may be asked to provide your full name, phone number, date of birth, bank account information, and government identification details.
A refundable ₹999 processing charge is required before the prize can be released.
DO NOT DELAY.
If verification is not completed within the specified period, your prize will be cancelled and permanently reassigned.
Congratulations on your incredible fortune!
International Rewards & Prize Verification Department"""

sender = "rewards@global-prize-dept.example"

result = compute_risk(subject, body, sender)

print("Verdict:", result['verdict'])
print("Final Score:", result['final_score'])
print("Fraud Pattern Score:", result['fraud_pattern_score'])
print("Matched Categories:", result['fraud_pattern_details']['matched_categories'])
print("\nReasons:")
for r in result['reasons']:
    print(" -", r)