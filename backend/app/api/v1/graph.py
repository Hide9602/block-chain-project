"""
Graph Analysis API endpoints
グラフ分析関連のAPIエンドポイント
"""

from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
import logging

from app.services.blockchain.etherscan import EtherscanClient
from app.services.ml.pattern_matcher import PatternMatcher
from app.services.ml.anomaly_detector import AnomalyDetector
from app.services.ml.risk_scorer import RiskScorer
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


# Enums
class BlockchainNetwork(str, Enum):
    """ブロックチェーンネットワーク"""
    ETHEREUM = "ethereum"
    BITCOIN = "bitcoin"
    POLYGON = "polygon"
    BSC = "bsc"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"


class NodeType(str, Enum):
    """ノードタイプ"""
    WALLET = "wallet"
    EXCHANGE = "exchange"
    MIXER = "mixer"
    CONTRACT = "contract"
    UNKNOWN = "unknown"


class RiskLevel(str, Enum):
    """リスクレベル"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"
    NONE = "none"


# リクエスト/レスポンスモデル
class GraphNode(BaseModel):
    """グラフノード"""
    id: str
    address: str
    node_type: NodeType
    label: Optional[str] = None
    balance: Optional[float] = None
    risk_level: RiskLevel = RiskLevel.NONE
    risk_score: Optional[float] = None
    is_sanctioned: bool = False
    transaction_count: Optional[int] = None
    total_received: Optional[float] = None
    total_sent: Optional[float] = None
    detected_patterns: List[str] = []


class GraphEdge(BaseModel):
    """グラフエッジ"""
    id: str
    source: str
    target: str
    amount: float
    timestamp: str
    tx_hash: str
    is_suspicious: bool = False
    risk_indicators: List[str] = []
    confidence: Optional[float] = None


class GraphResponse(BaseModel):
    """グラフレスポンス"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    total_nodes: int
    total_edges: int
    depth: int
    high_risk_nodes: List[str] = []
    suspicious_edges: List[str] = []
    analysis_summary: Optional[dict] = None


class TransactionDetail(BaseModel):
    """トランザクション詳細"""
    tx_hash: str
    from_address: str
    to_address: str
    value: float
    timestamp: str
    block_number: int
    gas_used: int
    gas_price: float
    status: str


