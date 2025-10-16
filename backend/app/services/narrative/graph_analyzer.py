"""
Graph Analyzer for transaction flow analysis
取引フロー分析のためのグラフアナライザー
"""
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import defaultdict, deque
from datetime import datetime

logger = logging.getLogger(__name__)


class GraphAnalyzer:
    """
    Analyze transaction graph structure and identify key paths
    取引グラフ構造を分析し、主要な経路を特定
    """
    
    def __init__(self):
        """Initialize graph analyzer"""
        logger.info("Initialized GraphAnalyzer")
    
    def build_graph(
        self,
        transactions: List[Dict[str, Any]],
        start_address: str
    ) -> Dict[str, Any]:
        """
        Build transaction graph from transaction list
        
        Args:
            transactions: List of transactions
            start_address: Starting address for analysis
        
        Returns:
            Graph structure with nodes and edges
        """
        graph = {
            "nodes": {},
            "edges": [],
            "adjacency": defaultdict(list)
        }
        
        start_address = start_address.lower()
        
        for tx in transactions:
            from_addr = tx.get("from", "").lower()
            to_addr = tx.get("to", "").lower()
            
            # Add nodes
            if from_addr not in graph["nodes"]:
                graph["nodes"][from_addr] = {
                    "address": from_addr,
                    "incoming_count": 0,
                    "outgoing_count": 0,
                    "total_received": 0.0,
                    "total_sent": 0.0
                }
            
            if to_addr not in graph["nodes"]:
                graph["nodes"][to_addr] = {
                    "address": to_addr,
                    "incoming_count": 0,
                    "outgoing_count": 0,
                    "total_received": 0.0,
                    "total_sent": 0.0
                }
            
            # Update node statistics
            amount = tx.get("value", 0.0)
            graph["nodes"][from_addr]["outgoing_count"] += 1
            graph["nodes"][from_addr]["total_sent"] += amount
            graph["nodes"][to_addr]["incoming_count"] += 1
            graph["nodes"][to_addr]["total_received"] += amount
            
            # Add edge
            edge = {
                "from": from_addr,
                "to": to_addr,
                "amount": amount,
                "timestamp": tx.get("timestamp"),
                "tx_hash": tx.get("hash")
            }
            graph["edges"].append(edge)
            
            # Build adjacency list
            graph["adjacency"][from_addr].append({
                "to": to_addr,
                "amount": amount,
                "timestamp": tx.get("timestamp"),
                "tx_hash": tx.get("hash")
            })
        
        return graph
    
    def find_main_paths(
        self,
        graph: Dict[str, Any],
        start_address: str,
        max_paths: int = 5,
        max_hops: int = 10
    ) -> List[List[Dict[str, Any]]]:
        """
        Find main transaction paths from starting address
        
        Args:
            graph: Transaction graph
            start_address: Starting address
            max_paths: Maximum number of paths to return
            max_hops: Maximum hops per path
        
        Returns:
            List of paths (each path is list of transactions)
        """
        start_address = start_address.lower()
        adjacency = graph["adjacency"]
        
        if start_address not in adjacency:
            return []
        
        # BFS to find paths
        paths = []
        queue = deque()
        
        # Initialize with outgoing transactions from start address
        for edge in adjacency[start_address]:
            queue.append([edge])
        
        visited_paths = set()
        
        while queue and len(paths) < max_paths:
            path = queue.popleft()
            
            if len(path) >= max_hops:
                paths.append(path)
                continue
            
            current_to = path[-1]["to"]
            
            # Create path signature to avoid duplicates
            path_sig = tuple(e["tx_hash"] for e in path)
            if path_sig in visited_paths:
                continue
            visited_paths.add(path_sig)
            
            # If no more outgoing edges, this is an end path
            if current_to not in adjacency or not adjacency[current_to]:
                if len(path) >= 2:  # Only keep paths with at least 2 hops
                    paths.append(path)
                continue
            
            # Extend path with next edges
            for next_edge in adjacency[current_to]:
                # Avoid cycles
                if any(e["to"] == next_edge["to"] for e in path):
                    continue
                
                new_path = path + [next_edge]
                queue.append(new_path)
        
        # Sort paths by total amount
        paths.sort(key=lambda p: sum(e["amount"] for e in p), reverse=True)
        
        return paths[:max_paths]
    
    def identify_intermediaries(
        self,
        graph: Dict[str, Any],
        path: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Identify intermediate addresses in a path
        
        Args:
            graph: Transaction graph
            path: Transaction path
        
        Returns:
            List of intermediary addresses
        """
        if len(path) < 2:
            return []
        
        # Intermediaries are addresses that appear in the middle of the path
        intermediaries = []
        for i in range(len(path) - 1):
            addr = path[i]["to"]
            intermediaries.append(addr)
        
        return intermediaries
    
    def calculate_path_statistics(
        self,
        path: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate statistics for a transaction path
        
        Args:
            path: Transaction path
        
        Returns:
            Statistics dictionary
        """
        if not path:
            return {}
        
        total_amount = sum(e["amount"] for e in path)
        hop_count = len(path)
        
        # Calculate time span
        timestamps = []
        for edge in path:
            ts = edge.get("timestamp")
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            if ts:
                timestamps.append(ts)
        
        time_span_seconds = 0
        if len(timestamps) >= 2:
            time_span_seconds = (max(timestamps) - min(timestamps)).total_seconds()
        
        # Get addresses involved
        addresses = set()
        for edge in path:
            addresses.add(edge["from"])
            addresses.add(edge["to"])
        
        return {
            "total_amount": total_amount,
            "hop_count": hop_count,
            "time_span_seconds": time_span_seconds,
            "addresses_count": len(addresses),
            "average_amount": total_amount / hop_count if hop_count > 0 else 0,
            "transactions": [e["tx_hash"] for e in path]
        }
    
    def detect_hubs(
        self,
        graph: Dict[str, Any],
        threshold: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Detect hub addresses (high degree nodes)
        
        Args:
            graph: Transaction graph
            threshold: Minimum degree to be considered a hub
        
        Returns:
            List of hub addresses with statistics
        """
        hubs = []
        
        for addr, node_data in graph["nodes"].items():
            degree = node_data["incoming_count"] + node_data["outgoing_count"]
            
            if degree >= threshold:
                hubs.append({
                    "address": addr,
                    "degree": degree,
                    "incoming_count": node_data["incoming_count"],
                    "outgoing_count": node_data["outgoing_count"],
                    "total_received": node_data["total_received"],
                    "total_sent": node_data["total_sent"]
                })
        
        # Sort by degree
        hubs.sort(key=lambda h: h["degree"], reverse=True)
        
        return hubs
    
    def analyze_flow_pattern(
        self,
        graph: Dict[str, Any],
        start_address: str
    ) -> Dict[str, Any]:
        """
        Analyze overall flow pattern from starting address
        
        Args:
            graph: Transaction graph
            start_address: Starting address
        
        Returns:
            Flow pattern analysis
        """
        start_address = start_address.lower()
        
        # Find main paths
        main_paths = self.find_main_paths(graph, start_address, max_paths=3)
        
        if not main_paths:
            return {
                "has_suspicious_flow": False,
                "pattern_type": "none",
                "main_paths": []
            }
        
        # Analyze each path
        path_analyses = []
        for path in main_paths:
            path_analyses.append(self.calculate_path_statistics(path))
        
        # Determine flow pattern
        avg_hops = sum(p["hop_count"] for p in path_analyses) / len(path_analyses)
        
        pattern_type = "simple"
        if avg_hops >= 5:
            pattern_type = "complex_layering"
        elif avg_hops >= 3:
            pattern_type = "moderate_layering"
        
        # Check for mixing (would need to compare against known mixer addresses)
        # This is simplified
        has_suspicious_flow = avg_hops >= 3
        
        return {
            "has_suspicious_flow": has_suspicious_flow,
            "pattern_type": pattern_type,
            "main_paths": path_analyses,
            "average_hops": avg_hops,
            "total_paths_analyzed": len(main_paths)
        }
