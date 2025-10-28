"""
Narrative Generator for automatic fund flow story generation
資金フローの自動ストーリー生成
"""
import json
import logging
import random
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from .graph_analyzer import GraphAnalyzer
from .timeline_analyzer import TimelineAnalyzer

logger = logging.getLogger(__name__)


class NarrativeGenerator:
    """
    Generate natural language narratives for transaction analysis
    取引分析のための自然言語ナラティブを生成
    """
    
    def __init__(self, templates_path: Optional[str] = None):
        """
        Initialize narrative generator
        
        Args:
            templates_path: Path to templates JSON file
        """
        if templates_path is None:
            templates_path = Path(__file__).parent / "narrative_templates.json"
        
        # Load templates
        with open(templates_path, "r", encoding="utf-8") as f:
            self.templates_data = json.load(f)
        
        self.templates = self.templates_data["templates"]
        self.risk_translations = self.templates_data["risk_level_translations"]
        self.pattern_translations = self.templates_data["pattern_translations"]
        self.timeframe_translations = self.templates_data["timeframe_translations"]
        
        # Initialize analyzers
        self.graph_analyzer = GraphAnalyzer()
        self.timeline_analyzer = TimelineAnalyzer()
        
        logger.info("Initialized NarrativeGenerator")
    
    def generate_narrative(
        self,
        address: str,
        transactions: List[Dict[str, Any]],
        detected_patterns: List[Dict[str, Any]],
        detected_anomalies: List[Dict[str, Any]],
        risk_assessment: Dict[str, Any],
        language: str = "ja"
    ) -> str:
        """
        Generate comprehensive narrative for investigation
        
        Args:
            address: Address being investigated
            transactions: List of transactions
            detected_patterns: Patterns detected by PatternMatcher
            detected_anomalies: Anomalies detected by AnomalyDetector
            risk_assessment: Risk assessment from RiskScorer
            language: Language for narrative (ja or en)
        
        Returns:
            Generated narrative text
        """
        if language not in ["ja", "en"]:
            language = "ja"
        
        # Analyze structure
        graph = self.graph_analyzer.build_graph(transactions, address)
        flow_analysis = self.graph_analyzer.analyze_flow_pattern(graph, address)
        timeline_analysis = self.timeline_analyzer.analyze_timeline(transactions)
        
        # Build narrative sections
        sections = []
        
        # 1. Opening
        sections.append(self._generate_opening(
            address, transactions, timeline_analysis, language
        ))
        
        # 2. Transaction overview
        sections.append(self._generate_transaction_overview(
            transactions, timeline_analysis, language
        ))
        
        # 3. Pattern descriptions
        if detected_patterns:
            sections.append(self._generate_pattern_narratives(
                detected_patterns, transactions, graph, language
            ))
        
        # 4. Anomaly descriptions
        if detected_anomalies:
            sections.append(self._generate_anomaly_narratives(
                detected_anomalies, language
            ))
        
        # 5. Flow analysis
        if flow_analysis.get("has_suspicious_flow"):
            sections.append(self._generate_flow_narrative(
                flow_analysis, graph, address, language
            ))
        
        # 6. Risk assessment
        sections.append(self._generate_risk_assessment(
            risk_assessment, detected_patterns, language
        ))
        
        # 7. Conclusion
        sections.append(self._generate_conclusion(
            risk_assessment, detected_patterns, language
        ))
        
        # Join all sections
        if language == "ja":
            narrative = "\n\n".join(sections)
        else:
            narrative = "\n\n".join(sections)
        
        return narrative
    
    def _generate_opening(
        self,
        address: str,
        transactions: List[Dict[str, Any]],
        timeline_analysis: Dict[str, Any],
        language: str
    ) -> str:
        """Generate opening paragraph"""
        template = random.choice(self.templates[language]["opening"])
        
        time_span = timeline_analysis.get("time_span", {})
        first_tx = time_span.get("first_transaction", "")
        
        if first_tx:
            timestamp = self._format_timestamp(first_tx, language)
        else:
            timestamp = "最近" if language == "ja" else "Recently"
        
        return template.format(
            timestamp=timestamp,
            address=self._format_address(address)
        )
    
    def _generate_transaction_overview(
        self,
        transactions: List[Dict[str, Any]],
        timeline_analysis: Dict[str, Any],
        language: str
    ) -> str:
        """Generate transaction overview"""
        total_count = len(transactions)
        total_amount = sum(tx.get("value", 0.0) for tx in transactions)
        
        time_span = timeline_analysis.get("time_span", {})
        duration_days = time_span.get("duration_days", 0)
        
        freq = timeline_analysis.get("frequency_pattern", {})
        avg_daily = freq.get("average_daily_transactions", 0)
        
        if language == "ja":
            overview = f"分析期間中に合計{total_count}件の取引が確認され、"
            overview += f"総取引額は{total_amount:.4f} ETHに達しています。"
            if duration_days > 0:
                overview += f"調査対象期間は{duration_days:.1f}日間にわたり、"
                overview += f"1日あたり平均{avg_daily:.1f}件の取引が実行されました。"
        else:
            overview = f"During the analysis period, a total of {total_count} transactions were confirmed, "
            overview += f"with a total transaction volume of {total_amount:.4f} ETH. "
            if duration_days > 0:
                overview += f"The investigation period spans {duration_days:.1f} days, "
                overview += f"with an average of {avg_daily:.1f} transactions per day executed."
        
        return overview
    
    def _generate_pattern_narratives(
        self,
        detected_patterns: List[Dict[str, Any]],
        transactions: List[Dict[str, Any]],
        graph: Dict[str, Any],
        language: str
    ) -> str:
        """Generate narratives for detected patterns"""
        narratives = []
        
        for pattern in detected_patterns:
            pattern_id = pattern.get("pattern_id", "")
            confidence = pattern.get("confidence", 0)
            details = pattern.get("details", {})
            
            # Select appropriate template
            narrative = self._generate_pattern_specific_narrative(
                pattern_id, details, language
            )
            
            if narrative:
                narratives.append(narrative)
        
        if not narratives:
            return ""
        
        if language == "ja":
            header = "【検出されたパターン】\n"
        else:
            header = "[Detected Patterns]\n"
        
        return header + "\n".join(narratives)
    
    def _generate_pattern_specific_narrative(
        self,
        pattern_id: str,
        details: Dict[str, Any],
        language: str
    ) -> str:
        """Generate narrative for specific pattern"""
        if pattern_id == "smurfing":
            return self._generate_smurfing_narrative(details, language)
        elif pattern_id == "layering":
            return self._generate_layering_narrative(details, language)
        elif pattern_id == "mixing":
            return self._generate_mixing_narrative(details, language)
        elif pattern_id == "rapid_movement":
            return self._generate_rapid_movement_narrative(details, language)
        elif pattern_id == "circular_trading":
            return self._generate_circular_narrative(details, language)
        
        return ""
    
    def _generate_smurfing_narrative(
        self,
        details: Dict[str, Any],
        language: str
    ) -> str:
        """Generate smurfing pattern narrative"""
        template = random.choice(self.templates[language]["smurfing"])
        
        tx_count = details.get("transaction_count", 0)
        avg_amount = details.get("average_amount", 0)
        timeframe_hours = details.get("timeframe_hours", 1)
        
        timeframe = self._format_timeframe(timeframe_hours, language)
        
        return template.format(
            timeframe=timeframe,
            transaction_count=tx_count,
            avg_amount=f"{avg_amount:.4f}",
            currency="ETH"
        )
    
    def _generate_layering_narrative(
        self,
        details: Dict[str, Any],
        language: str
    ) -> str:
        """Generate layering pattern narrative"""
        template = random.choice(self.templates[language]["layering"])
        
        intermediaries = details.get("intermediaries", [])
        intermediary_count = len(intermediaries)
        
        # Format intermediary addresses (show first 3)
        intermediary_str = ", ".join(
            self._format_address(addr) for addr in intermediaries[:3]
        )
        if len(intermediaries) > 3:
            intermediary_str += "..."
        
        return template.format(
            intermediary_count=intermediary_count,
            intermediaries=intermediary_str
        )
    
    def _generate_mixing_narrative(
        self,
        details: Dict[str, Any],
        language: str
    ) -> str:
        """Generate mixing pattern narrative"""
        template = random.choice(self.templates[language]["mixing"])
        
        mixer_addresses = details.get("mixer_addresses", [])
        tx_count = len(mixer_addresses)
        timeframe_hours = details.get("timeframe_hours", 24)
        
        mixer_name = "Tornado Cash"  # Simplified
        timeframe = self._format_timeframe(timeframe_hours, language)
        
        return template.format(
            timeframe=timeframe,
            mixer_name=mixer_name,
            transaction_count=tx_count
        )
    
    def _generate_rapid_movement_narrative(
        self,
        details: Dict[str, Any],
        language: str
    ) -> str:
        """Generate rapid movement pattern narrative"""
        template = random.choice(self.templates[language]["rapid_movement"])
        
        avg_interval = details.get("average_interval_minutes", 0)
        
        return template.format(
            minutes=f"{avg_interval:.0f}"
        )
    
    def _generate_circular_narrative(
        self,
        details: Dict[str, Any],
        language: str
    ) -> str:
        """Generate circular trading pattern narrative"""
        template = random.choice(self.templates[language]["circular"])
        
        hop_count = details.get("hop_count", 0)
        timeframe_hours = details.get("timeframe_hours", 24)
        
        timeframe = self._format_timeframe(timeframe_hours, language)
        
        return template.format(
            hop_count=hop_count,
            timeframe=timeframe
        )
    
    def _generate_anomaly_narratives(
        self,
        detected_anomalies: List[Dict[str, Any]],
        language: str
    ) -> str:
        """Generate narratives for detected anomalies"""
        if not detected_anomalies:
            return ""
        
        if language == "ja":
            header = "【検出された異常】\n"
        else:
            header = "[Detected Anomalies]\n"
        
        narratives = []
        for anomaly in detected_anomalies:
            anomaly_type = anomaly.get("anomaly_type", "")
            severity = anomaly.get("severity", "medium")
            details = anomaly.get("details", {})
            
            if anomaly_type == "amount":
                z_score = details.get("z_score", 0)
                amount = details.get("amount", 0)
                
                if language == "ja":
                    narrative = f"通常の取引額から大きく逸脱した{amount:.4f} ETHの取引が検出されました（Z-score: {abs(z_score):.2f}）。"
                else:
                    narrative = f"A transaction of {amount:.4f} ETH significantly deviating from normal transaction amounts was detected (Z-score: {abs(z_score):.2f})."
                
                narratives.append(narrative)
            
            elif anomaly_type == "time":
                hour = details.get("hour", 0)
                
                if language == "ja":
                    narrative = f"深夜早朝時間帯（{hour}時）に異常な取引活動が確認されました。"
                else:
                    narrative = f"Abnormal transaction activity was confirmed during off-hours ({hour}:00)."
                
                narratives.append(narrative)
        
        return header + "\n".join(narratives)
    
    def _generate_flow_narrative(
        self,
        flow_analysis: Dict[str, Any],
        graph: Dict[str, Any],
        start_address: str,
        language: str
    ) -> str:
        """Generate flow analysis narrative"""
        pattern_type = flow_analysis.get("pattern_type", "")
        avg_hops = flow_analysis.get("average_hops", 0)
        
        # Find main path
        main_paths = self.graph_analyzer.find_main_paths(graph, start_address, max_paths=1)
        
        if not main_paths:
            return ""
        
        path = main_paths[0]
        path_stats = self.graph_analyzer.calculate_path_statistics(path)
        
        total_amount = path_stats.get("total_amount", 0)
        hop_count = path_stats.get("hop_count", 0)
        
        if language == "ja":
            narrative = f"資金フロー分析の結果、{total_amount:.4f} ETHが{hop_count}段階を経て移動していることが判明しました。"
            
            if pattern_type == "complex_layering":
                narrative += "これは高度なレイヤリング手法を示唆する複雑な資金移動パターンです。"
            elif pattern_type == "moderate_layering":
                narrative += "中程度の複雑さを持つレイヤリングパターンが確認されました。"
        else:
            narrative = f"Fund flow analysis revealed that {total_amount:.4f} ETH moved through {hop_count} stages. "
            
            if pattern_type == "complex_layering":
                narrative += "This is a complex fund movement pattern suggesting advanced layering techniques."
            elif pattern_type == "moderate_layering":
                narrative += "A moderately complex layering pattern was confirmed."
        
        return narrative
    
    def _generate_risk_assessment(
        self,
        risk_assessment: Dict[str, Any],
        detected_patterns: List[Dict[str, Any]],
        language: str
    ) -> str:
        """Generate risk assessment narrative"""
        template = random.choice(self.templates[language]["risk_assessment"])
        
        risk_level = risk_assessment.get("risk_level", "medium")
        risk_score = risk_assessment.get("total_score", 0)
        
        # Get primary pattern
        pattern_name = "unknown"
        confidence = 0
        if detected_patterns:
            primary = max(detected_patterns, key=lambda p: p.get("confidence", 0))
            pattern_name = primary.get("pattern_id", "unknown")
            confidence = primary.get("confidence", 0)
        
        # Translate risk level and pattern
        risk_level_text = self.risk_translations[language].get(risk_level, risk_level)
        pattern_name_text = self.pattern_translations[language].get(pattern_name, pattern_name)
        
        return template.format(
            pattern_name=pattern_name_text,
            confidence=f"{confidence * 100:.0f}",
            risk_level=risk_level_text,
            risk_score=f"{risk_score:.1f}"
        )
    
    def _generate_conclusion(
        self,
        risk_assessment: Dict[str, Any],
        detected_patterns: List[Dict[str, Any]],
        language: str
    ) -> str:
        """Generate conclusion"""
        risk_level = risk_assessment.get("risk_level", "medium")
        
        # Choose conclusion based on risk level
        if risk_level in ["critical", "high"]:
            template = random.choice(self.templates[language]["conclusion"])
        elif detected_patterns:
            template = self.templates[language]["conclusion"][0]
        else:
            template = random.choice(self.templates[language]["no_suspicious_activity"])
        
        return template
    
    def _format_address(self, address: str) -> str:
        """Format address for display (show first 6 and last 4 chars)"""
        if len(address) > 12:
            return f"{address[:6]}...{address[-4:]}"
        return address
    
    def _format_timestamp(self, timestamp: str, language: str) -> str:
        """Format timestamp for display"""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            if language == "ja":
                return dt.strftime("%Y年%m月%d日 %H:%M")
            else:
                return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return timestamp
    
    def _format_timeframe(self, hours: float, language: str) -> str:
        """Format timeframe for display"""
        if hours < 1:
            minutes = int(hours * 60)
            return self.timeframe_translations[language]["minutes"].format(value=minutes)
        elif hours < 24:
            return self.timeframe_translations[language]["hours"].format(value=int(hours))
        elif hours < 168:
            days = int(hours / 24)
            return self.timeframe_translations[language]["days"].format(value=days)
        else:
            weeks = int(hours / 168)
            return self.timeframe_translations[language]["weeks"].format(value=weeks)
