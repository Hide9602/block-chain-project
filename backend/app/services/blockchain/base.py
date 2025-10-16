"""
Base blockchain client interface
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime


class BlockchainClient(ABC):
    """
    Abstract base class for blockchain API clients
    ブロックチェーンAPIクライアントの抽象基底クラス
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize blockchain client
        
        Args:
            api_key: API key for authentication
        """
        self.api_key = api_key
    
    @abstractmethod
    async def get_address_balance(self, address: str) -> float:
        """
        Get the balance of an address
        
        Args:
            address: Blockchain address
        
        Returns:
            Balance in native token (ETH, BTC, etc.)
        """
        pass
    
    @abstractmethod
    async def get_address_transactions(
        self,
        address: str,
        start_block: Optional[int] = None,
        end_block: Optional[int] = None,
        page: int = 1,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get transactions for an address
        
        Args:
            address: Blockchain address
            start_block: Starting block number
            end_block: Ending block number
            page: Page number for pagination
            page_size: Number of transactions per page
        
        Returns:
            List of transaction dictionaries
        """
        pass
    
    @abstractmethod
    async def get_transaction_details(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get details of a specific transaction
        
        Args:
            tx_hash: Transaction hash
        
        Returns:
            Transaction details dictionary
        """
        pass
    
    @abstractmethod
    async def get_token_transfers(
        self,
        address: str,
        contract_address: Optional[str] = None,
        page: int = 1,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get token transfer events for an address
        
        Args:
            address: Blockchain address
            contract_address: Token contract address (optional filter)
            page: Page number for pagination
            page_size: Number of transfers per page
        
        Returns:
            List of token transfer dictionaries
        """
        pass
    
    @abstractmethod
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
            address: Blockchain address
            start_block: Starting block number
            end_block: Ending block number
            page: Page number for pagination
            page_size: Number of transactions per page
        
        Returns:
            List of internal transaction dictionaries
        """
        pass
    
    def format_address(self, address: str) -> str:
        """
        Format address according to blockchain standards
        
        Args:
            address: Raw address string
        
        Returns:
            Formatted address string
        """
        return address.lower().strip()
    
    def format_amount(self, amount: str, decimals: int = 18) -> float:
        """
        Format amount from wei/satoshi to human-readable format
        
        Args:
            amount: Amount in smallest unit
            decimals: Token decimals (default 18 for ETH)
        
        Returns:
            Amount in human-readable format
        """
        try:
            return float(amount) / (10 ** decimals)
        except (ValueError, TypeError):
            return 0.0
