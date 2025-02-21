#version 330 core
out vec4 FragColor;
in vec2 TexCoords;
uniform sampler2D image;

void main()
{
    vec4 color = texture(image, TexCoords);

    // 1. Apply Sepia Effect
    vec3 sepiaColor = vec3(
        dot(color.rgb, vec3(0.393, 0.769, 0.189)),
        dot(color.rgb, vec3(0.349, 0.686, 0.168)),
        dot(color.rgb, vec3(0.272, 0.534, 0.131))
    );

    // 2. Adjust Brightness & Contrast
    float brightness = 0.1;  // Increase for more brightness
    float contrast = 1.2;    // Increase for more contrast
    vec3 finalColor = sepiaColor * contrast + brightness;

    // 3. Vignette Effect (Dark edges)
    float vignetteStrength = 0.5;
    vec2 position = TexCoords - vec2(0.5, 0.5);
    float vignette = 1.0 - vignetteStrength * length(position);
    finalColor *= vignette;

    // 4. Glitch Effect (RGB Shift)
    vec2 glitchOffset = vec2(0.001, 0.001);
    vec4 redChannel = texture(image, TexCoords + glitchOffset);
    vec4 blueChannel = texture(image, TexCoords - glitchOffset);

    FragColor = vec4(redChannel.r, finalColor.g, blueChannel.b, color.a);
}
