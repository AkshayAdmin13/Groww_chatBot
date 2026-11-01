import re

ADVICE_PATTERNS = [
    r'\b(should i|should i buy|should i sell|should i invest|recommend|recommendation|which is better|better to buy|good to buy|worth buying|hold or sell)\b',
    r'\b(buy now|sell now|good time to buy|sip amount recommend)\b'
]

PII_PATTERNS = [
    r'\b\d{10}\b',  # phone
    r'\b[A-Z]{5}\d{4}[A-Z]\b',  # PAN
    r'\b\d{4}\s?\d{4}\s?\d{4}\b',  # aadhaar-like
    r'\b[\w\.-]+@[\w\.-]+\.\w+\b',  # email
]

PERF_PATTERNS = [
    r'\b(returns?|return)\b.*\b(last|1 year|3 year|5 year|ytd|since inception)\b',
    r'\b(compare|comparison)\b.*\b(fund|scheme)\b'
]


def check_guardrails(query):
    q = query.lower()
    for p in PII_PATTERNS:
        if re.search(p, query, re.IGNORECASE):
            return False, "I cannot process queries containing personal information (PII). This assistant is facts-only and does not store any personal data. Please ask a factual question about the schemes."
    for p in ADVICE_PATTERNS:
        if re.search(p, q):
            return False, "This is a facts-only assistant. I cannot provide investment advice or recommendations. For general information, you may refer to SEBI/AMFI educational resources. Please ask a factual question (expense ratio, exit load, lock-in, SIP min, riskometer, benchmark)."
    for p in PERF_PATTERNS:
        if re.search(p, q):
            return False, "I cannot compute or compare returns/performance. For performance data, please refer to the official factsheet of the scheme on Groww/AMC website. Please ask for other factual details like expense ratio, exit load, minimum SIP, lock-in, riskometer, or benchmark."
    return True, None
