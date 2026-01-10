import pygame
import sys
import numpy as np
from math import sin, cos, radians
from pyquaternion import Quaternion
import pygame.gfxdraw

# Initialize Pygame
pygame.init()

# Perspective modes
perspectives = ["X-Y", "Y-Z", "X-Z", "X-Y (South)", "Y-Z (South)", "X-Z (South)"]

# Get screen dimensions
screen_info = pygame.display.Info()
display_width, display_height = screen_info.current_w, screen_info.current_h
large_width, large_height = display_width * 5, display_height * 5
large_screen = pygame.Surface((large_width, large_height))
screen = pygame.display.set_mode((display_width, display_height), pygame.FULLSCREEN)
pygame.display.set_caption('3D Spherical Rotation System with Galactic Center')

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Font for labels
font = pygame.font.Font(None, 96)
font_status = pygame.font.Font(None, 36)
font_distance = pygame.font.Font(None, 18)
font_menu = pygame.font.Font(None, 20)

# Define waypoints in Galactic Coordinates (longitude, latitude, distance)
waypoints = [
    (0, 0, 8000, 'Galactic Center Waypoint'),
    (0, 0, 1000, ' 0° Waypoint'),
    (180, 0, 1000, '180° Waypoint'),
    (90, 0, 1000, '90° Waypoint'),
    (270, 0, 1000, '270° Waypoint'),
    (0, 90, 1000, 'North Pole Waypoint'),
    (0, -90, 1000, 'South Pole Waypoint'),
    (45, 45, 1000, '+Q1'),
    (135, 45, 1000, '+Q2'),
    (225, 45, 1000, '+Q3'),
    (315, 45, 1000, '+Q4'),
    (45, -45, 1000, '-Q1'),
    (135, -45, 1000, '-Q2'),
    (225, -45, 1000, '-Q3'),
    (315, -45, 1000, '-Q4')
]

# Zoom levels
zoom_levels = [8200, 4000, 2000, 1000, 500, 250, 100, 50, 10, 5]
current_zoom_index = 3  # Start with the default zoom level (1000 parsecs)

# Conversion from Spherical to Cartesian Coordinates
def spherical_to_cartesian(lon, lat, distance):
    lon, lat = radians(lon), radians(lat)
    x = distance * cos(lat) * cos(lon)
    y = distance * cos(lat) * sin(lon)
    z = distance * sin(lat)
    return np.array([x, y, z])

# Initialize the quaternion representing the object's orientation
current_orientation = Quaternion()

# Rotate object using quaternion
def rotate_object(quaternion, axis, degrees):
    angle = np.radians(degrees)
    if axis == 'x':
        delta_rotation = Quaternion(axis=[1, 0, 0], angle=angle)
    elif axis == 'y':
        delta_rotation = Quaternion(axis=[0, 1, 0], angle=angle)
    elif axis == 'z':
        delta_rotation = Quaternion(axis=[0, 0, 1], angle=angle)
    return quaternion * delta_rotation  # Quaternion multiplication is non-commutative

def project_points(points, quaternion, scale_factor):
    rotated_points = [quaternion.rotate(p) for p in points]

    # Scale the points based on the current zoom level
    scaled_points = [p * scale_factor for p in rotated_points]

    # Project to 2D based on the current perspective with a 90-degree anticlockwise rotation and mirroring
    if perspectives[current_perspective] == "X-Y":
        projected_points = [(large_width / 2 + p[1], large_height / 2 - p[0]) for p in scaled_points]
    elif perspectives[current_perspective] == "Y-Z":
        projected_points = [(large_width / 2 + p[2], large_height / 2 - p[1]) for p in scaled_points]
    elif perspectives[current_perspective] == "X-Z":
        projected_points = [(large_width / 2 + p[2], large_height / 2 - p[0]) for p in scaled_points]
    elif perspectives[current_perspective] == "X-Y (South)":
        projected_points = [(large_width / 2 - p[1], large_height / 2 - p[0]) for p in scaled_points]
    elif perspectives[current_perspective] == "Y-Z (South)":
        projected_points = [(large_width / 2 - p[2], large_height / 2 - p[1]) for p in scaled_points]
    elif perspectives[current_perspective] == "X-Z (South)":
        projected_points = [(large_width / 2 - p[2], large_height / 2 - p[0]) for p in scaled_points]

    return projected_points

