# Allen TTS Custom Component Services
# These services are automatically registered when the component loads

"""Services provided by the Allen TTS custom component."""
import logging
import requests
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv
from homeassistant.const import ATTR_ENTITY_ID

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

SERVICE_SPEAK = "speak"
SERVICE_INTERRUPT = "interrupt"
SERVICE_SET_MOOD = "set_mood"

ATTR_MESSAGE = "message"
ATTR_MOOD = "mood"
ATTR_VOICE = "voice"
ATTR_ENGINE = "engine"

SPEAK_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_MESSAGE): cv.string,
        vol.Optional(ATTR_MOOD, default="Sarcastic"): cv.string,
        vol.Optional(ATTR_VOICE, default="allen_male"): cv.string,
        vol.Optional(ATTR_ENGINE, default="google"): cv.string,
    }
)

MOOD_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_MOOD): cv.string,
    }
)

def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Allen TTS."""

    async def handle_speak(call: ServiceCall) -> None:
        """Handle the speak service call."""
        message = call.data.get(ATTR_MESSAGE)
        mood = call.data.get(ATTR_MOOD, "Sarcastic")
        voice = call.data.get(ATTR_VOICE, "allen_male")
        engine = call.data.get(ATTR_ENGINE, "google")
        
        config = hass.data[DOMAIN]
        base_url = config["base_url"]
        
        data = {
            "text": message,
            "mood": mood,
            "voice": voice,
            "engine": engine
        }
        
        try:
            url = f"{base_url}/speak"
            response = await hass.async_add_executor_job(
                requests.post,
                url,
                {"json": data, "headers": {"Content-Type": "application/json"}, "timeout": 30}
            )
            
            if response.status_code == 200:
                _LOGGER.info("Allen TTS spoke: %s (mood: %s)", message, mood)
            else:
                _LOGGER.error("Allen TTS speak failed: %s", response.status_code)
                
        except Exception as ex:
            _LOGGER.error("Error calling Allen TTS speak service: %s", ex)

    async def handle_interrupt(call: ServiceCall) -> None:
        """Handle the interrupt service call."""
        config = hass.data[DOMAIN]
        base_url = config["base_url"]
        
        try:
            url = f"{base_url}/speak/interrupt"
            response = await hass.async_add_executor_job(
                requests.post,
                url,
                {"timeout": 10}
            )
            
            if response.status_code == 200:
                _LOGGER.info("Allen TTS interrupted")
            else:
                _LOGGER.error("Allen TTS interrupt failed: %s", response.status_code)
                
        except Exception as ex:
            _LOGGER.error("Error calling Allen TTS interrupt service: %s", ex)

    async def handle_set_mood(call: ServiceCall) -> None:
        """Handle the set mood service call."""
        mood = call.data.get(ATTR_MOOD)
        
        # Update input_select if it exists
        input_select_entity = "input_select.allen_mood"
        if hass.states.get(input_select_entity):
            await hass.services.async_call(
                "input_select",
                "select_option",
                {ATTR_ENTITY_ID: input_select_entity, "option": mood}
            )
        
        _LOGGER.info("Allen TTS mood set to: %s", mood)

    # Register services
    hass.services.async_register(
        DOMAIN, SERVICE_SPEAK, handle_speak, schema=SPEAK_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, SERVICE_INTERRUPT, handle_interrupt
    )
    
    hass.services.async_register(
        DOMAIN, SERVICE_SET_MOOD, handle_set_mood, schema=MOOD_SCHEMA
    )
