# HA Chatterbox TTS Client Integration

A Home Assistant custom component that provides Text-to-Speech functionality by connecting to a **Chatterbox TTS server**.

## ⚠️ Requirements

**This integration requires a separate Chatterbox TTS server to be running.** This is a client integration that connects to an external Chatterbox server.

- You must have a Chatterbox TTS server installed and running
- The server must be accessible from your Home Assistant instance
- Default server port is 8005

## Features

- 28 different voice options
- Configurable TTS server connection
- Adjustable voice parameters (temperature, exaggeration)
- Easy configuration through Home Assistant UI

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to "Integrations"
3. Click the "+" button
4. Search for "HA Chatterbox TTS"
5. Click "Install"
6. Restart Home Assistant

### Manual Installation

1. Download the `ha_chatterbox2` folder
2. Copy it to your `custom_components` directory
3. Restart Home Assistant

## Configuration

### Prerequisites

Before configuring this integration, ensure you have:

1. **Chatterbox TTS Server**: Install and run a Chatterbox TTS server
2. **Network Access**: Home Assistant can reach the server (test with `ping` or browser)
3. **Server Port**: Note the port your Chatterbox server is running on (default: 8005)

### Step 1: Add Integration

1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for **"HA Chatterbox TTS Client"**
4. Configure your **existing** Chatterbox server settings:
   - **Host**: IP address where your Chatterbox server is running
   - **Port**: Port number your server uses (default: 8005)
   - **Voice**: Select from voices available on your server

### Step 2: Enable TTS Platform

Add the following to your `configuration.yaml`:

```yaml
tts:
  - platform: ha_chatterbox2
```

Then restart Home Assistant.

## Available Voices

The integration includes 28 high-quality voices:

- Alice, Amy, Andrew, Ava, Ben
- Brian, Clara, David, Emily, Emma
- George, Hannah, Jack, James, Jessica
- John, Kate, Kevin, Liam, Linda
- Mark, Mary, Michael, Paul, Rachel
- Robert, Sarah, Thomas

## Configuration Options

- **Host**: Chatterbox server IP address
- **Port**: Server port (default: 8005)
- **Voice**: Choose from available voices
- **Temperature**: Voice variation (0.0-1.0)
- **Exaggeration**: Voice emphasis (0.0-2.0)

## Usage

Once configured, the TTS service will be available in:

- **Voice Assistants**: Select "HA Chatterbox TTS" as your voice assistant's TTS engine
- **Automations**: Use the `tts.ha_chatterbox2_say` service
- **Scripts**: Call TTS service with custom messages

### Example Automation

```yaml
automation:
  - alias: "Welcome Home"
    trigger:
      platform: state
      entity_id: person.your_name
      to: "home"
    action:
      service: tts.ha_chatterbox2_say
      data:
        entity_id: media_player.living_room
        message: "Welcome home!"
```

## Troubleshooting

### No Chatterbox Server

**Error**: "Connection refused" or "Unable to connect"

**Solution**: 
- Install and start your Chatterbox TTS server first
- Verify the server is running on the configured host/port
- Test connectivity: `curl http://YOUR_SERVER_IP:8005/health` (if available)

### TTS Not Available in Voice Assistant

Make sure you have added the platform to `configuration.yaml`:

```yaml
tts:
  - platform: ha_chatterbox2
```

### Connection Issues

**This integration is a client only** - it requires a separate Chatterbox server:

- **Install Chatterbox Server**: Set up the server software separately
- **Verify Server Status**: Ensure your Chatterbox server is running and accessible
- **Check Network**: Confirm Home Assistant can reach the server IP/port
- **Firewall**: Ensure the server port (default 8005) is not blocked

### Voice Not Working

- Confirm the selected voice is available on your server
- Try a different voice from the dropdown
- Check Home Assistant logs for error messages

## Support

For issues and feature requests, please visit the [GitHub repository](https://github.com/Jacid23/HA_Chatterbox).

## License

This project is licensed under the MIT License.
