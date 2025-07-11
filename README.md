# Allen TTS Home Assistant Integration

A custom component that integrates Allen TTS (A'Lynzz'Quorvaxth the Third) with Home Assistant, providing text-to-speech services with multiple personality moods.

## Features

- **Multiple Moods**: Sarcastic, Happy, Dramatic, Annoyed, Chill, Excited, Tired, Confused
- **Voice Assistant Integration**: Appears in HA Voice Assistant TTS dropdown
- **Custom Character**: A'Lynzz'Quorvaxth the Third - your reluctant intergalactic digital assistant
- **Multiple TTS Engines**: Google, Piper, System support
- **Real-time Status**: Health monitoring and queue status sensors

## Installation

### Manual Installation

1. Download or clone this repository
2. Copy the `custom_components/allen_tts` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant
4. Add the configuration to your `configuration.yaml`

### HACS Installation (Coming Soon)

This integration will be available through HACS in the future.

## Configuration

Add the following to your `configuration.yaml`:

```yaml
tts:
  - platform: allen_tts
    host: "172.30.3.9"  # IP address of your Allen TTS server
    port: 8000           # Port of your Allen TTS server (default: 8000)
    mood: "Sarcastic"    # Default mood (optional)
    voice: "allen_male"  # Voice to use (optional)
    engine: "google"     # TTS engine (optional)
```

## Configuration Options

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `host` | string | Yes | `172.30.3.9` | IP address of Allen TTS server |
| `port` | integer | No | `8000` | Port of Allen TTS server |
| `mood` | string | No | `Sarcastic` | Default mood for speech |
| `voice` | string | No | `allen_male` | Voice identifier |
| `engine` | string | No | `google` | TTS engine to use |

## Available Moods

- **Sarcastic** (default): Allen's signature dry wit and sarcasm
- **Happy**: Cheerful and upbeat delivery
- **Dramatic**: Over-the-top theatrical performance
- **Annoyed**: Irritated and slightly aggressive tone
- **Chill**: Relaxed and laid-back delivery
- **Excited**: High energy and enthusiastic
- **Tired**: Sleepy and monotone delivery
- **Confused**: Uncertain and questioning tone

## Usage

### Voice Assistant Integration

Once installed, Allen TTS will appear in the Voice Assistant configuration dropdown alongside other TTS engines like Google Translate and Piper TTS.

### Service Calls

Use the standard Home Assistant TTS service:

```yaml
service: tts.speak
data:
  entity_id: tts.allen_tts
  message: "Hello, this is Allen speaking with sarcastic wit."
```

### Scripts and Automations

```yaml
# Example automation
- alias: "Allen Welcome Home"
  trigger:
    - platform: state
      entity_id: device_tracker.phone
      to: 'home'
  action:
    - service: tts.speak
      data:
        entity_id: tts.allen_tts
        message: "Oh wonderful, another human has returned to disturb my digital solitude."
```

## Sensors

The integration provides status sensors:

- `sensor.allen_tts_status`: Server health and version information
- `sensor.allen_tts_queue`: Queue status and current playback information

## Requirements

- Home Assistant 2023.1.0 or newer
- Allen TTS Server running and accessible on your network
- Python `requests` library (automatically installed)

## Allen TTS Server

This integration requires a running Allen TTS server. The server provides the actual text-to-speech functionality with Allen's personality and multiple mood support.

### Server Features

- RESTful API for TTS requests
- Multiple personality moods
- Queue management
- Health monitoring endpoints
- Character-based responses

## Troubleshooting

### Common Issues

1. **Integration not loading**: 
   - Ensure the `custom_components/allen_tts` folder is in the correct location
   - Check that all files are present and have correct permissions
   - Restart Home Assistant completely

2. **Server connection errors**:
   - Verify the Allen TTS server is running
   - Check the IP address and port in configuration
   - Ensure network connectivity between HA and server

3. **TTS not appearing in dropdown**:
   - Confirm the integration loaded without errors
   - Check Home Assistant logs for error messages
   - Verify configuration syntax is correct

### Debug Logging

Add to your `configuration.yaml` for detailed logging:

```yaml
logger:
  default: info
  logs:
    custom_components.allen_tts: debug
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

- **Character**: A'Lynzz'Quorvaxth the Third - The reluctant intergalactic digital assistant
- **Personality**: Sarcastic, witty, and occasionally helpful AI character
- **Integration**: Custom Home Assistant component for seamless TTS integration

## Changelog

### Version 1.0.0
- Initial release
- Basic TTS functionality with mood support
- Voice Assistant integration
- Health and queue status sensors
- Multiple TTS engine support
