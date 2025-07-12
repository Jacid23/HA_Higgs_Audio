"""The Chatterbox TTS integration."""
import logging
import os

import voluptuous as vol
import requests

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_PORT
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, DEFAULT_HOST, DEFAULT_PORT

_LOGGER = logging.getLogger(__name__)

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
    hass.data[DOMAIN] = {}
    
    if DOMAIN in config:
        conf = config[DOMAIN]
        host = conf.get(CONF_HOST, DEFAULT_HOST)
        port = conf.get(CONF_PORT, DEFAULT_PORT)
        
        # Store configuration for platforms
        hass.data[DOMAIN] = {
            "host": host,
            "port": port,
            "base_url": f"http://{host}:{port}"
        }
    
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Chatterbox TTS from a config entry."""
    host = entry.data.get(CONF_HOST, DEFAULT_HOST)
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)
    
    hass.data.setdefault(DOMAIN, {})
    
    # Store configuration for platforms
    hass.data[DOMAIN][entry.entry_id] = {
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
    
    # Forward the setup to the TTS platform
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "tts")
    )
    
    entry.async_on_unload(entry.add_update_listener(update_listener))
    
    return True

async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "tts")
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok