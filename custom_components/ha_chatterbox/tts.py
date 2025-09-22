"""Higgs Audio TTS Provider Platform for Home Assistant."""
import logging
import requests
import json
import os
import functools
import voluptuous as vol

from homeassistant.components.tts import Provider, PLATFORM_SCHEMA, TtsAudioType
from homeassistant.const import CONF_NAME
import homeassistant.helpers.config_validation as cv
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

# Platform schema for TTS configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default="Higgs Audio TTS"): cv.string,
})

# Load voices from strings.json, fallback to const.py AVAILABLE_VOICES
_DEF_VOICES = None

def _load_voices():
    """Load available voices from strings.json or fallback to constants."""
    global _DEF_VOICES
    if _DEF_VOICES is not None:
        return _DEF_VOICES
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        strings_path = os.path.join(current_dir, "strings.json")
        if os.path.exists(strings_path):
            with open(strings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                voices_data = data.get("voices", {})
                if voices_data:
                    _DEF_VOICES = list(voices_data.keys())
                    _LOGGER.info("Loaded %d voices from strings.json", len(_DEF_VOICES))
                    return _DEF_VOICES
    except Exception as ex:
        _LOGGER.warning("Could not load voices from strings.json: %s", ex)
    
    # Fallback to constants
    try:
        from .const import AVAILABLE_VOICES
        _DEF_VOICES = AVAILABLE_VOICES
        _LOGGER.info("Using fallback voices from constants (%d voices)", len(_DEF_VOICES))
        return _DEF_VOICES
    except Exception:
        _DEF_VOICES = [DEFAULT_VOICE]
        _LOGGER.warning("Using default voice only: %s", _DEF_VOICES)
        return _DEF_VOICES

class HiggsAudioTTSProvider(Provider):
    """Higgs Audio TTS Provider."""

    def __init__(self, hass, host, port, base_url, config_entry):
        """Initialize the TTS provider."""
        self.hass = hass
        self._host = host
        self._port = port
        self._base_url = base_url
        self._config_entry = config_entry

        # Get configuration from config entry
        opts = (config_entry.options if config_entry else {})
        data = (config_entry.data if config_entry else {})
        self._language = data.get("language", "en-US")
        self._voice = opts.get(CONF_VOICE, data.get(CONF_VOICE, DEFAULT_VOICE))
        self._temperature = opts.get(CONF_TEMPERATURE, data.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE))
        self._exaggeration = opts.get(CONF_EXAGGERATION, data.get(CONF_EXAGGERATION, DEFAULT_EXAGGERATION))
        self._cfg_weight = opts.get(CONF_CFG_WEIGHT, data.get(CONF_CFG_WEIGHT, DEFAULT_CFG_WEIGHT))
        self._seed = opts.get(CONF_SEED, data.get(CONF_SEED, DEFAULT_SEED))
        self._speed_factor = opts.get(CONF_SPEED_FACTOR, data.get(CONF_SPEED_FACTOR, DEFAULT_SPEED_FACTOR))
        
        voices = _load_voices()
        _LOGGER.info("HiggsAudioTTSProvider initialized with %d voices", len(voices))

    @property
    def default_language(self):
        """Return the default language."""
        return "en-US"

    @property
    def supported_languages(self):
        """Return list of supported languages."""
        return ["en", "en-US"]

    @property
    def supported_options(self):
        """Return list of supported options."""
        return [CONF_VOICE, CONF_TEMPERATURE, CONF_EXAGGERATION, CONF_CFG_WEIGHT, CONF_SEED, CONF_SPEED_FACTOR]

    @property
    def default_options(self):
        """Return a dict including default options."""
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
        """Return list of supported voices."""
        voices = _load_voices()
        return voices

    @property
    def default_voice(self):
        """Return the default voice."""
        voices = _load_voices()
        default = voices[0] if voices else DEFAULT_VOICE
        return default
    
    @property
    def name(self):
        """Return the name of the TTS provider."""
        return "Higgs Audio TTS"

    async def async_get_tts_audio(self, message, language, options=None) -> TtsAudioType:
        """Load TTS from Higgs Audio server."""
        options = options or {}
        selected_voice = options.get(CONF_VOICE, self._voice)
        temperature = options.get(CONF_TEMPERATURE, self._temperature)
        exaggeration = options.get(CONF_EXAGGERATION, self._exaggeration)
        cfg_weight = options.get(CONF_CFG_WEIGHT, self._cfg_weight)
        seed = options.get(CONF_SEED, self._seed)
        speed_factor = options.get(CONF_SPEED_FACTOR, self._speed_factor)

        data = {
            "text": message,
            "predefined_voice_id": selected_voice,
            "temperature": temperature,
            "exaggeration": exaggeration,
            "cfg_weight": cfg_weight,
            "seed": seed,
            "speed_factor": speed_factor,
            "output_format": "wav",
        }

        _LOGGER.debug("Higgs Audio TTS request: %s", data)

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
                _LOGGER.error("Higgs Audio TTS request failed: %s %s", response.status_code, response.text)
                return ("wav", b"")
        except Exception as ex:
            _LOGGER.error("Error connecting to Higgs Audio TTS: %s", ex)
            return ("wav", b"")

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up TTS platform from config entry."""
    _LOGGER.debug("Setting up TTS platform from config entry: %s", config_entry.entry_id)
    
    # Get domain data
    domain_data = hass.data.get(DOMAIN, {})
    entry_data = domain_data.get(config_entry.entry_id)
    
    if not entry_data:
        _LOGGER.error("No entry data found for config entry: %s", config_entry.entry_id)
        return False

    # Create provider
    provider = HiggsAudioTTSProvider(
        hass=hass,
        host=entry_data["host"],
        port=entry_data["port"],
        base_url=entry_data["base_url"],
        config_entry=config_entry,
    )
    
    # Store provider in hass data for async_get_engine to find
    hass.data[DOMAIN][f"{config_entry.entry_id}_provider"] = provider
    _LOGGER.debug("TTS Provider stored in hass.data")
    
    return True

async def async_get_engine(hass, config, discovery_info=None):
    """Get the TTS engine."""
    _LOGGER.debug("async_get_engine called")
    
    # Find our stored provider
    domain_data = hass.data.get(DOMAIN, {})
    for key, value in domain_data.items():
        if key.endswith("_provider") and isinstance(value, HiggsAudioTTSProvider):
            _LOGGER.debug("Found and returning TTS provider")
            return value
    
    _LOGGER.debug("No TTS provider found, creating default")
    return HiggsAudioTTSProvider(
        hass=hass,
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        base_url=f"http://{DEFAULT_HOST}:{DEFAULT_PORT}",
        config_entry=None,
    )
