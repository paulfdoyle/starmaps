import pygame
import numpy as np
from line_profiler import profile
from datetime import datetime, timedelta
import math
from graphics import draw_constellation_lines, preprocess_coordinates, twinkle_star, precalculate_star_pairs, writeText, draw_orion_constellation_lines, buildStarImageDB ,draw_status, draw_clicked_star_hip, draw_fps, draw_placeholder, draw_menu
from celestial_mechanics import collect_celestial_data, update_star_positions, update_celestial_projection, calculate_apparent_magnitude, interpolate_shifts
from user_interface import handle_key_events, handle_continuous_input, draw_menu
from data_handling import load_custom_star_data, extract_orion_star_pairs
from utils import *


# Global variables
star_coordinates = {}  # Dictionary to store star coordinates
clicked_star_hip = None  # Variable to store the HIP ID of the clicked star
clicked_stars = []  # Global variable to store the list of clicked stars

# Functions
def initialize_pygame():
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    pygame.display.set_caption("Star Chart: Dublin, Ireland")
    return screen, pygame.time.Clock()

def create_canvas():
    canvas = pygame.Surface((canvas_width, canvas_height))
    canvas.fill(CIndex.BLACK)
    return canvas

def load_data():
    star_data_array, eph, constellations = load_custom_star_data('../datasets/star_database_colors.json')
    star_data_np, edges_star1, edges_star2 = collect_celestial_data(star_data_array, eph, constellations, lat, long, timescale, when)
    orion_star_pairs = extract_orion_star_pairs('constellationship.fab')
    np.savetxt("../datasets/star_data_np.csv", star_data_np, delimiter=',', header=header_string, comments='', fmt='%s')
    return star_data_array, star_data_np, eph, constellations, orion_star_pairs, edges_star1, edges_star2

def update_data(star_data_np, eph, constellations, control_vars):
    new_star_positions_np = update_star_positions(star_data_np, control_vars['shift_x'], control_vars['shift_y'], control_vars['shift_z'])
    updated_star_positions_np, edges_star1, edges_star2 = update_celestial_projection(new_star_positions_np, eph, constellations, lat, long, timescale, control_vars['current_time'].strftime('%Y-%m-%d %H:%M'))
    np.savetxt("../datasets/updated_star_positions.csv", updated_star_positions_np, delimiter=',', header=header_string, comments='', fmt='%s')
    return updated_star_positions_np

def initialize_labels():
    return {
        'sirius': writeText("Sirius", CIndex.WHITE, FIndex.MEDIUM),
        'polaris': writeText("Polaris", CIndex.WHITE, FIndex.MEDIUM),
        'orion': writeText("Betelgeuse", CIndex.WHITE, FIndex.MEDIUM),
        'alphaCentA': writeText("Alpha Centauri", CIndex.WHITE, FIndex.MEDIUM),
        'Galactic_Centre': writeText("GC", CIndex.WHITE, FIndex.MEDIUM),
        'Sun': writeText("Sun", CIndex.WHITE, FIndex.MEDIUM),
    }

