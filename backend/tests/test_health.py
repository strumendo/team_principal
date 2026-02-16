"""
Tests for health check endpoints.
Testes para endpoints de verificacao de saude.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    """Test GET /health returns ok / Testa GET /health retorna ok."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_check_db(client: AsyncClient) -> None:
    """Test GET /health/db returns ok / Testa GET /health/db retorna ok."""
    response = await client.get("/health/db")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
