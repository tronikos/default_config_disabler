"""Tests for the Default Config Disabler config and options flows."""

from pathlib import Path

from custom_components.default_config_disabler.const import (
    CONF_COMPONENTS_TO_DISABLE,
    DOMAIN,
    NAME,
)

from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from . import setup_integration
from .conftest import DEFAULT_CONFIG_COMPONENTS

from pytest_homeassistant_custom_component.common import MockConfigEntry


async def test_user_flow_creates_the_entry(
    hass: HomeAssistant,
    config_yaml: Path,
) -> None:
    """The user is asked to confirm, and confirming creates the entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == NAME


async def test_only_one_entry_is_allowed(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    config_yaml: Path,
) -> None:
    """A second entry has nothing left to disable."""
    await setup_integration(hass, mock_config_entry)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "single_instance_allowed"


async def test_options_flow_offers_the_default_config_components(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    config_yaml: Path,
) -> None:
    """The options are the components default_config depends on."""
    await setup_integration(hass, mock_config_entry)

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"
    schema = result["data_schema"].schema
    key = next(key for key in schema if key == CONF_COMPONENTS_TO_DISABLE)
    assert schema[key].options == DEFAULT_CONFIG_COMPONENTS
    assert key.default() == []

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_COMPONENTS_TO_DISABLE: ["logbook", "stream"]}
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert mock_config_entry.options == {
        CONF_COMPONENTS_TO_DISABLE: ["logbook", "stream"]
    }


async def test_options_flow_forgets_components_default_config_dropped(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    config_yaml: Path,
) -> None:
    """A component core removed from default_config is not preselected."""
    mock_config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        mock_config_entry,
        options={CONF_COMPONENTS_TO_DISABLE: ["logbook", "no_longer_a_dependency"]},
    )
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)

    key = next(
        key for key in result["data_schema"].schema if key == CONF_COMPONENTS_TO_DISABLE
    )
    assert key.default() == ["logbook"]