def draw_labels(canvas, active_star_data, control_vars, canvas_set, labels):
    global center_x, center_y
    global star_coordinates  # Access the global star_coordinates dictionary
    star_coordinates.clear()  # Clear the dictionary to avoid stale data

    index = 0
    center_x = canvas_width / 2
    center_y = canvas_height / 2
    for star in active_star_data:
        hip_id = star[SIndex.HIP]
        x, y = (star[-2], star[-1]) if control_vars['use_updated_positions'] else (star[SIndex.X], star[SIndex.Y])
        x, y = preprocess_coordinates(x, y, center_x, center_y, control_vars['zoom_factor'], control_vars['x_offset'], control_vars['y_offset'])

        star_coordinates[(x, y)] = hip_id

        newmag = calculate_apparent_magnitude(star[SIndex.ABS_MAG], star[SIndex.DISTANCE_PARSECS], hip_id)
        if newmag is not None and 0 <= x < canvas_width and 0 <= y < canvas_height:
            mag = round(newmag) if round(newmag) <= 6 else 6
            mag = min(max(mag, 0), 6)  # Ensure mag is within 0-6
            star_type_index = int(star[SIndex.STAR_TYPE])
            offset = canvas_set[star_type_index][mag][0].get_width() / 2
            canvas.blit(twinkle_star(canvas_set[star_type_index][mag]), (x - offset, y - offset), special_flags=pygame.BLEND_ADD)
            if hip_id == SIRIUS_HIP:
                canvas.blit(labels['sirius'], (x - offset, y - offset - 20))
            elif hip_id == POLARIS_HIP:
                canvas.blit(labels['polaris'], (x - offset, y - offset - 20))
            elif hip_id == BETELGEUSE_HIP:
                canvas.blit(labels['orion'], (x - offset, y - offset - 20))
            elif hip_id == APLHACENTAURI_HIP:
                canvas.blit(labels['alphaCentA'], (x - offset, y - offset - 20))
            elif hip_id == GC_HIP:
                canvas.blit(labels['Galactic_Centre'], (x - offset, y - offset - 20))
            elif hip_id == SOL_HIP:
                canvas.blit(labels['Sun'], (x - offset, y - offset - 20))
        index += 1

def transform_view_to_star(clicked_star_hip, control_vars):
    star_index = np.where(star_data_np[:, SIndex.HIP] == clicked_star_hip)[0][0]
    star_x = star_data_np[star_index, SIndex.Dx]
    star_y = star_data_np[star_index, SIndex.Dy]
    star_z = star_data_np[star_index, SIndex.Dz]

    # Number of steps for the animation
    steps = 20  # Adjust this value for smoother or faster animation

    # Generate the steps for each axis
    control_vars['shift_x_steps'] = interpolate_shifts(control_vars['shift_x'], -star_x, steps)
    control_vars['shift_y_steps'] = interpolate_shifts(control_vars['shift_y'], -star_y, steps)
    control_vars['shift_z_steps'] = interpolate_shifts(control_vars['shift_z'], -star_z, steps)

    control_vars['current_step'] = 0
    control_vars['animating'] = True  # Start the animation

    print(f"Initiating smooth transition to star HIP: {clicked_star_hip} at coordinates ({star_x}, {star_y}, {star_z})")


def handle_mouse_click(event, star_coordinates, control_vars):
    global clicked_star_hip  # Access the global clicked_star_hip variable
    global clicked_stars  # Global variable to store the list of clicked stars

    if event.type == pygame.MOUSEBUTTONDOWN:
        # Convert mouse click coordinates to canvas coordinates
        mouse_x, mouse_y = event.pos
        canvas_x = mouse_x * 5  # Scale by 5 to match the canvas size
        canvas_y = mouse_y * 5  # Scale by 5 to match the canvas size

        # Define a threshold distance to consider a star "clicked"
        threshold_distance = 50  # Adjust this value as needed for sensitivity

        # Find all star coordinates near the mouse click
        clicked_stars = [(hip, math.sqrt((x - canvas_x) ** 2 + (y - canvas_y) ** 2))
                         for (x, y), hip in star_coordinates.items() if math.sqrt((x - canvas_x) ** 2 + (y - canvas_y) ** 2) < threshold_distance]

        # Sort the clicked stars by distance
        clicked_stars.sort(key=lambda star: star[1])

        if clicked_stars:
            new_clicked_star_hip = clicked_stars[0][0]  # Set the closest star's HIP as the main clicked star

            if new_clicked_star_hip == clicked_star_hip:
                # Second click on the same star, transform the view
                print(f"Second click on star HIP: {new_clicked_star_hip}")
                transform_view_to_star(new_clicked_star_hip, control_vars)
            else:
                clicked_star_hip = new_clicked_star_hip  # Update the clicked star HIP
                print(f"Clicked star HIP IDs: {[hip for hip, _ in clicked_stars]}")

                # Center the clicked star on the screen
                clicked_star_coords = [(x, y) for (x, y), hip in star_coordinates.items() if hip == clicked_star_hip][0]

                star_x, star_y = clicked_star_coords
                screen_center_x = screen_width / 2 * 5  # Scale by 5 to match the canvas size
                screen_center_y = screen_height / 2 * 5

                # Adjust offsets to center the clicked star
                control_vars['x_offset'] += (screen_center_x - star_x) / control_vars['zoom_factor']
                control_vars['y_offset'] += (screen_center_y - star_y) / control_vars['zoom_factor']

    set_clicked_stars(clicked_stars)

