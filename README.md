# Chatterbox TTS Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub Latest Release](https://img.shields.io/github/v/release/devnen/Chatterbox-TTS-Server)](https://github.com/devnen/Chatterbox-TTS-Server/releases)
[![GitHub All Releases](https://img.shields.io/github/downloads/devnen/Chatterbox-TTS-Server/total)](https://github.com/devnen/Chatterbox-TTS-Server/releases)
[![Buy me a coffee](https://img.shields.io/static/v1.svg?label=Buy%20me%20a%20coffee&message=🥨&color=black&logo=buy%20me%20a%20coffee&logoColor=white&labelColor=6f4e37)](https://www.buymeacoffee.com/devnen)

A Home Assistant integration that connects to a Chatterbox TTS server to provide high-quality, natural-sounding voice synthesis using advanced AI models. This integration acts as a client that communicates with your self-hosted Chatterbox TTS server.

## Features

- 🔌 **Client Integration**: Seamlessly connects Home Assistant to your Chatterbox TTS server
- 🎯 **High-Quality Voices**: Access to 27+ premium AI voices including Emily, Gianna, Thomas, and more
- ⚡ **Fast Communication**: Optimized client-server communication for quick TTS response times
- 🎛️ **Advanced Controls**: Fine-tune voice characteristics with temperature, exaggeration, speed, and more
- 🔧 **Easy Configuration**: Simple setup through Home Assistant's UI
- 🏠 **Local Processing**: Keep your data private with self-hosted TTS generation (requires separate server)
- 📱 **Full Integration**: Works seamlessly with Home Assistant automations, scripts, and services

## Requirements

- Home Assistant 2023.1.0 or later
- A running [Chatterbox TTS Server](https://github.com/devnen/Chatterbox-TTS-Server) (separate installation required)
- Network access between Home Assistant and the TTS server

## Installation

### Method 1: HACS (Recommended)

1. Ensure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance
2. Add this repository to HACS as a custom repository:
   - Go to HACS → Integrations → ⋮ → Custom repositories
   - Add URL: `https://github.com/devnen/Chatterbox-TTS-Server`
   - Category: Integration
3. Install "Chatterbox TTS Integration" from HACS
4. Restart Home Assistant

### Method 2: Manual Installation

1. Download the latest release from the [releases page](https://github.com/devnen/Chatterbox-TTS-Server/releases)
2. Extract the `custom_components/chatterbox_tts` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## Configuration

### Setting up the Chatterbox TTS Server

**Important**: This integration is a client that requires a separate Chatterbox TTS server to be running. Before configuring this integration, you must first install and run the Chatterbox TTS server. See the [main project documentation](https://github.com/devnen/Chatterbox-TTS-Server) for server setup instructions.

### Adding the Integration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for "Chatterbox TTS"
3. Enter your server configuration:
   - **Host**: IP address of your Chatterbox TTS server (default: 172.30.3.9)
   - **Port**: Port number (default: 8005)
   - **Name**: Friendly name for this TTS service
   - **Default Voice**: Your preferred default voice

### Available Voices

The integration supports 27+ voices including:
- **Emily** - Clear, professional female voice
- **Gianna** - Warm, friendly female voice  
- **Thomas** - Authoritative male voice
- **Olivia** - Young, energetic female voice
- **Alexander** - Deep, commanding male voice
- **Cora** - Gentle, nurturing female voice
- And many more...

## Usage

### Basic TTS Service Call

```yaml
service: tts.speak
data:
  entity_id: tts.chatterbox_tts
  message: "Hello, this is a test of Chatterbox TTS"
target:
  entity_id: media_player.living_room_speaker
```

### Advanced Usage with Voice Parameters

```yaml
service: tts.speak
data:
  entity_id: tts.chatterbox_tts
  message: "This message uses advanced voice controls"
  options:
    voice: "Emily"
    temperature: 0.8
    exaggeration: 1.2
    speed_factor: 1.1
    cfg_weight: 0.6
    seed: 42
target:
  entity_id: media_player.kitchen_display
```

### In Automations

```yaml
automation:
  - alias: "Morning Greeting"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: tts.speak
        data:
          entity_id: tts.chatterbox_tts
          message: "Good morning! Today's weather is {{ states('weather.home') }}"
          options:
            voice: "Emily"
            temperature: 0.9
        target:
          entity_id: media_player.bedroom_speaker
```

## Voice Parameters

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| `voice` | String | Emily | Voice model to use |
| `temperature` | 0.0-1.0 | 0.8 | Controls voice variation and naturalness |
| `exaggeration` | 0.0-2.0 | 1.0 | Emphasizes emotional expression |
| `speed_factor` | 0.5-1.5 | 1.0 | Speech speed multiplier |
| `cfg_weight` | 0.0-1.0 | 0.5 | Classifier-free guidance weight |
| `seed` | Integer | 0 | Random seed (0 for random) |

## Input Selectors (Optional)

For easier voice control through the UI, you can add these input selectors to your `configuration.yaml`:

```yaml
input_select:
  chatterbox_voice:
    name: "Chatterbox Voice"
    options:
      - Emily
      - Gianna
      - Thomas
      - Olivia
      - Alexander
      - Cora
      - Gabriel
      # ... add more voices as needed
    initial: Emily
    icon: mdi:account-voice

  chatterbox_speed:
    name: "Speed Factor"
    options:
      - "0.5"
      - "0.75"
      - "1.0"
      - "1.25"
      - "1.5"
    initial: "1.0"
    icon: mdi:speedometer
```

## Troubleshooting

### Common Issues

1. **Integration not appearing in search**
   - Ensure HACS is properly installed
   - Check that the repository was added correctly
   - Restart Home Assistant after installation

2. **Cannot connect to server**
   - Verify the Chatterbox TTS server is running and accessible
   - Check the host and port configuration in the integration
   - Ensure network connectivity between Home Assistant and the TTS server
   - Test server connectivity: `curl http://[SERVER_IP]:[PORT]/health`

3. **TTS not working**
   - Check Home Assistant logs for error messages
   - Verify the server's `/health` endpoint responds: `http://[SERVER_IP]:[PORT]/health`
   - Test the server directly with its web interface (if available)
   - Ensure the server has the required voice models downloaded

### Enabling Debug Logging

Add this to your `configuration.yaml` to enable debug logging:

```yaml
logger:
  default: warning
  logs:
    custom_components.chatterbox_tts: debug
```

## Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/devnen/Chatterbox-TTS-Server/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/devnen/Chatterbox-TTS-Server/discussions)
- 📖 **Documentation**: [Main Project README](https://github.com/devnen/Chatterbox-TTS-Server)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- This is a client integration that connects to the separate Chatterbox TTS server
- Built on top of advanced TTS models and technologies (via the server)
- Inspired by the Home Assistant community's need for high-quality TTS
- Thanks to all contributors and testers

---

**Important**: This is a Home Assistant integration (client) that requires a separate Chatterbox TTS server installation. See the [main project repository](https://github.com/devnen/Chatterbox-TTS-Server) for server installation and setup instructions.
