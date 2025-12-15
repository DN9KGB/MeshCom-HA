from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from . import DOMAIN


class MeshComConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle initial configuration of the MeshCom integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step when the integration is added."""
        if user_input is not None:
            # Only allow a single instance of this integration
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title="MeshCom",
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required("bind_ip", default="0.0.0.0"): str,
                vol.Required("port", default=1799): int,
                vol.Required("my_call", default="DXXXXX"): str,
                vol.Required("groups", default="*,10,262"): str,
            }
        )

        # Labels, titles and descriptions are provided via translations
        # in translations/en.json and translations/de.json
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Return the options flow handler."""
        return MeshComOptionsFlow(config_entry)


class MeshComOptionsFlow(config_entries.OptionsFlow):
    """Handle the options flow for existing MeshCom entries."""

    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        """Initialize MeshCom options flow."""
        self.entry = entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Manage the MeshCom options."""
        if user_input is not None:
            # Store options; async_setup_entry should prefer entry.options over entry.data
            return self.async_create_entry(title="", data=user_input)

        # Use existing options first, fall back to initial data
        current = self.entry.options or self.entry.data

        data_schema = vol.Schema(
            {
                vol.Required("bind_ip", default=current.get("bind_ip", "0.0.0.0")): str,
                vol.Required("port", default=current.get("port", 1799)): int,
                vol.Required("my_call", default=current.get("my_call", "DN9XXX")): str,
                vol.Required("groups", default=current.get("groups", "*,LOCAL")): str,
            }
        )

        # Again, field labels and descriptions are taken from translations
        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
        )
