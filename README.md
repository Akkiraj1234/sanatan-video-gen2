# **Automatic Video Generator for Hindu/Religious/Content Creation**  

This project is a Python-based video generator that creates dynamic videos tailored for YouTube, Instagram Reels, or any platform. It leverages **FFmpeg**, **Pillow**, and **Elevnlabs API** to generate engaging, customizable content. Users can generate text-based videos, add effects, and configure video properties to create personalized, professional videos.

### **Key Features**

1. **Text-Based Template Videos**  
   - Easily create videos based on pre-defined templates where the text is dynamically added.
   - Customize the text content, font style, and animations.

2. **Watermark Addition**  
   - Add watermarks to videos, with the option to provide a custom logo or text.

3. **Compositing Effects**  
   - Add cool compositing effects like rain, fire, flowers, or other custom overlays to make the video visually appealing.

4. **Video Effects**  
   - Apply video effects such as zoom-in, glow, brightness, and other transformations to enhance the visual quality of the video.

5. **Transitions effects**  
   - Use smooth transitions between clips

6. **Custom Frame Rate and Dimensions**  
   - Generate videos with any specified frame rate, width, and height to match your needs.

7. **Text Styling and Customization**  
   - Change text styles (font, size, color) and apply animations to the text for a polished, professional look.

8. **Add Extra Subtitles in Multiple Languages**  
   - Add subtitles in different languages (such as Hindi, English, etc.), allowing for broader audience reach.

9. **Background Music Integration**  
   - Add background music to your video, with options to upload your own tracks or use a library of predefined music.

### future

1. **AI-Powered Auto-Captioning**
  - Automatically generate subtitles using speech recognition for uploaded audio or video.

2. **Auto Image & Video Asset Selection**
  - Automatically pick relevant background images or video clips from a pre-defined library based on the text content.

3. **Motion Graphics & Animated Elements**
  - Add animated elements like lower-thirds, progress bars, countdown timers, and overlays for a more dynamic video.

4. **AI Background Removal & Green Screen Support**
  - Remove or replace backgrounds in videos for a cleaner, more professional look.

5. **Auto Thumbnail Generator**
  - Generate eye-catching video thumbnails automatically based on key frames.





### **Technology Stack**
- **Python** – Core language for the project.
- **FFmpeg** – Video processing tool for encoding, effects, transitions, and compositing.
- **Pillow** – Image processing library for working with text and images.
- **Elevnlabs API** – For generating additional video effects or AI-related tasks (e.g., text-to-speech, image-to-video).


  
<!-- # Project Toolchain Overview

This document outlines the tools and approaches we are using for video editing and subtitle processing, as well as our planned future enhancements. We currently support two types of subtitles: **smart** subtitles (advanced animated text overlays) and **normal** subtitles (standard text overlays). Our primary video processing tool is **FFmpeg**, and we use **Pillow** (with optional OpenCV experiments) for prototyping subtitle effects.

---

## Current Approach

### Video Editing
- **FFmpeg**
  - **Role:** Core video editing tool.
  - **Usage:** Applying filters, compositing, and final video encoding.
  - **Key Features:** Wide format support, efficient filtering, and re-encoding capabilities.

### Subtitle Processing

#### 1. Smart Subtitles (Advanced Animated Subtitles)
- **Pillow**
  - **Role:** Prototyping tool for designing animated text overlays.
  - **Usage:** Creating image-based or animated text effects that can later be overlaid onto video.
- **FFmpeg (or FFmpeg + OpenCV)**
  - **Role:** Integration of animated subtitles into the video.
  - **Usage:** Use FFmpeg filter chains (or process frames with OpenCV) to overlay the generated text animations onto video frames.

#### 2. Normal Subtitles (Standard Text Overlays)
- **FFmpeg**
  - **Role:** Adding subtitles to videos.
  - **Usage:** Hardcoding or muxing subtitles using SRT or ASS files.
  - **Key Commands:**
    - Hardcoding SRT subtitles:  
      `ffmpeg -i input.mp4 -vf "subtitles=subtitle.srt" output.mp4`
    - Hardcoding ASS subtitles (for richer formatting):  
      `ffmpeg -i input.mp4 -vf "ass=subtitle.ass" output.mp4`

---

## Future Enhancements

### Advanced Video Editing and Effects
- **FFmpeg + OpenGL**
  - **Goal:** Implement advanced video effects and real-time filters with hardware acceleration.
  - **Approach:** Integrate FFmpeg with OpenGL to leverage GPU-based rendering.

### Advanced Subtitle Processing
- **FFmpeg + .ass Subtitles + Pillow**
  - **Goal:** Generate and overlay advanced animated subtitles with rich formatting.
  - **Approach:**
    - Use a Python template system (or libraries like `pysubs2`) to programmatically generate an ASS subtitle file containing advanced override tags (e.g., `\t`, `\move`).
    - Use Pillow to prototype and fine-tune these animations.
    - Burn the advanced subtitles into the video with FFmpeg:  
      `ffmpeg -i input.mp4 -vf "ass=advanced_subtitles.ass" output.mp4`
- **Additional Tool Considerations:**
  - **OpenCV:** For frame-by-frame processing if even more granular control is needed.
  - **Manim:** As an alternative for complex animated text sequences.
  - **pysubs2:** For programmatically creating and editing ASS subtitle files with rich styling options.

---

## Summary

- **Current Setup:**
  - **FFmpeg** is used for video editing, applying filters, and embedding subtitles.
  - **Pillow** (and optionally **OpenCV**) is used for prototyping animated “smart” subtitles.
  - **FFmpeg** handles both advanced (via ASS) and normal subtitle embedding.
  
- **Future Enhancements:**
  - Leverage **FFmpeg + OpenGL** for advanced video effects.
  - Use a combination of **FFmpeg + .ass subtitles + Pillow** (or **pysubs2**) for sophisticated animated subtitles.
  - Explore additional libraries like **Manim** for even more complex text animations.

This document serves as our roadmap for both our current implementation and future upgrades, ensuring a flexible and powerful pipeline for video editing and subtitle processing. -->
