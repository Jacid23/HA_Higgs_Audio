"""
Chatterbox TTS Platform for Home Assistant

Provides Text-to-Speech services using Chatterbox TTS server.
"""
import logging
import requests
import voluptuous as vol
import json
import os

from homeassistant.components.tts import PLATFORM_SCHEMA, Provider
from homeassistant.const import CONF_HOST, CONF_PORT
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEFAULT_HOST = "172.30.3.9"
DEFAULT_PORT = 8005
DEFAULT_VOICE = "Emily" 
DEFAULT_TEMPERATURE = 0.8
DEFAULT_EXAGGERATION = 1.0
DEFAULT_CFG_WEIGHT = 0.5
DEFAULT_SEED = 0
DEFAULT_SPEED_FACTOR = 1.0

# Add these constants first
CONF_LANGUAGE = "language"
CONF_VOICE = "voice"
CONF_TEMPERATURE = "temperature"
CONF_EXAGGERATION = "exaggeration"
CONF_CFG_WEIGHT = "cfg_weight"
CONF_SEED = "seed"
CONF_SPEED_FACTOR = "speed_factor"
CONF_OPTIONS = "options"

# Then update the schema to include all parameters
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_LANGUAGE, default="en-US"): cv.string,  # Add language
        vol.Optional(CONF_VOICE, default=DEFAULT_VOICE): cv.string,
        vol.Optional(CONF_TEMPERATURE, default=DEFAULT_TEMPERATURE): vol.Coerce(float),
        vol.Optional(CONF_EXAGGERATION, default=DEFAULT_EXAGGERATION): vol.Coerce(float),
        vol.Optional(CONF_CFG_WEIGHT, default=DEFAULT_CFG_WEIGHT): vol.Coerce(float),  # Add cfg_weight
        vol.Optional(CONF_SEED, default=DEFAULT_SEED): vol.Coerce(int),  # Add seed
        vol.Optional(CONF_SPEED_FACTOR, default=DEFAULT_SPEED_FACTOR): vol.Coerce(float),  # Add speed_factor
        vol.Optional(CONF_OPTIONS): dict,  # Add this line for options
    }
)


def get_engine(hass, config, discovery_info=None):
    """Set up Chatterbox TTS speech component."""
    return ChatterboxTTSProvider(hass, config)

async def async_get_engine(hass, config, discovery_info=None):
    """Set up Chatterbox TTS engine."""
    _LOGGER.debug("Setting up Chatterbox TTS engine asynchronously")
    return ChatterboxTTSProvider(hass, config)

def _load_voices_from_strings():
    """Load voice options from strings.json file."""
    try:
        # Get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        strings_path = os.path.join(current_dir, "strings.json")
        
        if os.path.exists(strings_path):
            with open(strings_path, 'r', encoding='utf-8') as f:
                strings_data = json.load(f)
                # Extract voice options from strings.json
                voice_options = strings_data.get("options", {}).get("step", {}).get("init", {}).get("data", {}).get("voice", {}).get("options", [])
                if voice_options:
                    _LOGGER.debug("Loaded %d voices from strings.json: %s", len(voice_options), voice_options)
                    return voice_options
    except Exception as ex:
        _LOGGER.warning("Could not load voices from strings.json: %s", ex)
    
    return None

