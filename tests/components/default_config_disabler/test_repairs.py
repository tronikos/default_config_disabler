"""Tests for the Default Config Disabler restart repair."""

from http import HTTPStatus
from pathlib import Path

from custom_components.default_config_disabler.const import DOMAIN

from homeassistant.components.homeassistant import (
    DOMAIN as HOMEASSISTANT_DOMAIN,
    SERVICE_HOMEASSISTANT_RESTART,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from homeassistant.setup import async_setup_component

from . import setup_integration

from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_mock_service,
)
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

ISSUE_ID = "restart_required"


async def test_restart_repair_restarts_home_assistant(
    hass: HomeAssistant,
    hass_client: ClientSessionGenerator,
    mock_config_entry: MockConfigEntry,
    config_yaml: Path,
    issue_registry: ir.IssueRegistry,
) -> None:
    """Confirming the repair restarts Home Assistant and clears the issue."""
    assert await async_setup_component(hass, "repairs", {})
    await setup_integration(hass, mock_config_entry)
    assert issue_registry.async_get_issue(DOMAIN, ISSUE_ID) is not None

    restart_calls = async_mock_service(
        hass, HOMEASSISTANT_DOMAIN, SERVICE_HOMEASSISTANT_RESTART
    )
    client = await hass_client()

    response = await client.post(
        "/api/repairs/issues/fix",
        json={"handler": DOMAIN, "issue_id": ISSUE_ID},
    )
    assert response.status == HTTPStatus.OK
    flow = await response.json()
    assert flow["step_id"] == "confirm"

    response = await client.post(f"/api/repairs/issues/fix/{flow['flow_id']}")
    assert response.status == HTTPStatus.OK
    assert (await response.json())["type"] == "create_entry"
    await hass.async_block_till_done()

    assert len(restart_calls) == 1
    assert issue_registry.async_get_issue(DOMAIN, ISSUE_ID) is None