def draw_axes(surface, center, quaternion, current_perspective, length=1500):
    # Define initial axes endpoints in 3D space
    axes = {
        'X': np.array([length, 0, 0]),
        'Y': np.array([0, length, 0]),
        'Z': np.array([0, 0, length])
    }

    # Rotate axes
    rotated_axes = {label: quaternion.rotate(pt) for label, pt in axes.items()}

    # Project and draw all axes
    for axis_label, axis in rotated_axes.items():
        if current_perspective == 0:  # X-Y
            end_point = (center[0] + axis[1], center[1] - axis[0])
        elif current_perspective == 1:  # Y-Z
            end_point = (center[0] + axis[2], center[1] - axis[1])
        elif current_perspective == 2:  # X-Z
            end_point = (center[0] + axis[2], center[1] - axis[0])
        elif current_perspective == 3:  # X-Y (South)
            end_point = (center[0] - axis[1], center[1] - axis[0])
        elif current_perspective == 4:  # Y-Z (South)
            end_point = (center[0] - axis[2], center[1] - axis[1])
        elif current_perspective == 5:  # X-Z (South)
            end_point = (center[0] - axis[2], center[1] - axis[0])

        color = RED if axis_label == 'X' else GREEN if axis_label == 'Y' else BLUE
        pygame.draw.line(surface, color, center, end_point, 10)
        label = font.render(axis_label, True, color)
        surface.blit(label, (end_point[0] + 10, end_point[1]))

# Convert waypoints to Cartesian coordinates
cartesian_points = np.array([spherical_to_cartesian(wp[0], wp[1], wp[2]) for wp in waypoints])

# Key status dictionary
key_status = {
    pygame.K_x: False,
    pygame.K_b: False,
    pygame.K_y: False,
    pygame.K_i: False,
    pygame.K_z: False,
    pygame.K_v: False,
    pygame.K_r: False,
    pygame.K_p: False,
    pygame.K_f: False,
    pygame.K_u: False,
    pygame.K_m: False,
    pygame.K_PLUS: False,
    pygame.K_EQUALS: False,
    pygame.K_MINUS: False,
    pygame.K_SLASH: False,
    pygame.K_n: False
}

# Define stars
star_data = [
    (84.28, 2.0, 990.1, 'Deneb', (192, 202, 255)),
    (67.44, 19.24, 7.6787, 'Vega', (89, 125, 255)),
    (47.74, -8.91, 5.1295, 'Altair', (162, 182, 255)),
    (351.95, 15.06, 169.7793, 'Antares', (255, 87, 16)),
    (199.79, -8.96, 152.6718, 'Betelgeuse', (255, 91, 18)),
    (209.24, -25.25, 264.5503, 'Rigel', (90, 127, 255)),
    (261.21, -25.29, 94.7867, 'Canopus', (153, 176, 255)),
    (180.94, -20.25, 20.4332, 'Aldebaran', (255, 182, 128)),
    (316.11, 50.84, 76.5697, 'Spica', (130, 160, 255)),
    (162.58, 4.57, 13.1234, 'Capella', (255, 212, 188)),
    (123.28, 26.46, 132.626, 'Polaris', (217, 218, 255)),
    (196.93, -15.95, 77.3994, 'Bellatrix', (117, 149, 255)),
    (205.21, -17.24, 606.0606, 'Alnilam', (76, 114, 255)),
    (203.86, -17.74, 212.3142, 'Mintaka', (76, 114, 255)),
    (214.51, -18.5, 198.4127, 'Saiph', (140, 167, 255)),
    (195.05, -12.0, 336.7003, 'Meissa', (77, 114, 255)),
    (206.45, -16.59, 225.7336, 'Alnitak',(147, 172, 255)),
    (359.944, -0.046, 8178, 'SGR-A,', (155, 176, 255))
]

# Initialize all stars with their original positions
stars = {name: {'position': spherical_to_cartesian(lon, lat, distance), 'color': color}
         for lon, lat, distance, name, color in star_data}

# Save the original positions for reset
original_star_positions = {name: np.copy(info['position']) for name, info in stars.items()}

