"""Constants for the Higgs Audio TTS integration."""

DOMAIN = "ha_higgs_audio"

# Default connection settings
DEFAULT_HOST = "172.30.3.9"
DEFAULT_PORT = 8005

# Default voice and TTS settings
DEFAULT_VOICE = "Emily.wav"
DEFAULT_TEMPERATURE = 0.8
DEFAULT_EXAGGERATION = 1.0
DEFAULT_CFG_WEIGHT = 0.5
DEFAULT_SEED = 101
DEFAULT_SPEED_FACTOR = 1.0

# Configuration keys
CONF_VOICE = "voice"
CONF_TEMPERATURE = "temperature"
CONF_EXAGGERATION = "exaggeration"
CONF_CFG_WEIGHT = "cfg_weight"
CONF_SEED = "seed"
CONF_SPEED_FACTOR = "speed_factor"

# Available voices (fallback if strings.json not available)
AVAILABLE_VOICES = [
    "Abigail.wav", "Adrian.wav", "Alexander.wav", "Alice.wav", "Austin.wav",
    "Axel.wav", "Connor.wav", "Cora.wav", "Elena.wav", "Eli.wav",
    "Emily.wav", "Everett.wav", "Gabriel.wav", "Gianna.wav", "Henry.wav",
    "Ian.wav", "Jade.wav", "Jeremiah.wav", "Jordan.wav", "Julian.wav",
    "Layla.wav", "Leonardo.wav", "Michael.wav", "Miles.wav", "Olivia.wav",
    "Ryan.wav", "Taylor.wav", "Thomas.wav"
]
