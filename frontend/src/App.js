import React, { useState } from "react";
import axios from "axios";

export default function App() {
    const [text, setText] = useState("");
    const [videoUrl, setVideoUrl] = useState(null);

    const handleSubmit = async () => {
        try {
            const response = await axios.post("http://127.0.0.1:5000/generate-video", 
                { text },
                { responseType: "blob" } // To receive binary video file
            );

            // Create a URL for the video file
            const videoBlob = new Blob([response.data], { type: "video/mp4" });
            const videoURL = URL.createObjectURL(videoBlob);
            setVideoUrl(videoURL);
        } catch (error) {
            console.error("Error generating video:", error);
        }
    };

    return (
        <div style={{ textAlign: "center", marginTop: "50px" }}>
            <h1>Text-to-Video Generator</h1>
            
            <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Enter your text..."
                style={{
                    width: "80%",
                    height: "100px",
                    padding: "10px",
                    fontSize: "16px",
                    resize: "none",
                }}
            />

            <br />
            <button onClick={handleSubmit} style={{ padding: "10px", margin: "10px", fontSize: "16px" }}>
                Generate Video
            </button>

            {videoUrl && (
                <div>
                    <h2>Generated Video:</h2>
                    <video src={videoUrl} controls style={{ width: "50%", marginTop: "20px" }}></video>
                    <br />
                    <a href={videoUrl} download="generated_video.mp4">
                        <button style={{ padding: "10px", margin: "10px", fontSize: "16px" }}>Download</button>
                    </a>
                </div>
            )}
        </div>
    );
}
