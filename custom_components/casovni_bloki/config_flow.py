import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN

class CasovniBlokiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Casovni Bloki."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Create or update the configuration entry
            return self.async_create_entry(title="Casovni Bloki", data=user_input)

        # Define the schema for the config flow
        data_schema = vol.Schema({
            vol.Required("block_1_limit", default=5.5): float,
            vol.Required("block_2_limit", default=7.3): float,
            vol.Required("block_3_limit", default=9.1): float,
            vol.Required("block_4_limit", default=9.1): float,
            vol.Required("block_5_limit", default=9.1): float,
        })

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow."""
        return CasovniBlokiOptionsFlow(config_entry)


class CasovniBlokiOptionsFlow(config_entries.OptionsFlow):
    """Handle Casovni Bloki options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            # Update the config entry options
            return self.async_create_entry(title="", data=user_input)

        # Fallback to data if options are not set yet
        data = self.config_entry.data
        options = self.config_entry.options

        # Show the form to modify the limits for each block
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("block_1_limit", default=options.get("block_1_limit", data.get("block_1_limit", 0))): vol.Coerce(float),
                vol.Required("block_2_limit", default=options.get("block_2_limit", data.get("block_2_limit", 0))): vol.Coerce(float),
                vol.Required("block_3_limit", default=options.get("block_3_limit", data.get("block_3_limit", 0))): vol.Coerce(float),
                vol.Required("block_4_limit", default=options.get("block_4_limit", data.get("block_4_limit", 0))): vol.Coerce(float),
                vol.Required("block_5_limit", default=options.get("block_5_limit", data.get("block_5_limit", 0))): vol.Coerce(float),
            })
        )
