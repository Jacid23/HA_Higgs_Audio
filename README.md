# HA Chatterbox TTS

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/devnen/Chatterbox-TTS-Server.svg)](https://github.com/devnen/Chatterbox-TTS-Server/releases/)
[![License](https://img.shields.io/github/license/devnen/Chatterbox-TTS-Server.svg)](LICENSE)

A modern Home Assistant custom integration that provides Text-to-Speech (TTS) capabilities by connecting to your Chatterbox TTS server. This integration creates TTS entities that seamlessly integrate with Home Assistant's Voice Assistant and automation systems.

**⚠️ Important: This is a client integration only. You must first set up and run a Chatterbox TTS server before installing this integration.**

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────┐
│ Home Assistant  │───▶│ HA Chatterbox TTS    │───▶│ Chatterbox TTS  │
│ Voice Assistant │    │ Integration (Client) │    │ Server          │
│ & Automations   │◀───│ (This Package)       │◀───│ (Separate Setup)│
└─────────────────┘    └──────────────────────┘    └─────────────────┘
```

**You need both components:**
1. **Chatterbox TTS Server** (separate installation) - Processes text and generates audio
2. **HA Chatterbox TTS Integration** (this package) - Connects Home Assistant to your server

## Features

- **28 High-Quality Voices**: Support for multiple voice personalities and styles
- **Voice Assistant Integration**: Full compatibility with Home Assistant's Voice Assistant
- **Modern Architecture**: Uses config flow for easy setup and management
- **Local Processing**: Works with your local Chatterbox TTS server
- **Automation Ready**: Perfect for notifications, announcements, and smart home responses
- **Advanced Voice Controls**: Support for temperature, speed, and other voice parameters

## Installation

**📋 Prerequisites: Ensure your Chatterbox TTS server is running and accessible before installing this integration.**

### HACS Installation (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/devnen/Chatterbox-TTS-Server`
6. Select "Integration" as the category
7. Click "Add"
8. Find "HA Chatterbox TTS" in the integration list and install it
9. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/devnen/Chatterbox-TTS-Server/releases)
2. Extract the contents
3. Copy the `custom_components/ha_chatterbox` folder to your Home Assistant `custom_components` directory
4. Restart Home Assistant

## Prerequisites

**🔧 Required: Chatterbox TTS Server**

This integration requires a separate Chatterbox TTS server to function. You must set up and run the server first.

**Server Setup**: [Chatterbox TTS Server Repository](https://github.com/devnen/Chatterbox-TTS-Server)

Once your server is running and accessible, proceed with installing this integration.

## Configuration

### Adding the Integration

1. Go to **Settings** → **Devices & Services** in Home Assistant
2. Click **"+ Add Integration"**
3. Search for **"HA Chatterbox TTS"**
4. Enter your Chatterbox TTS server details:
   - **Host**: IP address of your Chatterbox server (e.g., `192.168.1.100`)
   - **Port**: Port number (default: `8005`)
5. Click **Submit**

The integration will automatically test the connection and set up the TTS entity.

### Voice Assistant Configuration

Once installed, HA Chatterbox TTS will appear as an option in your Voice Assistant configuration:

1. Go to **Settings** → **Voice assistants**
2. Select your voice assistant
3. In the **Text-to-speech** dropdown, select **"ha_chatterbox"**
4. Choose your preferred voice from the available options

## Available Voices

The integration supports 28 different voices, including:

- **Emily** - Natural female voice
- **Marcus** - Professional male voice
- **Sarah** - Warm female voice
- **David** - Clear male voice
- **Luna** - Soft female voice
- **Oliver** - Friendly male voice
- And many more...

Each voice has unique characteristics suitable for different use cases and preferences.

## Usage

### In Automations

```yaml
service: tts.speak
target:
  entity_id: tts.ha_chatterbox
data:
  message: "Hello! Your automation has been triggered."
  options:
    voice: Emily
    temperature: 0.8
    speed_factor: 1.0
```

### In Scripts

```yaml
announce_status:
  sequence:
    - service: tts.speak
      target:
        entity_id: tts.ha_chatterbox
      data:
        message: "Good morning! All systems are operational."
        media_player_entity_id: media_player.living_room_speaker
        options:
          voice: Marcus
          temperature: 0.7
```

### Voice Assistant Integration

When configured with Voice Assistant, the integration automatically handles TTS requests with your selected voice and settings.

## Advanced Configuration

### Voice Parameters

- **voice**: Select from 28 available voices
- **temperature**: Controls voice variation (0.0-1.0, default: 0.8)
- **speed_factor**: Adjusts speaking speed (0.5-2.0, default: 1.0)
- **exaggeration**: Voice expressiveness (0.0-2.0, default: 1.0)
- **cfg_weight**: Configuration weight (0.0-1.0, default: 0.5)
- **seed**: Random seed for reproducible output (default: 0)

### Example with All Parameters

```yaml
service: tts.speak
target:
  entity_id: tts.ha_chatterbox
data:
  message: "This is a test with custom voice parameters."
  options:
    voice: Luna
    temperature: 0.9
    speed_factor: 1.2
    exaggeration: 1.1
    cfg_weight: 0.6
    seed: 42
```

## Troubleshooting

### Integration Not Loading

1. **Check server first**: Ensure the Chatterbox TTS server is running and accessible
2. **Test server directly**: Use `curl http://YOUR_SERVER_IP:8005/health` to verify server response
3. Verify the host and port configuration in the integration setup
4. Check Home Assistant logs for connection errors
5. Ensure firewall allows communication between Home Assistant and the server
6. **Server location**: Make sure the server IP is accessible from your Home Assistant instance

### Voice Assistant Shows Empty Options

1. Restart Home Assistant after installation
2. Check that the integration loaded successfully in **Settings** → **Devices & Services**
3. Verify the TTS entity is created and available
4. Re-configure your Voice Assistant settings

### Audio Not Playing

1. **Check server status**: Verify the Chatterbox TTS server is generating audio files correctly
2. **Test server directly**: Try generating audio via server API to confirm it's working
3. Ensure your media player supports the audio format (WAV/MP3)
4. Verify network connectivity between all components (HA ↔ Server ↔ Media Player)
5. Test with a simple automation first
6. **Server resources**: Ensure the server has sufficient RAM and isn't overloaded

### Common Log Messages

- `"HA Chatterbox TTS server not responding"`: Server connection issue
- `"Failed to connect to HA Chatterbox TTS server"`: Network or server problem
- `"Voice 'X' not available"`: Invalid voice name in configuration

## Support

- **Server Setup Help**: [Chatterbox TTS Server Documentation](https://github.com/devnen/Chatterbox-TTS-Server)
- **Integration Issues**: [GitHub Issues](https://github.com/devnen/Chatterbox-TTS-Server/issues)
- **Discussions**: [GitHub Discussions](https://github.com/devnen/Chatterbox-TTS-Server/discussions)
- **Documentation**: [Project Wiki](https://github.com/devnen/Chatterbox-TTS-Server/wiki)

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests for any improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### Version 2.0.0
- Complete rewrite using modern Home Assistant architecture
- Added config flow support for easy setup
- Implemented proper TTS entity structure
- Enhanced Voice Assistant integration
- Added 28 voice options
- Improved error handling and logging
- Added advanced voice parameter controls

### Version 1.x
- Initial release with basic TTS functionality
- Legacy configuration method

## Credits

- **Home Assistant Integration** by [@devnen](https://github.com/devnen)
- **Chatterbox TTS Server** - Separate server component required for operation
- Built for the Home Assistant community
