"""
Security Guardian Agent - PII Detection and Data Protection
Custom Tool implementation for complex security logic
"""

import re
from typing import Dict, Any, List
from loguru import logger
from .base_agent import BaseAgent


class SecurityGuardianAgent(BaseAgent):
    """
    Security Guardian Agent for PII detection and data protection.
    Implements Custom Tool pattern with complex business logic.
    """

    def __init__(self):
        super().__init__(
            name="security_guardian",
            description="Protects user data by detecting and handling PII"
        )

        # PII detection patterns with severity levels
        self.pii_patterns = {
            "ssn": {
                "pattern": r'\b\d{3}-\d{2}-\d{4}\b',
                "severity": "critical",
                "description": "Social Security Number"
            },
            "credit_card": {
                "pattern": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
                "severity": "critical",
                "description": "Credit Card Number"
            },
            "passport": {
                "pattern": r'\b[A-Z]{1,2}\d{6,9}\b',
                "severity": "high",
                "description": "Passport Number"
            },
            "email": {
                "pattern": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                "severity": "medium",
                "description": "Email Address"
            },
            "phone": {
                "pattern": r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
                "severity": "medium",
                "description": "Phone Number"
            },
            "drivers_license": {
                "pattern": r'\b[A-Z]\d{7,8}\b',
                "severity": "high",
                "description": "Driver's License Number"
            },
            "bank_account": {
                "pattern": r'\b\d{8,17}\b',
                "severity": "high",
                "description": "Bank Account Number"
            },
            "date_of_birth": {
                "pattern": r'\b(?:0[1-9]|1[0-2])[/-](?:0[1-9]|[12]\d|3[01])[/-](?:19|20)\d{2}\b',
                "severity": "medium",
                "description": "Date of Birth"
            }
        }

    async def _execute_impl(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scan input for PII and return detection results.

        Args:
            input_data: Contains 'text' to scan

        Returns:
            PII detection results with recommendations
        """
        text = input_data.get("text", "")

        if not text:
            return {
                "status": "success",
                "pii_detected": False,
                "message": "No text provided for scanning"
            }

        # Detect PII
        findings = self._detect_pii(text)

        # Determine overall risk level
        risk_level = self._calculate_risk_level(findings)

        # Generate recommendations
        recommendations = self._generate_recommendations(findings, risk_level)

        # Send advisory to other agents if critical PII found
        if risk_level == "critical":
            self.send_message(
                to_agent="orchestrator",
                message_type="security_alert",
                content={
                    "alert_type": "critical_pii_detected",
                    "findings_count": len(findings),
                    "risk_level": risk_level
                },
                priority="critical"
            )

        return {
            "status": "success",
            "pii_detected": len(findings) > 0,
            "findings_count": len(findings),
            "findings": findings,
            "risk_level": risk_level,
            "recommendations": recommendations,
            "safe_to_proceed": risk_level not in ["critical", "high"]
        }

    def _detect_pii(self, text: str) -> List[Dict[str, Any]]:
        """Detect all PII patterns in text."""
        findings = []

        for pii_type, config in self.pii_patterns.items():
            matches = re.findall(config["pattern"], text, re.IGNORECASE)

            if matches:
                findings.append({
                    "type": pii_type,
                    "description": config["description"],
                    "severity": config["severity"],
                    "count": len(matches),
                    "action": "redact" if config["severity"] in ["critical", "high"] else "warn"
                })
                logger.warning(f"[PII] Detected {config['description']}: {len(matches)} instance(s)")

        return findings

    def _calculate_risk_level(self, findings: List[Dict[str, Any]]) -> str:
        """Calculate overall risk level from findings."""
        if not findings:
            return "none"

        severities = [f["severity"] for f in findings]

        if "critical" in severities:
            return "critical"
        elif "high" in severities:
            return "high"
        elif "medium" in severities:
            return "medium"
        else:
            return "low"

    def _generate_recommendations(
        self,
        findings: List[Dict[str, Any]],
        risk_level: str
    ) -> List[str]:
        """Generate security recommendations."""
        recommendations = []

        if risk_level == "none":
            recommendations.append("No sensitive information detected. Safe to proceed.")
            return recommendations

        recommendations.append(
            f"WARNING: {len(findings)} type(s) of sensitive information detected."
        )

        for finding in findings:
            if finding["severity"] == "critical":
                recommendations.append(
                    f"CRITICAL: Remove {finding['description']} before proceeding. "
                    "This data should never be shared."
                )
            elif finding["severity"] == "high":
                recommendations.append(
                    f"HIGH: Consider removing {finding['description']}. "
                    "This data could be used for identity theft."
                )
            elif finding["severity"] == "medium":
                recommendations.append(
                    f"MEDIUM: {finding['description']} detected. "
                    "Only share if absolutely necessary for booking."
                )

        if risk_level in ["critical", "high"]:
            recommendations.append(
                "RECOMMENDATION: Please revise your input to remove sensitive data."
            )

        return recommendations

    def redact_pii(self, text: str) -> Dict[str, Any]:
        """
        Redact PII from text.

        Args:
            text: Text to redact

        Returns:
            Redacted text and redaction details
        """
        redacted_text = text
        redactions = []

        for pii_type, config in self.pii_patterns.items():
            if config["severity"] in ["critical", "high"]:
                pattern = config["pattern"]
                matches = re.findall(pattern, text, re.IGNORECASE)

                if matches:
                    redacted_text = re.sub(
                        pattern,
                        f"[REDACTED-{pii_type.upper()}]",
                        redacted_text,
                        flags=re.IGNORECASE
                    )
                    redactions.append({
                        "type": pii_type,
                        "count": len(matches)
                    })

        return {
            "original_length": len(text),
            "redacted_text": redacted_text,
            "redacted_length": len(redacted_text),
            "redactions": redactions,
            "total_redactions": sum(r["count"] for r in redactions)
        }
