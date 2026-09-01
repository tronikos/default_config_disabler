"""Tests for the Default Config Disabler setup and teardown."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

from custom_components.default_config_disabler.const import (
    CONF_COMPONENTS_TO_DISABLE,
    DOMAIN,
)
import pytest

from homeassistant.config_entries import ConfigEntryDisabler, ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from homeassistant.setup import async_setup_component

from . import setup_integration
from .conftest import DEFAULT_CONFIG_COMPONENTS, DISABLED_YAML, ENABLED_YAML

from pytest_homeassistant_custom_component.common import MockConfigEntry

ISSUE_ID = "restart_required"


def _issue(issue_registry: ir.IssueRegistry) -> ir.IssueEntry | None:
    return issue_registry.async_get_issue(DOMAIN, ISSUE_ID)


async def test_setup_entry_disables_default_config(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    config_yaml: Path,
    issue_registry: ir.IssueRegistry,
) -> None:
    """Setting up the entry comments default_config out and asks for a restart."""
    await setup_integration(hass, mock_config_entry)

    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert config_yaml.read_text(encoding="utf-8") == DISABLED_YAML
    assert _issue(issue_registry) is not None


async def test_setup_entry_when_already_disabled(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    config_yaml: Path,
    issue_registry: ir.IssueRegistry,
) -> None:
    """An already commented out default_config needs no restart."""
    config_yaml.write_text(DISABLED_YAML, encoding="utf-8")

    await setup_integration(hass, mock_config_entry)

    assert config_yaml.read_text(encoding="utf-8") == DISABLED_YAML
    assert _issue(issue_registry) is None


async def test_remove_entry_enables_default_config(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    config_yaml: Path,
    issue_registry: ir.IssueRegistry,
) -> None:
    """Removing the entry puts default_config back."""
    await setup_integration(hass, mock_config_entry)
    assert config_yaml.read_text(encoding="utf-8") == DISABLED_YAML

    ir.async_delete_issue(hass, DOMAIN, ISSUE_ID)

    await hass.config_entries.async_remove(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_yaml.read_text(encoding="utf-8") == ENABLED_YAML
    assert _issue(issue_registry) is not None


async def test_remove_entry_when_default_config_is_already_enabled(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    config_yaml: Path,
    issue_registry: ir.IssueRegistry,
) -> None:
    """Nothing to put back means nothing to restart for."""
    await setup_integration(hass, mock_config_entry)
    config_yaml.write_text(ENABLED_YAML, encoding="utf-8")
    ir.async_delete_issue(hass, DOMAIN, ISSUE_ID)

    await hass.config_entries.async_remove(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_yaml.read_text(encoding="utf-8") == ENABLED_YAML
    assert _issue(issue_registry) is None


async def test_reload_entry_leaves_configuration_alone(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    config_yaml: Path,
    issue_registry: ir.IssueRegistry,
) -> None:
    """A reload must not uncomment and recomment default_config."""
    await setup_integration(hass, mock_config_entry)
    ir.async_delete_issue(hass, DOMAIN, ISSUE_ID)

    with patch(
        "custom_components.default_config_disabler._update_default_config",
        return_value=False,
    ) as mock_update:
        assert await hass.config_entries.async_reload(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    mock_update.assert_called_once_with(hass, True)
    assert config_yaml.read_text(encoding="utf-8") == DISABLED_YAML
    assert _issue(issue_registry) is None


async def test_disabling_entry_enables_default_config(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    config_yaml: Path,
) -> None:
    """Disabling the entry restores default_config, since nothing else would."""
    await setup_integration(hass, mock_config_entry)

    await hass.config_entries.async_set_disabled_by(
        mock_config_entry.entry_id, ConfigEntryDisabler.USER
    )
    await hass.async_block_till_done()

    assert config_yaml.read_text(encoding="utf-8") == ENABLED_YAML


@pytest.mark.parametrize(
    ("before", "after"),
    [
        ("default_config:\nfrontend:\n", "# default_config:\nfrontend:\n"),
        ("frontend:\ndefault_config:", "frontend:\n# default_config:"),
        ("default_config:   \n", "# default_config:   \n"),
        ("default_config: # keep\n", "# default_config: # keep\n"),
        ("frontend:\r\ndefault_config:\r\n", "frontend:\r\n# default_config:\r\n"),
    ],
    ids=[
        "first-line",
        "no-trailing-newline",
        "trailing-space",
        "inline-comment",
        "crlf",
    ],
)
async def test_default_config_is_found_in_any_shape(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    config_yaml: Path,
    before: str,
    after: str,
) -> None:
    """The line is recognised wherever and however it is written."""
    config_yaml.write_text(before, encoding="utf-8", newline="")

    await setup_integration(hass, mock_config_entry)
    assert config_yaml.read_text(encoding="utf-8", newline="") == after

    await hass.config_entries.async_remove(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_yaml.read_text(encoding="utf-8", newline="") == before


@pytest.mark.parametrize(
    "content",
    ["foo:\n  default_config:\n", "my_default_config:\n", "zdefault_config: x\n"],
    ids=["indented", "prefixed", "not-a-bare-key"],
)
async def test_lookalike_lines_are_left_alone(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    config_yaml: Path,
    content: str,
    issue_registry: ir.IssueRegistry,
) -> None:
    """Only a top level default_config key is touched."""
    config_yaml.write_text(content, encoding="utf-8")

    await setup_integration(hass, mock_config_entry)

    assert config_yaml.read_text(encoding="utf-8") == content
    assert _issue(issue_registry) is None


async def test_failed_write_leaves_configuration_intact(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    config_yaml: Path,
    caplog: pytest.LogCaptureFixture,
    issue_registry: ir.IssueRegistry,
) -> None:
    """A write that dies part way through must not truncate configuration.yaml."""
    with patch(
        "custom_components.default_config_disabler.os.replace",
        side_effect=OSError("no space left on device"),
    ):
        await setup_integration(hass, mock_config_entry)

    assert config_yaml.read_text(encoding="utf-8") == ENABLED_YAML
    assert not list(config_yaml.parent.glob("*.tmp"))
    assert "Error writing" in caplog.text
    assert _issue(issue_registry) is None


async def test_missing_configuration_yaml_is_reported(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    config_yaml: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """An unreadable configuration.yaml is logged instead of failing setup."""
    config_yaml.unlink()

    await setup_integration(hass, mock_config_entry)

    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert "Error reading" in caplog.text


async def test_yaml_default_config_disables_and_defers(
    hass: HomeAssistant,
    config_yaml: Path,
    mock_setup_components: AsyncMock,
) -> None:
    """While default_config is still enabled it sets its own components up."""
    assert await async_setup_component(hass, DOMAIN, {"default_config": None})
    await hass.async_block_till_done()

    assert config_yaml.read_text(encoding="utf-8") == DISABLED_YAML
    mock_setup_components.assert_not_called()


async def test_components_are_set_up_except_the_disabled_ones(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    config_yaml: Path,
    mock_setup_components: AsyncMock,
) -> None:
    """Everything default_config depends on is set up bar the user's selection."""
    mock_config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        mock_config_entry, options={CONF_COMPONENTS_TO_DISABLE: ["logbook"]}
    )
    config_yaml.write_text(DISABLED_YAML, encoding="utf-8")

    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()

    assert {call.args[1] for call in mock_setup_components.call_args_list} == set(
        DEFAULT_CONFIG_COMPONENTS
    ) - {"logbook"}


async def test_setup_clears_a_stale_restart_issue(
    hass: HomeAssistant,
    config_yaml: Path,
    issue_registry: ir.IssueRegistry,
) -> None:
    """A restart clears the issue the previous run raised."""
    config_yaml.write_text(DISABLED_YAML, encoding="utf-8")
    ir.async_create_issue(
        hass,
        DOMAIN,
        ISSUE_ID,
        is_fixable=True,
        severity=ir.IssueSeverity.WARNING,
        translation_key=ISSUE_ID,
    )

    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()

    assert _issue(issue_registry) is None


async def test_changing_options_asks_for_a_restart(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    config_yaml: Path,
    issue_registry: ir.IssueRegistry,
) -> None:
    """Disabling a different set of components needs a restart to take effect."""
    await setup_integration(hass, mock_config_entry)
    ir.async_delete_issue(hass, DOMAIN, ISSUE_ID)

    hass.config_entries.async_update_entry(
        mock_config_entry, options={CONF_COMPONENTS_TO_DISABLE: ["logbook"]}
    )
    await hass.async_block_till_done()

    assert _issue(issue_registry) is not None
