"""
Risk Scorer for blockchain address assessment
ブロックチェーンアドレスのリスク評価
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class RiskScorer:
    """
    Comprehensive risk scoring system for blockchain addresses
    ブロックチェーンアドレスの総合的なリスクスコアリングシステム
    """
    
    def __init__(self):
        """Initialize risk scorer with default weights"""
        # Risk factor weights (total should be 1.0)
        self.weights = {
            "pattern_risk": 0.35,      # Detected ML patterns
            "anomaly_risk": 0.25,      # Statistical anomalies
            "counterparty_risk": 0.20, # Known risky entities
            "volume_risk": 0.10,       # Transaction volume
            "age_risk": 0.10           # Address age and activity
        }
        
        logger.info("Initialized RiskScorer with default weights")
    
    def calculate_risk_score(
        self,
        address: str,
        transactions: List[Dict[str, Any]],
        detected_patterns: List[Dict[str, Any]],
        detected_anomalies: List[Dict[str, Any]],
        address_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive risk score for an address
        
        Args:
            address: Target blockchain address
            transactions: List of transactions
            detected_patterns: Detected ML patterns
            detected_anomalies: Detected anomalies
            address_metadata: Additional address metadata
        
        Returns:
            Risk assessment dictionary with score and breakdown
        """
        # Calculate individual risk components
        pattern_score = self._calculate_pattern_risk(detected_patterns)
        anomaly_score = self._calculate_anomaly_risk(detected_anomalies)
        counterparty_score = self._calculate_counterparty_risk(transactions)
        volume_score = self._calculate_volume_risk(transactions)
        age_score = self._calculate_age_risk(transactions, address_metadata)
        
        # Calculate weighted total
        total_score = (
            pattern_score * self.weights["pattern_risk"] +
            anomaly_score * self.weights["anomaly_risk"] +
            counterparty_score * self.weights["counterparty_risk"] +
            volume_score * self.weights["volume_risk"] +
            age_score * self.weights["age_risk"]
        )
        
        # Determine risk level
        risk_level = self._determine_risk_level(total_score)
        
        # Build detailed breakdown
        breakdown = {
            "pattern_risk": {
                "score": pattern_score,
                "weight": self.weights["pattern_risk"],
                "contribution": pattern_score * self.weights["pattern_risk"],
                "description_ja": "検出されたマネーロンダリングパターン",
                "description_en": "Detected money laundering patterns"
            },
            "anomaly_risk": {
                "score": anomaly_score,
                "weight": self.weights["anomaly_risk"],
                "contribution": anomaly_score * self.weights["anomaly_risk"],
                "description_ja": "統計的異常検知",
                "description_en": "Statistical anomaly detection"
            },
            "counterparty_risk": {
                "score": counterparty_score,
                "weight": self.weights["counterparty_risk"],
                "contribution": counterparty_score * self.weights["counterparty_risk"],
                "description_ja": "高リスク取引相手との関連性",
                "description_en": "Association with high-risk entities"
            },
            "volume_risk": {
                "score": volume_score,
                "weight": self.weights["volume_risk"],
                "contribution": volume_score * self.weights["volume_risk"],
                "description_ja": "取引量ベースのリスク",
                "description_en": "Volume-based risk assessment"
            },
            "age_risk": {
                "score": age_score,
                "weight": self.weights["age_risk"],
                "contribution": age_score * self.weights["age_risk"],
                "description_ja": "アドレス年齢と活動パターン",
                "description_en": "Address age and activity pattern"
            }
        }
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            total_score,
            risk_level,
            detected_patterns,
            detected_anomalies
        )
        
        result = {
            "address": address,
            "risk_score": round(total_score, 2),
            "risk_level": risk_level,
            "risk_level_ja": self._translate_risk_level(risk_level, "ja"),
            "risk_level_en": self._translate_risk_level(risk_level, "en"),
            "breakdown": breakdown,
            "total_patterns_detected": len(detected_patterns),
            "total_anomalies_detected": len(detected_anomalies),
            "recommendations": recommendations,
            "assessed_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Calculated risk score for {address}: {total_score} ({risk_level})")
        return result
    
    def _calculate_pattern_risk(
        self,
        detected_patterns: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate risk score based on detected patterns
        
        Args:
            detected_patterns: List of detected patterns
        
        Returns:
            Risk score (0-100)
        """
        if not detected_patterns:
            return 0.0
        
        # Weight patterns by risk level and confidence
        risk_weights = {
            "critical": 1.0,
            "high": 0.75,
            "medium": 0.5,
            "low": 0.25
        }
        
        total_risk = 0.0
        for pattern in detected_patterns:
            risk_level = pattern.get("risk_level", "medium")
            confidence = pattern.get("confidence", 0.5)
            
            pattern_risk = risk_weights.get(risk_level, 0.5) * confidence
            total_risk += pattern_risk
        
        # Normalize to 0-100 scale
        # Multiple patterns increase risk, but cap at 100
        score = min(total_risk * 50, 100)
        
        return round(score, 2)
    
    def _calculate_anomaly_risk(
        self,
        detected_anomalies: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate risk score based on detected anomalies
        
        Args:
            detected_anomalies: List of detected anomalies
        
        Returns:
            Risk score (0-100)
        """
        if not detected_anomalies:
            return 0.0
        
        severity_weights = {
            "critical": 1.0,
            "high": 0.75,
            "medium": 0.5,
            "low": 0.25
        }
        
        total_risk = 0.0
        for anomaly in detected_anomalies:
            severity = anomaly.get("severity", "medium")
            anomaly_risk = severity_weights.get(severity, 0.5)
            total_risk += anomaly_risk
        
        # Normalize to 0-100 scale
        score = min(total_risk * 30, 100)
        
        return round(score, 2)
    
    def _calculate_counterparty_risk(
        self,
        transactions: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate risk based on counterparty interactions
        
        Args:
            transactions: List of transactions
        
        Returns:
            Risk score (0-100)
        """
        if not transactions:
            return 0.0
        
        # Known high-risk entities (simplified - would be in database in production)
        known_high_risk = set([
            "0xd90e2f925DA726b50C4Ed8D0Fb90Ad053324F31b",  # Tornado Cash
            "0x47CE0C6eD5B0Ce3d3A51fdb1C52DC66a7c3c2936",  # Tornado Cash
            # Add more known addresses
        ])
        
        high_risk_interactions = 0
        total_interactions = 0
        
        for tx in transactions:
            from_addr = tx.get("from", "").lower()
            to_addr = tx.get("to", "").lower()
            
            total_interactions += 1
            
            if from_addr in known_high_risk or to_addr in known_high_risk:
                high_risk_interactions += 1
        
        if total_interactions == 0:
            return 0.0
        
        # Calculate risk ratio
        risk_ratio = high_risk_interactions / total_interactions
        
        # Convert to 0-100 scale
        score = risk_ratio * 100
        
        return round(score, 2)
    
    def _calculate_volume_risk(
        self,
        transactions: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate risk based on transaction volume
        
        Args:
            transactions: List of transactions
        
        Returns:
            Risk score (0-100)
        """
        if not transactions:
            return 0.0
        
        total_volume = sum(tx.get("value", 0) for tx in transactions)
        transaction_count = len(transactions)
        
        # Risk thresholds (in ETH)
        volume_thresholds = {
            "very_high": 1000,  # > 1000 ETH
            "high": 100,        # > 100 ETH
            "medium": 10,       # > 10 ETH
            "low": 1            # > 1 ETH
        }
        
        # Calculate volume risk
        if total_volume > volume_thresholds["very_high"]:
            volume_risk = 80
        elif total_volume > volume_thresholds["high"]:
            volume_risk = 60
        elif total_volume > volume_thresholds["medium"]:
            volume_risk = 40
        elif total_volume > volume_thresholds["low"]:
            volume_risk = 20
        else:
            volume_risk = 10
        
        # Adjust for transaction count (more transactions = potentially higher risk)
        if transaction_count > 1000:
            volume_risk = min(volume_risk * 1.2, 100)
        elif transaction_count > 100:
            volume_risk = min(volume_risk * 1.1, 100)
        
        return round(volume_risk, 2)
    
    def _calculate_age_risk(
        self,
        transactions: List[Dict[str, Any]],
        address_metadata: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Calculate risk based on address age and activity pattern
        
        Args:
            transactions: List of transactions
            address_metadata: Additional metadata
        
        Returns:
            Risk score (0-100)
        """
        if not transactions:
            return 50.0  # Unknown age = medium risk
        
        # Sort transactions by timestamp
        sorted_txs = sorted(
            transactions,
            key=lambda x: x.get("timestamp", "")
        )
        
        if not sorted_txs:
            return 50.0
        
        # Calculate address age
        first_tx = sorted_txs[0].get("timestamp")
        last_tx = sorted_txs[-1].get("timestamp")
        
        if isinstance(first_tx, str):
            first_tx = datetime.fromisoformat(first_tx.replace('Z', '+00:00'))
        if isinstance(last_tx, str):
            last_tx = datetime.fromisoformat(last_tx.replace('Z', '+00:00'))
        
        age_days = (datetime.utcnow() - first_tx).days
        activity_days = (last_tx - first_tx).days + 1
        
        # New addresses are higher risk
        if age_days < 7:
            age_risk = 80  # Very new
        elif age_days < 30:
            age_risk = 60  # New
        elif age_days < 90:
            age_risk = 40  # Relatively new
        elif age_days < 365:
            age_risk = 20  # Established
        else:
            age_risk = 10  # Old/trusted
        
        # Inactive addresses are also risky (dormant then suddenly active)
        inactivity_ratio = (datetime.utcnow() - last_tx).days / max(age_days, 1)
        if inactivity_ratio > 0.5:  # More than 50% of life inactive
            age_risk = min(age_risk * 1.3, 100)
        
        return round(age_risk, 2)
    
    def _determine_risk_level(self, score: float) -> str:
        """
        Determine categorical risk level from numerical score
        
        Args:
            score: Numerical risk score (0-100)
        
        Returns:
            Risk level category
        """
        if score >= 80:
            return "critical"
        elif score >= 60:
            return "high"
        elif score >= 40:
            return "medium"
        elif score >= 20:
            return "low"
        else:
            return "minimal"
    
    def _translate_risk_level(self, risk_level: str, language: str) -> str:
        """
        Translate risk level to specified language
        
        Args:
            risk_level: Risk level in English
            language: Target language ("ja" or "en")
        
        Returns:
            Translated risk level
        """
        translations = {
            "ja": {
                "critical": "極めて高い",
                "high": "高い",
                "medium": "中程度",
                "low": "低い",
                "minimal": "極めて低い"
            },
            "en": {
                "critical": "Critical",
                "high": "High",
                "medium": "Medium",
                "low": "Low",
                "minimal": "Minimal"
            }
        }
        
        return translations.get(language, {}).get(risk_level, risk_level)
    
    def _generate_recommendations(
        self,
        score: float,
        risk_level: str,
        detected_patterns: List[Dict[str, Any]],
        detected_anomalies: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """
        Generate actionable recommendations based on risk assessment
        
        Args:
            score: Risk score
            risk_level: Risk level category
            detected_patterns: Detected patterns
            detected_anomalies: Detected anomalies
        
        Returns:
            Recommendations in Japanese and English
        """
        recommendations_ja = []
        recommendations_en = []
        
        if risk_level == "critical":
            recommendations_ja.append("即座に法執行機関への通報を検討してください")
            recommendations_ja.append("関連する全ての取引を詳細に調査してください")
            recommendations_ja.append("このアドレスとの取引を直ちに停止してください")
            
            recommendations_en.append("Consider immediate reporting to law enforcement")
            recommendations_en.append("Conduct detailed investigation of all related transactions")
            recommendations_en.append("Cease all transactions with this address immediately")
        
        elif risk_level == "high":
            recommendations_ja.append("詳細な調査を実施してください")
            recommendations_ja.append("このアドレスを監視リストに追加してください")
            recommendations_ja.append("上級管理職に報告してください")
            
            recommendations_en.append("Conduct detailed investigation")
            recommendations_en.append("Add this address to monitoring watchlist")
            recommendations_en.append("Report to senior management")
        
        elif risk_level == "medium":
            recommendations_ja.append("継続的な監視を推奨します")
            recommendations_ja.append("追加の取引履歴を確認してください")
            
            recommendations_en.append("Continued monitoring recommended")
            recommendations_en.append("Review additional transaction history")
        
        # Pattern-specific recommendations
        if any(p.get("pattern_id") == "mixing" for p in detected_patterns):
            recommendations_ja.append("ミキシングサービスの使用が確認されました - 高リスク")
            recommendations_en.append("Mixing service usage confirmed - high risk")
        
        if any(p.get("pattern_id") == "layering" for p in detected_patterns):
            recommendations_ja.append("レイヤリングパターンが検出されました - 資金源の追跡を強化してください")
            recommendations_en.append("Layering pattern detected - enhance source tracking")
        
        return {
            "ja": recommendations_ja,
            "en": recommendations_en
        }
