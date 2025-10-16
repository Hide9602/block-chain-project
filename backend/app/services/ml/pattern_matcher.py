"""
Pattern Matcher for detecting money laundering patterns
マネーロンダリングパターン検出のためのパターンマッチャー
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

logger = logging.getLogger(__name__)


class PatternMatcher:
    """
    Rule-based pattern matcher for detecting suspicious transaction patterns
    ルールベースのパターンマッチャー：疑わしい取引パターンを検出
    """
    
    def __init__(self, patterns_file: Optional[str] = None):
        """
        Initialize pattern matcher
        
        Args:
            patterns_file: Path to patterns.json file
        """
        if patterns_file is None:
            patterns_file = Path(__file__).parent / "patterns.json"
        
        with open(patterns_file, 'r', encoding='utf-8') as f:
            self.patterns_config = json.load(f)
        
        self.patterns = self.patterns_config["patterns"]
        self.risk_weights = self.patterns_config["risk_weights"]
        self.confidence_thresholds = self.patterns_config["confidence_thresholds"]
        
        logger.info(f"Loaded {len(self.patterns)} patterns from {patterns_file}")
    
    def detect_patterns(
        self,
        transactions: List[Dict[str, Any]],
        address: str
    ) -> List[Dict[str, Any]]:
        """
        Detect all patterns in transaction list
        
        Args:
            transactions: List of transaction dictionaries
            address: Target address for analysis
        
        Returns:
            List of detected patterns with confidence scores
        """
        detected = []
        
        for pattern in self.patterns:
            result = self._match_pattern(pattern, transactions, address)
            if result:
                detected.append(result)
        
        logger.info(f"Detected {len(detected)} patterns for address {address}")
        return detected
    
    def _match_pattern(
        self,
        pattern: Dict[str, Any],
        transactions: List[Dict[str, Any]],
        address: str
    ) -> Optional[Dict[str, Any]]:
        """
        Match a specific pattern against transactions
        
        Args:
            pattern: Pattern definition
            transactions: List of transactions
            address: Target address
        
        Returns:
            Pattern match result or None if no match
        """
        pattern_id = pattern["id"]
        
        # Dispatch to specific pattern detector
        if pattern_id == "smurfing":
            return self._detect_smurfing(pattern, transactions, address)
        elif pattern_id == "layering":
            return self._detect_layering(pattern, transactions, address)
        elif pattern_id == "mixing":
            return self._detect_mixing(pattern, transactions, address)
        elif pattern_id == "structuring":
            return self._detect_structuring(pattern, transactions, address)
        elif pattern_id == "circular_trading":
            return self._detect_circular_trading(pattern, transactions, address)
        elif pattern_id == "rapid_movement":
            return self._detect_rapid_movement(pattern, transactions, address)
        elif pattern_id == "dusting":
            return self._detect_dusting(pattern, transactions, address)
        elif pattern_id == "peel_chain":
            return self._detect_peel_chain(pattern, transactions, address)
        
        return None
    
    def _detect_smurfing(
        self,
        pattern: Dict[str, Any],
        transactions: List[Dict[str, Any]],
        address: str
    ) -> Optional[Dict[str, Any]]:
        """
        Detect smurfing pattern: many small transactions in short period
        スマーフィング検出：短期間に多数の小額取引
        """
        # Group transactions by 1-hour windows
        time_windows = defaultdict(list)
        
        for tx in transactions:
            if tx.get("from", "").lower() != address.lower():
                continue
            
            timestamp = tx.get("timestamp")
            if not timestamp:
                continue
            
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            # Group by hour
            hour_key = timestamp.replace(minute=0, second=0, microsecond=0)
            time_windows[hour_key].append(tx)
        
        # Check each window for smurfing pattern
        for hour, txs in time_windows.items():
            if len(txs) < 10:  # Need at least 10 transactions
                continue
            
            # Check amounts are small
            amounts = [tx.get("value", 0) for tx in txs]
            if not all(amt < 1.0 for amt in amounts):
                continue
            
            # Check variance is low (similar amounts)
            if len(amounts) > 1:
                variance = statistics.pvariance(amounts)
                mean = statistics.mean(amounts)
                if mean > 0:
                    cv = (variance ** 0.5) / mean
                    if cv >= 0.3:
                        continue
            
            # Pattern detected
            confidence = min(len(txs) / 20, 1.0)  # More transactions = higher confidence
            
            return {
                "pattern_id": pattern["id"],
                "pattern_name": pattern["name"],
                "pattern_name_ja": pattern["name_ja"],
                "pattern_name_en": pattern["name_en"],
                "description_ja": pattern["description_ja"],
                "description_en": pattern["description_en"],
                "risk_level": pattern["risk_level"],
                "confidence": confidence,
                "addresses_count": len(set(tx.get("to", "") for tx in txs)),
                "total_amount": sum(amounts),
                "transaction_count": len(txs),
                "timeframe": "1 hour",
                "timestamp": hour.isoformat(),
                "evidence": {
                    "transaction_hashes": [tx.get("hash") for tx in txs[:10]],  # First 10
                    "average_amount": statistics.mean(amounts),
                    "amount_variance": variance if len(amounts) > 1 else 0
                }
            }
        
        return None
    
    def _detect_layering(
        self,
        pattern: Dict[str, Any],
        transactions: List[Dict[str, Any]],
        address: str
    ) -> Optional[Dict[str, Any]]:
        """
        Detect layering pattern: funds through multiple intermediaries
        レイヤリング検出：複数の中間アドレスを経由する資金移動
        """
        # Build transaction chains
        chains = self._build_transaction_chains(transactions, address, max_hops=10)
        
        for chain in chains:
            if len(chain) < 5:  # Need at least 5 hops
                continue
            
            # Check if chain completed within 24 hours
            first_time = chain[0].get("timestamp")
            last_time = chain[-1].get("timestamp")
            
            if isinstance(first_time, str):
                first_time = datetime.fromisoformat(first_time.replace('Z', '+00:00'))
            if isinstance(last_time, str):
                last_time = datetime.fromisoformat(last_time.replace('Z', '+00:00'))
            
            time_diff = (last_time - first_time).total_seconds()
            if time_diff > 86400:  # More than 24 hours
                continue
            
            # Check for address reuse (should be minimal)
            addresses = [tx.get("from") for tx in chain] + [tx.get("to") for tx in chain]
            if len(addresses) != len(set(addresses)):  # Duplicate addresses
                continue
            
            # Pattern detected
            confidence = min(len(chain) / 10, 1.0)
            
            return {
                "pattern_id": pattern["id"],
                "pattern_name": pattern["name"],
                "pattern_name_ja": pattern["name_ja"],
                "pattern_name_en": pattern["name_en"],
                "description_ja": pattern["description_ja"],
                "description_en": pattern["description_en"],
                "risk_level": pattern["risk_level"],
                "confidence": confidence,
                "addresses_count": len(set(addresses)),
                "total_amount": sum(tx.get("value", 0) for tx in chain),
                "hop_count": len(chain),
                "timeframe_seconds": int(time_diff),
                "evidence": {
                    "transaction_hashes": [tx.get("hash") for tx in chain],
                    "chain_addresses": addresses[:10]  # First 10 addresses
                }
            }
        
        return None
    
    def _detect_mixing(
        self,
        pattern: Dict[str, Any],
        transactions: List[Dict[str, Any]],
        address: str
    ) -> Optional[Dict[str, Any]]:
        """
        Detect mixing pattern: interaction with known mixers
        ミキシング検出：既知のミキサーとの取引
        """
        known_mixers = set(mixer.lower() for mixer in pattern.get("known_mixers", []))
        
        mixer_txs = []
        for tx in transactions:
            from_addr = tx.get("from", "").lower()
            to_addr = tx.get("to", "").lower()
            
            if from_addr in known_mixers or to_addr in known_mixers:
                mixer_txs.append(tx)
        
        if not mixer_txs:
            return None
        
        # Pattern detected - this is critical risk
        total_amount = sum(tx.get("value", 0) for tx in mixer_txs)
        
        return {
            "pattern_id": pattern["id"],
            "pattern_name": pattern["name"],
            "pattern_name_ja": pattern["name_ja"],
            "pattern_name_en": pattern["name_en"],
            "description_ja": pattern["description_ja"],
            "description_en": pattern["description_en"],
            "risk_level": pattern["risk_level"],
            "confidence": 1.0,  # Mixer detection is definitive
            "addresses_count": len(set(tx.get("to") for tx in mixer_txs)),
            "total_amount": total_amount,
            "transaction_count": len(mixer_txs),
            "evidence": {
                "transaction_hashes": [tx.get("hash") for tx in mixer_txs],
                "mixer_addresses": list(set(
                    tx.get("to") if tx.get("to", "").lower() in known_mixers
                    else tx.get("from")
                    for tx in mixer_txs
                ))
            }
        }
    
    def _detect_structuring(
        self,
        pattern: Dict[str, Any],
        transactions: List[Dict[str, Any]],
        address: str
    ) -> Optional[Dict[str, Any]]:
        """
        Detect structuring pattern: amounts just below reporting thresholds
        ストラクチャリング検出：報告閾値直下の金額
        """
        thresholds = pattern.get("reporting_thresholds", {})
        eth_threshold = thresholds.get("ETH", 10.0)
        
        # Find transactions close to threshold
        suspicious_txs = []
        for tx in transactions:
            if tx.get("from", "").lower() != address.lower():
                continue
            
            amount = tx.get("value", 0)
            if 0.9 * eth_threshold <= amount < eth_threshold:
                suspicious_txs.append(tx)
        
        if len(suspicious_txs) < 3:  # Need at least 3 occurrences
            return None
        
        # Check if pattern repeats over time (within a week)
        timestamps = []
        for tx in suspicious_txs:
            ts = tx.get("timestamp")
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            timestamps.append(ts)
        
        if timestamps:
            time_span = (max(timestamps) - min(timestamps)).total_seconds()
            if time_span > 604800:  # More than 1 week
                return None
        
        # Pattern detected
        confidence = min(len(suspicious_txs) / 5, 1.0)
        
        return {
            "pattern_id": pattern["id"],
            "pattern_name": pattern["name"],
            "pattern_name_ja": pattern["name_ja"],
            "pattern_name_en": pattern["name_en"],
            "description_ja": pattern["description_ja"],
            "description_en": pattern["description_en"],
            "risk_level": pattern["risk_level"],
            "confidence": confidence,
            "addresses_count": len(set(tx.get("to") for tx in suspicious_txs)),
            "total_amount": sum(tx.get("value", 0) for tx in suspicious_txs),
            "transaction_count": len(suspicious_txs),
            "threshold": eth_threshold,
            "evidence": {
                "transaction_hashes": [tx.get("hash") for tx in suspicious_txs],
                "amounts": [tx.get("value") for tx in suspicious_txs]
            }
        }
    
    def _detect_circular_trading(
        self,
        pattern: Dict[str, Any],
        transactions: List[Dict[str, Any]],
        address: str
    ) -> Optional[Dict[str, Any]]:
        """
        Detect circular trading: funds return to original address
        循環取引検出：資金が元のアドレスに戻る
        """
        # Build chains and check for cycles
        chains = self._build_transaction_chains(transactions, address, max_hops=10)
        
        for chain in chains:
            if len(chain) < 3:
                continue
            
            # Check if last transaction returns to original address
            last_to = chain[-1].get("to", "").lower()
            if last_to != address.lower():
                continue
            
            # Check timeframe
            first_time = chain[0].get("timestamp")
            last_time = chain[-1].get("timestamp")
            
            if isinstance(first_time, str):
                first_time = datetime.fromisoformat(first_time.replace('Z', '+00:00'))
            if isinstance(last_time, str):
                last_time = datetime.fromisoformat(last_time.replace('Z', '+00:00'))
            
            time_diff = (last_time - first_time).total_seconds()
            if time_diff > 172800:  # More than 48 hours
                continue
            
            # Pattern detected
            confidence = min(len(chain) / 6, 1.0)
            
            return {
                "pattern_id": pattern["id"],
                "pattern_name": pattern["name"],
                "pattern_name_ja": pattern["name_ja"],
                "pattern_name_en": pattern["name_en"],
                "description_ja": pattern["description_ja"],
                "description_en": pattern["description_en"],
                "risk_level": pattern["risk_level"],
                "confidence": confidence,
                "addresses_count": len(chain),
                "total_amount": sum(tx.get("value", 0) for tx in chain),
                "cycle_length": len(chain),
                "timeframe_seconds": int(time_diff),
                "evidence": {
                    "transaction_hashes": [tx.get("hash") for tx in chain]
                }
            }
        
        return None
    
    def _detect_rapid_movement(
        self,
        pattern: Dict[str, Any],
        transactions: List[Dict[str, Any]],
        address: str
    ) -> Optional[Dict[str, Any]]:
        """
        Detect rapid movement: funds transferred immediately after receipt
        急速移動検出：受取直後の転送
        """
        # Group incoming and outgoing transactions
        incoming = [tx for tx in transactions if tx.get("to", "").lower() == address.lower()]
        outgoing = [tx for tx in transactions if tx.get("from", "").lower() == address.lower()]
        
        rapid_movements = []
        
        for in_tx in incoming:
            in_time = in_tx.get("timestamp")
            if isinstance(in_time, str):
                in_time = datetime.fromisoformat(in_time.replace('Z', '+00:00'))
            
            in_amount = in_tx.get("value", 0)
            
            # Find outgoing transactions within 5 minutes
            for out_tx in outgoing:
                out_time = out_tx.get("timestamp")
                if isinstance(out_time, str):
                    out_time = datetime.fromisoformat(out_time.replace('Z', '+00:00'))
                
                time_diff = (out_time - in_time).total_seconds()
                if 0 < time_diff <= 300:  # Within 5 minutes
                    out_amount = out_tx.get("value", 0)
                    if out_amount >= 0.95 * in_amount:  # 95% or more of received amount
                        rapid_movements.append((in_tx, out_tx, time_diff))
        
        if not rapid_movements:
            return None
        
        # Pattern detected
        confidence = min(len(rapid_movements) / 3, 1.0)
        
        return {
            "pattern_id": pattern["id"],
            "pattern_name": pattern["name"],
            "pattern_name_ja": pattern["name_ja"],
            "pattern_name_en": pattern["name_en"],
            "description_ja": pattern["description_ja"],
            "description_en": pattern["description_en"],
            "risk_level": pattern["risk_level"],
            "confidence": confidence,
            "addresses_count": len(set(out_tx.get("to") for _, out_tx, _ in rapid_movements)),
            "total_amount": sum(in_tx.get("value", 0) for in_tx, _, _ in rapid_movements),
            "occurrence_count": len(rapid_movements),
            "evidence": {
                "movements": [
                    {
                        "incoming_tx": in_tx.get("hash"),
                        "outgoing_tx": out_tx.get("hash"),
                        "time_diff_seconds": int(time_diff)
                    }
                    for in_tx, out_tx, time_diff in rapid_movements[:5]  # First 5
                ]
            }
        }
    
    def _detect_dusting(
        self,
        pattern: Dict[str, Any],
        transactions: List[Dict[str, Any]],
        address: str
    ) -> Optional[Dict[str, Any]]:
        """
        Detect dusting attack: tiny amounts to many addresses
        ダスティング攻撃検出：極小額を多数のアドレスへ
        """
        # Find outgoing transactions with tiny amounts
        dust_txs = []
        recipients = set()
        
        for tx in transactions:
            if tx.get("from", "").lower() != address.lower():
                continue
            
            amount = tx.get("value", 0)
            if amount <= 0.001:  # 0.001 ETH or less
                dust_txs.append(tx)
                recipients.add(tx.get("to", "").lower())
        
        if len(recipients) < 100:  # Need at least 100 unique recipients
            return None
        
        # Pattern detected
        confidence = min(len(recipients) / 200, 1.0)
        
        return {
            "pattern_id": pattern["id"],
            "pattern_name": pattern["name"],
            "pattern_name_ja": pattern["name_ja"],
            "pattern_name_en": pattern["name_en"],
            "description_ja": pattern["description_ja"],
            "description_en": pattern["description_en"],
            "risk_level": pattern["risk_level"],
            "confidence": confidence,
            "addresses_count": len(recipients),
            "total_amount": sum(tx.get("value", 0) for tx in dust_txs),
            "transaction_count": len(dust_txs),
            "evidence": {
                "transaction_hashes": [tx.get("hash") for tx in dust_txs[:10]],
                "average_dust_amount": statistics.mean([tx.get("value", 0) for tx in dust_txs])
            }
        }
    
    def _detect_peel_chain(
        self,
        pattern: Dict[str, Any],
        transactions: List[Dict[str, Any]],
        address: str
    ) -> Optional[Dict[str, Any]]:
        """
        Detect peel chain: gradually peeling funds from large pool
        ピールチェーン検出：大きな資金プールから段階的に剥離
        """
        # Find sequential outgoing transactions from same address
        outgoing = sorted(
            [tx for tx in transactions if tx.get("from", "").lower() == address.lower()],
            key=lambda x: x.get("timestamp", "")
        )
        
        if len(outgoing) < 5:  # Need at least 5 transactions
            return None
        
        # Track balance changes
        peels = []
        for i, tx in enumerate(outgoing):
            if i == 0:
                continue
            
            # Check if this looks like a peel (portion of balance)
            amount = tx.get("value", 0)
            if 0 < amount < 100:  # Reasonable peel amount
                peels.append(tx)
        
        if len(peels) < 5:
            return None
        
        # Pattern detected
        confidence = min(len(peels) / 10, 1.0)
        
        return {
            "pattern_id": pattern["id"],
            "pattern_name": pattern["name"],
            "pattern_name_ja": pattern["name_ja"],
            "pattern_name_en": pattern["name_en"],
            "description_ja": pattern["description_ja"],
            "description_en": pattern["description_en"],
            "risk_level": pattern["risk_level"],
            "confidence": confidence,
            "addresses_count": len(set(tx.get("to") for tx in peels)),
            "total_amount": sum(tx.get("value", 0) for tx in peels),
            "peel_count": len(peels),
            "evidence": {
                "transaction_hashes": [tx.get("hash") for tx in peels[:10]],
                "peel_amounts": [tx.get("value") for tx in peels[:10]]
            }
        }
    
    def _build_transaction_chains(
        self,
        transactions: List[Dict[str, Any]],
        start_address: str,
        max_hops: int = 10
    ) -> List[List[Dict[str, Any]]]:
        """
        Build transaction chains starting from given address
        
        Args:
            transactions: List of all transactions
            start_address: Starting address
            max_hops: Maximum chain length
        
        Returns:
            List of transaction chains
        """
        # Build adjacency map
        adj_map = defaultdict(list)
        for tx in transactions:
            from_addr = tx.get("from", "").lower()
            adj_map[from_addr].append(tx)
        
        # BFS to build chains
        chains = []
        queue = [([tx], tx.get("to", "").lower()) for tx in adj_map[start_address.lower()]]
        
        while queue:
            chain, current_addr = queue.pop(0)
            
            if len(chain) >= max_hops:
                chains.append(chain)
                continue
            
            # Find next transactions
            next_txs = adj_map.get(current_addr, [])
            if not next_txs:
                if len(chain) >= 3:  # Only keep chains with at least 3 hops
                    chains.append(chain)
            else:
                for next_tx in next_txs:
                    new_chain = chain + [next_tx]
                    new_addr = next_tx.get("to", "").lower()
                    queue.append((new_chain, new_addr))
        
        return chains
