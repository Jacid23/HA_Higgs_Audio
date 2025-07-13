"""
Chatterbox HA TTS Provider Platform for Home Assistant (Provider API)

Provides Text-to-Speech services using Chatterbox TTS server, with selectable voices/options.
"""
import logging
import requests
import json
import os
import functools

from homeassistant.components.tts import Provider
from .const import (
    DOMAIN,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_VOICE,
    DEFAULT_TEMPERATURE,
    DEFAULT_EXAGGERATION,
    DEFAULT_CFG_WEIGHT,
    DEFAULT_SEED,
    DEFAULT_SPEED_FACTOR,
    CONF_VOICE,
    CONF_TEMPERATURE,
    CONF_EXAGGERATION,
    CONF_CFG_WEIGHT,
    CONF_SEED,
    CONF_SPEED_FACTOR,
)

_LOGGER = logging.getLogger(__name__)

# Util: Load voices from strings.json, fallback to const.py AVAILABLE_VOICES
_DEF_VOICES = None

def _load_voices():
    global _DEF_VOICES
    if _DEF_VOICES is not None:
        return _DEF_VOICES
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        strings_path = os.path.join(current_dir, "strings.json")
        if os.path.exists(strings_path):
            with open(strings_path, 'r', encoding='utf-8') as f:
                voices = json.load(f).get("voices", {})
                if voices:
                    _DEF_VOICES = list(voices.keys())
                    return _DEF_VOICES
    except Exception as ex:
        _LOGGER.warning("Could not load voices from strings.json: %s", ex)
    # fallback
    try:
        from .const import AVAILABLE_VOICES
        _DEF_VOICES = AVAILABLE_VOICES
        return _DEF_VOICES
    except Exception:
        _DEF_VOICES = [DEFAULT_VOICE]
        return _DEF_VOICES

class ChatterboxTTSProvider(Provider):
    def __init__(self, hass, host, port, base_url, config_entry):
        self.hass = hass
        self._host = host
        self._port = port
        self._base_url = base_url
        self._config_entry = config_entry

        opts = (config_entry.options if config_entry else {})
        data = (config_entry.data if config_entry else {})
        self._language = data.get("language", "en-US")
        self._voice = opts.get(CONF_VOICE, data.get(CONF_VOICE, DEFAULT_VOICE))
        self._temperature = opts.get(CONF_TEMPERATURE, data.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE))
        self._exaggeration = opts.get(CONF_EXAGGERATION, data.get(CONF_EXAGGERATION, DEFAULT_EXAGGERATION))
        self._cfg_weight = opts.get(CONF_CFG_WEIGHT, data.get(CONF_CFG_WEIGHT, DEFAULT_CFG_WEIGHT))
        self._seed = opts.get(CONF_SEED, data.get(CONF_SEED, DEFAULT_SEED))
        self._speed_factor = opts.get(CONF_SPEED_FACTOR, data.get(CONF_SPEED_FACTOR, DEFAULT_SPEED_FACTOR))

    @property
    def default_language(self):
        return "en-US"

    @property
    def supported_languages(self):
        return ["en-US"]

    @property
    def supported_options(self):
        return [CONF_VOICE, CONF_TEMPERATURE, CONF_EXAGGERATION, CONF_CFG_WEIGHT, CONF_SEED, CONF_SPEED_FACTOR]

    @property
    def default_options(self):
        voices = _load_voices()
        return {
            CONF_VOICE: voices[0] if voices else DEFAULT_VOICE,
            CONF_TEMPERATURE: self._temperature,
            CONF_EXAGGERATION: self._exaggeration,
            CONF_CFG_WEIGHT: self._cfg_weight,
            CONF_SEED: self._seed,
            CONF_SPEED_FACTOR: self._speed_factor,
        }

    @property
    def supported_voices(self):
        voices = _load_voices()
        return {"en-US": voices}

    @property
    def default_voice(self):
        voices = _load_voices()
        return voices[0] if voices else DEFAULT_VOICE

    def _get_voice_filename(self, name: str):
        if not name:
            return None
        return name if name.endswith('.wav') else f"{name}.wav"

    async def async_get_tts_audio(self, message, language, options=None):
        options = options or {}
        selected_voice = options.get(CONF_VOICE, self._voice)
        temperature = options.get(CONF_TEMPERATURE, self._temperature)
        exaggeration = options.get(CONF_EXAGGERATION, self._exaggeration)
        cfg_weight = options.get(CONF_CFG_WEIGHT, self._cfg_weight)
        seed = options.get(CONF_SEED, self._seed)
        speed_factor = options.get(CONF_SPEED_FACTOR, self._speed_factor)
        voice_filename = self._get_voice_filename(selected_voice)

        data = {
            "text": message,
            "predefined_voice_id": voice_filename,
            "temperature": temperature,
            "exaggeration": exaggeration,
            "cfg_weight": cfg_weight,
            "seed": seed,
            "speed_factor": speed_factor,
            "output_format": "wav",
        }

        _LOGGER.debug("ChatterboxTTSProvider TTS request: %s", data)

        try:
            url = f"{self._base_url}/tts"
            response = await self.hass.async_add_executor_job(
                functools.partial(
                    requests.post,
                    url,
                    json=data,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
            )
            if response.status_code == 200:
                return ("wav", response.content)
            else:
                _LOGGER.error("Chatterbox TTS request failed: %s %s", response.status_code, response.text)
                return ("wav", b"")
        except Exception as ex:
            _LOGGER.error("Error connecting to Chatterbox TTS: %s", ex)
            return ("wav", b"")

# PLATFORM REGISTRATION
async def async_get_engine(hass, config, discovery_info=None):
    """Set up the TTS provider for HA."""
    # Find config entry
    entry_id = None
    for eid, e in getattr(hass.data.get(DOMAIN, {}), "items", lambda: [])():
        entry_id = eid
        entry = e
        break
    if entry_id is None:
        raise RuntimeError("No config entry found for Chatterbox HA TTS!")
    return ChatterboxTTSProvider(
        hass=hass,
        host=entry["host"],
        port=entry["port"],
        base_url=entry["base_url"],
        config_entry=getattr(hass.config_entries, "async_get_entry", lambda eid: None)(entry_id),
    )
