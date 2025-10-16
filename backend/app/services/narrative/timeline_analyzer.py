"""
Timeline Analyzer for temporal pattern analysis
時系列パターン分析のためのタイムラインアナライザー
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class TimelineAnalyzer:
    """
    Analyze temporal patterns in transactions
    取引の時系列パターンを分析
    """
    
    def __init__(self):
        """Initialize timeline analyzer"""
        logger.info("Initialized TimelineAnalyzer")
    
    def analyze_timeline(
        self,
        transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive timeline analysis
        
        Args:
            transactions: List of transactions
        
        Returns:
            Timeline analysis results
        """
        if not transactions:
            return {
                "time_span": {},
                "activity_periods": [],
                "frequency_pattern": {},
                "velocity_analysis": {}
            }
        
        # Sort by timestamp
        sorted_txs = self._sort_by_timestamp(transactions)
        
        # Analyze different aspects
        time_span = self._calculate_time_span(sorted_txs)
        activity_periods = self._identify_activity_periods(sorted_txs)
        frequency_pattern = self._analyze_frequency(sorted_txs)
        velocity_analysis = self._analyze_velocity(sorted_txs)
        
        return {
            "time_span": time_span,
            "activity_periods": activity_periods,
            "frequency_pattern": frequency_pattern,
            "velocity_analysis": velocity_analysis
        }
    
    def _sort_by_timestamp(
        self,
        transactions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Sort transactions by timestamp"""
        def get_timestamp(tx):
            ts = tx.get("timestamp")
            if isinstance(ts, str):
                return datetime.fromisoformat(ts.replace('Z', '+00:00'))
            return ts or datetime.min
        
        return sorted(transactions, key=get_timestamp)
    
    def _calculate_time_span(
        self,
        sorted_transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate time span of transaction activity
        
        Args:
            sorted_transactions: Transactions sorted by timestamp
        
        Returns:
            Time span information
        """
        if not sorted_transactions:
            return {}
        
        timestamps = []
        for tx in sorted_transactions:
            ts = tx.get("timestamp")
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            if ts:
                timestamps.append(ts)
        
        if not timestamps:
            return {}
        
        first = min(timestamps)
        last = max(timestamps)
        duration = (last - first).total_seconds()
        
        return {
            "first_transaction": first.isoformat(),
            "last_transaction": last.isoformat(),
            "duration_seconds": duration,
            "duration_days": duration / 86400,
            "duration_hours": duration / 3600
        }
    
    def _identify_activity_periods(
        self,
        sorted_transactions: List[Dict[str, Any]],
        burst_threshold_seconds: int = 3600  # 1 hour
    ) -> List[Dict[str, Any]]:
        """
        Identify burst periods of activity
        
        Args:
            sorted_transactions: Transactions sorted by timestamp
            burst_threshold_seconds: Gap to define new burst period
        
        Returns:
            List of activity periods
        """
        if not sorted_transactions:
            return []
        
        periods = []
        current_period = {
            "transactions": [],
            "start_time": None,
            "end_time": None
        }
        
        for tx in sorted_transactions:
            ts = tx.get("timestamp")
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            
            if not ts:
                continue
            
            # Start new period if first transaction
            if not current_period["start_time"]:
                current_period["start_time"] = ts
                current_period["end_time"] = ts
                current_period["transactions"].append(tx)
                continue
            
            # Check if still in current period
            time_gap = (ts - current_period["end_time"]).total_seconds()
            
            if time_gap <= burst_threshold_seconds:
                # Continue current period
                current_period["end_time"] = ts
                current_period["transactions"].append(tx)
            else:
                # Finalize current period
                if current_period["transactions"]:
                    periods.append(self._summarize_period(current_period))
                
                # Start new period
                current_period = {
                    "transactions": [tx],
                    "start_time": ts,
                    "end_time": ts
                }
        
        # Add last period
        if current_period["transactions"]:
            periods.append(self._summarize_period(current_period))
        
        return periods
    
    def _summarize_period(
        self,
        period: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Summarize an activity period"""
        duration = (period["end_time"] - period["start_time"]).total_seconds()
        
        total_amount = sum(tx.get("value", 0.0) for tx in period["transactions"])
        transaction_count = len(period["transactions"])
        
        return {
            "start_time": period["start_time"].isoformat(),
            "end_time": period["end_time"].isoformat(),
            "duration_seconds": duration,
            "transaction_count": transaction_count,
            "total_amount": total_amount,
            "average_amount": total_amount / transaction_count if transaction_count > 0 else 0,
            "intensity": transaction_count / (duration / 60) if duration > 0 else transaction_count  # txs per minute
        }
    
    def _analyze_frequency(
        self,
        sorted_transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze transaction frequency patterns
        
        Args:
            sorted_transactions: Transactions sorted by timestamp
        
        Returns:
            Frequency analysis
        """
        if not sorted_transactions:
            return {}
        
        # Group by day
        daily_counts = defaultdict(int)
        daily_amounts = defaultdict(float)
        
        # Group by hour of day
        hourly_distribution = defaultdict(int)
        
        for tx in sorted_transactions:
            ts = tx.get("timestamp")
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            
            if not ts:
                continue
            
            # Daily grouping
            date_key = ts.date().isoformat()
            daily_counts[date_key] += 1
            daily_amounts[date_key] += tx.get("value", 0.0)
            
            # Hourly distribution
            hourly_distribution[ts.hour] += 1
        
        # Calculate statistics
        counts = list(daily_counts.values())
        avg_daily_count = statistics.mean(counts) if counts else 0
        
        # Identify peak hours (off-hours: 1-5 AM are suspicious)
        off_hours_count = sum(hourly_distribution[h] for h in range(1, 6))
        total_count = sum(hourly_distribution.values())
        off_hours_ratio = off_hours_count / total_count if total_count > 0 else 0
        
        return {
            "total_transactions": len(sorted_transactions),
            "active_days": len(daily_counts),
            "average_daily_transactions": avg_daily_count,
            "max_daily_transactions": max(counts) if counts else 0,
            "off_hours_count": off_hours_count,
            "off_hours_ratio": off_hours_ratio,
            "hourly_distribution": dict(hourly_distribution)
        }
    
    def _analyze_velocity(
        self,
        sorted_transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze transaction velocity (time between transactions)
        
        Args:
            sorted_transactions: Transactions sorted by timestamp
        
        Returns:
            Velocity analysis
        """
        if len(sorted_transactions) < 2:
            return {}
        
        intervals = []
        rapid_movements = []  # Movements < 10 minutes
        
        for i in range(1, len(sorted_transactions)):
            prev_tx = sorted_transactions[i - 1]
            curr_tx = sorted_transactions[i]
            
            prev_ts = prev_tx.get("timestamp")
            curr_ts = curr_tx.get("timestamp")
            
            if isinstance(prev_ts, str):
                prev_ts = datetime.fromisoformat(prev_ts.replace('Z', '+00:00'))
            if isinstance(curr_ts, str):
                curr_ts = datetime.fromisoformat(curr_ts.replace('Z', '+00:00'))
            
            if not prev_ts or not curr_ts:
                continue
            
            interval_seconds = (curr_ts - prev_ts).total_seconds()
            intervals.append(interval_seconds)
            
            # Check for rapid movement (< 10 minutes)
            if interval_seconds < 600:
                rapid_movements.append({
                    "from_tx": prev_tx.get("hash"),
                    "to_tx": curr_tx.get("hash"),
                    "interval_seconds": interval_seconds,
                    "interval_minutes": interval_seconds / 60
                })
        
        if not intervals:
            return {}
        
        avg_interval = statistics.mean(intervals)
        median_interval = statistics.median(intervals)
        min_interval = min(intervals)
        
        return {
            "average_interval_seconds": avg_interval,
            "average_interval_minutes": avg_interval / 60,
            "median_interval_seconds": median_interval,
            "median_interval_minutes": median_interval / 60,
            "min_interval_seconds": min_interval,
            "min_interval_minutes": min_interval / 60,
            "rapid_movements_count": len(rapid_movements),
            "rapid_movements": rapid_movements[:10]  # Top 10
        }
    
    def identify_temporal_anomalies(
        self,
        timeline_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Identify temporal anomalies based on timeline analysis
        
        Args:
            timeline_analysis: Results from analyze_timeline()
        
        Returns:
            List of temporal anomalies detected
        """
        anomalies = []
        
        freq = timeline_analysis.get("frequency_pattern", {})
        velocity = timeline_analysis.get("velocity_analysis", {})
        
        # Check for off-hours activity
        off_hours_ratio = freq.get("off_hours_ratio", 0)
        if off_hours_ratio > 0.3:
            anomalies.append({
                "type": "off_hours_activity",
                "severity": "medium" if off_hours_ratio < 0.5 else "high",
                "description_ja": f"深夜早朝（1-5時）の取引が全体の{off_hours_ratio * 100:.1f}%を占めています。",
                "description_en": f"Off-hours (1-5 AM) transactions account for {off_hours_ratio * 100:.1f}% of total activity.",
                "value": off_hours_ratio
            })
        
        # Check for rapid movements
        rapid_count = velocity.get("rapid_movements_count", 0)
        total_txs = freq.get("total_transactions", 1)
        rapid_ratio = rapid_count / total_txs
        
        if rapid_ratio > 0.2:
            avg_interval = velocity.get("average_interval_minutes", 0)
            anomalies.append({
                "type": "rapid_movement",
                "severity": "high" if rapid_ratio > 0.5 else "medium",
                "description_ja": f"受取後{avg_interval:.1f}分以内の高速転送が{rapid_count}件検出されました。",
                "description_en": f"Detected {rapid_count} rapid transfers within {avg_interval:.1f} minutes of receipt.",
                "value": rapid_ratio
            })
        
        # Check for burst activity
        periods = timeline_analysis.get("activity_periods", [])
        if len(periods) > 0:
            high_intensity_periods = [p for p in periods if p.get("intensity", 0) > 5]  # > 5 txs/minute
            if high_intensity_periods:
                anomalies.append({
                    "type": "burst_activity",
                    "severity": "medium",
                    "description_ja": f"{len(high_intensity_periods)}回の集中的な取引バースト（毎分5件以上）が検出されました。",
                    "description_en": f"Detected {len(high_intensity_periods)} intense transaction bursts (>5 txs/minute).",
                    "value": len(high_intensity_periods)
                })
        
        return anomalies
