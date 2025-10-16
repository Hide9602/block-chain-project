"""
Anomaly Detector for blockchain transactions
ブロックチェーン取引の異常検知
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import math

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Statistical anomaly detector for blockchain transactions
    統計的手法によるブロックチェーン取引の異常検知
    """
    
    def __init__(self, z_score_threshold: float = 3.0):
        """
        Initialize anomaly detector
        
        Args:
            z_score_threshold: Z-score threshold for anomaly detection (default: 3.0)
        """
        self.z_score_threshold = z_score_threshold
        logger.info(f"Initialized AnomalyDetector with z-score threshold: {z_score_threshold}")
    
    def detect_anomalies(
        self,
        transactions: List[Dict[str, Any]],
        address: str
    ) -> List[Dict[str, Any]]:
        """
        Detect all types of anomalies in transactions
        
        Args:
            transactions: List of transaction dictionaries
            address: Target address for analysis
        
        Returns:
            List of detected anomalies with details
        """
        anomalies = []
        
        # Amount anomalies
        amount_anomalies = self._detect_amount_anomalies(transactions, address)
        anomalies.extend(amount_anomalies)
        
        # Frequency anomalies
        frequency_anomalies = self._detect_frequency_anomalies(transactions, address)
        anomalies.extend(frequency_anomalies)
        
        # Time pattern anomalies
        time_anomalies = self._detect_time_anomalies(transactions, address)
        anomalies.extend(time_anomalies)
        
        # Counterparty anomalies
        counterparty_anomalies = self._detect_counterparty_anomalies(transactions, address)
        anomalies.extend(counterparty_anomalies)
        
        logger.info(f"Detected {len(anomalies)} anomalies for address {address}")
        return anomalies
    
    def _detect_amount_anomalies(
        self,
        transactions: List[Dict[str, Any]],
        address: str
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalous transaction amounts using z-score
        金額の異常検知（Z-scoreを使用）
        """
        amounts = [tx.get("value", 0) for tx in transactions]
        
        if len(amounts) < 10:  # Need sufficient data
            return []
        
        mean = statistics.mean(amounts)
        stdev = statistics.pstdev(amounts)
        
        if stdev == 0:  # All amounts are the same
            return []
        
        anomalies = []
        for tx in transactions:
            amount = tx.get("value", 0)
            z_score = (amount - mean) / stdev
            
            if abs(z_score) > self.z_score_threshold:
                anomalies.append({
                    "type": "amount_anomaly",
                    "type_ja": "金額異常",
                    "type_en": "Amount Anomaly",
                    "severity": "high" if abs(z_score) > 4.0 else "medium",
                    "description_ja": f"通常と大きく異なる取引金額（Z-score: {z_score:.2f}）",
                    "description_en": f"Transaction amount significantly different from normal (Z-score: {z_score:.2f})",
                    "transaction_hash": tx.get("hash"),
                    "amount": amount,
                    "z_score": z_score,
                    "mean": mean,
                    "stdev": stdev,
                    "timestamp": tx.get("timestamp")
                })
        
        return anomalies
    
    def _detect_frequency_anomalies(
        self,
        transactions: List[Dict[str, Any]],
        address: str
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalous transaction frequencies
        取引頻度の異常検知
        """
        # Group transactions by day
        daily_counts = defaultdict(int)
        
        for tx in transactions:
            timestamp = tx.get("timestamp")
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            date_key = timestamp.date()
            daily_counts[date_key] += 1
        
        if len(daily_counts) < 7:  # Need at least a week of data
            return []
        
        counts = list(daily_counts.values())
        mean = statistics.mean(counts)
        stdev = statistics.pstdev(counts)
        
        if stdev == 0:
            return []
        
        anomalies = []
        for date, count in daily_counts.items():
            z_score = (count - mean) / stdev
            
            if z_score > self.z_score_threshold:
                anomalies.append({
                    "type": "frequency_anomaly",
                    "type_ja": "頻度異常",
                    "type_en": "Frequency Anomaly",
                    "severity": "high" if z_score > 4.0 else "medium",
                    "description_ja": f"異常に高い取引頻度（Z-score: {z_score:.2f}）",
                    "description_en": f"Abnormally high transaction frequency (Z-score: {z_score:.2f})",
                    "date": date.isoformat(),
                    "transaction_count": count,
                    "z_score": z_score,
                    "mean": mean,
                    "stdev": stdev
                })
        
        return anomalies
    
    def _detect_time_anomalies(
        self,
        transactions: List[Dict[str, Any]],
        address: str
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalous time patterns (e.g., unusual hours)
        時間パターンの異常検知（例：異常な時間帯）
        """
        # Group transactions by hour of day
        hourly_counts = defaultdict(int)
        
        for tx in transactions:
            timestamp = tx.get("timestamp")
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            hour = timestamp.hour
            hourly_counts[hour] += 1
        
        if len(hourly_counts) < 6:  # Need sufficient diversity
            return []
        
        counts = list(hourly_counts.values())
        mean = statistics.mean(counts)
        stdev = statistics.pstdev(counts)
        
        if stdev == 0:
            return []
        
        anomalies = []
        
        # Check for unusual activity in off-peak hours (1-5 AM)
        off_peak_hours = [1, 2, 3, 4, 5]
        off_peak_total = sum(hourly_counts.get(h, 0) for h in off_peak_hours)
        total_transactions = sum(hourly_counts.values())
        
        if total_transactions > 0:
            off_peak_ratio = off_peak_total / total_transactions
            
            if off_peak_ratio > 0.4:  # More than 40% during off-peak
                anomalies.append({
                    "type": "time_pattern_anomaly",
                    "type_ja": "時間パターン異常",
                    "type_en": "Time Pattern Anomaly",
                    "severity": "medium",
                    "description_ja": f"深夜時間帯（1-5時）に異常に多い取引（{off_peak_ratio*100:.1f}%）",
                    "description_en": f"Abnormally high activity during off-peak hours 1-5 AM ({off_peak_ratio*100:.1f}%)",
                    "off_peak_ratio": off_peak_ratio,
                    "off_peak_count": off_peak_total,
                    "total_count": total_transactions
                })
        
        return anomalies
    
    def _detect_counterparty_anomalies(
        self,
        transactions: List[Dict[str, Any]],
        address: str
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalous counterparty patterns
        取引相手の異常パターン検知
        """
        # Count interactions per counterparty
        counterparty_counts = defaultdict(int)
        counterparty_amounts = defaultdict(float)
        
        for tx in transactions:
            from_addr = tx.get("from", "").lower()
            to_addr = tx.get("to", "").lower()
            amount = tx.get("value", 0)
            
            counterparty = to_addr if from_addr == address.lower() else from_addr
            counterparty_counts[counterparty] += 1
            counterparty_amounts[counterparty] += amount
        
        if len(counterparty_counts) < 5:  # Need sufficient counterparties
            return []
        
        counts = list(counterparty_counts.values())
        amounts = list(counterparty_amounts.values())
        
        mean_count = statistics.mean(counts)
        stdev_count = statistics.pstdev(counts)
        
        anomalies = []
        
        # Detect highly concentrated trading relationships
        if stdev_count > 0:
            for counterparty, count in counterparty_counts.items():
                z_score = (count - mean_count) / stdev_count
                
                if z_score > self.z_score_threshold:
                    total_amount = counterparty_amounts[counterparty]
                    
                    anomalies.append({
                        "type": "counterparty_concentration",
                        "type_ja": "取引相手集中",
                        "type_en": "Counterparty Concentration",
                        "severity": "medium",
                        "description_ja": f"特定アドレスとの異常に多い取引（Z-score: {z_score:.2f}）",
                        "description_en": f"Abnormally high concentration with specific address (Z-score: {z_score:.2f})",
                        "counterparty": counterparty,
                        "transaction_count": count,
                        "total_amount": total_amount,
                        "z_score": z_score,
                        "mean": mean_count,
                        "stdev": stdev_count
                    })
        
        # Detect one-time large transactions (potential rug pull indicator)
        for counterparty, count in counterparty_counts.items():
            if count == 1:  # Only one transaction
                amount = counterparty_amounts[counterparty]
                if amount > statistics.mean(amounts) * 2:  # Significantly larger than average
                    anomalies.append({
                        "type": "one_time_large_transaction",
                        "type_ja": "一回限りの大口取引",
                        "type_en": "One-time Large Transaction",
                        "severity": "high",
                        "description_ja": "新規アドレスとの一回限りの大口取引",
                        "description_en": "One-time large transaction with new address",
                        "counterparty": counterparty,
                        "amount": amount,
                        "average_amount": statistics.mean(amounts)
                    })
        
        return anomalies
    
    def calculate_anomaly_score(
        self,
        anomalies: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate overall anomaly score from detected anomalies
        
        Args:
            anomalies: List of detected anomalies
        
        Returns:
            Anomaly score between 0 and 100
        """
        if not anomalies:
            return 0.0
        
        severity_weights = {
            "critical": 1.0,
            "high": 0.75,
            "medium": 0.5,
            "low": 0.25
        }
        
        total_weight = 0.0
        for anomaly in anomalies:
            severity = anomaly.get("severity", "medium")
            total_weight += severity_weights.get(severity, 0.5)
        
        # Normalize to 0-100 scale
        # More anomalies and higher severity = higher score
        score = min(total_weight * 10, 100)
        
        return round(score, 2)
    
    def get_anomaly_summary(
        self,
        anomalies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate summary statistics for anomalies
        
        Args:
            anomalies: List of detected anomalies
        
        Returns:
            Summary dictionary with counts and severity breakdown
        """
        type_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        
        for anomaly in anomalies:
            anomaly_type = anomaly.get("type", "unknown")
            severity = anomaly.get("severity", "medium")
            
            type_counts[anomaly_type] += 1
            severity_counts[severity] += 1
        
        return {
            "total_anomalies": len(anomalies),
            "anomaly_score": self.calculate_anomaly_score(anomalies),
            "by_type": dict(type_counts),
            "by_severity": dict(severity_counts),
            "has_critical": severity_counts.get("critical", 0) > 0,
            "has_high": severity_counts.get("high", 0) > 0
        }
