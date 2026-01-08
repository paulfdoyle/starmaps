import pygame
import numpy as np
from datetime import datetime, timedelta
from data_handling import load_custom_star_data, extract_orion_star_pairs
from celestial_mechanics import collect_celestial_data, update_star_positions, update_celestial_projection, calculate_apparent_magnitude
from graphics import buildImageDB, draw_constellation_lines, preprocess_coordinates, twinkle_star, precalculate_star_pairs, writeText, draw_orion_constellation_lines
from user_interface import handle_key_events, handle_continuous_input, draw_menu, handle_mouse_click
from utils import *

def main():
    global shift_x, shift_y, shift_z
    global prev_shift_x, prev_shift_y, prev_shift_z
    pygame.init()
    clock = pygame.time.Clock()

    # Setup Pygame display
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Star Chart: Dublin, Ireland")

    # Create a canvas 5 times larger than the screen
    canvas = pygame.Surface((canvas_width, canvas_height), pygame.SRCALPHA)
    canvas.fill(CIndex.BLACK)

    star_data_array, eph, constellations = load_custom_star_data('../datasets/star_database_colors.json')
    star_data_np, edges_star1, edges_star2 = collect_celestial_data(star_data_array, eph, constellations, lat, long, timescale, when)
    orion_star_pairs = extract_orion_star_pairs('constellationship.fab')
    np.savetxt("../datasets/star_data_np.csv", star_data_np, delimiter=',', header=header_string, comments='', fmt='%s')

    new_star_positions_np = update_star_positions(star_data_np, shift_x, shift_y, shift_z)
    updated_star_positions_np, edges_star1, edges_star2 = update_celestial_projection(new_star_positions_np, eph, constellations, lat, long, timescale, when)
    np.savetxt("../datasets/updated_star_positions.csv", updated_star_positions_np, delimiter=',', header=header_string, comments='', fmt='%s')
    canvas_set = buildImageDB(star_data_np)

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
        'clicked_star_data': None
    }

    menu_items = [
        "Y/I: Move Y axis", "X/B: Move X axis", "Z/V: Move Z axis",
        "C: Toggle constellations", "R: Rotate", "+/-: Zoom",
        "Arrow Keys right/left: Move time forward/backward", "WASD: Pan", "U: Toggle positions to enable axis shifting",
        "M: Show/Hide this menu", "F: Reset Axis shifts"
    ]

    sirius_label = writeText("Sirius", CIndex.WHITE, FIndex.MEDIUM)
    polaris_label = writeText("Polaris", CIndex.WHITE, FIndex.MEDIUM)
    orion_label = writeText("Betelgeuse", CIndex.WHITE, FIndex.MEDIUM)
    alphaCentA = writeText("Alpha Centauri", CIndex.WHITE, FIndex.MEDIUM)
    waypoint_a_label = writeText("A", CIndex.WHITE, FIndex.MEDIUM)
    waypoint_b_label = writeText("B", CIndex.WHITE, FIndex.MEDIUM)
    waypoint_c_label = writeText("C", CIndex.WHITE, FIndex.MEDIUM)
    waypoint_d_label = writeText("D", CIndex.WHITE, FIndex.MEDIUM)
    waypoint_e_label = writeText("E", CIndex.WHITE, FIndex.MEDIUM)
    waypoint_f_label = writeText("F", CIndex.WHITE, FIndex.MEDIUM)

    print("running simulation")
    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            running = handle_key_events(event, {}, control_vars)
            handle_mouse_click(event, control_vars, updated_star_positions_np if control_vars['use_updated_positions'] else star_data_np, canvas_width, canvas_height, control_vars['zoom_factor'], control_vars['x_offset'], control_vars['y_offset'])

        handle_continuous_input(control_vars)
        shift_x, shift_y, shift_z = control_vars['shift_x'], control_vars['shift_y'], control_vars['shift_z']
        prev_shift_x, prev_shift_y, prev_shift_z = control_vars['prev_shift_x'], control_vars['prev_shift_y'], control_vars['prev_shift_z']

        if control_vars['track_axes_changes'] and (control_vars['shift_x'] != control_vars['prev_shift_x'] or control_vars['shift_y'] != control_vars['prev_shift_y'] or control_vars['shift_z'] != control_vars['prev_shift_z']):
            print(f"Axes changed to X: {shift_x}, Y: {shift_y}, Z: {shift_z}")
            if control_vars['use_updated_positions']:
                new_star_positions_np = update_star_positions(star_data_np, shift_x, shift_y, shift_z)
                updated_star_positions_np, edges_star1, edges_star2 = update_celestial_projection(new_star_positions_np, eph, constellations, lat, long, timescale, control_vars['current_time'].strftime('%Y-%m-%d %H:%M'))
                control_vars['prev_shift_x'], control_vars['prev_shift_y'], control_vars['prev_shift_z'] = control_vars['shift_x'], control_vars['shift_y'], control_vars['shift_z']

        if control_vars['rotate']:
            control_vars['current_time'] += control_vars['time_delta']

        if not control_vars['use_updated_positions']:
            star_data_np, edges_star1, edges_star2 = collect_celestial_data(star_data_array, eph, constellations, lat, long, timescale, control_vars['current_time'].strftime('%Y-%m-%d %H:%M'))
        else:
            updated_star_positions_np, edges_star1, edges_star2 = update_celestial_projection(new_star_positions_np, eph, constellations, lat, long, timescale, control_vars['current_time'].strftime('%Y-%m-%d %H:%M'))

        active_star_data = updated_star_positions_np if control_vars['use_updated_positions'] else star_data_np
        canvas.fill(CIndex.BLACK)
        index = 0
        center_x = canvas_width / 2
        center_y = canvas_height / 2
        for star in active_star_data:
            hip_id = star[SIndex.HIP]
            x, y = (star[-2], star[-1]) if control_vars['use_updated_positions'] else (star[SIndex.X], star[SIndex.Y])
            x, y = preprocess_coordinates(x, y, center_x, center_y, control_vars['zoom_factor'], control_vars['x_offset'], control_vars['y_offset'])

            newmag = calculate_apparent_magnitude(star[SIndex.ABS_MAG], star[SIndex.DISTANCE_PARSECS], hip_id)

            if 0 <= x < canvas_width and 0 <= y < canvas_height:
                mag = round(newmag) if round(newmag) <= 6 else 6
                offset = canvas_set[index][mag][0].get_width() / 2
                canvas.blit(twinkle_star(canvas_set[index][mag]), (x - offset, y - offset), special_flags=pygame.BLEND_ADD)
                if hip_id == SIRIUS_HIP:
                    canvas.blit(sirius_label, (x - offset, y - offset - 20))
                elif hip_id == POLARIS_HIP:
                    canvas.blit(polaris_label, (x - offset, y - offset - 20))
                elif hip_id == BETELGEUSE_HIP:
                    canvas.blit(orion_label, (x - offset, y - offset - 20))
                elif hip_id == APLHACENTAURI_HIP:
                    canvas.blit(alphaCentA, (x - offset, y - offset - 20))
                elif hip_id == WAYPOINT_A_HIP:
                    canvas.blit(waypoint_a_label, (x - offset, y - offset - 20))
                elif hip_id == WAYPOINT_B_HIP:
                    canvas.blit(waypoint_b_label, (x - offset, y - offset - 20))
                elif hip_id == WAYPOINT_C_HIP:
                    canvas.blit(waypoint_c_label, (x - offset, y - offset - 20))
                elif hip_id == WAYPOINT_D_HIP:
                    canvas.blit(waypoint_d_label, (x - offset, y - offset - 20))
                elif hip_id == WAYPOINT_E_HIP:
                    canvas.blit(waypoint_e_label, (x - offset, y - offset - 20))
                elif hip_id == WAYPOINT_F_HIP:
                    canvas.blit(waypoint_f_label, (x - offset, y - offset - 20))
            index += 1

        if control_vars['draw_constellations']:
            precalculated_pairs = precalculate_star_pairs(active_star_data, edges_star1, edges_star2, center_x, center_y, control_vars['zoom_factor'], control_vars['x_offset'], control_vars['y_offset'])
            canvas = draw_constellation_lines(canvas, precalculated_pairs, active_star_data)
        if control_vars['draw_orion']:
            canvas = draw_orion_constellation_lines(canvas, orion_star_pairs, active_star_data, control_vars['zoom_factor'], control_vars['x_offset'], control_vars['y_offset'])

        # Scale the canvas to fit the screen while maintaining the aspect ratio
        scaled_canvas = pygame.transform.smoothscale(canvas, (screen_width, screen_height))

        # Center the scaled canvas on the screen
        screen.fill(CIndex.BLACK)  # Clear the screen before drawing
        screen.blit(scaled_canvas, (0, 0))

        label_area_rect = pygame.Rect(950, 330, 350, 100)
        screen.fill(CIndex.BLACK, label_area_rect)

        axis_status = "Axis Shifting Enabled" if control_vars['track_axes_changes'] else "Axis Shifting Disabled"
        status_text = writeText(axis_status, (255, 255, 255), 24)
        screen.blit(status_text, (1000, 350))

        if control_vars['track_axes_changes']:
            offset_text = f"Offsets - X: {control_vars['shift_x']}, Y: {control_vars['shift_y']}, Z: {control_vars['shift_z']}"
            offsets_text = writeText(offset_text, (255, 255, 255), 24)
            screen.blit(offsets_text, (1000, 400))

        if control_vars['clicked_star_data']:
            star_info = control_vars['clicked_star_data']
            info_text = f"Star Data: HIP: {star_info[SIndex.HIP]}, Mag: {star_info[SIndex.ABS_MAG]}, Dist: {star_info[SIndex.DISTANCE_PARSECS]}"
            star_info_text = writeText(info_text, (255, 255, 255), 24)
            screen.blit(star_info_text, (50, 50))

        if control_vars['show_menu']:
            draw_menu(screen, menu_items)
        pygame.display.flip()

if __name__ == "__main__":
    main()

pygame.quit()