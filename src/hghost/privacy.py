from __future__ import annotations

import re


_PRIVATE_KEY_RE = re.compile(
    r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----", re.IGNORECASE
)
_MYSQL_PASSWORD_HASH_RE = re.compile(r"(?<![0-9A-Fa-f])\*[0-9A-Fa-f]{40}(?![0-9A-Fa-f])")
_PASSWORD_HASH_RE = re.compile(
    r"(?:\$2[aby]\$[./A-Za-z0-9]{53}|\$argon2(?:id|i|d)\$[^\s|]{20,}|\$[156]\$[^\s|]{20,})"
)
_PASSWORD_FIELD_RE = re.compile(r"(?i)(?:\|\s*password\s*\||\bpassword(?:_hash)?\b)")
_KNOWN_TOKEN_RE = re.compile(
    r"(?:AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|"
    r"github_pat_[A-Za-z0-9_]{50,}|xox[baprs]-[A-Za-z0-9-]{20,}|"
    r"sk-(?:proj-)?[A-Za-z0-9_-]{24,})"
)
_SECRET_ASSIGNMENT_RE = re.compile(
    r"(?im)^\s*(?:api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|"
    r"password|passwd)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=:@-]{16,}"
)
_CREDENTIAL_URI_RE = re.compile(
    r"(?i)\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis)://"
    r"[^\s/:@]{1,128}:[^\s/@]{8,128}@"
)


def credential_indicator_count(text: str) -> int:
    """Count high-confidence credential material without retaining its values."""
    indicators = len(_PRIVATE_KEY_RE.findall(text))
    indicators += len(_KNOWN_TOKEN_RE.findall(text))
    indicators += len(_SECRET_ASSIGNMENT_RE.findall(text))
    indicators += len(_CREDENTIAL_URI_RE.findall(text))
    password_hashes = len(_MYSQL_PASSWORD_HASH_RE.findall(text)) + len(
        _PASSWORD_HASH_RE.findall(text)
    )
    # A password-labelled table containing several hashes is characteristic of
    # a credential dump. A lone hash in security writing is not enough.
    if password_hashes >= 3 and _PASSWORD_FIELD_RE.search(text):
        indicators += 1
    return indicators


def credential_dump_indicator_count(text: str) -> int:
    """Identify a credential *dataset*, not an incidental secret-like string.

    A book, incident report, or security manual can legitimately quote one
    token or key.  That remains useful corpus text and should be reviewed, not
    automatically discarded.  A password-labelled table containing many
    hashes is qualitatively different and is safe to exclude automatically.
    """

    password_hashes = len(_MYSQL_PASSWORD_HASH_RE.findall(text)) + len(
        _PASSWORD_HASH_RE.findall(text)
    )
    return int(password_hashes >= 3 and _PASSWORD_FIELD_RE.search(text) is not None)
