import re
import tldextract
from urllib.parse import urlparse

SUSPICIOUS_KEYWORDS = [
    'login', 'verify', 'secure', 'account', 'update', 'confirm',
    'banking', 'signin', 'password', 'suspend', 'urgent'
]

SHORTENERS = ['bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'ow.ly', 'is.gd']

def extract_urls(text):
    url_pattern = re.compile(r'https?://[^\s<>"\']+')
    return url_pattern.findall(text or "")

def analyze_url(url):
    result = {
        "url": url,
        "length": len(url),
        "has_ip": False,
        "num_subdomains": 0,
        "is_shortener": False,
        "has_suspicious_keyword": False,
        "has_at_symbol": '@' in url,
        "has_https": url.startswith('https'),
        "special_char_count": len(re.findall(r'[-_%=?&]', url)),
        "risk_score": 0
    }

    parsed = urlparse(url)
    ext = tldextract.extract(url)

    # IP address in domain check
    ip_pattern = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
    if ip_pattern.search(parsed.netloc):
        result["has_ip"] = True

    result["num_subdomains"] = len(ext.subdomain.split('.')) if ext.subdomain else 0
    result["is_shortener"] = any(s in url for s in SHORTENERS)
    result["has_suspicious_keyword"] = any(k in url.lower() for k in SUSPICIOUS_KEYWORDS)

    # scoring heuristic
    score = 0
    if result["length"] > 75: score += 15
    if result["has_ip"]: score += 30
    if result["num_subdomains"] >= 3: score += 20
    if result["is_shortener"]: score += 20
    if result["has_suspicious_keyword"]: score += 20
    if not result["has_https"]: score += 10
    if result["has_at_symbol"]: score += 25
    if result["special_char_count"] > 5: score += 10

    result["risk_score"] = min(score, 100)
    return result

def analyze_all_urls(text):
    urls = extract_urls(text)
    return [analyze_url(u) for u in urls]