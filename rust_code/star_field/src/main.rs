use serde_json::Value;
use std::f64::consts::PI;
use std::fs;
use minifb::{Key, Window, WindowOptions};

// Structure to hold Cartesian coordinates after conversion
struct Star {
    x: f64,
    y: f64,
    z: f64,
}

// Convert Galactic coordinates (l, b, d) to Cartesian (x, y, z)
fn galactic_to_cartesian(glon: f64, glat: f64, dist: f64) -> (f64, f64, f64) {
    let l_rad = glon.to_radians();
    let b_rad = glat.to_radians();

    let x = dist * b_rad.cos() * l_rad.cos();
    let y = dist * b_rad.cos() * l_rad.sin();
    let z = dist * b_rad.sin();

    (x, y, z)
}

fn main() {
    let file_content = fs::read_to_string("../datasets/updated_merged_star_exo_data.json")
        .expect("Could not read JSON file");

    // Parse the JSON as a generic Value to handle missing fields manually
    let json_data: Vec<Value> = serde_json::from_str(&file_content).expect("Could not parse JSON");

    // Debugging: Print the keys of the first few records to inspect field names
    for (i, star_data) in json_data.iter().enumerate().take(5) {
        if let Some(object) = star_data.as_object() {
            let keys: Vec<String> = object.keys().cloned().collect();
            println!("Record {}: Keys = {:?}", i, keys);
        }
    }

    // Convert galactic to Cartesian coordinates for each star, ignoring entries with missing fields
    let mut stars = Vec::new();
    for star_data in json_data {
        if let (Some(GLON), Some(GLAT), Some(dist)) = (
            star_data["GLON"].as_f64(),
            star_data["GLAT"].as_f64(),
            star_data["dist"].as_f64(),
        ) {
            // Only add stars that have valid glon, glat, and dist values
            let (x, y, z) = galactic_to_cartesian(GLON, GLAT, dist);
            stars.push(Star { x, y, z });
        }
    }

    println!("Loaded {} stars with complete data.", stars.len());

    let (width, height) = (3000, 1800);
    let mut window = Window::new("Star Field", width, height, WindowOptions::default())
        .expect("Unable to open window");

    let mut buffer: Vec<u32> = vec![0; width * height];
    let mut angle_x = 0.0;
    let mut angle_y = 0.0;
    let mut angle_z = 0.0;
    let scale = 1.0; // Increase the scale for visibility

    while window.is_open() && !window.is_key_down(Key::Escape) {
        buffer.iter_mut().for_each(|pixel| *pixel = 0);

        // Rotate when keys are pressed
        if window.is_key_down(Key::Y) {
            angle_y += 0.05;
            if angle_y > 2.0 * PI {
                angle_y -= 2.0 * PI;
            }
        }
        if window.is_key_down(Key::X) {
            angle_x += 0.05;
            if angle_x > 2.0 * PI {
                angle_x -= 2.0 * PI;
            }
        }
        if window.is_key_down(Key::Z) {
            angle_z += 0.05;
            if angle_z > 2.0 * PI {
                angle_z -= 2.0 * PI;
            }
        }

        let cos_x = angle_x.cos();
        let sin_x = angle_x.sin();
        let cos_y = angle_y.cos();
        let sin_y = angle_y.sin();
        let cos_z = angle_z.cos();
        let sin_z = angle_z.sin();

        for star in &stars {
            let rotated_y = star.y * cos_x - star.z * sin_x;
            let rotated_z_x = star.y * sin_x + star.z * cos_x;

            let rotated_x = star.x * cos_y + rotated_z_x * sin_y;
            let rotated_z_y = -star.x * sin_y + rotated_z_x * cos_y;

            let final_x = rotated_x * cos_z - rotated_y * sin_z;
            let final_y = rotated_x * sin_z + rotated_y * cos_z;

            let screen_x = (width as f64 / 2.0) + (final_x * scale);
            let screen_y = (height as f64 / 2.0) - (final_y * scale);

            if screen_x >= 0.0 && screen_x < width as f64 && screen_y >= 0.0 && screen_y < height as f64 {
                let idx = screen_x as usize + screen_y as usize * width;
                buffer[idx] = 0xFFFFFF;
            }
        }

        window.update_with_buffer(&buffer, width, height).unwrap();
    }
}
