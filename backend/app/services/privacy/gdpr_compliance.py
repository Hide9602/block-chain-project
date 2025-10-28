"""
GDPR Compliance Service
GDPR準拠サービス
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import hashlib
import json
from enum import Enum


class DataCategory(str, Enum):
    """Data category for GDPR classification"""
    PERSONAL_IDENTIFIABLE = "personal_identifiable"  # Name, email, etc.
    SENSITIVE = "sensitive"  # Investigation data, blockchain addresses
    TECHNICAL = "technical"  # IP addresses, session data
    ANALYTICAL = "analytical"  # Usage metrics, ML results


class ProcessingPurpose(str, Enum):
    """Purpose of data processing"""
    INVESTIGATION = "investigation"
    ANALYSIS = "analysis"
    REPORTING = "reporting"
    SYSTEM_OPERATION = "system_operation"
    AUDIT = "audit"


class LegalBasis(str, Enum):
    """Legal basis for processing under GDPR"""
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    LEGITIMATE_INTEREST = "legitimate_interest"
    PUBLIC_INTEREST = "public_interest"


class GDPRService:
    """GDPR compliance service"""
    
    # Data retention periods (in days)
    RETENTION_PERIODS = {
        DataCategory.PERSONAL_IDENTIFIABLE: 365 * 3,  # 3 years
        DataCategory.SENSITIVE: 365 * 7,  # 7 years (legal requirement)
        DataCategory.TECHNICAL: 365,  # 1 year
        DataCategory.ANALYTICAL: 365 * 2,  # 2 years
    }
    
    def __init__(self):
        """Initialize GDPR service"""
        pass
    
    def anonymize_address(self, address: str, method: str = "hash") -> str:
        """
        Anonymize blockchain address for GDPR compliance
        
        Args:
            address: Blockchain address to anonymize
            method: Anonymization method (hash, partial, pseudonym)
        
        Returns:
            Anonymized address
        """
        if method == "hash":
            # SHA-256 hash of address
            return hashlib.sha256(address.encode()).hexdigest()[:16]
        
        elif method == "partial":
            # Show first 6 and last 4 characters
            if len(address) > 10:
                return f"{address[:6]}...{address[-4:]}"
            return address
        
        elif method == "pseudonym":
            # Generate consistent pseudonym
            hash_val = int(hashlib.sha256(address.encode()).hexdigest(), 16)
            return f"ADDR-{hash_val % 1000000:06d}"
        
        return address
    
    def pseudonymize_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pseudonymize user data for privacy protection
        
        Args:
            user_data: User data dictionary
        
        Returns:
            Pseudonymized user data
        """
        pseudonymized = user_data.copy()
        
        # Pseudonymize email
        if "email" in pseudonymized:
            email = pseudonymized["email"]
            username, domain = email.split("@")
            pseudonymized["email"] = f"{username[:3]}***@{domain}"
        
        # Pseudonymize name
        if "name" in pseudonymized:
            name_parts = pseudonymized["name"].split()
            if len(name_parts) > 0:
                pseudonymized["name"] = f"{name_parts[0]} {'*' * len(' '.join(name_parts[1:]))}"
        
        # Hash sensitive IDs
        if "user_id" in pseudonymized:
            pseudonymized["user_id"] = hashlib.sha256(
                pseudonymized["user_id"].encode()
            ).hexdigest()[:16]
        
        return pseudonymized
    
    def check_data_retention(
        self,
        data_category: DataCategory,
        created_at: datetime
    ) -> bool:
        """
        Check if data should be retained based on GDPR retention policy
        
        Args:
            data_category: Category of data
            created_at: When data was created
        
        Returns:
            True if data should be retained, False if should be deleted
        """
        retention_days = self.RETENTION_PERIODS.get(data_category, 365)
        retention_period = timedelta(days=retention_days)
        
        return datetime.utcnow() - created_at < retention_period
    
    def generate_data_export(
        self,
        user_id: str,
        include_categories: Optional[List[DataCategory]] = None
    ) -> Dict[str, Any]:
        """
        Generate GDPR-compliant data export for user (Right to Data Portability)
        
        Args:
            user_id: User ID
            include_categories: Categories to include (None = all)
        
        Returns:
            User data export
        """
        # In production, fetch from database
        export_data = {
            "export_metadata": {
                "user_id": user_id,
                "export_date": datetime.utcnow().isoformat(),
                "format": "JSON",
                "version": "1.0"
            },
            "personal_data": {
                # Would fetch from database
                "user_profile": {},
                "investigations": [],
                "reports": []
            },
            "processing_activities": {
                # Log of data processing
                "purposes": [],
                "legal_basis": []
            },
            "data_categories": {}
        }
        
        return export_data
    
    def process_deletion_request(
        self,
        user_id: str,
        categories: Optional[List[DataCategory]] = None
    ) -> Dict[str, Any]:
        """
        Process data deletion request (Right to Erasure)
        
        Args:
            user_id: User ID
            categories: Categories to delete (None = all non-legal)
        
        Returns:
            Deletion report
        """
        deletion_report = {
            "user_id": user_id,
            "deletion_date": datetime.utcnow().isoformat(),
            "deleted_categories": [],
            "retained_categories": [],
            "retention_reasons": {}
        }
        
        # Determine what can be deleted vs must be retained
        if categories is None:
            categories = list(DataCategory)
        
        for category in categories:
            # Check legal obligations
            if category == DataCategory.SENSITIVE:
                # Investigation data must be retained for legal reasons
                deletion_report["retained_categories"].append(category.value)
                deletion_report["retention_reasons"][category.value] = "Legal obligation to retain investigation data"
            else:
                # Can be deleted
                deletion_report["deleted_categories"].append(category.value)
                # In production: execute deletion from database
        
        return deletion_report
    
    def record_consent(
        self,
        user_id: str,
        purpose: ProcessingPurpose,
        legal_basis: LegalBasis,
        consent_text: str
    ) -> Dict[str, Any]:
        """
        Record user consent for data processing
        
        Args:
            user_id: User ID
            purpose: Purpose of processing
            legal_basis: Legal basis
            consent_text: Consent text shown to user
        
        Returns:
            Consent record
        """
        consent_record = {
            "user_id": user_id,
            "purpose": purpose.value,
            "legal_basis": legal_basis.value,
            "consent_text": consent_text,
            "granted_at": datetime.utcnow().isoformat(),
            "version": "1.0"
        }
        
        # In production: save to database
        return consent_record
    
    def generate_privacy_report(self, user_id: str) -> Dict[str, Any]:
        """
        Generate privacy report for user (Right to Access)
        
        Args:
            user_id: User ID
        
        Returns:
            Privacy report
        """
        report = {
            "user_id": user_id,
            "report_date": datetime.utcnow().isoformat(),
            "data_categories": [],
            "processing_purposes": [],
            "legal_bases": [],
            "data_recipients": [],  # Who has access to data
            "retention_periods": {},
            "user_rights": {
                "right_to_access": "Available",
                "right_to_rectification": "Available",
                "right_to_erasure": "Available (with legal limitations)",
                "right_to_data_portability": "Available",
                "right_to_object": "Available",
                "right_to_restrict_processing": "Available"
            }
        }
        
        # In production: fetch actual data from database
        for category in DataCategory:
            retention_days = self.RETENTION_PERIODS.get(category, 365)
            report["retention_periods"][category.value] = f"{retention_days} days"
        
        return report
    
    def validate_cross_border_transfer(
        self,
        source_country: str,
        destination_country: str
    ) -> Dict[str, Any]:
        """
        Validate data transfer between countries (GDPR Article 44-50)
        
        Args:
            source_country: Source country code
            destination_country: Destination country code
        
        Returns:
            Transfer validation result
        """
        # EU/EEA countries
        eu_countries = {
            "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR",
            "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL",
            "PL", "PT", "RO", "SK", "SI", "ES", "SE", "IS", "LI", "NO"
        }
        
        # Countries with adequacy decision
        adequate_countries = {
            "JP",  # Japan
            "CH",  # Switzerland
            "GB",  # United Kingdom
            # Add more as needed
        }
        
        is_valid = False
        mechanism = None
        
        if source_country in eu_countries:
            if destination_country in eu_countries:
                is_valid = True
                mechanism = "Intra-EU transfer"
            elif destination_country in adequate_countries:
                is_valid = True
                mechanism = "Adequacy decision"
            else:
                is_valid = False
                mechanism = "Requires Standard Contractual Clauses (SCC) or Binding Corporate Rules (BCR)"
        
        return {
            "is_valid": is_valid,
            "mechanism": mechanism,
            "source_country": source_country,
            "destination_country": destination_country,
            "requires_additional_safeguards": not is_valid
        }


# Global GDPR service instance
gdpr_service = GDPRService()