@router.get("/address/{address}", response_model=GraphResponse)
async def get_address_graph(
    address: str,
    chain: BlockchainNetwork = Query(BlockchainNetwork.ETHEREUM, description="ブロックチェーンネットワーク"),
    depth: int = Query(3, ge=1, le=10, description="探索深度"),
    min_amount: float = Query(0.0, ge=0, description="最小取引額（フィルタリング用）")
):
    """
    アドレスを起点としたグラフ分析
    
    Args:
        address: ブロックチェーンアドレス
        chain: ブロックチェーンネットワーク
        depth: 探索深度（1-10）
        min_amount: 最小取引額
    
    Returns:
        GraphResponse: グラフデータ
    
    Raises:
        HTTPException: アドレスが無効な場合
    """
    try:
        # Only Ethereum is supported for now
        if chain != BlockchainNetwork.ETHEREUM:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Blockchain {chain.value} is not supported yet. Only Ethereum is currently supported."
            )
        
        # Initialize clients
        client = EtherscanClient()
        pattern_matcher = PatternMatcher()
        anomaly_detector = AnomalyDetector()
        risk_scorer = RiskScorer()
        
        # Get address balance
        balance = await client.get_address_balance(address)
        logger.info(f"Address {address} balance: {balance} ETH")
        
        # Get transactions for the address
        transactions = await client.get_address_transactions(
            address=address,
            page=1,
            page_size=500  # Increased for better ML analysis
        )
        logger.info(f"Retrieved {len(transactions)} transactions for address {address}")
        
        # Run ML analysis on main address
        detected_patterns = []
        detected_anomalies = []
        risk_assessment = {}
        
        if transactions:
            detected_patterns = pattern_matcher.detect_patterns(transactions, address)
            detected_anomalies = anomaly_detector.detect_anomalies(transactions, address)
            risk_assessment = risk_scorer.calculate_risk_score(
                address=address,
                transactions=transactions,
                detected_patterns=detected_patterns,
                detected_anomalies=detected_anomalies
            )
        
        # Build graph nodes and edges with ML insights
        nodes_dict = {}
        edges_list = []
        address_transactions = {}  # Track transactions per address
        
        # Known mixer addresses (simplified)
        known_mixers = {
            "0x8589427373d6d84e98730d7795d8f6f8731fda16",  # Tornado Cash ETH
            "0x722122df12d4e14e13ac3b6895a86e84145b6967",  # Tornado Cash
            "0xdd4c48c0b24039969fc16d1cdf626eab821d3384",  # Tornado Cash
        }
        
        # Calculate risk level for main address
        main_risk_level = RiskLevel.NONE
        main_risk_score = 0
        if risk_assessment:
            risk_level_str = risk_assessment.get("risk_level", "none")
            main_risk_score = risk_assessment.get("risk_score", 0)
            
            # Map to enum
            risk_level_map = {
                "critical": RiskLevel.CRITICAL,
                "high": RiskLevel.HIGH,
                "medium": RiskLevel.MEDIUM,
                "low": RiskLevel.LOW,
                "minimal": RiskLevel.MINIMAL,
                "none": RiskLevel.NONE
            }
            main_risk_level = risk_level_map.get(risk_level_str, RiskLevel.NONE)
        
        # Add the starting address as a node with risk info
        pattern_names = [p.get("name_en", "") for p in detected_patterns]
        nodes_dict[address.lower()] = GraphNode(
            id=f"node-{address.lower()}",
            address=address.lower(),
            node_type=NodeType.WALLET,
            balance=balance,
            risk_level=main_risk_level,
            risk_score=main_risk_score,
            transaction_count=len(transactions),
            detected_patterns=pattern_names
        )
        
        # Track transaction counts per address
        for tx in transactions:
            from_addr = tx["from"].lower()
            to_addr = tx["to"].lower()
            
            if from_addr not in address_transactions:
                address_transactions[from_addr] = {"sent": 0, "received": 0, "total_sent": 0.0, "total_received": 0.0}
            if to_addr not in address_transactions:
                address_transactions[to_addr] = {"sent": 0, "received": 0, "total_sent": 0.0, "total_received": 0.0}
            
            address_transactions[from_addr]["sent"] += 1
            address_transactions[from_addr]["total_sent"] += tx["value"]
            address_transactions[to_addr]["received"] += 1
            address_transactions[to_addr]["total_received"] += tx["value"]
        
        # Process transactions to create nodes and edges
        for tx in transactions:
            # Filter by minimum amount
            if tx["value"] < min_amount:
                continue
            
            from_addr = tx["from"].lower()
            to_addr = tx["to"].lower()
            
            # Determine node type and risk
            def determine_node_type(addr: str) -> NodeType:
                if addr in known_mixers:
                    return NodeType.MIXER
                # High transaction count suggests exchange
                if addr in address_transactions:
                    tx_count = address_transactions[addr]["sent"] + address_transactions[addr]["received"]
                    if tx_count > 50:
                        return NodeType.EXCHANGE
                return NodeType.WALLET
            
            def determine_node_risk(addr: str) -> RiskLevel:
                if addr in known_mixers:
                    return RiskLevel.HIGH
                if addr in address_transactions:
                    tx_count = address_transactions[addr]["sent"] + address_transactions[addr]["received"]
                    total_volume = address_transactions[addr]["total_sent"] + address_transactions[addr]["total_received"]
                    # Simple heuristic
                    if total_volume > 100:
                        return RiskLevel.MEDIUM
                    elif tx_count > 20:
                        return RiskLevel.LOW
                return RiskLevel.NONE
            
            # Add nodes if not already present
            if from_addr not in nodes_dict:
                node_type = determine_node_type(from_addr)
                node_risk = determine_node_risk(from_addr)
                stats = address_transactions.get(from_addr, {})
                
                nodes_dict[from_addr] = GraphNode(
                    id=f"node-{from_addr}",
                    address=from_addr,
                    node_type=node_type,
                    risk_level=node_risk,
                    is_sanctioned=(from_addr in known_mixers),
                    transaction_count=stats.get("sent", 0) + stats.get("received", 0),
                    total_sent=stats.get("total_sent", 0.0),
                    total_received=stats.get("total_received", 0.0)
                )
            
            if to_addr not in nodes_dict:
                node_type = determine_node_type(to_addr)
                node_risk = determine_node_risk(to_addr)
                stats = address_transactions.get(to_addr, {})
                
                nodes_dict[to_addr] = GraphNode(
                    id=f"node-{to_addr}",
                    address=to_addr,
                    node_type=node_type,
                    risk_level=node_risk,
                    is_sanctioned=(to_addr in known_mixers),
                    transaction_count=stats.get("sent", 0) + stats.get("received", 0),
                    total_sent=stats.get("total_sent", 0.0),
                    total_received=stats.get("total_received", 0.0)
                )
            
            # Determine if edge is suspicious
            is_suspicious = False
            risk_indicators = []
            
            # Check if involves mixer
            if from_addr in known_mixers or to_addr in known_mixers:
                is_suspicious = True
                risk_indicators.append("mixer_interaction")
            
            # Check if large amount
            if tx["value"] > 10.0:
                risk_indicators.append("large_amount")
            
            # Check if involves high-risk node
            if (nodes_dict[from_addr].risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] or
                nodes_dict[to_addr].risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]):
                is_suspicious = True
                risk_indicators.append("high_risk_address")
            
            # Add edge
            edges_list.append(GraphEdge(
                id=f"edge-{tx['hash']}",
                source=f"node-{from_addr}",
                target=f"node-{to_addr}",
                amount=tx["value"],
                timestamp=tx["timestamp"].isoformat(),
                tx_hash=tx["hash"],
                is_suspicious=is_suspicious,
                risk_indicators=risk_indicators,
                confidence=0.8 if is_suspicious else None
            ))
            
            # Limit depth (only direct transactions for depth=1)
            if depth == 1:
                continue
        
        nodes_list = list(nodes_dict.values())
        
        # Identify high risk nodes and suspicious edges
        high_risk_nodes = [
            node.id for node in nodes_list 
            if node.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]
        ]
        
        suspicious_edges = [
            edge.id for edge in edges_list 
            if edge.is_suspicious
        ]
        
        # Create analysis summary
        analysis_summary = {
            "total_volume": sum(tx["value"] for tx in transactions),
            "patterns_detected": len(detected_patterns),
            "anomalies_detected": len(detected_anomalies),
            "risk_score": main_risk_score,
            "risk_level": main_risk_level.value,
            "high_risk_count": len(high_risk_nodes),
            "suspicious_tx_count": len(suspicious_edges)
        }
        
        logger.info(f"Built graph with {len(nodes_list)} nodes and {len(edges_list)} edges")
        logger.info(f"Identified {len(high_risk_nodes)} high-risk nodes and {len(suspicious_edges)} suspicious edges")
        
        return GraphResponse(
            nodes=nodes_list,
            edges=edges_list,
            total_nodes=len(nodes_list),
            total_edges=len(edges_list),
            depth=depth,
            high_risk_nodes=high_risk_nodes,
            suspicious_edges=suspicious_edges,
            analysis_summary=analysis_summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error building graph for address {address}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to build address graph: {str(e)}"
        )


