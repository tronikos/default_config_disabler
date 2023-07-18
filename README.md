[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Home Assistant integration to disable selected components from default_config.
See popular feature request at https://community.home-assistant.io/t/why-the-heck-is-default-config-so-difficult-to-customize/220112

Note: After a Home Assistant update this integration will re-disable selected components and automatically restart Home Assistant.

# Installation

## HACS
1. [Add](http://homeassistant.local:8123/hacs/integrations) custom integrations repository: https://github.com/tronikos/default_config_disabler
2. Select "Default Config Disabler" in the Integration tab and click download
3. Restart Home Assistant
4. Enable the integration

## Manual
1. Copy directory `custom_components/default_config_disabler` to your `<config dir>/custom_components` directory
2. Restart Home-Assistant
3. Enable the integration

## Enable the integration
1. Go to [Settings / Devices & Services / Integrations](http://homeassistant.local:8123/config/integrations). Click **+ ADD INTEGRATION**
2. Search for "Default Config Disabler" and click on it
3. Restart Home Assistant

# Configuration
1. Go to [Settings / Devices & Services / Integrations](http://homeassistant.local:8123/config/integrations)
2. Select "Default Config Disabler" and click on "Configure"
3. Select the default_config components you want to disable
