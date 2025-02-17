from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Allow frontend to communicate

# Video Storage Path
VIDEO_OUTPUT = "/home/akkiraj/Desktop/sanatan-video-gen2/assets/temp/hanumanji.mp4"

@app.route("/generate-video", methods=["POST"])
def generate_video():
    try:
        data = request.json
        text = data.get("text", "No text provided")

        print("resived the file", text)
        return send_file(VIDEO_OUTPUT, as_attachment=True)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
