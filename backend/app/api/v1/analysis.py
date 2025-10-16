"""
AI Analysis API endpoints
AI分析関連のAPIエンドポイント
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
import logging

from app.services.ml.pattern_matcher import PatternMatcher
from app.services.ml.anomaly_detector import AnomalyDetector
from app.services.ml.risk_scorer import RiskScorer
from app.services.blockchain.etherscan import EtherscanClient
from app.services.narrative.narrative_generator import NarrativeGenerator

logger = logging.getLogger(__name__)

router = APIRouter()


# Enums
class PatternType(str, Enum):
    """マネーロンダリングパターンタイプ"""
    SMURFING = "smurfing"  # スマーフィング
    LAYERING = "layering"  # レイヤリング
    MIXING = "mixing"  # ミキシング
    STRUCTURING = "structuring"  # ストラクチャリング
    CIRCULAR = "circular"  # 循環取引


# リクエスト/レスポンスモデル
class PatternDetection(BaseModel):
    """パターン検出結果"""
    pattern_type: PatternType
    confidence: float
    description_en: str
    description_ja: str
    addresses_involved: List[str]
    total_amount: float
    transactions_count: int


class PatternAnalysisRequest(BaseModel):
    """パターン分析リクエスト"""
    address: str
    chain: str
    lookback_days: int = 30


class PatternAnalysisResponse(BaseModel):
    """パターン分析レスポンス"""
    address: str
    detected_patterns: List[PatternDetection]
    overall_risk_score: int
    total_patterns_detected: int


class NarrativeRequest(BaseModel):
    """物語化リクエスト"""
    address: str
    chain: str
    language: str = "ja"  # ja or en
    max_hops: int = 10


class NarrativeResponse(BaseModel):
    """物語化レスポンス"""
    address: str
    language: str
    narrative: str
    key_findings: List[str]
    timeline: List[dict]


class RiskScoreRequest(BaseModel):
    """リスクスコアリングリクエスト"""
    address: str
    chain: str


class RiskScoreResponse(BaseModel):
    """リスクスコアリングレスポンス"""
    address: str
    risk_score: int  # 0-100
    risk_level: str  # high, medium, low, none
    factors: List[dict]
    is_sanctioned: bool
    sanctioned_lists: List[str]


@router.post("/pattern", response_model=PatternAnalysisResponse)
async def analyze_patterns(request: PatternAnalysisRequest):
    """
    マネーロンダリングパターン検出
    
    Args:
        request: パターン分析リクエスト
    
    Returns:
        PatternAnalysisResponse: 検出されたパターン
    """
    try:
        # Initialize clients
        etherscan_client = EtherscanClient()
        pattern_matcher = PatternMatcher()
        anomaly_detector = AnomalyDetector()
        risk_scorer = RiskScorer()
        
        # Fetch transactions from blockchain
        logger.info(f"Fetching transactions for address: {request.address}")
        transactions = await etherscan_client.get_address_transactions(
            address=request.address,
            page=1,
            page_size=1000  # Get more transactions for pattern analysis
        )
        
        if not transactions:
            return PatternAnalysisResponse(
                address=request.address,
                detected_patterns=[],
                overall_risk_score=0,
                total_patterns_detected=0
            )
        
        # Detect patterns
        logger.info(f"Analyzing {len(transactions)} transactions for patterns")
        detected_patterns = pattern_matcher.detect_patterns(transactions, request.address)
        
        # Detect anomalies
        detected_anomalies = anomaly_detector.detect_anomalies(transactions, request.address)
        
        # Calculate risk score
        risk_assessment = risk_scorer.calculate_risk_score(
            address=request.address,
            transactions=transactions,
            detected_patterns=detected_patterns,
            detected_anomalies=detected_anomalies
        )
        
        # Convert to response format
        pattern_detections = []
        for pattern in detected_patterns:
            # Map pattern_id to PatternType enum
            pattern_type_map = {
                "smurfing": PatternType.SMURFING,
                "layering": PatternType.LAYERING,
                "mixing": PatternType.MIXING,
                "structuring": PatternType.STRUCTURING,
                "circular_trading": PatternType.CIRCULAR
            }
            
            pattern_type = pattern_type_map.get(
                pattern.get("pattern_id", ""),
                PatternType.LAYERING  # Default
            )
            
            pattern_detections.append(PatternDetection(
                pattern_type=pattern_type,
                confidence=pattern.get("confidence", 0.0),
                description_en=pattern.get("description_en", ""),
                description_ja=pattern.get("description_ja", ""),
                addresses_involved=pattern.get("evidence", {}).get("chain_addresses", [])[:5],
                total_amount=pattern.get("total_amount", 0.0),
                transactions_count=pattern.get("transaction_count", 0)
            ))
        
        logger.info(f"Pattern analysis complete: {len(pattern_detections)} patterns detected")
        
        return PatternAnalysisResponse(
            address=request.address,
            detected_patterns=pattern_detections,
            overall_risk_score=int(risk_assessment["risk_score"]),
            total_patterns_detected=len(pattern_detections)
        )
        
    except Exception as e:
        logger.error(f"Error analyzing patterns for {request.address}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze patterns: {str(e)}"
        )


@router.post("/narrative", response_model=NarrativeResponse)
async def generate_narrative(request: NarrativeRequest):
    """
    資金フローの物語化生成
    
    Args:
        request: 物語化リクエスト
    
    Returns:
        NarrativeResponse: 自然言語で表現された調査報告
    """
    try:
        # Initialize clients and generators
        etherscan_client = EtherscanClient()
        pattern_matcher = PatternMatcher()
        anomaly_detector = AnomalyDetector()
        risk_scorer = RiskScorer()
        narrative_generator = NarrativeGenerator()
        
        # Fetch transactions from blockchain
        logger.info(f"Fetching transactions for narrative generation: {request.address}")
        transactions = await etherscan_client.get_address_transactions(
            address=request.address,
            page=1,
            page_size=1000
        )
        
        if not transactions:
            # Return basic narrative for addresses with no transactions
            if request.language == "ja":
                narrative = f"調査対象アドレス（{request.address}）において、分析期間中の取引は確認されませんでした。"
                key_findings = ["取引履歴なし"]
            else:
                narrative = f"No transactions were found for the investigation target address ({request.address}) during the analysis period."
                key_findings = ["No transaction history"]
            
            return NarrativeResponse(
                address=request.address,
                language=request.language,
                narrative=narrative,
                key_findings=key_findings,
                timeline=[]
            )
        
        # Detect patterns
        logger.info(f"Detecting patterns in {len(transactions)} transactions")
        detected_patterns = pattern_matcher.detect_patterns(transactions, request.address)
        
        # Detect anomalies
        detected_anomalies = anomaly_detector.detect_anomalies(transactions, request.address)
        
        # Calculate risk score
        risk_assessment = risk_scorer.calculate_risk_score(
            address=request.address,
            transactions=transactions,
            detected_patterns=detected_patterns,
            detected_anomalies=detected_anomalies
        )
        
        # Generate narrative
        logger.info(f"Generating narrative in {request.language}")
        narrative = narrative_generator.generate_narrative(
            address=request.address,
            transactions=transactions,
            detected_patterns=detected_patterns,
            detected_anomalies=detected_anomalies,
            risk_assessment=risk_assessment,
            language=request.language
        )
        
        # Extract key findings
        key_findings = []
        
        # Add pattern findings
        for pattern in detected_patterns:
            if request.language == "ja":
                finding = f"{pattern.get('name_ja', '')}: 信頼度{pattern.get('confidence', 0) * 100:.0f}%"
            else:
                finding = f"{pattern.get('name_en', '')}: {pattern.get('confidence', 0) * 100:.0f}% confidence"
            key_findings.append(finding)
        
        # Add anomaly findings
        for anomaly in detected_anomalies[:3]:  # Top 3 anomalies
            if request.language == "ja":
                finding = f"異常検出: {anomaly.get('description_ja', '')}"
            else:
                finding = f"Anomaly: {anomaly.get('description_en', '')}"
            key_findings.append(finding)
        
        # Add risk level
        risk_level = risk_assessment.get("risk_level", "medium")
        risk_score = risk_assessment.get("risk_score", 0)
        if request.language == "ja":
            risk_translations = {
                "critical": "極めて高い",
                "high": "高い",
                "medium": "中程度",
                "low": "低い",
                "minimal": "極めて低い"
            }
            key_findings.append(f"総合リスク: {risk_translations.get(risk_level, risk_level)}（{risk_score:.1f}/100）")
        else:
            key_findings.append(f"Overall Risk: {risk_level} ({risk_score:.1f}/100)")
        
        # Build timeline from transactions
        timeline = []
        sorted_txs = sorted(transactions, key=lambda t: t.get("timestamp", ""))
        
        # Add first transaction
        if sorted_txs:
            first_tx = sorted_txs[0]
            timeline.append({
                "timestamp": first_tx.get("timestamp", ""),
                "event": "First transaction" if request.language == "en" else "初回取引",
                "amount": first_tx.get("value", 0.0)
            })
        
        # Add pattern-related events
        for pattern in detected_patterns[:2]:  # Top 2 patterns
            if pattern.get("matched_transactions"):
                matched_tx = pattern["matched_transactions"][0]
                timeline.append({
                    "timestamp": matched_tx.get("timestamp", ""),
                    "event": pattern.get("name_en", "") if request.language == "en" else pattern.get("name_ja", ""),
                    "amount": matched_tx.get("value", 0.0)
                })
        
        # Add last transaction
        if sorted_txs and len(sorted_txs) > 1:
            last_tx = sorted_txs[-1]
            timeline.append({
                "timestamp": last_tx.get("timestamp", ""),
                "event": "Latest transaction" if request.language == "en" else "最新取引",
                "amount": last_tx.get("value", 0.0)
            })
        
        logger.info(f"Narrative generation complete: {len(key_findings)} key findings")
        
        return NarrativeResponse(
            address=request.address,
            language=request.language,
            narrative=narrative,
            key_findings=key_findings,
            timeline=timeline
        )
        
    except Exception as e:
        logger.error(f"Error generating narrative for {request.address}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate narrative: {str(e)}"
        )


@router.post("/risk-score", response_model=RiskScoreResponse)
async def calculate_risk_score(request: RiskScoreRequest):
    """
    リスクスコア計算
    
    Args:
        request: リスクスコアリングリクエスト
    
    Returns:
        RiskScoreResponse: リスクスコアと詳細
    """
    try:
        # Initialize clients
        etherscan_client = EtherscanClient()
        pattern_matcher = PatternMatcher()
        anomaly_detector = AnomalyDetector()
        risk_scorer = RiskScorer()
        
        # Fetch transactions
        logger.info(f"Fetching transactions for risk scoring: {request.address}")
        transactions = await etherscan_client.get_address_transactions(
            address=request.address,
            page=1,
            page_size=1000
        )
        
        if not transactions:
            return RiskScoreResponse(
                address=request.address,
                risk_score=50,  # Unknown = medium risk
                risk_level="medium",
                factors=[],
                is_sanctioned=False,
                sanctioned_lists=[]
            )
        
        # Detect patterns and anomalies
        detected_patterns = pattern_matcher.detect_patterns(transactions, request.address)
        detected_anomalies = anomaly_detector.detect_anomalies(transactions, request.address)
        
        # Calculate comprehensive risk score
        risk_assessment = risk_scorer.calculate_risk_score(
            address=request.address,
            transactions=transactions,
            detected_patterns=detected_patterns,
            detected_anomalies=detected_anomalies
        )
        
        # Convert breakdown to factors list
        factors = []
        for factor_name, factor_data in risk_assessment["breakdown"].items():
            factors.append({
                "factor": factor_data["description_en"],
                "score_impact": int(factor_data["contribution"]),
                "description": factor_data["description_ja"]
            })
        
        # TODO: Check sanctions lists (OFAC, EU, etc.)
        # For now, check if mixing service was used
        is_sanctioned = any(
            p.get("pattern_id") == "mixing" 
            for p in detected_patterns
        )
        
        sanctioned_lists = ["OFAC SDN List"] if is_sanctioned else []
        
        logger.info(f"Risk score calculated: {risk_assessment['risk_score']} ({risk_assessment['risk_level']})")
        
        return RiskScoreResponse(
            address=request.address,
            risk_score=int(risk_assessment["risk_score"]),
            risk_level=risk_assessment["risk_level"],
            factors=factors,
            is_sanctioned=is_sanctioned,
            sanctioned_lists=sanctioned_lists
        )
        
    except Exception as e:
        logger.error(f"Error calculating risk score for {request.address}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate risk score: {str(e)}"
        )