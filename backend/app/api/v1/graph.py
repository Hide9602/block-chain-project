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
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
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
    is_sanctioned: bool = False


class GraphEdge(BaseModel):
    """グラフエッジ"""
    id: str
    source: str
    target: str
    amount: float
    timestamp: str
    tx_hash: str
    is_suspicious: bool = False


class GraphResponse(BaseModel):
    """グラフレスポンス"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    total_nodes: int
    total_edges: int
    depth: int


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
        
        # Initialize Etherscan client
        client = EtherscanClient()
        
        # Get address balance
        balance = await client.get_address_balance(address)
        logger.info(f"Address {address} balance: {balance} ETH")
        
        # Get transactions for the address
        transactions = await client.get_address_transactions(
            address=address,
            page=1,
            page_size=100  # Limit to 100 most recent transactions
        )
        logger.info(f"Retrieved {len(transactions)} transactions for address {address}")
        
        # Build graph nodes and edges
        nodes_dict = {}
        edges_list = []
        
        # Add the starting address as a node
        nodes_dict[address.lower()] = GraphNode(
            id=f"node-{address.lower()}",
            address=address.lower(),
            node_type=NodeType.WALLET,
            balance=balance,
            risk_level=RiskLevel.NONE  # TODO: Calculate risk level
        )
        
        # Process transactions to create nodes and edges
        for tx in transactions:
            # Filter by minimum amount
            if tx["value"] < min_amount:
                continue
            
            from_addr = tx["from"].lower()
            to_addr = tx["to"].lower()
            
            # Add nodes if not already present
            if from_addr not in nodes_dict:
                nodes_dict[from_addr] = GraphNode(
                    id=f"node-{from_addr}",
                    address=from_addr,
                    node_type=NodeType.UNKNOWN,  # TODO: Identify node type
                    risk_level=RiskLevel.NONE
                )
            
            if to_addr not in nodes_dict:
                nodes_dict[to_addr] = GraphNode(
                    id=f"node-{to_addr}",
                    address=to_addr,
                    node_type=NodeType.UNKNOWN,  # TODO: Identify node type
                    risk_level=RiskLevel.NONE
                )
            
            # Add edge
            edges_list.append(GraphEdge(
                id=f"edge-{tx['hash']}",
                source=f"node-{from_addr}",
                target=f"node-{to_addr}",
                amount=tx["value"],
                timestamp=tx["timestamp"].isoformat(),
                tx_hash=tx["hash"],
                is_suspicious=False  # TODO: Detect suspicious transactions
            ))
            
            # Limit depth (only direct transactions for depth=1)
            if depth == 1:
                continue
        
        nodes_list = list(nodes_dict.values())
        
        logger.info(f"Built graph with {len(nodes_list)} nodes and {len(edges_list)} edges")
        
        return GraphResponse(
            nodes=nodes_list,
            edges=edges_list,
            total_nodes=len(nodes_list),
            total_edges=len(edges_list),
            depth=depth
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