"""Fixtures for the Default Config Disabler integration tests."""

from collections.abc import Generator
from pathlib import Path
from unittest.mock import AsyncMock, patch

from custom_components.default_config_disabler.const import DOMAIN, NAME
import pytest

from homeassistant.components.recorder import Recorder
from homeassistant.core import HomeAssistant

from . import configuration_yaml

from pytest_homeassistant_custom_component.common import MockConfigEntry

# A stand-in for the dependencies of core's default_config manifest. Using a
# fixed list keeps the tests from changing meaning every time core adds one.
DEFAULT_CONFIG_COMPONENTS = ["conversation", "logbook", "stream"]

ENABLED_YAML = """\
# Loads default set of integrations. Do not remove.
default_config:

frontend:
"""

DISABLED_YAML = ENABLED_YAML.replace("default_config:", "# default_config:")


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Load the integration from custom_components rather than from core."""


@pytest.fixture(autouse=True)
def mock_recorder_before_hass(recorder_db_url: str) -> None:
    """Prepare the recorder database before Home Assistant starts."""


@pytest.fixture(autouse=True)
def setup_recorder(recorder_mock: Recorder) -> None:
    """Provide the recorder that the integration lists as a dependency."""


@pytest.fixture
def hass_config_dir(hass_tmp_config_dir: str) -> str:
    """Give each test a configuration directory it is allowed to write to."""
    return hass_tmp_config_dir


@pytest.fixture
def config_yaml(hass: HomeAssistant) -> Path:
    """Return a configuration.yaml that has default_config enabled."""
    path = configuration_yaml(hass)
    path.write_text(ENABLED_YAML, encoding="utf-8")
    return path


@pytest.fixture(autouse=True)
def mock_setup_components() -> Generator[AsyncMock]:
    """Keep the tests from setting up the real default_config dependencies."""
    with (
        patch(
            "custom_components.default_config_disabler.async_setup_component",
            return_value=True,
        ) as mock_setup_component,
        patch(
            "custom_components.default_config_disabler.ha_default_config.async_setup",
            return_value=True,
        ),
        patch(
            "custom_components.default_config_disabler.async_get_default_config_components",
            return_value=DEFAULT_CONFIG_COMPONENTS,
        ),
        patch(
            "custom_components.default_config_disabler.config_flow.async_get_default_config_components",
            return_value=DEFAULT_CONFIG_COMPONENTS,
        ),
    ):
        yield mock_setup_component


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a config entry for the integration."""
    return MockConfigEntry(domain=DOMAIN, title=NAME)
