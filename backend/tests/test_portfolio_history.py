import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from backend.services.portfolio_service import PortfolioService
from backend.models.models import Trade


# Helper function to generate mock trade models dynamically
def create_mock_trade(user_id, symbol, price, timestamp):
    return Trade(
        id=uuid4(),
        user_id=user_id,
        symbol=symbol,
        action="BUY",
        quantity=0.002,
        price=price,
        order_id=f"MOCK_{uuid4().hex[:6]}",
        timestamp=timestamp
    )


@pytest.fixture
def setup_service():
    """Fixture to initialize the service with mocked dependencies."""
    mock_db = AsyncMock()
    mock_binance = MagicMock()
    service = PortfolioService(binance_tool=mock_binance)
    return service, mock_db

# -------------------------------------------------------------------------
# TEST CASES
# -------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_trade_history_no_filters(setup_service):
    """Ensure the query returns all trades when start_date and end_date are None."""
    service, mock_db = setup_service
    user_id = uuid4()
    base_time = datetime(2026, 5, 26, 12, 0, 0)

    trades = [
        create_mock_trade(user_id, "BTCUSDT", 64000.0, base_time - timedelta(days=1)),
        create_mock_trade(user_id, "BTCUSDT", 65000.0, base_time)
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = trades
    mock_db.execute.return_value = mock_result

    results = await service.get_trade_history(db=mock_db, user_id=user_id)

    assert len(results) == 2
    compiled_sql = str(mock_db.execute.call_args[0][0].compile(compile_kwargs={"literal_binds": True}))
    assert ">=" not in compiled_sql
    assert "<=" not in compiled_sql


@pytest.mark.asyncio
async def test_get_trade_history_only_start_date(setup_service):
    """Verify trades after a certain date are included, older ones excluded."""
    service, mock_db = setup_service
    user_id = uuid4()
    base_time = datetime(2026, 5, 26, 12, 0, 0)
    start_filter = base_time - timedelta(hours=1)

    # Target trade falls after start_filter
    trade_target = create_mock_trade(user_id, "BTCUSDT", 65000.0, base_time)

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [trade_target]
    mock_db.execute.return_value = mock_result

    results = await service.get_trade_history(db=mock_db, user_id=user_id, start_date=start_filter)

    assert len(results) == 1
    compiled_sql = str(mock_db.execute.call_args[0][0].compile(compile_kwargs={"literal_binds": True}))
    assert ">=" in compiled_sql
    assert "<=" not in compiled_sql


@pytest.mark.asyncio
async def test_get_trade_history_only_end_date(setup_service):
    """Verify trades before a certain date are included, newer ones excluded."""
    service, mock_db = setup_service
    user_id = uuid4()
    base_time = datetime(2026, 5, 26, 12, 0, 0)
    end_filter = base_time + timedelta(hours=1)

    # Target trade falls before end_filter
    trade_target = create_mock_trade(user_id, "BTCUSDT", 63000.0, base_time)

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [trade_target]
    mock_db.execute.return_value = mock_result

    results = await service.get_trade_history(db=mock_db, user_id=user_id, end_date=end_filter)

    assert len(results) == 1
    compiled_sql = str(mock_db.execute.call_args[0][0].compile(compile_kwargs={"literal_binds": True}))
    assert "<=" in compiled_sql
    assert ">=" not in compiled_sql


@pytest.mark.asyncio
async def test_get_trade_history_invalid_date_range(setup_service):
    """Should return an empty list gracefully if start_date > end_date[cite: 4]."""
    service, mock_db = setup_service
    user_id = uuid4()
    base_time = datetime(2026, 5, 26, 12, 0, 0)

    start_filter = base_time + timedelta(days=1)
    end_filter = base_time - timedelta(days=1)  # Invalid: start is in front of end

    # SQLAlchemy query will execute, but database engine naturally evaluates this intersection to zero rows
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    results = await service.get_trade_history(
        db=mock_db, user_id=user_id, start_date=start_filter, end_date=end_filter
    )

    assert results == []


@pytest.mark.asyncio
async def test_get_trade_history_symbol_filter_without_dates(setup_service):
    """Test that filtering by symbol alone works cleanly without any date bounds."""
    service, mock_db = setup_service
    user_id = uuid4()

    trade_eth = create_mock_trade(user_id, "ETHUSDT", 3200.0, datetime.utcnow())

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [trade_eth]
    mock_db.execute.return_value = mock_result

    results = await service.get_trade_history(db=mock_db, user_id=user_id, symbol="ETHUSDT")

    assert len(results) == 1
    assert results[0].symbol == "ETHUSDT"

    compiled_sql = str(mock_db.execute.call_args[0][0].compile(compile_kwargs={"literal_binds": True}))
    assert "trades.symbol =" in compiled_sql


@pytest.mark.asyncio
async def test_get_trade_history_pagination_limit(setup_service):
    """Verify the upper boundary limit parameter is mapped and passed down correctly[cite: 4]."""
    service, mock_db = setup_service
    user_id = uuid4()

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    custom_limit = 25
    await service.get_trade_history(db=mock_db, user_id=user_id, limit=custom_limit)

    compiled_sql = str(mock_db.execute.call_args[0][0].compile(compile_kwargs={"literal_binds": True}))
    assert "LIMIT 25" in compiled_sql or "LIMIT :limit" in str(mock_db.execute.call_args[0][0])


@pytest.mark.asyncio
async def test_get_trade_history_empty_result_set(setup_service):
    """Ensure the function safely maps and returns an empty list, never an unexpected error or None."""
    service, mock_db = setup_service
    user_id = uuid4()

    # Setup mock to simulate zero rows found matching criteria
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    results = await service.get_trade_history(db=mock_db, user_id=user_id)

    assert isinstance(results, list)
    assert len(results) == 0
