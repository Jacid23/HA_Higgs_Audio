"""Config flow for Chatterbox TTS integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME

from .const import DOMAIN, DEFAULT_HOST, DEFAULT_PORT, CONF_VOICE

_LOGGER = logging.getLogger(__name__)

class ChatterboxTTSFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Chatterbox TTS."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            # Validate connection to server
            try:
                # Return configuration if valid
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, "Chatterbox TTS"),
                    data=user_input,
                )
            except Exception as ex:
                _LOGGER.error("Error connecting to Chatterbox TTS: %s", ex)
                errors["base"] = "cannot_connect"

        # Show form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Optional(CONF_NAME, default="Chatterbox TTS"): str,
                    vol.Optional(CONF_VOICE, default="Emily"): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return ChatterboxTTSOptionsFlowHandler(config_entry)


class ChatterboxTTSOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for Chatterbox TTS."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return await self.async_step_tts_options(user_input)

    async def async_step_tts_options(self, user_input=None):
        """Handle TTS options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="tts_options",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_VOICE,
                        default=self.config_entry.options.get(
                            CONF_VOICE, 
                            self.config_entry.data.get(CONF_VOICE, "Emily")
                        ),
                    ): str,
                }
            ),
        )