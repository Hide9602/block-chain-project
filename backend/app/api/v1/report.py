"""
Report Generation API endpoints
レポート生成関連のAPIエンドポイント
"""

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from datetime import datetime
from pathlib import Path
import logging

from app.tasks.report_tasks import generate_report_task
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


# Enums
class ReportFormat(str, Enum):
    """レポートフォーマット"""
    PDF = "pdf"
    WORD = "word"
    JSON = "json"


class ReportLanguage(str, Enum):
    """レポート言語"""
    JAPANESE = "ja"
    ENGLISH = "en"


class ReportStatus(str, Enum):
    """レポートステータス"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# リクエスト/レスポンスモデル
class ReportGenerateRequest(BaseModel):
    """レポート生成リクエスト"""
    address: str
    chain: str
    language: ReportLanguage = ReportLanguage.JAPANESE
    format: ReportFormat = ReportFormat.PDF
    include_narrative: bool = True
    include_risk_assessment: bool = True
    case_title: Optional[str] = None
    case_number: Optional[str] = None
    investigator_name: Optional[str] = None


class ReportResponse(BaseModel):
    """レポートレスポンス"""
    report_id: str
    status: ReportStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    download_url: Optional[str] = None
    format: ReportFormat
    language: ReportLanguage
    file_size: Optional[int] = None


class ReportMetadata(BaseModel):
    """レポートメタデータ"""
    report_id: str
    case_title: str
    case_number: Optional[str] = None
    target_address: str
    chain: str
    investigation_period_start: str
    investigation_period_end: str
    total_transactions: int
    total_addresses: int
    risk_score: int
    investigator_name: Optional[str] = None
    generated_at: datetime
    digital_signature: str
    verification_hash: str


@router.post("/generate", response_model=ReportResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_report(request: ReportGenerateRequest):
    """
    レポート生成（非同期）
    
    Args:
        request: レポート生成リクエスト
    
    Returns:
        ReportResponse: レポート情報（生成中）
    """
    try:
        # Generate unique report ID
        import uuid
        report_id = str(uuid.uuid4())
        
        # Generate case number if not provided
        case_number = request.case_number or f"CASE-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        case_title = request.case_title or f"Blockchain Investigation Report - {request.address[:10]}..."
        
        # TODO: Fetch actual investigation data from database
        # For now, using sample data
        sample_patterns = [
            {
                "type": "Layering",
                "description": "Multiple intermediate wallet transfers detected",
                "confidence": 0.85,
                "addresses_count": 12,
                "total_amount": 45.67
            }
        ]
        
        sample_findings = [
            "High-risk transaction pattern detected with known mixing service",
            "Multiple transactions exceeding reporting thresholds",
            "Association with addresses on sanctions watchlist"
        ]
        
        # Submit Celery task for async report generation
        task = generate_report_task.delay(
            investigation_id=report_id,
            case_number=case_number,
            case_title=case_title,
            target_address=request.address,
            blockchain=request.chain,
            risk_score=75,  # TODO: Calculate actual risk score
            risk_level="high",  # TODO: Determine actual risk level
            total_transactions=156,  # TODO: Get from database
            total_addresses=43,  # TODO: Get from database
            total_volume=123.45,  # TODO: Calculate from transactions
            detected_patterns=sample_patterns,
            key_findings=sample_findings,
            investigator_name=request.investigator_name,
            language=request.language.value,
            format=request.format.value
        )
        
        logger.info(f"Report generation task submitted: {task.id} for investigation {report_id}")
        
        return ReportResponse(
            report_id=task.id,  # Use Celery task ID as report ID
            status=ReportStatus.PENDING,
            created_at=datetime.utcnow(),
            format=request.format,
            language=request.language
        )
        
    except Exception as e:
        logger.error(f"Error submitting report generation task: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit report generation task: {str(e)}"
        )


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report_status(report_id: str):
    """
    レポートステータス取得
    
    Args:
        report_id: レポートID (Celery task ID)
    
    Returns:
        ReportResponse: レポート情報
    """
    try:
        from celery.result import AsyncResult
        
        # Get task result from Celery
        task_result = AsyncResult(report_id)
        
        # Map Celery states to our ReportStatus
        status_mapping = {
            "PENDING": ReportStatus.PENDING,
            "PROCESSING": ReportStatus.PROCESSING,
            "SUCCESS": ReportStatus.COMPLETED,
            "FAILURE": ReportStatus.FAILED
        }
        
        report_status = status_mapping.get(task_result.state, ReportStatus.PENDING)
        
        response = ReportResponse(
            report_id=report_id,
            status=report_status,
            created_at=datetime.utcnow(),  # TODO: Get actual creation time from DB
            format=ReportFormat.PDF,  # TODO: Get from task metadata
            language=ReportLanguage.JAPANESE  # TODO: Get from task metadata
        )
        
        # If task is completed successfully, add download URL and file info
        if task_result.state == "SUCCESS":
            result_data = task_result.result
            response.completed_at = datetime.utcnow()  # TODO: Get actual completion time
            response.download_url = f"/api/v1/report/{report_id}/download"
            response.file_size = result_data.get("file_size")
        
        # If task failed, raise an exception with error details
        elif task_result.state == "FAILURE":
            error_msg = str(task_result.info) if task_result.info else "Unknown error"
            logger.error(f"Report generation failed for {report_id}: {error_msg}")
            # Still return the response but with FAILED status
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting report status for {report_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get report status: {str(e)}"
        )


@router.get("/{report_id}/download")
async def download_report(report_id: str):
    """
    レポートダウンロード
    
    Args:
        report_id: レポートID (Celery task ID)
    
    Returns:
        FileResponse: レポートファイル
    """
    try:
        from celery.result import AsyncResult
        
        # Get task result from Celery
        task_result = AsyncResult(report_id)
        
        # Check if task is completed
        if task_result.state != "SUCCESS":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Report is not ready yet. Current status: {task_result.state}"
            )
        
        # Get file path from task result
        result_data = task_result.result
        file_path = Path(result_data["file_path"])
        
        # Check if file exists
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report file not found"
            )
        
        # Determine media type based on format
        format_type = result_data.get("format", "pdf")
        media_types = {
            "pdf": "application/pdf",
            "word": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "json": "application/json"
        }
        media_type = media_types.get(format_type, "application/octet-stream")
        
        # Return file response
        return FileResponse(
            path=str(file_path),
            media_type=media_type,
            filename=result_data["filename"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading report {report_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download report: {str(e)}"
        )


@router.get("/{report_id}/metadata", response_model=ReportMetadata)
async def get_report_metadata(report_id: str):
    """
    レポートメタデータ取得
    
    Args:
        report_id: レポートID (Celery task ID)
    
    Returns:
        ReportMetadata: レポートメタデータ
    """
    try:
        from celery.result import AsyncResult
        
        # Get task result from Celery
        task_result = AsyncResult(report_id)
        
        # Check if task is completed
        if task_result.state != "SUCCESS":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Report is not ready yet. Current status: {task_result.state}"
            )
        
        # Get metadata from task result
        result_data = task_result.result
        
        # TODO: Get actual investigation data from database
        # For now, return sample metadata with data from task result
        return ReportMetadata(
            report_id=report_id,
            case_title="Blockchain Investigation Report",  # TODO: Get from DB
            case_number="CASE-2024-001",  # TODO: Get from DB
            target_address="0x1234...5678",  # TODO: Get from DB
            chain="ethereum",  # TODO: Get from DB
            investigation_period_start="2024-01-01T00:00:00Z",  # TODO: Get from DB
            investigation_period_end="2024-01-31T23:59:59Z",  # TODO: Get from DB
            total_transactions=156,  # TODO: Get from DB
            total_addresses=43,  # TODO: Get from DB
            risk_score=75,  # TODO: Get from DB
            investigator_name="Investigation Team",  # TODO: Get from DB
            generated_at=datetime.fromisoformat(result_data["generated_at"]),
            digital_signature=result_data.get("digital_signature", "N/A"),
            verification_hash=result_data.get("content_hash", "N/A")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting report metadata for {report_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get report metadata: {str(e)}"
        )


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(report_id: str):
    """
    レポート削除
    
    Args:
        report_id: レポートID (Celery task ID)
    
    Returns:
        None
    """
    try:
        from celery.result import AsyncResult
        
        # Get task result from Celery
        task_result = AsyncResult(report_id)
        
        # If task is completed, delete the file
        if task_result.state == "SUCCESS":
            result_data = task_result.result
            file_path = Path(result_data["file_path"])
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted report file: {file_path}")
        
        # Revoke the Celery task (if still pending/processing)
        task_result.revoke(terminate=True)
        
        # TODO: Delete from database
        
        return None
        
    except Exception as e:
        logger.error(f"Error deleting report {report_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete report: {str(e)}"
        )