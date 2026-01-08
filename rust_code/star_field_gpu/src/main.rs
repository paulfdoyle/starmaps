use serde_json::Value;
use std::fs;
use wgpu::util::DeviceExt;
use winit::{
    event::*,
    event_loop::{ControlFlow, EventLoop},
    window::WindowBuilder,
};

#[repr(C)]
#[derive(Copy, Clone, bytemuck::Pod, bytemuck::Zeroable)]
struct Vertex {
    position: [f32; 3],
}

impl Vertex {
    fn new(x: f32, y: f32, z: f32) -> Self {
        Vertex { position: [x, y, z] }
    }
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

#[tokio::main]
async fn main() {
    // Load data
    let file_content = fs::read_to_string("../datasets/updated_merged_star_exo_data.json")
        .expect("Could not read JSON file");

    let json_data: Vec<Value> = serde_json::from_str(&file_content).expect("Could not parse JSON");

    let mut vertices = Vec::new();
    for star_data in json_data {
        if let (Some(glon), Some(glat), Some(dist)) = (
            star_data["GLON"].as_f64(),
            star_data["GLAT"].as_f64(),
            star_data["dist"].as_f64(),
        ) {
            let (x, y, z) = galactic_to_cartesian(glon, glat, dist);
            vertices.push(Vertex::new(x as f32, y as f32, z as f32));
        }
    }
    // Debugging: Print the first few vertices to check their coordinates
    for (i, vertex) in vertices.iter().take(100).enumerate() {
        println!("Vertex {}: x = {}, y = {}, z = {}", i, vertex.position[0], vertex.position[1], vertex.position[2]);
    }
    // Add a single test vertex at the center for debugging purposes
    vertices.push(Vertex::new(0.0, 0.0, -3.0));
    println!("Added debug vertex at (0, 0, -3)");

    // Debugging: Print the number of vertices created
    println!("Total vertices created: {}", vertices.len());

    // Winit window and wgpu setup
    let event_loop = EventLoop::new();
    let window = WindowBuilder::new().build(&event_loop).unwrap();

    let instance = wgpu::Instance::new(wgpu::Backends::PRIMARY);
    let surface = unsafe { instance.create_surface(&window) };
    let adapter = instance
        .request_adapter(&wgpu::RequestAdapterOptions {
            power_preference: wgpu::PowerPreference::HighPerformance,
            compatible_surface: Some(&surface),
            force_fallback_adapter: false,
        })
        .await
        .expect("Failed to find an appropriate adapter");

    let (device, queue) = adapter
        .request_device(
            &wgpu::DeviceDescriptor {
                features: wgpu::Features::empty(),
                limits: wgpu::Limits::default(),
                label: None,
            },
            None,
        )
        .await
        .expect("Failed to create device");

    // Set the surface format directly
    let swapchain_format = wgpu::TextureFormat::Bgra8UnormSrgb;
    let config = wgpu::SurfaceConfiguration {
        usage: wgpu::TextureUsages::RENDER_ATTACHMENT,
        format: swapchain_format,
        width: 2800,
        height: 1800,
        present_mode: wgpu::PresentMode::Fifo,
    };
    surface.configure(&device, &config);

    // Create the vertex buffer
    let vertex_buffer = device.create_buffer_init(&wgpu::util::BufferInitDescriptor {
        label: Some("Vertex Buffer"),
        contents: bytemuck::cast_slice(&vertices),
        usage: wgpu::BufferUsages::VERTEX,
    });

    // Shader setup
    let shader = device.create_shader_module(wgpu::include_wgsl!("shader.wgsl"));

    let render_pipeline_layout = device.create_pipeline_layout(&wgpu::PipelineLayoutDescriptor {
        label: Some("Render Pipeline Layout"),
        bind_group_layouts: &[],
        push_constant_ranges: &[],
    });

    let render_pipeline = device.create_render_pipeline(&wgpu::RenderPipelineDescriptor {
        label: Some("Render Pipeline"),
        layout: Some(&render_pipeline_layout),
        vertex: wgpu::VertexState {
            module: &shader,
            entry_point: "vs_main",
            buffers: &[wgpu::VertexBufferLayout {
                array_stride: std::mem::size_of::<Vertex>() as wgpu::BufferAddress,
                step_mode: wgpu::VertexStepMode::Vertex,
                attributes: &[
                    wgpu::VertexAttribute {
                        offset: 0,
                        shader_location: 0,
                        format: wgpu::VertexFormat::Float32x3,
                    },
                ],
            }],
        },
        fragment: Some(wgpu::FragmentState {
            module: &shader,
            entry_point: "fs_main",
            targets: &[Some(wgpu::ColorTargetState {
                format: swapchain_format,
                blend: Some(wgpu::BlendState::REPLACE),
                write_mask: wgpu::ColorWrites::ALL,
            })],
        }),
        primitive: wgpu::PrimitiveState {
            topology: wgpu::PrimitiveTopology::PointList,
            ..Default::default()
        },
        depth_stencil: None,
        multisample: wgpu::MultisampleState {
            count: 1,
            mask: !0,
            alpha_to_coverage_enabled: false,
        },
        multiview: None, // Added multiview field
    });

    event_loop.run(move |event, _, control_flow| {
        *control_flow = ControlFlow::Poll;

        match event {
            Event::WindowEvent {
                event: WindowEvent::CloseRequested,
                ..
            } => *control_flow = ControlFlow::Exit,
            Event::RedrawRequested(_) => {
                let frame = surface
                    .get_current_texture()
                    .expect("Failed to acquire next swap chain texture");
                let view = frame
                    .texture
                    .create_view(&wgpu::TextureViewDescriptor::default());

                let mut encoder = device.create_command_encoder(&wgpu::CommandEncoderDescriptor {
                    label: Some("Render Encoder"),
                });

                {
                    let mut render_pass = encoder.begin_render_pass(&wgpu::RenderPassDescriptor {
                        label: Some("Render Pass"),
                        color_attachments: &[Some(wgpu::RenderPassColorAttachment {
                            view: &view,
                            resolve_target: None,
                            ops: wgpu::Operations {
                                load: wgpu::LoadOp::Clear(wgpu::Color {
                                    r: 0.0,
                                    g: 0.0,
                                    b: 0.0,
                                    a: 1.0,
                                }),
                                store: true,
                            },
                        })],
                        depth_stencil_attachment: None,
                    });

                    render_pass.set_pipeline(&render_pipeline);
                    render_pass.set_vertex_buffer(0, vertex_buffer.slice(..));
                    render_pass.draw(0..vertices.len() as u32, 0..1);
                }

                queue.submit(std::iter::once(encoder.finish()));
                frame.present();
            }
            _ => {}
        }
    });
}
