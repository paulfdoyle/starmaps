@vertex
fn vs_main(@location(0) position: vec3<f32>) -> @builtin(position) vec4<f32> {
    // Adjust scale to bring stars closer
    let scale = 0.005;          // Smaller scale to accommodate larger values
    let translation = vec3(0.0, 0.0, -6.0); // Move stars back along Z-axis for visibility
    return vec4(position * scale + translation, 1.0);
}

@fragment
fn fs_main() -> @location(0) vec4<f32> {
    return vec4(1.0, 1.0, 1.0, 1.0); // White color for each star
}
