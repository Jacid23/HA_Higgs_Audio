"""
Chatterbox TTS Integration for Home Assistant

This integration provides TTS services using the Chatterbox TTS server
running on the local network (IoT VLAN: 172.30.3.9).
"""
import logging
import requests
import voluptuous as vol
from datetime import timedelta

from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
import homeassistant.helpers.config_validation as cv
from homeassistant.exceptions import ConfigEntryNotReady

_LOGGER = logging.getLogger(__name__)

DOMAIN = "chatterbox_tts"
DEFAULT_HOST = "172.30.3.9"
DEFAULT_PORT = 8005

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Chatterbox TTS component."""
    conf = config.get(DOMAIN, {})
    host = conf.get(CONF_HOST, DEFAULT_HOST)
    port = conf.get(CONF_PORT, DEFAULT_PORT)
    
    # Store configuration
    hass.data[DOMAIN] = {
        "host": host,
        "port": port,
        "base_url": f"http://{host}:{port}"
    }
    
    # Test connection to Chatterbox TTS server
    try:
        url = f"http://{host}:{port}/health"
        response = await hass.async_add_executor_job(
            requests.get, url, {"timeout": 10}
        )
        if response.status_code != 200:
            _LOGGER.error("Chatterbox TTS server not responding at %s", url)
            return False
        _LOGGER.info("Chatterbox TTS server found at %s", url)
    except Exception as ex:
        _LOGGER.error("Cannot connect to Chatterbox TTS server: %s", ex)
        return False

    # Store config for platforms to access
    hass.data[DOMAIN] = config[DOMAIN]
    
    return True
