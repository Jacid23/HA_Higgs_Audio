"""
Chatterbox TTS Platform for Home Assistant

Provides Text-to-Speech services using Chatterbox TTS server.
"""
import logging
import requests
import voluptuous as vol

from homeassistant.components.tts import PLATFORM_SCHEMA, Provider
from homeassistant.const import CONF_HOST, CONF_PORT
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEFAULT_HOST = "172.30.3.9"
DEFAULT_PORT = 8005
DEFAULT_EMOTION = "Sarcastic"
DEFAULT_VOICE = "Emily" 
DEFAULT_TEMPERATURE = 0.8
DEFAULT_EXAGGERATION = 1.3

CONF_EMOTION = "emotion"
CONF_VOICE = "voice"
CONF_TEMPERATURE = "temperature"
CONF_EXAGGERATION = "exaggeration"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_EMOTION, default=DEFAULT_EMOTION): cv.string,
        vol.Optional(CONF_VOICE, default=DEFAULT_VOICE): cv.string,
        vol.Optional(CONF_TEMPERATURE, default=DEFAULT_TEMPERATURE): vol.Coerce(float),
        vol.Optional(CONF_EXAGGERATION, default=DEFAULT_EXAGGERATION): vol.Coerce(float),
    }
)

def get_engine(hass, config, discovery_info=None):
    """Set up Chatterbox TTS speech component."""
    return ChatterboxTTSProvider(hass, config)

class ChatterboxTTSProvider(Provider):
    """Chatterbox TTS speech api provider."""

    def __init__(self, hass, conf):
        """Initialize Chatterbox TTS provider."""
        self.hass = hass
        self._host = conf.get(CONF_HOST, DEFAULT_HOST)
        self._port = conf.get(CONF_PORT, DEFAULT_PORT)
        self._emotion = conf.get(CONF_EMOTION, DEFAULT_EMOTION)
        self._voice = conf.get(CONF_VOICE, DEFAULT_VOICE)
        self._temperature = conf.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE)
        self._exaggeration = conf.get(CONF_EXAGGERATION, DEFAULT_EXAGGERATION)
        self._base_url = f"http://{self._host}:{self._port}"
        
        self.name = "Chatterbox TTS"

    @property
    def default_language(self):
        """Return the default language."""
        return "en"

    @property
    def supported_languages(self):
        """Return list of supported languages."""
        return ["en"]

    @property
    def supported_options(self):
        """Return list of supported options."""
        return [CONF_EMOTION, CONF_VOICE, CONF_TEMPERATURE, CONF_EXAGGERATION]

    def get_tts_audio(self, message, language, options=None):
        """Load TTS from Chatterbox TTS server."""
        if options is None:
            options = {}
            
        emotion = options.get(CONF_EMOTION, self._emotion)
        voice = options.get(CONF_VOICE, self._voice)
        temperature = options.get(CONF_TEMPERATURE, self._temperature)
        exaggeration = options.get(CONF_EXAGGERATION, self._exaggeration)
        
        # Prepare request data
        data = {
            "text": message,
            "voice": voice,
            "temperature": temperature,
            "exaggeration": exaggeration,
            "speed_factor": 1.0
        }
        
        try:
            # Send request to Chatterbox TTS server
            url = f"{self._base_url}/tts"
            response = requests.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                _LOGGER.debug("Chatterbox TTS request successful")
                # Return the audio data from the response
                return "wav", response.content
            else:
                _LOGGER.error("Chatterbox TTS request failed: %s", response.status_code)
                return None, None
                
        except requests.exceptions.RequestException as ex:
            _LOGGER.error("Error connecting to Chatterbox TTS: %s", ex)
            return None, None
