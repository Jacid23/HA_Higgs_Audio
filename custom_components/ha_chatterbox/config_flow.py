"""Config flow for HA Higgs Audio TTS integration."""
import logging
import asyncio
import voluptuous as vol
import requests
import json
import os

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME

from .const import (
    DOMAIN, 
    DEFAULT_HOST, 
    DEFAULT_PORT, 
    CONF_VOICE,
    DEFAULT_VOICE,
    DEFAULT_TEMPERATURE,
    DEFAULT_EXAGGERATION,
    DEFAULT_CFG_WEIGHT,
    DEFAULT_SEED,
    DEFAULT_SPEED_FACTOR,
    CONF_TEMPERATURE,
    CONF_EXAGGERATION,
    CONF_CFG_WEIGHT,
    CONF_SEED,
    CONF_SPEED_FACTOR,
    AVAILABLE_VOICES
)

_LOGGER = logging.getLogger(__name__)

def _load_voices_from_strings():
    """Load voice options from strings.json file."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        strings_path = os.path.join(current_dir, "strings.json")
        if os.path.exists(strings_path):
            with open(strings_path, 'r', encoding='utf-8') as f:
                strings_data = json.load(f)
                voices = strings_data.get("voices", {})
                if voices:
                    voice_list = list(voices.keys())
                    _LOGGER.debug("Config flow loaded %d voices from strings.json: %s", len(voice_list), voice_list)
                    return voice_list
    except Exception as ex:
        _LOGGER.warning("Config flow could not load voices from strings.json: %s", ex)
    _LOGGER.debug("Config flow using fallback voices from const.py")
    return AVAILABLE_VOICES

class HaHiggsAudioConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HA Higgs Audio TTS."""

    VERSION = 1

    def __init__(self):
        self._host = None
        self._port = None

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            await self.async_set_unique_id(f"{host}:{port}")
            self._abort_if_unique_id_configured()
            try:
                is_valid = await self._test_connection(host, port)
                if is_valid:
                    return self.async_create_entry(
                        title=user_input.get(CONF_NAME, f"HA Higgs Audio ({host}:{port})"),
                        data={
                            CONF_HOST: host,
                            CONF_PORT: port,
                            CONF_NAME: user_input.get(CONF_NAME, "HA Higgs Audio TTS"),
                            CONF_VOICE: user_input.get(CONF_VOICE, DEFAULT_VOICE),
                            CONF_TEMPERATURE: user_input.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE),
                            CONF_EXAGGERATION: user_input.get(CONF_EXAGGERATION, DEFAULT_EXAGGERATION),
                            CONF_CFG_WEIGHT: user_input.get(CONF_CFG_WEIGHT, DEFAULT_CFG_WEIGHT),
                            CONF_SEED: user_input.get(CONF_SEED, DEFAULT_SEED),
                            CONF_SPEED_FACTOR: user_input.get(CONF_SPEED_FACTOR, DEFAULT_SPEED_FACTOR),
                        }
                    )
                else:
                    errors["base"] = "cannot_connect"
            except requests.RequestException:
                _LOGGER.error("Connection error to HA Higgs Audio TTS server")
                errors["base"] = "cannot_connect"
            except Exception as ex:
                _LOGGER.error("Unexpected error connecting to HA Higgs Audio TTS: %s", ex)
                errors["base"] = "unknown"

        available_voices = _load_voices_from_strings()
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.Coerce(int),
                    vol.Optional(CONF_NAME, default="HA Higgs Audio TTS"): str,
                    vol.Optional(CONF_VOICE, default=DEFAULT_VOICE): vol.In(available_voices),
                    vol.Optional(CONF_TEMPERATURE, default=DEFAULT_TEMPERATURE): vol.All(
                        vol.Coerce(float), vol.Range(min=0.0, max=1.0)
                    ),
                    vol.Optional(CONF_EXAGGERATION, default=DEFAULT_EXAGGERATION): vol.All(
                        vol.Coerce(float), vol.Range(min=0.0, max=2.0)
                    ),
                    vol.Optional(CONF_CFG_WEIGHT, default=DEFAULT_CFG_WEIGHT): vol.All(
                        vol.Coerce(float), vol.Range(min=0.0, max=1.0)
                    ),
                    vol.Optional(CONF_SEED, default=DEFAULT_SEED): vol.Coerce(int),
                    vol.Optional(CONF_SPEED_FACTOR, default=DEFAULT_SPEED_FACTOR): vol.All(
                        vol.Coerce(float), vol.Range(min=0.5, max=2.0)
                    ),
                }
            ),
            errors=errors,
        )

    async def _test_connection(self, host: str, port: int) -> bool:
        url = f"http://{host}:{port}/health"
        def _make_request():
            try:
                response = requests.get(url, timeout=10)
                return response.status_code == 200
            except requests.RequestException as ex:
                _LOGGER.error("Connection test failed: %s", ex)
                raise
        return await self.hass.async_add_executor_job(_make_request)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return HAChatterboxOptionsFlowHandler(config_entry)

class HAChatterboxOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry
    async def async_step_init(self, user_input=None):
        return await self.async_step_tts_options(user_input)
    async def async_step_tts_options(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        options = self.config_entry.options
        data = self.config_entry.data
        current_voice = options.get(CONF_VOICE, data.get(CONF_VOICE, DEFAULT_VOICE))
        current_temperature = options.get(CONF_TEMPERATURE, data.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE))
        current_exaggeration = options.get(CONF_EXAGGERATION, data.get(CONF_EXAGGERATION, DEFAULT_EXAGGERATION))
        current_cfg_weight = options.get(CONF_CFG_WEIGHT, data.get(CONF_CFG_WEIGHT, DEFAULT_CFG_WEIGHT))
        current_seed = options.get(CONF_SEED, data.get(CONF_SEED, DEFAULT_SEED))
        current_speed = options.get(CONF_SPEED_FACTOR, data.get(CONF_SPEED_FACTOR, DEFAULT_SPEED_FACTOR))
        available_voices = _load_voices_from_strings()
        return self.async_show_form(
            step_id="tts_options",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_VOICE, default=current_voice): vol.In(available_voices),
                    vol.Optional(CONF_TEMPERATURE, default=current_temperature): vol.All(
                        vol.Coerce(float), vol.Range(min=0.0, max=1.0)
                    ),
                    vol.Optional(CONF_EXAGGERATION, default=current_exaggeration): vol.All(
                        vol.Coerce(float), vol.Range(min=0.0, max=2.0)
                    ),
                    vol.Optional(CONF_CFG_WEIGHT, default=current_cfg_weight): vol.All(
                        vol.Coerce(float), vol.Range(min=0.0, max=1.0)
                    ),
                    vol.Optional(CONF_SEED, default=current_seed): vol.Coerce(int),
                    vol.Optional(CONF_SPEED_FACTOR, default=current_speed): vol.All(
                        vol.Coerce(float), vol.Range(min=0.5, max=2.0)
                    ),
                }
            ),
        )
