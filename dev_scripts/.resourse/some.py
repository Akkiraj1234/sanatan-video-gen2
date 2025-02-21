# import glfw
# import OpenGL.GL as gl
# import numpy as np
# import cv2
# import os

# # Initialize GLFW
# if not glfw.init():
#     raise Exception("GLFW could not be initialized!")

# # Create OpenGL Window (Hidden)
# width, height = 720, 1280  # Ensure this matches video resolution
# glfw.window_hint(glfw.VISIBLE, glfw.FALSE)  # Hide window
# window = glfw.create_window(width, height, "Offscreen", None, None)
# glfw.make_context_current(window)

# # OpenGL Shaders
# VERTEX_SHADER = """
# #version 330 core
# layout (location = 0) in vec2 aPos;
# layout (location = 1) in vec2 aTexCoords;
# out vec2 TexCoords;
# void main() {
#     TexCoords = aTexCoords;
#     gl_Position = vec4(aPos, 0.0, 1.0);
# }
# """

# FRAGMENT_SHADER = """
# #version 330 core
# out vec4 FragColor;
# in vec2 TexCoords;
# uniform sampler2D tex;
# uniform float playTime;
# void main() {
#     float offset = sin(playTime) * 0.1;
#     vec2 offsetCoords = TexCoords + vec2(offset, offset);
#     FragColor = texture(tex, offsetCoords);
# }
# """

# # Shader Compilation
# def compile_shader(shader_type, source):
#     shader = gl.glCreateShader(shader_type)
#     gl.glShaderSource(shader, source)
#     gl.glCompileShader(shader)
#     if not gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS):
#         raise RuntimeError(gl.glGetShaderInfoLog(shader).decode())
#     return shader

# vertex_shader = compile_shader(gl.GL_VERTEX_SHADER, VERTEX_SHADER)
# fragment_shader = compile_shader(gl.GL_FRAGMENT_SHADER, FRAGMENT_SHADER)

# shader_program = gl.glCreateProgram()
# gl.glAttachShader(shader_program, vertex_shader)
# gl.glAttachShader(shader_program, fragment_shader)
# gl.glLinkProgram(shader_program)

# if not gl.glGetProgramiv(shader_program, gl.GL_LINK_STATUS):
#     raise RuntimeError(gl.glGetProgramInfoLog(shader_program).decode())

# gl.glUseProgram(shader_program)

# # Define Quad (Full-Screen) with VAO/VBO
# quad_vertices = np.array([
#     -1.0,  1.0,  0.0, 1.0,  # Top-left
#     -1.0, -1.0,  0.0, 0.0,  # Bottom-left
#      1.0, -1.0,  1.0, 0.0,  # Bottom-right
#      1.0,  1.0,  1.0, 1.0   # Top-right
# ], dtype=np.float32)

# quad_indices = np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)

# VAO = gl.glGenVertexArrays(1)
# VBO = gl.glGenBuffers(1)
# EBO = gl.glGenBuffers(1)

# gl.glBindVertexArray(VAO)

# # Upload Vertex Data
# gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO)
# gl.glBufferData(gl.GL_ARRAY_BUFFER, quad_vertices.nbytes, quad_vertices, gl.GL_STATIC_DRAW)

# gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, EBO)
# gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, quad_indices.nbytes, quad_indices, gl.GL_STATIC_DRAW)

# # Position Attribute
# gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 4 * quad_vertices.itemsize, None)
# gl.glEnableVertexAttribArray(0)

# # Texture Coordinate Attribute
# gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 4 * quad_vertices.itemsize, gl.ctypes.c_void_p(2 * quad_vertices.itemsize))
# gl.glEnableVertexAttribArray(1)

# gl.glBindVertexArray(0)

# # Load Video & Process Frames
# video_path = "1.mp4"
# output_folder = "frames"
# os.makedirs(output_folder, exist_ok=True)

# cap = cv2.VideoCapture(video_path)
# frame_count = 0

# # Texture Setup
# texture = gl.glGenTextures(1)
# gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
# gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
# gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break

#     # Resize frame if needed
#     frame = cv2.resize(frame, (width, height))  # Resize to match OpenGL
#     frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     frame = cv2.flip(frame, 0)

#     # Upload frame to texture
#     gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
#     gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, width, height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, frame)

#     # Set Shader Time Uniform
#     gl.glUniform1f(gl.glGetUniformLocation(shader_program, "playTime"), frame_count * 0.05)

#     # Render
#     gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
#     gl.glBindVertexArray(VAO)
#     gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, None)
#     glfw.swap_buffers(window)

#     # Read OpenGL Frame & Save as Image
#     output_frame = gl.glReadPixels(0, 0, width, height, gl.GL_RGB, gl.GL_UNSIGNED_BYTE)
#     output_frame = np.frombuffer(output_frame, dtype=np.uint8).reshape(height, width, 3)
#     output_frame = cv2.flip(output_frame, 0)
#     cv2.imwrite(f"{output_folder}/frame_{frame_count:04d}.png", output_frame)

#     frame_count += 1
#     glfw.poll_events()

# cap.release()
# glfw.terminate()

# # Combine Frames into Video with FFmpeg
# output_video = "output.mp4"
# ffmpeg_cmd = f"ffmpeg -r 30 -i frames/frame_%04d.png -c:v libx264 -pix_fmt yuv420p {output_video}"
# os.system(ffmpeg_cmd)

# print(f"✅ Process Complete! Output saved as {output_video}")



import cv2
import subprocess
import numpy as np

# Load video
cap = cv2.VideoCapture("1.mp4")
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

# FFmpeg command (faster encoding + small file size)
ffmpeg_cmd = [
    "ffmpeg", "-y",
    "-f", "rawvideo",
    "-pix_fmt", "bgr24",
    "-s", f"{width}x{height}",
    "-r", str(fps),
    "-i", "-",
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "23",
    "-pix_fmt", "yuv420p",
    "output.mp4"
]

# Open FFmpeg process
ffmpeg_pipe = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Apply effects (Blur + Shake + Animated Text)
    frame = cv2.GaussianBlur(frame, (9, 9), 0)  # Blur Effect
    # Add shake effect by shifting pixels (example)
    dx, dy = np.random.randint(-5, 5, size=2)
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    frame = cv2.warpAffine(frame, M, (width, height))

    # Write frame to FFmpeg (instead of saving PNGs)
    ffmpeg_pipe.stdin.write(frame.tobytes())

# Cleanup
cap.release()
ffmpeg_pipe.stdin.close()
ffmpeg_pipe.wait()
