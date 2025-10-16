"""
Investigation Models
調査関連モデル
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Investigation(Base):
    """調査案件モデル"""
    
    __tablename__ = "investigations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # 案件情報
    case_number = Column(String(100), unique=True, index=True, nullable=False)
    case_title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # 調査対象
    target_address = Column(String(255), index=True, nullable=False)
    blockchain = Column(String(50), nullable=False)  # ethereum, bitcoin, etc.
    
    # ステータス
    status = Column(String(50), default="pending", nullable=False)  # pending, in_progress, completed, archived
    
    # 調査結果
    risk_score = Column(Integer, nullable=True)  # 0-100
    risk_level = Column(String(50), nullable=True)  # high, medium, low, none
    total_transactions = Column(Integer, default=0)
    total_addresses = Column(Integer, default=0)
    total_volume = Column(Float, default=0.0)
    
    # 検出されたパターン
    detected_patterns = Column(JSON, nullable=True)
    
    # タイムスタンプ
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # リレーション
    # user = relationship("User", back_populates="investigations")
    # reports = relationship("Report", back_populates="investigation")
    
    def __repr__(self) -> str:
        return f"<Investigation {self.case_number}>"


class Report(Base):
    """レポートモデル"""
    
    __tablename__ = "reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_id = Column(UUID(as_uuid=True), ForeignKey("investigations.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # レポート情報
    title = Column(String(255), nullable=False)
    format = Column(String(50), nullable=False)  # pdf, word, json
    language = Column(String(10), nullable=False)  # ja, en
    
    # ファイル情報
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    file_hash = Column(String(255), nullable=True)  # SHA-256
    
    # ステータス
    status = Column(String(50), default="pending", nullable=False)  # pending, processing, completed, failed
    
    # 証拠性担保
    digital_signature = Column(Text, nullable=True)
    verification_hash = Column(String(255), nullable=True)
    timestamp = Column(DateTime, nullable=True)
    
    # メタデータ
    metadata = Column(JSON, nullable=True)
    
    # タイムスタンプ
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # リレーション
    # investigation = relationship("Investigation", back_populates="reports")
    
    def __repr__(self) -> str:
        return f"<Report {self.id} - {self.format}>"


class Address(Base):
    """ブロックチェーンアドレスモデル"""
    
    __tablename__ = "addresses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # アドレス情報
    address = Column(String(255), unique=True, index=True, nullable=False)
    blockchain = Column(String(50), nullable=False)
    
    # ラベル
    label = Column(String(255), nullable=True)
    address_type = Column(String(50), nullable=True)  # wallet, exchange, mixer, contract
    
    # リスク評価
    risk_score = Column(Integer, nullable=True)
    risk_level = Column(String(50), nullable=True)
    is_sanctioned = Column(Boolean, default=False)
    sanctioned_lists = Column(JSON, nullable=True)
    
    # 統計情報
    balance = Column(Float, nullable=True)
    total_received = Column(Float, nullable=True)
    total_sent = Column(Float, nullable=True)
    transaction_count = Column(Integer, default=0)
    
    # タイムスタンプ
    first_seen = Column(DateTime, nullable=True)
    last_seen = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # メタデータ
    metadata = Column(JSON, nullable=True)
    
    def __repr__(self) -> str:
        return f"<Address {self.address[:10]}...>"


class Transaction(Base):
    """トランザクションモデル"""
    
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # トランザクション情報
    tx_hash = Column(String(255), unique=True, index=True, nullable=False)
    blockchain = Column(String(50), nullable=False)
    block_number = Column(Integer, nullable=True)
    block_hash = Column(String(255), nullable=True)
    
    # 送受信情報
    from_address = Column(String(255), index=True, nullable=False)
    to_address = Column(String(255), index=True, nullable=True)
    value = Column(Float, nullable=False)
    
    # ガス情報
    gas_used = Column(Integer, nullable=True)
    gas_price = Column(Float, nullable=True)
    
    # ステータス
    status = Column(String(50), nullable=True)  # success, failed, pending
    is_suspicious = Column(Boolean, default=False)
    
    # タイムスタンプ
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # メタデータ
    metadata = Column(JSON, nullable=True)
    
    def __repr__(self) -> str:
        return f"<Transaction {self.tx_hash[:10]}...>"
