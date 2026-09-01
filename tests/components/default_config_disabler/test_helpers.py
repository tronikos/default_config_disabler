"""Tests for the Default Config Disabler helpers."""

from custom_components.default_config_disabler.const import DEFAULT_CONFIG_DOMAIN
from custom_components.default_config_disabler.helpers import (
    async_get_default_config_components,
)

from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration


async def test_components_come_from_the_default_config_manifest(
    hass: HomeAssistant,
) -> None:
    """The components on offer are the dependencies core's manifest declares."""
    integration = await async_get_integration(hass, DEFAULT_CONFIG_DOMAIN)

    components = await async_get_default_config_components(hass)

    assert components == integration.dependencies
    assert "conversation" in components
    # A copy, so a caller cannot mutate the loader's cached manifest.
    assert components is not integration.dependencies