class ChatterboxTTSProvider(Provider):
    """Chatterbox TTS speech api provider."""

    def __init__(self, hass, conf):
        """Initialize Chatterbox TTS provider."""
        self.hass = hass
        self._host = conf.get(CONF_HOST)
        self._port = conf.get(CONF_PORT)
        self._language = conf.get(CONF_LANGUAGE, "en-US")
        self._voice = conf.get(CONF_VOICE)
        self._options = conf.get(CONF_OPTIONS, {})  # Store options
        self._temperature = conf.get(CONF_TEMPERATURE)
        self._exaggeration = conf.get(CONF_EXAGGERATION)
        self._cfg_weight = conf.get(CONF_CFG_WEIGHT)
        self._seed = conf.get(CONF_SEED)
        self._speed_factor = conf.get(CONF_SPEED_FACTOR)
        
        # Base URL for API calls
        self._base_url = f"http://{self._host}:{self._port}"
        
        # Voice cache
        self._voice_cache = None
        self._voice_cache_time = 0
        
        # Create a simple name for the TTS platform
        self.name = "Chatterbox TTS"
        
        _LOGGER.debug("Chatterbox TTS provider initialized, base_url: %s, name: %s", self._base_url, self.name)

    @property
    def default_language(self):
        """Return the default language."""
        return "en-US"  # CHANGE THIS FROM "en" TO "en-US"

    @property
    def supported_languages(self):
        """Return list of supported languages."""
        return ["en-US"]  # CHANGE THIS FROM ["en"] TO ["en-US"]

    @property
    def supported_options(self):
        """Return list of supported options."""
        return [CONF_VOICE, CONF_TEMPERATURE, CONF_EXAGGERATION, CONF_CFG_WEIGHT, CONF_SEED, CONF_SPEED_FACTOR]

    @property
    def default_voice(self):
        """Return the default voice."""
        return self._voice

    @property
    def supported_voices(self):
        """Return list of supported voices in the expected format."""
        # First try to load from strings.json
        strings_voices = _load_voices_from_strings()
        if strings_voices:
            # CRUCIAL: Return voices in dictionary format with language as key
            result = {"en-US": strings_voices}
            _LOGGER.debug("Chatterbox TTS supported_voices returning: %s", result)
            return result
        
        # Fallback to server discovery
        voices = self._get_voices_from_server()
        result = {"en-US": voices}
        _LOGGER.debug("Chatterbox TTS supported_voices returning: %s", result)
        return result
    
    def _get_voices_from_server(self):
        """Get voices from server with caching."""
        import time
        
        _LOGGER.debug("Chatterbox TTS _get_voices_from_server called")
        
        # Cache for 5 minutes
        current_time = time.time()
        if self._voice_cache and (current_time - self._voice_cache_time) < 300:
            cached_voices = [voice["display_name"] for voice in self._voice_cache]
            _LOGGER.debug("Returning cached voices: %s", cached_voices)
            return cached_voices
        
        try:
            # Fetch available voices from the Chatterbox TTS server
            url = f"{self._base_url}/get_predefined_voices"
            _LOGGER.debug("Fetching voices from: %s", url)
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                self._voice_cache = response.json()
                self._voice_cache_time = current_time
                # Return list of voice names (display_name from the API)
                voices = [voice["display_name"] for voice in self._voice_cache]
                _LOGGER.debug("Successfully fetched %d voices from server: %s", len(voices), voices)
                return voices
            else:
                _LOGGER.warning("Failed to fetch voices, status code: %s", response.status_code)
        except Exception as ex:
            _LOGGER.error("Error fetching voices from Chatterbox TTS: %s", ex)
        
        # Fallback to a basic list if the API call fails (using actual available voices)
        fallback_voices = ["Abigail", "Adrian", "Alexander", "Alice", "Austin", "Axel", "Connor", 
                "Cora", "Elena", "Eli", "Emily", "Everett", "Gabriel", "Gianna", "Henry",
                "Ian", "Jade", "Jeremiah", "Jordan", "Julian", "Layla", "Leonardo", 
                "Michael", "Miles", "Olivia", "Ryan", "Taylor", "Thomas"]
        _LOGGER.debug("Using fallback voices: %s", fallback_voices)
        return fallback_voices

    def _get_voice_filename(self, voice_name):
        """Convert voice display name to filename."""
        # Use cached voice data if available
        if self._voice_cache:
            for voice in self._voice_cache:
                if voice["display_name"] == voice_name:
                    return voice["filename"]
        
        # If not in cache, try to fetch
        try:
            url = f"{self._base_url}/get_predefined_voices"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                voices_data = response.json()
                # Find the filename for the given display name
                for voice in voices_data:
                    if voice["display_name"] == voice_name:
                        return voice["filename"]
        except Exception as ex:
            _LOGGER.error("Error fetching voice filename from Chatterbox TTS: %s", ex)
        
        # Fallback: assume the voice name is already a filename or add appropriate extension
        if voice_name.endswith(('.wav', '.mp3')):
            return voice_name
        # Default to .wav extension for fallback
        return f"{voice_name}.wav"

    def get_tts_audio(self, message, language, options=None):
        """Load TTS from Chatterbox TTS server."""
        if options is None:
            options = {}
            
        # Priority 1: voice in options
        # Priority 2: read from input_select.chatterbox_voice
        # Priority 3: configured default voice
        selected_voice = options.get(CONF_VOICE)
        if not selected_voice and self.hass.states.get('input_select.chatterbox_voice'):
            selected_voice = self.hass.states.get('input_select.chatterbox_voice').state
        if not selected_voice:
            selected_voice = self._voice
                
        # Get parameters from options or input_select entities
        temperature = options.get(CONF_TEMPERATURE)
        if not temperature and self.hass.states.get('input_select.chatterbox_temperature'):
            temperature = float(self.hass.states.get('input_select.chatterbox_temperature').state)
        if not temperature:
            temperature = self._temperature
            
        exaggeration = options.get(CONF_EXAGGERATION)
        if not exaggeration and self.hass.states.get('input_select.chatterbox_exaggeration'):
            exaggeration = float(self.hass.states.get('input_select.chatterbox_exaggeration').state)
        if not exaggeration:
            exaggeration = self._exaggeration
            
        cfg_weight = options.get(CONF_CFG_WEIGHT)
        if not cfg_weight and self.hass.states.get('input_select.chatterbox_cfg'):
            cfg_weight = float(self.hass.states.get('input_select.chatterbox_cfg').state)
        if not cfg_weight:
            cfg_weight = self._cfg_weight
            
        seed = options.get(CONF_SEED, self._seed)
        
        speed_factor = options.get(CONF_SPEED_FACTOR)
        if not speed_factor and self.hass.states.get('input_select.chatterbox_speed'):
            speed_factor = float(self.hass.states.get('input_select.chatterbox_speed').state)
        if not speed_factor:
            speed_factor = self._speed_factor
        
        # Convert voice display name to filename if needed
        voice_filename = self._get_voice_filename(selected_voice)
        
        _LOGGER.debug("Using voice: %s (filename: %s)", selected_voice, voice_filename)
        
        # Prepare request data with ALL supported parameters
        data = {
            "text": message,
            "predefined_voice_id": voice_filename,
            "temperature": temperature,
            "exaggeration": exaggeration,
            "cfg_weight": cfg_weight,
            "seed": seed,
            "speed_factor": speed_factor,
            "output_format": "mp3"
        }
    
    # Rest of the method remains the same...
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
                # Return the audio data from the response in MP3 format
                return "mp3", response.content
            else:
                _LOGGER.error("Chatterbox TTS request failed: %s", response.status_code)
                return None, None
                
        except requests.exceptions.RequestException as ex:
            _LOGGER.error("Error connecting to Chatterbox TTS: %s", ex)
            return None, None
