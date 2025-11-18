"""
PII Detector Tool - Detect and flag sensitive personal information
"""

import re
from typing import Dict, Any, List


def detect_pii(text: str) -> Dict[str, Any]:
    """
    Detect PII (Personally Identifiable Information) in text.

    Args:
        text: Text to check for PII

    Returns:
        PII detection results with findings and recommendations
    """
    findings: List[Dict[str, str]] = []

    # Check for SSN (US Social Security Number)
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b'
    if re.search(ssn_pattern, text):
        findings.append({
            "type": "Social Security Number",
            "severity": "critical",
            "action": "Never share SSN in travel planning"
        })

    # Check for credit card numbers
    cc_pattern = r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
    if re.search(cc_pattern, text):
        findings.append({
            "type": "Credit Card Number",
            "severity": "critical",
            "action": "Never share credit card details in chat"
        })

    # Check for passport numbers
    passport_pattern = r'\b[A-Z]{1,2}\d{6,9}\b'
    if re.search(passport_pattern, text):
        findings.append({
            "type": "Passport Number",
            "severity": "high",
            "action": "Avoid sharing passport numbers unless absolutely necessary"
        })

    # Check for email addresses
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    if re.search(email_pattern, text):
        findings.append({
            "type": "Email Address",
            "severity": "medium",
            "action": "Be cautious about sharing email"
        })

    # Check for phone numbers
    phone_pattern = r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    if re.search(phone_pattern, text):
        findings.append({
            "type": "Phone Number",
            "severity": "medium",
            "action": "Consider if phone number is necessary"
        })

    # Check for driver's license patterns
    dl_pattern = r'\b[A-Z]{1,2}\d{5,8}\b'
    if re.search(dl_pattern, text) and not re.search(passport_pattern, text):
        findings.append({
            "type": "Possible Driver's License",
            "severity": "high",
            "action": "Avoid sharing driver's license numbers"
        })

    # Check for bank account numbers
    bank_pattern = r'\b\d{8,17}\b'
    if re.search(bank_pattern, text) and not re.search(cc_pattern, text):
        # Only flag if it's a standalone long number
        findings.append({
            "type": "Possible Bank Account Number",
            "severity": "high",
            "action": "Never share bank account details"
        })

    # Generate response
    if findings:
        critical_count = sum(1 for f in findings if f["severity"] == "critical")
        high_count = sum(1 for f in findings if f["severity"] == "high")

        return {
            "pii_detected": True,
            "findings_count": len(findings),
            "findings": findings,
            "risk_level": "critical" if critical_count > 0 else ("high" if high_count > 0 else "medium"),
            "recommendation": (
                "⚠️ CRITICAL: Sensitive information detected! "
                "Please do not share financial or identity documents in chat. "
                "This information is not needed for vacation planning."
            ),
            "source": "pii_detector",
            "status": "warning"
        }

    return {
        "pii_detected": False,
        "findings_count": 0,
        "findings": [],
        "risk_level": "none",
        "recommendation": "✅ No sensitive personal information detected.",
        "source": "pii_detector",
        "status": "success"
    }


def redact_pii(text: str) -> Dict[str, Any]:
    """
    Redact detected PII from text.

    Args:
        text: Text to redact PII from

    Returns:
        Redacted text and redaction summary
    """
    redacted_text = text
    redactions = []

    # Redact SSN
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
    if re.search(ssn_pattern, redacted_text):
        redacted_text = re.sub(ssn_pattern, '[SSN REDACTED]', redacted_text)
        redactions.append("SSN")

    # Redact credit cards
    cc_pattern = r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
    if re.search(cc_pattern, redacted_text):
        redacted_text = re.sub(cc_pattern, '[CREDIT CARD REDACTED]', redacted_text)
        redactions.append("Credit Card")

    # Redact passport numbers
    passport_pattern = r'\b[A-Z]{1,2}\d{6,9}\b'
    if re.search(passport_pattern, redacted_text):
        redacted_text = re.sub(passport_pattern, '[PASSPORT REDACTED]', redacted_text)
        redactions.append("Passport")

    return {
        "original_length": len(text),
        "redacted_text": redacted_text,
        "redacted_length": len(redacted_text),
        "redactions_made": redactions,
        "redaction_count": len(redactions),
        "source": "pii_redactor",
        "status": "success" if redactions else "no_action"
    }
