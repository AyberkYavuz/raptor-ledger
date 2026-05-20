import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from backend.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    trades = relationship("Trade", back_populates="user", cascade="all, delete-orphan")
    decisions = relationship("AgentDecision", back_populates="user", cascade="all, delete-orphan")
    llm_logs = relationship("LLMLog", back_populates="user", cascade="all, delete-orphan")
    snapshots = relationship("PortfolioSnapshot", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_users_email_uniq", "email", unique=True),)


class Trade(Base):
    __tablename__ = "trades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(20), nullable=False)
    action = Column(String(10), nullable=False)  # BUY, SELL
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    profit_loss = Column(Float, nullable=True)
    order_id = Column(String(100), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="trades")

    __table_args__ = (
        Index("idx_trades_user_symbol", "user_id", "symbol"),
        Index("idx_trades_timestamp", "timestamp"),
    )


class AgentDecision(Base):
    __tablename__ = "agent_decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    decision = Column(String(20), nullable=False)  # BUY, SELL, HOLD
    confidence = Column(Float, nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="decisions")

    __table_args__ = (
        Index("idx_agent_decisions_lookup", "user_id", "agent_name"),
        Index("idx_agent_decisions_created_at", "created_at"),
    )


class LLMLog(Base):
    __tablename__ = "llm_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    model_name = Column(String(100), nullable=False)
    prompt_tokens = Column(Integer, nullable=False)
    completion_tokens = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    latency = Column(Float, nullable=False)
    agent_name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="llm_logs")

    __table_args__ = (
        Index("idx_llm_logs_metrics", "created_at"),
        Index("idx_llm_logs_agent", "agent_name"),
    )


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    balance = Column(Float, nullable=False)
    daily_pnl = Column(Float, nullable=False)
    open_positions = Column(JSONB, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="snapshots")

    __table_args__ = (Index("idx_portfolio_snapshots_lookup", "user_id", "created_at"),)