@router.get("/transaction/{tx_hash}", response_model=TransactionDetail)
async def get_transaction_detail(
    tx_hash: str,
    chain: BlockchainNetwork = Query(BlockchainNetwork.ETHEREUM)
):
    """
    トランザクション詳細取得
    
    Args:
        tx_hash: トランザクションハッシュ
        chain: ブロックチェーンネットワーク
    
    Returns:
        TransactionDetail: トランザクション詳細
    """
    try:
        # Only Ethereum is supported for now
        if chain != BlockchainNetwork.ETHEREUM:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Blockchain {chain.value} is not supported yet. Only Ethereum is currently supported."
            )
        
        # Initialize Etherscan client
        client = EtherscanClient()
        
        # Get transaction details
        tx = await client.get_transaction_details(tx_hash)
        
        if not tx:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction {tx_hash} not found"
            )
        
        logger.info(f"Retrieved transaction details for {tx_hash}")
        
        return TransactionDetail(
            tx_hash=tx_hash,
            from_address=tx.get("from", ""),
            to_address=tx.get("to", ""),
            value=tx.get("value", 0.0),
            timestamp="2024-01-15T12:34:56Z",  # TODO: Get actual timestamp
            block_number=tx.get("block_number", 0),
            gas_used=0,  # Not available in proxy response
            gas_price=tx.get("gas_price", 0.0),
            status="success"  # TODO: Get actual status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transaction details for {tx_hash}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get transaction details: {str(e)}"
        )


@router.post("/trace")
async def trace_funds(
    start_address: str,
    chain: BlockchainNetwork = BlockchainNetwork.ETHEREUM,
    max_hops: int = Query(10, ge=1, le=20)
):
    """
    資金トレース（複数ホップ追跡）
    
    Args:
        start_address: 開始アドレス
        chain: ブロックチェーンネットワーク
        max_hops: 最大ホップ数
    
    Returns:
        dict: トレース結果
    """
    # TODO: 資金フロー追跡アルゴリズム実装
    
    return {
        "start_address": start_address,
        "chain": chain,
        "paths": [
            {
                "hops": 3,
                "addresses": [start_address, "0xaaa...", "0xbbb...", "0xccc..."],
                "total_amount": 10.5,
                "risk_score": 65
            }
        ]
    }