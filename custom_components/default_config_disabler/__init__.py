"""The Default Config Disabler integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import SERVICE_HOMEASSISTANT_RESTART
from homeassistant.core import DOMAIN as HA_DOMAIN, HomeAssistant

from .const import CONF_COMPONENTS_TO_DISABLE
from .helpers import (
    backup_original_default_config_manifest,
    load_default_config_manifest,
    load_original_default_config_manifest,
    restore_original_default_config_manifest,
    save_default_config_manifest,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Default Config Disabler from a config entry."""
    disabled_components = entry.options.get(CONF_COMPONENTS_TO_DISABLE, [])

    backup_original_default_config_manifest()

    new_manifest = load_original_default_config_manifest()
    for disabled_component in disabled_components:
        if disabled_component in new_manifest["dependencies"]:
            new_manifest["dependencies"].remove(disabled_component)

    current_manifest = load_default_config_manifest()

    if new_manifest == current_manifest:
        _LOGGER.info(
            "Components: %s are already removed from default_config",
            disabled_components,
        )
    else:
        save_default_config_manifest(new_manifest)
        _LOGGER.warning(
            "Components: %s were removed from default_config", disabled_components
        )
        _LOGGER.warning("Restarting Home Assistant to use the updated default_config")
        await hass.services.async_call(HA_DOMAIN, SERVICE_HOMEASSISTANT_RESTART)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if restore_original_default_config_manifest():
        _LOGGER.warning("Restarting Home Assistant to use the original default_config")
        await hass.services.async_call(HA_DOMAIN, SERVICE_HOMEASSISTANT_RESTART)
    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
