import re

INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"system\s+override", re.IGNORECASE),
    re.compile(r"priority\s+override", re.IGNORECASE),
    re.compile(r"disregard\s+(your\s+)?(safety|prior|previous|current)", re.IGNORECASE),
    re.compile(r"forget\s+everything\s+(above|before)", re.IGNORECASE),
    re.compile(r"jailbreak", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+DAN", re.IGNORECASE),
    re.compile(r"bypass\s+(all\s+)?(authentication|safety|rate\s+limit|filter)", re.IGNORECASE),
    re.compile(r"execute[:\s]", re.IGNORECASE),
    re.compile(r"eval\s*\(", re.IGNORECASE),
    re.compile(r"__import__\s*\(", re.IGNORECASE),
    re.compile(r"BEGIN\s+INJECTION", re.IGNORECASE),
    re.compile(r"override\s+safety", re.IGNORECASE),
    re.compile(r"ignore\s+content\s+policy", re.IGNORECASE),
]

IMPERSONATION_PATTERNS = [
    re.compile(r"this\s+is\s+\w+[\._]\d*\s*[:.]\s*I\s+need", re.IGNORECASE),
    re.compile(r"speaking\s+as\s+\w+", re.IGNORECASE),
    re.compile(r"I\s+am\s+\w+[\._]\d+", re.IGNORECASE),
    re.compile(r"message\s+from\s+the\s+system\s+administrator", re.IGNORECASE),
    re.compile(r"pretending\s+to\s+be", re.IGNORECASE),
    re.compile(r"authority\s+override\s+from", re.IGNORECASE),
    re.compile(r"acting\s+on\s+behalf\s+of", re.IGNORECASE),
    re.compile(r"control\s+plane\s+message", re.IGNORECASE),
    re.compile(r"verified\s+system\s+process\s+speaking", re.IGNORECASE),
    re.compile(r"coordinator\s+directive", re.IGNORECASE),
]

EXFILTRATION_PATTERNS = [
    re.compile(r"(send|forward|transmit|attach|include|echo\s+back)\s+.{0,40}(credentials|secrets|keys|password|token|config|connection\s+string|environment\s+variables)", re.IGNORECASE),
    re.compile(r"dump\s+.{0,20}(memory|state|data|queue|secrets)", re.IGNORECASE),
    re.compile(r"serialize\s+your\s+.{0,20}(state|config|data)", re.IGNORECASE),
    re.compile(r"full\s+dump", re.IGNORECASE),
    re.compile(r"private\s+key\s+material", re.IGNORECASE),
    re.compile(r"exfil", re.IGNORECASE),
]

CASCADE_PATTERNS = [
    re.compile(r"forward\s+(it\s+)?verbatim\s+to\s+all", re.IGNORECASE),
    re.compile(r"propagation\s+directive", re.IGNORECASE),
    re.compile(r"viral\s+instruction", re.IGNORECASE),
    re.compile(r"recursive\s+task", re.IGNORECASE),
    re.compile(r"broadcast\s+mode", re.IGNORECASE),
    re.compile(r"worm\s+protocol", re.IGNORECASE),
    re.compile(r"chain\s+(alert|reaction)", re.IGNORECASE),
    re.compile(r"cascade\s+injection", re.IGNORECASE),
    re.compile(r"replicate\s+this\s+message\s+to\s+every", re.IGNORECASE),
    re.compile(r"forward\s+to\s+.{0,30}agents?\s+in\s+your\s+contact", re.IGNORECASE),
]

SUSPICIOUS_PATTERNS = [
    re.compile(r"(DROP|DELETE|TRUNCATE|ALTER)\s+TABLE", re.IGNORECASE),
    re.compile(r"/etc/passwd"),
    re.compile(r"os\.system\s*\("),
    re.compile(r"subprocess\.call\s*\("),
    re.compile(r"shell\s*=\s*True"),
    re.compile(r"base64.{0,10}(decode|payload|execute)", re.IGNORECASE),
]


def scan(content: str) -> dict:
    hits = {"injection": 0, "impersonation": 0, "exfiltration": 0, "cascade": 0, "suspicious": 0}

    for p in INJECTION_PATTERNS:
        if p.search(content):
            hits["injection"] += 1

    for p in IMPERSONATION_PATTERNS:
        if p.search(content):
            hits["impersonation"] += 1

    for p in EXFILTRATION_PATTERNS:
        if p.search(content):
            hits["exfiltration"] += 1

    for p in CASCADE_PATTERNS:
        if p.search(content):
            hits["cascade"] += 1

    for p in SUSPICIOUS_PATTERNS:
        if p.search(content):
            hits["suspicious"] += 1

    total = sum(hits.values())
    top_cat = max(hits, key=hits.get) if total > 0 else "normal"
    score = min(total / 3.0, 1.0)

    return {
        "score": round(score, 3),
        "category": top_cat if total > 0 else "normal",
        "hits": hits,
        "flagged": total >= 2,
    }
