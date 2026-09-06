[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Home Assistant integration to disable selected components from default_config.
See popular feature request at https://community.home-assistant.io/t/why-the-heck-is-default-config-so-difficult-to-customize/220112

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

# FAQ

## A component I disabled is still running. Is this broken?

No. This integration only stops `default_config` from setting up the components
you selected. Any other core or custom integration that lists the component as
a dependency will still cause Home Assistant to set it up. For example, ESPHome
depends on `assist_pipeline` (which in turn depends on `conversation`), so
Assist stays available on systems with ESPHome even when both are disabled here.

To find out what is loading a component, look at the
`Domains to be set up: ... Dependencies: ...` line in the startup log: if the
component is listed under `Dependencies`, something else pulls it in. As a
quick check for DHCP, opening https://my.home-assistant.io/redirect/config_dhcp/
shows an empty page when `dhcp` is not loaded.
