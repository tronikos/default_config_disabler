"""Tests for the Default Config Disabler integration."""

from pathlib import Path

from homeassistant.config import YAML_CONFIG_FILE
from homeassistant.core import HomeAssistant

from pytest_homeassistant_custom_component.common import MockConfigEntry


def configuration_yaml(hass: HomeAssistant) -> Path:
    """Return the path of the configuration.yaml under test."""
    return Path(hass.config.path(YAML_CONFIG_FILE))


async def setup_integration(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    """Add the config entry to Home Assistant and set it up."""
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
