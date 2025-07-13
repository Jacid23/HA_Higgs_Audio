"""The HA Chatterbox TTS integration (Provider version)."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, DEFAULT_HOST, DEFAULT_PORT

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the HA Chatterbox TTS component (Provider)."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HA Chatterbox TTS config entry (Provider)."""
    host = entry.data.get(CONF_HOST, DEFAULT_HOST)
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "host": host,
        "port": port,
        "base_url": f"http://{host}:{port}"
    }
    # Test connection to server
    try:
        import requests
        url = f"http://{host}:{port}/health"
        response = await hass.async_add_executor_job(
            requests.get, url, {"timeout": 10}
        )
        if response.status_code != 200:
            _LOGGER.error("HA Chatterbox TTS server not responding at %s", url)
            return False
    except Exception as ex:
        _LOGGER.error("Failed to connect to HA Chatterbox TTS server: %s", ex)
        return False
    _LOGGER.info("HA Chatterbox TTS setup complete")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
