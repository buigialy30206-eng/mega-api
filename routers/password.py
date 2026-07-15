"""
Password Strength Checker API
Pure Python. Checks password strength via entropy, length, character variety.
No passwords stored — all processing in memory.
"""

import math, re
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()

@router.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "ok"}

class PasswordResult(BaseModel):
    score: int  # 0-100
    strength: str  # Very Weak / Weak / Fair / Strong / Very Strong
    length: int
    has_upper: bool
    has_lower: bool
    has_digit: bool
    has_special: bool
    suggestions: list[str] = []
    crack_time: Optional[str] = None

COMMON_PASSWORDS = {
    "password", "123456", "12345678", "qwerty", "abc123", "monkey",
    "1234567", "letmein", "trustno1", "dragon", "baseball", "iloveyou",
    "master", "sunshine", "ashley", "bailey", "shadow", "123123",
    "654321", "superman", "qazwsx", "michael", "football", "admin",
    "welcome", "password1", "111111", "000000", "admin123",
}

def check_password(password: str) -> PasswordResult:
    length = len(password)
    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r"[^a-zA-Z0-9]", password))

    # Entropy calculation
    charset = 0
    if has_lower: charset += 26
    if has_upper: charset += 26
    if has_digit: charset += 10
    if has_special: charset += 32
    entropy = length * math.log2(charset) if charset > 0 else 0

    # Common password check
    is_common = password.lower() in COMMON_PASSWORDS

    # Scoring
    score = 0
    if length >= 8: score += 15
    if length >= 12: score += 15
    if length >= 16: score += 10
    if has_upper: score += 10
    if has_lower: score += 10
    if has_digit: score += 10
    if has_special: score += 15
    if entropy > 50: score += 10
    if entropy > 75: score += 5
    if is_common: score = min(score, 10)  # Common passwords max 10

    score = min(100, max(0, score))

    if score < 20: strength = "Very Weak"
    elif score < 40: strength = "Weak"
    elif score < 60: strength = "Fair"
    elif score < 80: strength = "Strong"
    else: strength = "Very Strong"

    suggestions = []
    if length < 8: suggestions.append("Use at least 8 characters")
    if not has_upper: suggestions.append("Add uppercase letters")
    if not has_digit: suggestions.append("Add numbers")
    if not has_special: suggestions.append("Add special characters (!@#$)")
    if is_common: suggestions.append("This is a commonly used password — avoid it")

    # Crack time estimate
    combinations = charset ** length if charset > 0 else 1
    seconds = combinations / 1e9  # Assuming 1 billion guesses/sec
    if seconds < 1: ct = "Instantly"
    elif seconds < 60: ct = f"{seconds:.0f} seconds"
    elif seconds < 3600: ct = f"{seconds/60:.0f} minutes"
    elif seconds < 86400: ct = f"{seconds/3600:.0f} hours"
    elif seconds < 31536000: ct = f"{seconds/86400:.0f} days"
    else: ct = f"{seconds/31536000:.0f} years"

    return PasswordResult(
        score=score, strength=strength, length=length,
        has_upper=has_upper, has_lower=has_lower,
        has_digit=has_digit, has_special=has_special,
        suggestions=suggestions, crack_time=ct,
    )

@router.get("/")
async def root():
    return {"service": "Password Strength Checker API", "version": "1.0.0", "related": ["UUID Generator API", "Email Validator API"]}

@router.get("/check", response_model=PasswordResult)
async def check(password: str = Query(..., description="Password to analyze")):
    return check_password(password)