# Key event handling for moving stars
def handle_star_movement(key):
    move_amount = 1  # Movement increment
    if key == pygame.K_d:  # Increase X
        for star_info in stars.values():
            star_info['position'][0] += move_amount
    elif key == pygame.K_a:  # Decrease X
        for star_info in stars.values():
            star_info['position'][0] -= move_amount
    elif key == pygame.K_w:  # Increase Y
        for star_info in stars.values():
            star_info['position'][1] += move_amount
    elif key == pygame.K_s:  # Decrease Y
        for star_info in stars.values():
            star_info['position'][1] -= move_amount
    elif key == pygame.K_e:  # Increase Z
        for star_info in stars.values():
            star_info['position'][2] += move_amount
    elif key == pygame.K_q:  # Decrease Z
        for star_info in stars.values():
            star_info['position'][2] -= move_amount

# Reset star positions
def reset_star_positions():
    for name, pos in original_star_positions.items():
        stars[name]['position'] = np.copy(pos)

# Function to draw a star with gradient
def draw_star_surface(radius, color):
    star_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    for i in range(radius, 0, -1):
        if i < radius // 4:
            gradient_color = (255, 255, 255)
        elif i < radius // 2:
            mix_ratio = (i - radius // 4) / (radius // 4)
            gradient_color = [int(255 + (color_component - 255) * mix_ratio) for color_component in color]
        else:
            mix_ratio = (i - radius // 2) / (radius // 2)
            gradient_color = [int(color_component * (1 - mix_ratio)) for color_component in color]

        gradient_color = tuple(max(0, min(255, c)) for c in gradient_color)
        pygame.gfxdraw.filled_circle(star_surface, radius, radius, i, gradient_color)
    return star_surface

# Display function for stars and distance information
def display_stars(surface, stars, quaternion, scale_factor, show_labels):
    for star_name, star_info in stars.items():
        pos = star_info['position']
        scaled_pos = pos * scale_factor
        color = star_info['color']
        projected = project_points([scaled_pos], quaternion, 1.0)[0]  # Use 1.0 to prevent double scaling
        star_surface = draw_star_surface(15, color)  # Adjust radius as needed
        surface.blit(star_surface, (int(projected[0] - 10), int(projected[1] - 10)))
        if show_labels:
            label = font.render(star_name, True, WHITE)
            surface.blit(label, (int(projected[0] + 25), int(projected[1])))

# Display function for star distances on the left side
def display_star_distances(surface, stars, scale_factor):
    y_offset = 350
    column = 0
    max_rows = 9  # Maximum number of rows per column
    for index, (star_name, star_info) in enumerate(stars.items()):
        if index != 0 and index % max_rows == 0:
            column += 1  # Move to the next column
        position = star_info['position']
        distance = np.linalg.norm(position)  # Keep the actual distance
        distance_label = font_distance.render(f"{star_name}: {distance:.2f} pc", True, WHITE)
        
        # Determine the x and y position for the current label
        x_position = 20 + column * 300
        y_position = y_offset + (index % max_rows) * 30
        surface.blit(distance_label, (x_position, y_position))

# Menu for keypress events
keypress_events = [
    ("X / B", "Rotate around X-axis (positive/negative)"),
    ("Y / I", "Rotate around Y-axis (positive/negative)"),
    ("Z / V", "Rotate around Z-axis (positive/negative)"),
    ("R", "Reset rotation"),
    ("P", "Change perspective"),
    ("F", "Reset star positions"),
    ("W / S", "Move stars along Y-axis (positive/negative)"),
    ("A / D", "Move stars along X-axis (positive/negative)"),
    ("Q / E", "Move stars along Z-axis (positive/negative)"),
    ("K", "Toggle waypoints on/off"),
    ("J", "Toggle stars on/off"),
    ("M", "Toggle labels on/off"),
    ("N", "Toggle axes on/off"),
    ("+ / =", "Zoom in"),
    ("-", "Zoom out"),
    ("/", "Toggle menu on/off"),
    ("ESC", "Quit the program")
]

def display_menu(surface):
    y_offset = 50
    for event in keypress_events:
        key_label = font_menu.render(event[0], True, WHITE)
        description_label = font_menu.render(event[1], True, WHITE)
        surface.blit(key_label, (display_width - 350, y_offset))
        surface.blit(description_label, (display_width - 300, y_offset))
        y_offset += 30

current_perspective = 0  # Start with X-Y as the default perspective
current_rotation_axis = "No rotation"
show_waypoints = True  # Flag to toggle waypoints
show_stars = True  # Flag to toggle stars
show_labels = True  # Flag to toggle labels
show_axes = True  # Flag to toggle axes
show_menu = True  # Flag to toggle menu

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            handle_star_movement(event.key)
            key_status[event.key] = True
            if event.key == pygame.K_p:
                current_perspective = (current_perspective + 1) % len(perspectives)
            if event.key == pygame.K_f:
                reset_star_positions()
            if event.key == pygame.K_k:
                show_waypoints = not show_waypoints
            if event.key == pygame.K_j:
                show_stars = not show_stars
            if event.key == pygame.K_m:
                show_labels = not show_labels
            if event.key == pygame.K_n:
                show_axes = not show_axes
            if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                current_zoom_index = max(0, current_zoom_index - 1)
            if event.key == pygame.K_MINUS:
                current_zoom_index = min(len(zoom_levels) - 1, current_zoom_index + 1)
            if event.key == pygame.K_SLASH:
                show_menu = not show_menu
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.KEYUP:
            key_status[event.key] = False

    # Reset rotation angles if 'r' is pressed
    if key_status[pygame.K_r]:
        current_orientation = Quaternion()
        current_rotation_axis = "No rotation"

    # Update rotation based on key status
    if key_status[pygame.K_x]:
        current_orientation = rotate_object(current_orientation, 'x', 2)
        current_rotation_axis = "Rotating around X axis"
    if key_status[pygame.K_b]:
        current_orientation = rotate_object(current_orientation, 'x', -2)
        current_rotation_axis = "Rotating around X axis"
    if key_status[pygame.K_y]:
        current_orientation = rotate_object(current_orientation, 'y', 2)
        current_rotation_axis = "Rotating around Y axis"
    if key_status[pygame.K_i]:
        current_orientation = rotate_object(current_orientation, 'y', -2)
        current_rotation_axis = "Rotating around Y axis"
    if key_status[pygame.K_z]:
        current_orientation = rotate_object(current_orientation, 'z', 2)
        current_rotation_axis = "Rotating around Z axis"
    if key_status[pygame.K_v]:
        current_orientation = rotate_object(current_orientation, 'z', -2)
        current_rotation_axis = "Rotating around Z axis"

    # Clear the large screen
    large_screen.fill(BLACK)

    # Get the current zoom level
    current_zoom_level = zoom_levels[current_zoom_index]

    # Calculate the scale factor
    default_zoom_level = 1000
    scale_factor = default_zoom_level / current_zoom_level

    # Project and draw waypoints if enabled
    if show_waypoints:
        projected = project_points(cartesian_points, current_orientation, scale_factor)
        for i, point in enumerate(projected):
            pygame.draw.circle(large_screen, GREEN, (int(point[0]), int(point[1])), 20)
            if show_labels:
                label = font.render(waypoints[i][3], True, WHITE)
                large_screen.blit(label, (int(point[0] + 25), int(point[1])))

    # Draw the axes if enabled
    if show_axes:
        draw_axes(large_screen, (large_width // 2, large_height // 2), current_orientation, current_perspective)

    # Display stars with their labels if enabled
    if show_stars:
        display_stars(large_screen, stars, current_orientation, scale_factor, show_labels)

    # Draw a large circle to represent the sphere
    pygame.draw.circle(large_screen, WHITE, (large_width // 2, large_height // 2), 1000, 10)

    # Scale down to the display screen
    scaled_screen = pygame.transform.scale(large_screen, (display_width, display_height))
    screen.blit(scaled_screen, (0, 0))

    # Display current rotation axis, perspective, and zoom level
    zoom_label = font_status.render(f"Zoom Level: {current_zoom_level} pc", True, WHITE)
    screen.blit(zoom_label, (100, 150))

    axis_label = font_status.render(current_rotation_axis, True, WHITE)
    perspective_label = font_status.render(f"Perspective: {perspectives[current_perspective]}", True, WHITE)
    screen.blit(axis_label, (100, 200))
    screen.blit(perspective_label, (100, 250))

    # Display the current distance of each star if enabled
    if show_stars:
        display_star_distances(screen, stars, scale_factor)

    # Display the menu of keypress events if enabled
    if show_menu:
        display_menu(screen)

    # Update the display
    pygame.display.flip()

pygame.quit()
sys.exit()
