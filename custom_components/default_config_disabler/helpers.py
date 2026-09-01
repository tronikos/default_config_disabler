"""Helper functions for the Default Config Disabler integration."""

from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration

from .const import DEFAULT_CONFIG_DOMAIN


async def async_get_default_config_components(hass: HomeAssistant) -> list[str]:
    """Return the list of components default_config depends on."""
    integration = await async_get_integration(hass, DEFAULT_CONFIG_DOMAIN)
    return list(integration.dependencies)
