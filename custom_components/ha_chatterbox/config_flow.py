"""Config flow for HA Chatterbox TTS integration."""
import logging
import asyncio
import voluptuous as vol
import requests
import json
import os

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME
from homeassistant.helpers import selector

from .const import (
    DOMAIN, 
    DEFAULT_HOST, 
    DEFAULT_PORT, 
    CONF_VOICE,
    DEFAULT_VOICE,
    DEFAULT_TEMPERATURE,
    DEFAULT_SPEED_FACTOR,
    CONF_TEMPERATURE,
    CONF_SPEED_FACTOR,
    AVAILABLE_VOICES
)

_LOGGER = logging.getLogger(__name__)

def _load_voices_from_strings():
    """Load voice options from strings.json file."""
    try:
        # Get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        strings_path = os.path.join(current_dir, "strings.json")
        
        if os.path.exists(strings_path):
            with open(strings_path, 'r', encoding='utf-8') as f:
                strings_data = json.load(f)
                # Extract voice options from the voices section
                voices = strings_data.get("voices", {})
                if voices:
                    # Return list of voice IDs (keys)
                    voice_list = list(voices.keys())
                    _LOGGER.debug("Config flow loaded %d voices from strings.json: %s", len(voice_list), voice_list)
                    return voice_list
    except Exception as ex:
        _LOGGER.warning("Config flow could not load voices from strings.json: %s", ex)
    
    # Fallback to const.py voices
    _LOGGER.debug("Config flow using fallback voices from const.py")
    return AVAILABLE_VOICES

class HaChatterboxConfigFlow(config_entries.ConfigFlow):
    """Handle a config flow for HA Chatterbox TTS."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH
    
    @property
    def domain(self):
        """Return the domain."""
        return DOMAIN

    def __init__(self):
        """Initialize the config flow."""
        self._host = None
        self._port = None

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            # Validate connection to server
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            
            # Check for existing entries
            await self.async_set_unique_id(f"{host}:{port}")
            self._abort_if_unique_id_configured()
            
            # Test connection
            try:
                is_valid = await self._test_connection(host, port)
                if is_valid:
                    return self.async_create_entry(
                        title=f"HA Chatterbox TTS ({host}:{port})",
                        data={
                            CONF_HOST: host,
                            CONF_PORT: port,
                            CONF_NAME: user_input.get(CONF_NAME, "HA Chatterbox TTS"),
                        },
                        options={
                            CONF_VOICE: user_input.get(CONF_VOICE, DEFAULT_VOICE),
                            CONF_TEMPERATURE: user_input.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE),
                            CONF_SPEED_FACTOR: user_input.get(CONF_SPEED_FACTOR, DEFAULT_SPEED_FACTOR),
                        }
                    )
                else:
                    errors["base"] = "cannot_connect"
            except Exception as ex:
                _LOGGER.error("Error connecting to HA Chatterbox TTS: %s", ex)
                errors["base"] = "cannot_connect"

        # Show form with voice dropdown
        available_voices = _load_voices_from_strings()
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.Coerce(int),
                    vol.Optional(CONF_NAME, default="HA Chatterbox TTS"): str,
                    vol.Optional(CONF_VOICE, default=DEFAULT_VOICE): vol.In(available_voices),
                    vol.Optional(CONF_TEMPERATURE, default=DEFAULT_TEMPERATURE): vol.All(
                        vol.Coerce(float), vol.Range(min=0.0, max=1.0)
                    ),
                    vol.Optional(CONF_SPEED_FACTOR, default=DEFAULT_SPEED_FACTOR): vol.All(
                        vol.Coerce(float), vol.Range(min=0.5, max=2.0)
                    ),
                }
            ),
            errors=errors,
        )

    async def _test_connection(self, host: str, port: int) -> bool:
        """Test connection to the Chatterbox TTS server."""
        try:
            url = f"http://{host}:{port}/health"
            
            def _make_request():
                response = requests.get(url, timeout=10)
                return response.status_code == 200
            
            # Run in executor to avoid blocking
            return await self.hass.async_add_executor_job(_make_request)
            
        except Exception as ex:
            _LOGGER.error("Connection test failed: %s", ex)
            return False

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return HaChatterboxOptionsFlowHandler(config_entry)


class HaChatterboxOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for HA Chatterbox TTS."""

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

        # Get current values
        current_voice = self.config_entry.options.get(
            CONF_VOICE, 
            self.config_entry.data.get(CONF_VOICE, DEFAULT_VOICE)
        )
        current_temperature = self.config_entry.options.get(
            CONF_TEMPERATURE, DEFAULT_TEMPERATURE
        )
        current_speed = self.config_entry.options.get(
            CONF_SPEED_FACTOR, DEFAULT_SPEED_FACTOR
        )

        available_voices = _load_voices_from_strings()
        return self.async_show_form(
            step_id="tts_options",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_VOICE, default=current_voice): vol.In(available_voices),
                    vol.Optional(CONF_TEMPERATURE, default=current_temperature): vol.All(
                        vol.Coerce(float), vol.Range(min=0.0, max=1.0)
                    ),
                    vol.Optional(CONF_SPEED_FACTOR, default=current_speed): vol.All(
                        vol.Coerce(float), vol.Range(min=0.5, max=2.0)
                    ),
                }
            ),
        )