"""
Etherscan API client for Ethereum blockchain
"""
import logging
from typing import Dict, List, Optional, Any
import httpx
from datetime import datetime

from .base import BlockchainClient
from app.core.config import settings

logger = logging.getLogger(__name__)


class EtherscanClient(BlockchainClient):
    """
    Etherscan API client for querying Ethereum blockchain data
    EtherscanAPIクライアント（Ethereumブロックチェーンデータ取得用）
    """
    
    BASE_URL = "https://api.etherscan.io/api"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Etherscan client
        
        Args:
            api_key: Etherscan API key (optional, will use settings if not provided)
        """
        super().__init__(api_key or settings.ETHERSCAN_API_KEY)
        
        if not self.api_key:
            logger.warning("Etherscan API key not provided. Rate limits will apply.")
    
    async def _make_request(
        self,
        module: str,
        action: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make API request to Etherscan
        
        Args:
            module: API module (e.g., "account", "transaction")
            action: API action (e.g., "balance", "txlist")
            params: Additional parameters
        
        Returns:
            API response dictionary
        
        Raises:
            httpx.HTTPError: If API request fails
        """
        request_params = {
            "module": module,
            "action": action,
            "apikey": self.api_key or ""
        }
        
        if params:
            request_params.update(params)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(self.BASE_URL, params=request_params)
                response.raise_for_status()
                
                data = response.json()
                
                # Check for API errors
                if data.get("status") == "0" and data.get("message") != "No transactions found":
                    logger.error(f"Etherscan API error: {data.get('result', 'Unknown error')}")
                    return {"status": "0", "result": [], "message": data.get("message", "")}
                
                return data
                
            except httpx.HTTPError as e:
                logger.error(f"HTTP error calling Etherscan API: {str(e)}", exc_info=True)
                raise
            except Exception as e:
                logger.error(f"Unexpected error calling Etherscan API: {str(e)}", exc_info=True)
                raise
    
    async def get_address_balance(self, address: str) -> float:
        """
        Get the ETH balance of an address
        
        Args:
            address: Ethereum address
        
        Returns:
            Balance in ETH
        """
        address = self.format_address(address)
        
        response = await self._make_request(
            module="account",
            action="balance",
            params={"address": address, "tag": "latest"}
        )
        
        if response.get("status") == "1":
            balance_wei = response.get("result", "0")
            return self.format_amount(balance_wei, decimals=18)
        
        return 0.0
    
    async def get_address_transactions(
        self,
        address: str,
        start_block: Optional[int] = None,
        end_block: Optional[int] = None,
        page: int = 1,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get normal transactions for an address
        
        Args:
            address: Ethereum address
            start_block: Starting block number
            end_block: Ending block number
            page: Page number for pagination
            page_size: Number of transactions per page (max 10000)
        
        Returns:
            List of transaction dictionaries
        """
        address = self.format_address(address)
        
        params = {
            "address": address,
            "startblock": start_block or 0,
            "endblock": end_block or 99999999,
            "page": page,
            "offset": min(page_size, 10000),  # Etherscan max is 10000
            "sort": "desc"  # Most recent first
        }
        
        response = await self._make_request(
            module="account",
            action="txlist",
            params=params
        )
        
        if response.get("status") == "1":
            transactions = response.get("result", [])
            return self._format_transactions(transactions)
        
        return []
    
    async def get_transaction_details(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get details of a specific transaction
        
        Args:
            tx_hash: Transaction hash
        
        Returns:
            Transaction details dictionary
        """
        response = await self._make_request(
            module="proxy",
            action="eth_getTransactionByHash",
            params={"txhash": tx_hash}
        )
        
        if response.get("result"):
            tx = response["result"]
            return self._format_transaction_detail(tx)
        
        return {}
    
    async def get_token_transfers(
        self,
        address: str,
        contract_address: Optional[str] = None,
        page: int = 1,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get ERC-20 token transfer events for an address
        
        Args:
            address: Ethereum address
            contract_address: Token contract address (optional filter)
            page: Page number for pagination
            page_size: Number of transfers per page
        
        Returns:
            List of token transfer dictionaries
        """
        address = self.format_address(address)
        
        params = {
            "address": address,
            "page": page,
            "offset": min(page_size, 10000),
            "sort": "desc"
        }
        
        if contract_address:
            params["contractaddress"] = self.format_address(contract_address)
        
        response = await self._make_request(
            module="account",
            action="tokentx",
            params=params
        )
        
        if response.get("status") == "1":
            transfers = response.get("result", [])
            return self._format_token_transfers(transfers)
        
        return []
    
    async def get_internal_transactions(
        self,
        address: str,
        start_block: Optional[int] = None,
        end_block: Optional[int] = None,
        page: int = 1,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get internal transactions for an address
        
        Args:
            address: Ethereum address
            start_block: Starting block number
            end_block: Ending block number
            page: Page number for pagination
            page_size: Number of transactions per page
        
        Returns:
            List of internal transaction dictionaries
        """
        address = self.format_address(address)
        
        params = {
            "address": address,
            "startblock": start_block or 0,
            "endblock": end_block or 99999999,
            "page": page,
            "offset": min(page_size, 10000),
            "sort": "desc"
        }
        
        response = await self._make_request(
            module="account",
            action="txlistinternal",
            params=params
        )
        
        if response.get("status") == "1":
            transactions = response.get("result", [])
            return self._format_internal_transactions(transactions)
        
        return []
    
    async def get_erc721_transfers(
        self,
        address: str,
        contract_address: Optional[str] = None,
        page: int = 1,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get ERC-721 (NFT) transfer events for an address
        
        Args:
            address: Ethereum address
            contract_address: NFT contract address (optional filter)
            page: Page number for pagination
            page_size: Number of transfers per page
        
        Returns:
            List of NFT transfer dictionaries
        """
        address = self.format_address(address)
        
        params = {
            "address": address,
            "page": page,
            "offset": min(page_size, 10000),
            "sort": "desc"
        }
        
        if contract_address:
            params["contractaddress"] = self.format_address(contract_address)
        
        response = await self._make_request(
            module="account",
            action="tokennfttx",
            params=params
        )
        
        if response.get("status") == "1":
            transfers = response.get("result", [])
            return self._format_nft_transfers(transfers)
        
        return []
    
    def _format_transactions(self, transactions: List[Dict]) -> List[Dict[str, Any]]:
        """
        Format transaction list to standardized format
        
        Args:
            transactions: Raw transaction list from API
        
        Returns:
            Formatted transaction list
        """
        formatted = []
        
        for tx in transactions:
            formatted.append({
                "hash": tx.get("hash"),
                "from": tx.get("from"),
                "to": tx.get("to"),
                "value": self.format_amount(tx.get("value", "0"), decimals=18),
                "value_wei": tx.get("value", "0"),
                "block_number": int(tx.get("blockNumber", 0)),
                "timestamp": datetime.fromtimestamp(int(tx.get("timeStamp", 0))),
                "gas_used": int(tx.get("gasUsed", 0)),
                "gas_price": self.format_amount(tx.get("gasPrice", "0"), decimals=9),  # Gwei
                "is_error": tx.get("isError") == "1",
                "tx_receipt_status": tx.get("txreceipt_status") == "1",
                "input": tx.get("input", ""),
                "contract_address": tx.get("contractAddress", ""),
                "cumulative_gas_used": int(tx.get("cumulativeGasUsed", 0)),
                "confirmations": int(tx.get("confirmations", 0))
            })
        
        return formatted
    
    def _format_transaction_detail(self, tx: Dict) -> Dict[str, Any]:
        """
        Format transaction detail to standardized format
        
        Args:
            tx: Raw transaction detail from API
        
        Returns:
            Formatted transaction detail
        """
        return {
            "hash": tx.get("hash"),
            "from": tx.get("from"),
            "to": tx.get("to"),
            "value": self.format_amount(tx.get("value", "0x0"), decimals=18),
            "block_number": int(tx.get("blockNumber", "0x0"), 16),
            "gas": int(tx.get("gas", "0x0"), 16),
            "gas_price": self.format_amount(tx.get("gasPrice", "0x0"), decimals=9),
            "input": tx.get("input", ""),
            "nonce": int(tx.get("nonce", "0x0"), 16),
            "transaction_index": int(tx.get("transactionIndex", "0x0"), 16),
            "v": tx.get("v", ""),
            "r": tx.get("r", ""),
            "s": tx.get("s", "")
        }
    
    def _format_token_transfers(self, transfers: List[Dict]) -> List[Dict[str, Any]]:
        """
        Format token transfer list to standardized format
        
        Args:
            transfers: Raw token transfer list from API
        
        Returns:
            Formatted token transfer list
        """
        formatted = []
        
        for transfer in transfers:
            decimals = int(transfer.get("tokenDecimal", 18))
            formatted.append({
                "hash": transfer.get("hash"),
                "from": transfer.get("from"),
                "to": transfer.get("to"),
                "value": self.format_amount(transfer.get("value", "0"), decimals=decimals),
                "value_raw": transfer.get("value", "0"),
                "token_name": transfer.get("tokenName", ""),
                "token_symbol": transfer.get("tokenSymbol", ""),
                "token_decimal": decimals,
                "contract_address": transfer.get("contractAddress"),
                "block_number": int(transfer.get("blockNumber", 0)),
                "timestamp": datetime.fromtimestamp(int(transfer.get("timeStamp", 0))),
                "gas_used": int(transfer.get("gasUsed", 0)),
                "gas_price": self.format_amount(transfer.get("gasPrice", "0"), decimals=9),
                "confirmations": int(transfer.get("confirmations", 0))
            })
        
        return formatted
    
    def _format_internal_transactions(self, transactions: List[Dict]) -> List[Dict[str, Any]]:
        """
        Format internal transaction list to standardized format
        
        Args:
            transactions: Raw internal transaction list from API
        
        Returns:
            Formatted internal transaction list
        """
        formatted = []
        
        for tx in transactions:
            formatted.append({
                "hash": tx.get("hash"),
                "from": tx.get("from"),
                "to": tx.get("to"),
                "value": self.format_amount(tx.get("value", "0"), decimals=18),
                "value_wei": tx.get("value", "0"),
                "block_number": int(tx.get("blockNumber", 0)),
                "timestamp": datetime.fromtimestamp(int(tx.get("timeStamp", 0))),
                "gas": int(tx.get("gas", 0)),
                "gas_used": int(tx.get("gasUsed", 0)),
                "is_error": tx.get("isError") == "1",
                "trace_id": tx.get("traceId", ""),
                "type": tx.get("type", ""),
                "contract_address": tx.get("contractAddress", "")
            })
        
        return formatted
    
    def _format_nft_transfers(self, transfers: List[Dict]) -> List[Dict[str, Any]]:
        """
        Format NFT transfer list to standardized format
        
        Args:
            transfers: Raw NFT transfer list from API
        
        Returns:
            Formatted NFT transfer list
        """
        formatted = []
        
        for transfer in transfers:
            formatted.append({
                "hash": transfer.get("hash"),
                "from": transfer.get("from"),
                "to": transfer.get("to"),
                "token_id": transfer.get("tokenID", ""),
                "token_name": transfer.get("tokenName", ""),
                "token_symbol": transfer.get("tokenSymbol", ""),
                "contract_address": transfer.get("contractAddress"),
                "block_number": int(transfer.get("blockNumber", 0)),
                "timestamp": datetime.fromtimestamp(int(transfer.get("timeStamp", 0))),
                "gas_used": int(transfer.get("gasUsed", 0)),
                "gas_price": self.format_amount(transfer.get("gasPrice", "0"), decimals=9),
                "confirmations": int(transfer.get("confirmations", 0))
            })
        
        return formatted
