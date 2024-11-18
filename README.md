# Sonos Chime Server

A Flask-based server that allows you to play custom chime sounds on Sonos speakers using the Sonos Audio Clips API.

## Features

- Play custom MP3 chimes on any Sonos speaker
- Adjustable volume control
- Priority levels support (HIGH/LOW)
- Simple REST API interface
- Built-in chime file management

## Prerequisites

- Python 3.6+
- Flask
- requests
- A Sonos speaker with Audio Clips API support

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sonos-chime-server.git
cd sonos-chime-server
```

2. Install dependencies:
```bash
pip install flask requests
```

3. Set the host url where the server will be reachable:
```bash
export HOST="http://your-server-address:8080"
```

## Usage

### Starting the Server for testing

```bash
python app.py
```

The server will start on port 8080 by default.

### Starting Server using container image

```bash
docker run -d --name sonos-chime -p 8080:8080 -e "HOST=http://localhost:8080" ghcr.io/vchrisb/sonos_chime:0.1.0
```

### Retrieve Sonos Player ID

```bash
curl -v --insecure \
        -H 'X-Sonos-Api-Key:123e4567-e89b-12d3-a456-426655440000' \
        https://192.168.1.100:1443/api/v1/players/local/info
```

### API Endpoints

#### Play a Chime

```
GET /api/play_chime
```

Query Parameters:
- `playerIP` (required): IP address of the Sonos speaker
- `playerID` (required): ID of the Sonos player
- `chime` (optional): Name of the chime file without .mp3 extension (default: "doorbell1")
- `volume` (optional): Volume level 0-100 (default: 30)
- `priority` (optional): Priority level "HIGH" or "LOW" (default: "LOW")

Example:
```bash
curl "http://localhost:8080/api/play_chime?playerIP=192.168.1.100&playerID=RINCON_123456&chime=doorbell1&volume=50&priority=HIGH"
```

#### List Available Chimes

```
GET /api/list_chimes
```

Returns a list of available chime files.

Example:
```bash
curl "http://localhost:8080/api/list_chimes"
```

### Adding Custom Chimes

1. Convert your audio file to MP3 format
2. Place the MP3 file in the `chimes` directory
3. The filename (without .mp3 extension) will be used as the chime name in the API

## Configuration

The server uses the following configuration:

- `HOST`: Environment variable for the server's public URL (required)
- Default port: 8080
- Default chime directory: `./chimes`