@profile
def main():
    global shift_x, shift_y, shift_z
    global prev_shift_x, prev_shift_y, prev_shift_z
    global star_data_array, star_data_np, eph, constellations, orion_star_pairs, edges_star1, edges_star2
    global screen_width, screen_height, canvas_width, canvas_height

    screen, clock = initialize_pygame()
    canvas = create_canvas()
    star_data_array, star_data_np, eph, constellations, orion_star_pairs, edges_star1, edges_star2 = load_data()

    control_vars = {
        'draw_constellations': False,
        'draw_orion': False,
        'track_axes_changes': False,
        'rotate': False,
        'use_updated_positions': False,
        'show_menu': False,
        'x_offset': 0,
        'y_offset': 0,
        'zoom_factor': 1.0,
        'shift_x': 0,
        'shift_y': 0,
        'shift_z': 0,
        'prev_shift_x': 0,
        'prev_shift_y': 0,
        'prev_shift_z': 0,
        'current_time': datetime.strptime(when, '%Y-%m-%d %H:%M'),
        'time_delta': timedelta(minutes=1),
        'animating': False,  # Flag to indicate if an animation is in progress
        'paused': False,  # Flag to indicate if the animation is paused
        'current_step': 0  # To track the current step in the animation
    }

    menu_items = [
        "Y/I: Move Y axis",
        "X/B: Move X axis",
        "Z/V: Move Z axis",
        "C: Toggle constellations",
        "R: Rotate",
        "+/-: Zoom",
        "Arrow Keys right/left: Move time forward/backward",
        "WASD: Pan",
        "U: Toggle positions to enable axis shifting",
        "M: Show/Hide this menu",
        "F: Reset Panning and Zooms",
        "G: Reset Axis rotations",
        "H: Return to Home",
        "Space: Pause/Resume Animation",
        "Click a star to focus, click again to zoom",
    ]

    placeholder_text = "Press M to toggle functions menu"

    updated_star_positions_np = update_data(star_data_np, eph, constellations, control_vars)
    labels = initialize_labels()
    canvas_set = buildStarImageDB()
    new_star_positions_np = None  # Initialize here

    print("running simulation")
    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                set_size_screen(event.w, event.h)
                screen_width, screen_height = get_size_screen()
                set_size_canvas(max(event.w, event.h))
                canvas_width, canvas_height = get_size_canvas()
                screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
                canvas = pygame.Surface((canvas_width, canvas_height))
                canvas.fill(CIndex.BLACK)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_mouse_click(event, star_coordinates, control_vars)

            running = handle_key_events(event, {}, control_vars)

        handle_continuous_input(control_vars)

        # If animating and not paused, update shifts based on steps
        if control_vars.get('animating', False) and not control_vars.get('paused', False):
            step = control_vars['current_step']
            if step < len(control_vars['shift_x_steps']) - 1:
                control_vars['shift_x'] = control_vars['shift_x_steps'][step]
                control_vars['shift_y'] = control_vars['shift_y_steps'][step]
                control_vars['shift_z'] = control_vars['shift_z_steps'][step]
                control_vars['current_step'] += 1
            else:
                # Final step: set exact target values
                control_vars['shift_x'] = control_vars['shift_x_steps'][-1]
                control_vars['shift_y'] = control_vars['shift_y_steps'][-1]
                control_vars['shift_z'] = control_vars['shift_z_steps'][-1]
                control_vars['animating'] = False  # Animation finished
                print("Animation completed at final position:", control_vars['shift_x'], control_vars['shift_y'], control_vars['shift_z'])

        # Continue with the usual update process
        shift_x, shift_y, shift_z = control_vars['shift_x'], control_vars['shift_y'], control_vars['shift_z']
        prev_shift_x, prev_shift_y, prev_shift_z = control_vars['prev_shift_x'], control_vars['prev_shift_y'], control_vars['prev_shift_z']

        if control_vars['track_axes_changes'] and (control_vars['shift_x'] != control_vars['prev_shift_x'] or control_vars['shift_y'] != control_vars['prev_shift_y'] or control_vars['shift_z'] != control_vars['prev_shift_z']):
            print(f"Axes changed to X: {shift_x}, Y: {shift_y}, Z: {shift_z}")
            new_star_positions_np = update_star_positions(star_data_np, shift_x, shift_y, shift_z)
            updated_star_positions_np, edges_star1, edges_star2 = update_celestial_projection(new_star_positions_np, eph, constellations, lat, long, timescale, control_vars['current_time'].strftime('%Y-%m-%d %H:%M'))
            control_vars['prev_shift_x'], control_vars['prev_shift_y'], control_vars['prev_shift_z'] = control_vars['shift_x'], control_vars['shift_y'], control_vars['shift_z']

        if control_vars['rotate']:
            control_vars['current_time'] += control_vars['time_delta']

        if not control_vars['use_updated_positions']:
            star_data_np, edges_star1, edges_star2 = collect_celestial_data(star_data_array, eph, constellations, lat, long, timescale, control_vars['current_time'].strftime('%Y-%m-%d %H:%M'))
        else:
            if new_star_positions_np is None:
                new_star_positions_np = update_star_positions(star_data_np, shift_x, shift_y, shift_z)
            updated_star_positions_np, edges_star1, edges_star2 = update_celestial_projection(new_star_positions_np, eph, constellations, lat, long, timescale, control_vars['current_time'].strftime('%Y-%m-%d %H:%M'))

        active_star_data = updated_star_positions_np if control_vars['use_updated_positions'] else star_data_np
        canvas.fill(CIndex.BLACK)
        draw_labels(canvas, active_star_data, control_vars, canvas_set, labels)

        if control_vars['draw_constellations']:
            precalculated_pairs = precalculate_star_pairs(active_star_data, edges_star1, edges_star2, canvas_width / 2, canvas_height / 2, control_vars['zoom_factor'], control_vars['x_offset'], control_vars['y_offset'])
            canvas = draw_constellation_lines(canvas, precalculated_pairs, active_star_data)
        elif control_vars['draw_orion']:
            canvas = draw_orion_constellation_lines(canvas, orion_star_pairs, active_star_data, control_vars['zoom_factor'], control_vars['x_offset'], control_vars['y_offset'])

        scaled_canvas = pygame.transform.smoothscale(canvas, (max(screen_width, screen_height), max(screen_width, screen_height)))
        screen.fill(CIndex.BLACK)

        screen_width, screen_height = get_size_screen()
        canvas_width, canvas_height = get_size_canvas()
        screen.blit(scaled_canvas, (0,0))

        # Draw the FPS on the screen
        draw_fps(screen, clock)

        draw_status(screen, control_vars)
        draw_clicked_star_hip(screen, clicked_stars, control_vars)

        # Draw the placeholder text or the menu based on the show_menu flag
        if control_vars['show_menu']:
            draw_menu(screen, menu_items, font_size=20, color=CIndex.WHITE, start_x=10, start_y=screen_height - len(menu_items) * 30 - 20)
        else:
            draw_placeholder(screen, placeholder_text)

        pygame.display.flip()

if __name__ == "__main__":
    main()

pygame.quit()
