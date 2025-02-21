import cv2
import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import time
import random

# Initialize GLFW
glfw.init()
width, height = 300, 600  # Default window size
window = glfw.create_window(width, height, "Video Renderer", None, None)
glfw.make_context_current(window)

# Load video
cap = cv2.VideoCapture("1.mp4")
fps = cap.get(cv2.CAP_PROP_FPS)
frame_time = 1.0 / fps if fps > 0 else 1.0 / 30  # Avoid division by zero

# OpenGL shader program with cinematic motion effects
vertex_shader = """
#version 330 core
layout (location = 0) in vec2 aPos;
layout (location = 1) in vec2 aTexCoord;
out vec2 TexCoord;
uniform float time;
void main()
{
    float wave = sin(time * 2.0) * 0.05;
    float warpX = cos(time * 3.0) * 0.02;
    float warpY = sin(time * 3.0) * 0.02;
    gl_Position = vec4(aPos.x + warpX, aPos.y + warpY + wave, 0.0, 1.0);
    TexCoord = aTexCoord + vec2(warpX, warpY);
}
"""
fragment_shader = """
#version 330 core
out vec4 FragColor;
in vec2 TexCoord;
uniform sampler2D texture1;
void main()
{
    vec3 color = texture(texture1, TexCoord).rgb;
    float glitch = fract(sin(dot(TexCoord, vec2(12.9898, 78.233))) * 43758.5453);
    color.r += glitch * 0.02;
    color.b -= glitch * 0.02;
    FragColor = vec4(color, 1.0);
}
"""

shader = compileProgram(compileShader(vertex_shader, GL_VERTEX_SHADER), compileShader(fragment_shader, GL_FRAGMENT_SHADER))

# Set up fullscreen quad
vertices = np.array([
    -1.0, -1.0, 0.0, 0.0,
     1.0, -1.0, 1.0, 0.0,
     1.0,  1.0, 1.0, 1.0,
    -1.0,  1.0, 0.0, 1.0
], dtype=np.float32)
indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

vao = glGenVertexArrays(1)
vbo = glGenBuffers(1)
ebo = glGenBuffers(1)

glBindVertexArray(vao)
glBindBuffer(GL_ARRAY_BUFFER, vbo)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * vertices.itemsize, ctypes.c_void_p(0))
glEnableVertexAttribArray(0)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * vertices.itemsize, ctypes.c_void_p(2 * vertices.itemsize))
glEnableVertexAttribArray(1)

glUseProgram(shader)
time_location = glGetUniformLocation(shader, "time")

def update_texture(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    frame = cv2.flip(frame, 0)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, frame.shape[1], frame.shape[0], 0, GL_RGBA, GL_UNSIGNED_BYTE, frame)

glEnable(GL_TEXTURE_2D)
texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, texture)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

time_start = time.time()
while not glfw.window_should_close(window):
    glfw.poll_events()
    ret, frame = cap.read()
    if not ret:
        break
    update_texture(frame)
    
    elapsed = time.time() - time_start
    glUniform1f(time_location, elapsed)
    
    glClear(GL_COLOR_BUFFER_BIT)
    glBindVertexArray(vao)
    glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
    glfw.swap_buffers(window)

glfw.terminate()
cap.release()
