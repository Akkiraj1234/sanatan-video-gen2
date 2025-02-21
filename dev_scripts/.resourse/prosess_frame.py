import glfw
import OpenGL.GL as gl
import OpenGL.GL.shaders
import numpy as np
import cv2
from PIL import Image

# Initialize OpenGL
if not glfw.init():
    raise Exception("GLFW cannot be initialized!")

window = glfw.create_window(800, 600, "Instagram Filter Renderer", None, None)
if not window:
    glfw.terminate()
    raise Exception("Window could not be created!")

glfw.make_context_current(window)

# Load Shader
with open("shader.frag", "r") as f:
    fragment_shader_code = f.read()

vertex_shader_code = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoords;
out vec2 TexCoords;
void main()
{
    TexCoords = aTexCoords;
    gl_Position = vec4(aPos, 1.0);
}
"""

# Compile shaders
shader_program = OpenGL.GL.shaders.compileProgram(
    OpenGL.GL.shaders.compileShader(vertex_shader_code, gl.GL_VERTEX_SHADER),
    OpenGL.GL.shaders.compileShader(fragment_shader_code, gl.GL_FRAGMENT_SHADER)
)

gl.useProgram(shader_program)

# Function to process each frame
def process_frame(input_path, output_path):
    image = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    height, width, _ = image.shape
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Create OpenGL Texture
    texture = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, width, height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, image)
    
    # Render frame
    glfw.poll_events()
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)
    glfw.swap_buffers(window)

    # Capture frame from OpenGL and save it
    frame = gl.glReadPixels(0, 0, width, height, gl.GL_RGB, gl.GL_UNSIGNED_BYTE)
    frame = np.frombuffer(frame, dtype=np.uint8).reshape(height, width, 3)
    frame = np.flipud(frame)  # Flip vertically
    Image.fromarray(frame).save(output_path)

    # Cleanup
    gl.glDeleteTextures(1, [texture])

# Process all frames
for i in range(1, 1000):  # Adjust based on the number of frames
    input_frame = f"frame_{i:04d}.png"
    output_frame = f"processed_frame_{i:04d}.png"
    try:
        process_frame(input_frame, output_frame)
        print(f"Processed {input_frame} -> {output_frame}")
    except Exception as e:
        print(f"Skipping {input_frame}: {e}")

glfw.terminate()
