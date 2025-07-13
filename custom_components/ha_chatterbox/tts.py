"""
HA Chatterbox TTS Platform for Home Assistant    # Create the TTS entity
    entity = HAChatterboxTTSEntity(
        hass=hass,
        entry=entry,
        host=data["host"],
        port=data["port"],
        base_url=data["base_url"]
    )
    
    async_add_entities([entity], True)
    _LOGGER.debug("Added HA Chatterbox TTS entity: %s", entity.unique_id)s Text-to-Speech services using Chatterbox TTS server.
"""
import logging
import requests
import json
import os
import functools

from homeassistant.components.tts import TextToSpeechEntity, TtsAudioType
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.entity_platform import AddEntitiesCallback

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
    CONF_SPEED_FACTOR
)

_LOGGER = logging.getLogger(__name__)

# Configuration constants
CONF_LANGUAGE = "language"
CONF_OPTIONS = "options"

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up HA Chatterbox TTS from a config entry."""
    _LOGGER.debug("Setting up HA Chatterbox TTS entity from config entry")
    
    # Get the stored configuration from the integration
    data = hass.data[DOMAIN][entry.entry_id]
    
    # Create the TTS entity
    entity = HAChatterboxTTSEntity(
        hass=hass,
        entry=entry,
        host=data["host"],
        port=data["port"],
        base_url=data["base_url"]
    )
    
    async_add_entities([entity], True)
    _LOGGER.debug("Added HA Chatterbox TTS entity: %s", entity.unique_id)

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
                    _LOGGER.debug("Loaded %d voices from strings.json: %s", len(voice_list), voice_list)
                    return voice_list
    except Exception as ex:
        _LOGGER.warning("Could not load voices from strings.json: %s", ex)
    
    return None

class HAChatterboxTTSEntity(TextToSpeechEntity):
    """HA Chatterbox TTS Entity."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, host: str, port: int, base_url: str):
        """Initialize HA Chatterbox TTS entity."""
        self.hass = hass
        self._entry = entry
        self._host = host
        self._port = port
        self._base_url = base_url
        
        # Get configuration from entry data
        self._language = entry.data.get(CONF_LANGUAGE, "en-US")
        self._voice = entry.data.get(CONF_VOICE, DEFAULT_VOICE)
        self._temperature = entry.data.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE)
        self._exaggeration = entry.data.get(CONF_EXAGGERATION, DEFAULT_EXAGGERATION)
        self._cfg_weight = entry.data.get(CONF_CFG_WEIGHT, DEFAULT_CFG_WEIGHT)
        self._seed = entry.data.get(CONF_SEED, DEFAULT_SEED)
        self._speed_factor = entry.data.get(CONF_SPEED_FACTOR, DEFAULT_SPEED_FACTOR)
        
        _LOGGER.debug("HA Chatterbox TTS entity initialized, base_url: %s", self._base_url)

    @property
    def unique_id(self) -> str:
        """Return unique ID for the entity."""
        return f"ha_chatterbox_tts_{self._host}_{self._port}"

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return "HA Chatterbox"

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return True

    @property
    def default_language(self) -> str:
        """Return the default language."""
        return "en-US"

    @property
    def supported_languages(self) -> list[str]:
        """Return list of supported languages."""
        return ["en-US"]

    @property
    def supported_options(self) -> list[str]:
        """Return list of supported options."""
        return [CONF_VOICE, CONF_TEMPERATURE, CONF_EXAGGERATION, CONF_CFG_WEIGHT, CONF_SEED, CONF_SPEED_FACTOR]

    @property
    def default_options(self) -> dict[str, str | int | float]:
        """Return default options."""
        voices = _load_voices_from_strings()
        if voices:
            default_voice = voices[0]
        else:
            default_voice = DEFAULT_VOICE
            
        defaults = {
            CONF_VOICE: default_voice,
            CONF_TEMPERATURE: self._temperature,
            CONF_EXAGGERATION: self._exaggeration,
            CONF_CFG_WEIGHT: self._cfg_weight,
            CONF_SEED: self._seed,
            CONF_SPEED_FACTOR: self._speed_factor
        }
        _LOGGER.debug("Entity default_options: %s", defaults)
        return defaults

    @property
    def default_voice(self) -> str:
        """Return the default voice."""
        voices = _load_voices_from_strings()
        if voices:
            return voices[0]
        return DEFAULT_VOICE

    @property
    def supported_voices(self) -> dict[str, list[str]]:
        """Return list of supported voices in the expected format."""
        # Load voices from strings.json file
        voices = _load_voices_from_strings()
        if voices:
            result = {"en-US": voices}
            _LOGGER.debug("HA Chatterbox supported_voices: %s", result)
            return result
        
        _LOGGER.warning("No voices found in strings.json")
        return {"en-US": []}
    
    def _get_voice_filename(self, voice_name: str) -> str | None:
        """Convert voice display name to filename."""
        if not voice_name:
            return None
        
        # For strings.json voices, add .wav extension if not present
        if not voice_name.endswith('.wav'):
            return f"{voice_name}.wav"
        return voice_name

    async def async_get_tts_audio(self, message: str, language: str, options: dict | None = None) -> TtsAudioType:
        """Load TTS from HA Chatterbox TTS server."""
        _LOGGER.debug("async_get_tts_audio called with message: %s, language: %s, options: %s", message, language, options)
        
        if options is None:
            options = {}
        
        # Get voice and parameters
        selected_voice = options.get(CONF_VOICE, self._voice)
        temperature = options.get(CONF_TEMPERATURE, self._temperature)
        exaggeration = options.get(CONF_EXAGGERATION, self._exaggeration)
        cfg_weight = options.get(CONF_CFG_WEIGHT, self._cfg_weight)
        seed = options.get(CONF_SEED, self._seed)
        speed_factor = options.get(CONF_SPEED_FACTOR, self._speed_factor)
        
        # Convert voice display name to filename
        voice_filename = self._get_voice_filename(selected_voice)
        
        _LOGGER.debug("TTS request - Voice: %s (filename: %s), Temp: %s, Speed: %s", 
                     selected_voice, voice_filename, temperature, speed_factor)
        
        # Prepare request data
        data = {
            "text": message,
            "predefined_voice_id": voice_filename,
            "temperature": temperature,
            "exaggeration": exaggeration,
            "cfg_weight": cfg_weight,
            "seed": seed,
            "speed_factor": speed_factor,
            "output_format": "wav"
        }
        
        _LOGGER.debug("Sending request to %s with data: %s", f"{self._base_url}/tts", data)
        
        try:
            # Send request to HA Chatterbox TTS server
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
                _LOGGER.debug("HA Chatterbox TTS request successful")
                return "wav", response.content
            else:
                _LOGGER.error("HA Chatterbox TTS request failed: %s", response.status_code)
                return "wav", b""
                
        except Exception as ex:
            _LOGGER.error("Error connecting to HA Chatterbox TTS: %s", ex)
            return "wav", b""
