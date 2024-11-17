import os
from enum import Enum
from functools import wraps
from urllib.parse import quote, urljoin

import requests
from flask import Flask, jsonify, request, send_from_directory


# Create the Flask application
def create_app():
    app = Flask(__name__)

    # Get host from environment variable
    host = os.environ.get("HOST")
    if not host:
        raise ValueError("HOST environment variable must be set")
    if not (host.startswith("http://") or host.startswith("https://")):
        raise ValueError("HOST must include scheme (http:// or https://)")

    # Constants
    sonos_api_key = "622493a2-4877-496c-9bba-abcb502908a5"
    chimes_directory = "chimes"  # Subdirectory for MP3 files

    # Ensure the chimes directory exists
    os.makedirs(chimes_directory, exist_ok=True)

    class Priority(Enum):
        HIGH = "HIGH"
        LOW = "LOW"

    def validate_parameters(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            required_params = ["playerIP", "playerID"]

            # Check if all required parameters are present
            missing_params = [param for param in required_params if param not in request.args]
            if missing_params:
                return jsonify({"error": f'Missing required parameters: {", ".join(missing_params)}'}), 400

            # Validate volume range
            try:
                volume = int(request.args.get("volume"))
                if not 0 <= volume <= 100:
                    return jsonify({"error": "Volume must be between 0 and 100"}), 400
            except ValueError:
                return jsonify({"error": "Volume must be a valid integer"}), 400

            # Validate priority if provided
            priority = request.args.get("priority", "LOW")
            try:
                Priority(priority)
            except ValueError:
                return jsonify({"error": "Priority must be either HIGH or LOW"}), 400

            # Check if chime file exists
            chime = request.args.get("chime")
            if not os.path.exists(os.path.join(chimes_directory, f"{chime}.mp3")):
                return jsonify({"error": f"Chime file {chime}.mp3 not found"}), 404

            return f(*args, **kwargs)

        return decorated_function

    # Serve MP3 files from the chimes directory
    @app.route("/chimes/<path:filename>")
    def serve_chime(filename):
        return send_from_directory(chimes_directory, filename)

    @app.route("/api/play_chime")
    @validate_parameters
    def play_chime():
        # Get parameters from request
        chime = request.args.get("chime", "doorbell1")
        volume = int(request.args.get("volume", "30"))
        player_ip = request.args.get("playerIP")
        player_id = request.args.get("playerID")
        priority = request.args.get("priority", "LOW")  # Default to LOW if not provided

        # Construct the stream URL using urljoin to handle path properly
        stream_url = urljoin(host, f"/chimes/{quote(chime)}.mp3")

        # Prepare the request to Sonos API
        sonos_url = f"https://{player_ip}:1443/api/v1/players/{player_id}/audioClip"
        headers = {"X-Sonos-Api-Key": sonos_api_key, "Content-Type": "application/json"}
        payload = {
            "name": "Pull Bell",
            "appId": "com.acme.app",
            "streamUrl": stream_url,
            "volume": volume,
            "priority": priority,
        }

        try:
            # Make the request to Sonos API
            response = requests.post(
                sonos_url,
                headers=headers,
                json=payload,
                verify=False,  # Note: In production, you should properly handle SSL verification
            )

            # Try to parse the response as JSON
            try:
                response_data = response.json()
            except ValueError:
                response_data = None

            # If we got a non-2xx response and have JSON data, return the Sonos error
            if not response.ok and response_data:
                return jsonify(
                    {"status": "error", "sonos_status_code": response.status_code, "sonos_error": response_data}
                ), response.status_code

            # If we got a non-2xx response but no JSON, return the HTTP error
            if not response.ok:
                return jsonify(
                    {"status": "error", "sonos_status_code": response.status_code, "error": response.reason}
                ), response.status_code

            # Success case
            return jsonify({"status": "success", "sonos_response": response_data})

        except requests.exceptions.RequestException as e:
            return jsonify({"status": "error", "error": f"Failed to communicate with Sonos API: {str(e)}"}), 500

    @app.route("/api/list_chimes")
    def list_chimes():
        """List all available chime files"""
        try:
            chimes = [f.replace(".mp3", "") for f in os.listdir(chimes_directory) if f.endswith(".mp3")]
            return jsonify({"chimes": chimes})
        except Exception as e:
            return jsonify({"error": f"Failed to list chimes: {str(e)}"}), 500

    return app


# This is only used when running with `python app.py`
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8080)
