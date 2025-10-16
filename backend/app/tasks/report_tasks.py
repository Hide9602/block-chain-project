"""
Celery tasks for report generation
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from .celery_app import celery_app
from app.services.report.report_generator import ReportGenerator
from app.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="generate_report")
def generate_report_task(
    self,
    investigation_id: str,
    case_number: str,
    case_title: str,
    target_address: str,
    blockchain: str,
    risk_score: int,
    risk_level: str,
    total_transactions: int,
    total_addresses: int,
    total_volume: float,
    detected_patterns: list,
    key_findings: list,
    investigator_name: Optional[str] = None,
    language: str = "ja",
    format: str = "pdf"
) -> Dict[str, Any]:
    """
    Asynchronous task to generate investigation report
    
    Args:
        self: Celery task instance (bind=True)
        investigation_id: Unique investigation identifier
        case_number: Case number (e.g., "CASE-2024-0001")
        case_title: Report title
        target_address: Target blockchain address
        blockchain: Blockchain name (e.g., "ethereum")
        risk_score: Risk score (0-100)
        risk_level: Risk level ("high", "medium", "low")
        total_transactions: Total number of transactions analyzed
        total_addresses: Total number of addresses involved
        total_volume: Total transaction volume
        detected_patterns: List of detected suspicious patterns
        key_findings: List of key findings
        investigator_name: Name of investigator (optional)
        language: Report language ("ja" or "en")
        format: Report format ("pdf", "word", or "json")
    
    Returns:
        Dict containing report metadata and file path
    """
    try:
        logger.info(f"Starting report generation for investigation {investigation_id}")
        
        # Update task state
        self.update_state(
            state="PROCESSING",
            meta={
                "investigation_id": investigation_id,
                "status": "Generating report content...",
                "progress": 10
            }
        )
        
        # Create report generator instance
        generator = ReportGenerator()
        
        # Update progress
        self.update_state(
            state="PROCESSING",
            meta={
                "investigation_id": investigation_id,
                "status": "Rendering template...",
                "progress": 30
            }
        )
        
        # Generate report
        report_data = generator.create_investigation_report(
            investigation_id=investigation_id,
            case_number=case_number,
            case_title=case_title,
            target_address=target_address,
            blockchain=blockchain,
            risk_score=risk_score,
            risk_level=risk_level,
            total_transactions=total_transactions,
            total_addresses=total_addresses,
            total_volume=total_volume,
            detected_patterns=detected_patterns,
            key_findings=key_findings,
            investigator_name=investigator_name,
            language=language,
            format=format
        )
        
        # Update progress
        self.update_state(
            state="PROCESSING",
            meta={
                "investigation_id": investigation_id,
                "status": "Saving report file...",
                "progress": 80
            }
        )
        
        # Save report to file system
        reports_dir = Path(settings.REPORTS_DIR)
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        extension = "pdf" if format == "pdf" else "docx" if format == "word" else "json"
        filename = f"{case_number}_{timestamp}.{extension}"
        file_path = reports_dir / filename
        
        # Write file
        if format in ["pdf", "word"]:
            with open(file_path, "wb") as f:
                f.write(report_data["content"])
        else:  # json
            import json
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Report generated successfully: {file_path}")
        
        # Return success result
        return {
            "status": "success",
            "investigation_id": investigation_id,
            "file_path": str(file_path),
            "filename": filename,
            "format": format,
            "language": language,
            "digital_signature": report_data.get("digital_signature"),
            "content_hash": report_data.get("content_hash"),
            "generated_at": report_data.get("generated_at"),
            "file_size": file_path.stat().st_size if format in ["pdf", "word"] else len(report_data["content"])
        }
        
    except Exception as e:
        logger.error(f"Error generating report for investigation {investigation_id}: {str(e)}", exc_info=True)
        
        # Update task state to FAILURE
        self.update_state(
            state="FAILURE",
            meta={
                "investigation_id": investigation_id,
                "status": f"Report generation failed: {str(e)}",
                "error": str(e)
            }
        )
        
        # Re-raise exception to mark task as failed
        raise
