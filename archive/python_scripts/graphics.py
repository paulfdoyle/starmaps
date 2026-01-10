import pygame
import pygame.gfxdraw
import numpy as np
import random
import math
from utils import *
from celestial_mechanics import calculate_apparent_magnitude

# Global variables
star_coordinates = {}  # Dictionary to store star coordinates
clicked_star_hip = None  # Variable to store the HIP ID of the clicked star
clicked_stars = []  # Global variable to store the list of clicked stars


def twinkle_star(elements):
    """
    Randomly choose one of the surface elements to simulate the twinkle effect of stars.

    Args:
    - elements (list): List of pygame.Surface objects representing different brightness variants.

    Returns:
    - pygame.Surface: Randomly selected surface from the elements.
    """
    if not elements:  # Check if the list is empty
        return None   # Or raise an exception, depending on how you want to handle this case
    return random.choice(elements)

def star_mag_size_scaling(canvas, placeholder=None):

# Create a 2D array of canvas. Rows are different sizes, cols are different brightness
    """
    starcanvas [MAG0 Size][Brighness] [Brighness] [Brighness]
    starcanvas [MAG1 Size][Brighness] [Brighness] [Brighness]
    starcanvas [MAG2 Size][Brighness] [Brighness] [Brighness]
    starcanvas [MAG3 Size][Brighness] [Brighness] [Brighness]

    """
    MAG_RANGE = 7  # 0 to 6

    rows, cols = MAG_RANGE, len(canvas)
    canvas2D = [[None for _ in range(cols)] for _ in range(rows)]        

    for x in range(rows):
        for y in range(cols):
            scaling_factor = BF ** (6 - x) if x < 6 else 1
            radius = int(BRM6 * math.sqrt(scaling_factor))
            canvas2D[x][y] = pygame.transform.smoothscale(canvas[y], (radius, radius))
               
    return canvas2D  

def precalculate_star_pairs(star_data_np, edges_star1, edges_star2, center_x, center_y, zoom_factor, x_offset, y_offset):
    precalculated_pairs = []
    for s1, s2 in zip(edges_star1, edges_star2):
        # Find indices in star_data_np where HIP matches s1 or s2
        indices1 = np.where(star_data_np[:, SIndex.HIP] == s1)[0]
        indices2 = np.where(star_data_np[:, SIndex.HIP] == s2)[0]

        # Check if both stars are found in the dataset
        if indices1.size > 0 and indices2.size > 0:
            index1 = indices1[0]
            index2 = indices2[0]

            # Extract X, Y coordinates for both stars
            x1, y1 = star_data_np[index1, SIndex.X], star_data_np[index1, SIndex.Y]
            x2, y2 = star_data_np[index2, SIndex.X], star_data_np[index2, SIndex.Y]

            # Adjust coordinates based on the provided parameters
            x1, y1 = preprocess_coordinates(x1, y1, center_x, center_y, zoom_factor, x_offset, y_offset)
            x2, y2 = preprocess_coordinates(x2, y2, center_x, center_y, zoom_factor, x_offset, y_offset)

            # Add the adjusted coordinates to the list of precalculated pairs
            precalculated_pairs.append(((x1, y1), (x2, y2)))

    return precalculated_pairs

def preprocess_coordinates(x, y, center_x, center_y, zoom_factor, x_offset, y_offset):
    # Apply translation and zoom to the star coordinates
    translated_x = (x + 1) * center_x - center_x
    translated_y = (y + 1) * center_y - center_y
    # Apply zoom
    zoomed_x = (translated_x + x_offset) * zoom_factor
    zoomed_y = (translated_y + y_offset) * zoom_factor
    # Translate back with offset
    final_x = center_x + zoomed_x
    final_y = center_y + zoomed_y
    return final_x, final_y

# This function takes the color for a star as a parameter in the form of a tuple (255, 255, 255)
# It draws the star on a single Pygame surface 100 pixels wide and returns a pointer to the star surface.
# The star can be scaled by another function to match different magnitudes
#
# The function draws a series of filled circles starting from the largest to the smallest
# The outer part of the star contains the color of the star, while the center is white
# There are 3 distinct areas drawn, the outer section, the middle and the inner section
# The middle and outer sections modify the circle color to be more faint the larger the radius


def draw_star_surfaces__(color):
    RADIUS = 100
    TR = 0         # The twinkle level, this is used to change the color of each image very slightly
    radius_half = RADIUS // 2
    radius_quarter = RADIUS // 4
    star_surface = []  # Surface to draw on using a constant radius value
    mix_ratios1 = [(i - radius_quarter) / radius_quarter for i in range(radius_quarter, radius_half)]
    mix_ratios2 = [(i - radius_half) / radius_half for i in range(radius_half, RADIUS)]

    surface = pygame.Surface((RADIUS * 2, RADIUS * 2), pygame.SRCALPHA)
    star_surface.append(surface)
    for i in range(RADIUS, 0, -1):
        if i < radius_quarter:
            gradient_color = (255-(TR), 255-(TR), 255-(TR))
        elif i in range(radius_quarter, radius_half):
            mix_ratio = mix_ratios1[i - radius_quarter]
            gradient_color = [int(255-(TR) + (color_component - 255) * mix_ratio) for color_component in color]
        else:
            mix_index = max(0, min(len(mix_ratios2) - 1, i - radius_half))
            mix_ratio = mix_ratios2[mix_index]
            gradient_color = [int(color_component * (1 - mix_ratio)-(TR)) for color_component in color]

        gradient_color = tuple(max(0, min(255, c)) for c in gradient_color)  # Keep in range of 0-255
        pygame.gfxdraw.filled_circle(star_surface[0], RADIUS, RADIUS, i, gradient_color)  # Draw the circle
    return star_surface


def draw_star_surfaces(color):
    RADIUS = 100
    NUMIMAGES = 4  # The number of images to create, the more images, the more variants in the images
    TR = 10         # The twinkle level, this is used to change the color of each image very slightly
    star_surface = []  # Surface to draw on using a constant radius value
    radius_half = RADIUS // 2
    radius_quarter = RADIUS // 4
    star_surface = []  # Surface to draw on using a constant radius value
    mix_ratios1 = [(i - radius_quarter) / radius_quarter for i in range(radius_quarter, radius_half)]
    mix_ratios2 = [(i - radius_half) / radius_half for i in range(radius_half, RADIUS)]

    # i starts at RADIUS and is reduced as the loop progresses.
    for j in range(NUMIMAGES):
        star_surface.append(pygame.Surface((RADIUS*2, RADIUS*2), pygame.SRCALPHA))
        for i in range(RADIUS, 0, -1):
            if i < radius_quarter:
                gradient_color = (255-(j*TR), 255-(j*TR), 255-(j*TR))
            elif i < radius_half:
                mix_ratio = mix_ratios1[i - radius_quarter]
                gradient_color = [int(255-(j*TR) + (color_component - 255) * mix_ratio) for color_component in color]
            else:
                mix_index = max(0, min(len(mix_ratios2) - 1, i - radius_half))
                mix_ratio = mix_ratios2[mix_index]
                gradient_color = [int(color_component * (1 - mix_ratio)-(j*TR)) for color_component in color]

            gradient_color = tuple(max(0, min(255, c)) for c in gradient_color)  # Keep in range of 0-255
            pygame.gfxdraw.filled_circle(star_surface[j], RADIUS, RADIUS, i, gradient_color)  # Draw the circle

    return star_surface

def buildStarImageDB():
    canvas_set = []  # Empty list to store surfaces
    for star_rgb in star_list:
        canvas_set.append(star_mag_size_scaling(draw_star_surfaces(star_rgb)))
    print("Created new star DB")
    return canvas_set

def draw_constellation_lines(canvas, precalculated_pairs, active_star_data):
    for (x1, y1), (x2, y2) in precalculated_pairs:
        # Perform a visibility check for both stars forming the constellation line
        star1_visible = 0 <= x1 < canvas_width and 0 <= y1 < canvas_height
        star2_visible = 0 <= x2 < canvas_width and 0 <= y2 < canvas_height

        # Draw the line only if both stars are visible on the canvas
        if star1_visible and star2_visible:
            pygame.draw.line(canvas, (255, 255, 255), (x1, y1), (x2, y2), 3)
    return canvas

def draw_orion_constellation_lines(canvas, orion_pairs, active_star_data, zoom_factor, x_offset, y_offset):
    center_x = canvas_width / 2
    center_y = canvas_height / 2
    for star1, star2 in orion_pairs:
        # Find indices in star_data_np where HIP matches star1 or star2
        indices1 = np.where(active_star_data[:, SIndex.HIP] == int(star1))[0]
        indices2 = np.where(active_star_data[:, SIndex.HIP] == int(star2))[0]

        # Check if both stars are found in the dataset
        if indices1.size > 0 and indices2.size > 0:
            index1 = indices1[0]
            index2 = indices2[0]

            # Extract X, Y coordinates for both stars
            x1, y1 = active_star_data[index1, SIndex.X], active_star_data[index1, SIndex.Y]
            x2, y2 = active_star_data[index2, SIndex.X], active_star_data[index2, SIndex.Y]

            # Adjust coordinates based on the provided parameters
            x1, y1 = preprocess_coordinates(x1, y1, center_x, center_y, zoom_factor, x_offset, y_offset)
            x2, y2 = preprocess_coordinates(x2, y2, center_x, center_y, zoom_factor, x_offset, y_offset)

            # Draw the line
            pygame.draw.line(canvas, (255, 255, 255), (x1, y1), (x2, y2), 3)
    return canvas

def writeText(text, color, fontsize):
    font = pygame.font.Font(None, fontsize)
    return font.render(text, True, color)

def draw_clicked_star_hip(screen, clicked_stars, control_vars):
    star_coordinates_clicked = None
    clicked_stars = get_clicked_stars()

    if clicked_stars:
        # Display the main clicked star
        main_hip, main_distance = clicked_stars[0]
        main_hip_text = writeText(f"Main star clicked: HIP ID: {main_hip}", CIndex.WHITE, 20)
        screen.blit(main_hip_text, (10, 10))
        # Display other stars in close vicinity
        if len(clicked_stars) > 1:
            vicinity_text = writeText("Other stars in close vicinity:", CIndex.WHITE, 20)
            screen.blit(vicinity_text, (10, 40))
            for i, (hip, distance) in enumerate(clicked_stars[1:], start=1):
                hip_text = writeText(f"HIP ID: {hip}", CIndex.WHITE, 20)
                screen.blit(hip_text, (10, 40 + i * 30))  # Display each HIP ID on a new line

        # Get the coordinates of the clicked star
        if(get_star_coordinates_clicked() is None):
            print("set coordinate")
            for (x, y), hip in star_coordinates.items():
                if hip == main_hip:
                    coordinates_text = writeText(f"Coordinates: ({x:.2f}, {y:.2f})", CIndex.WHITE, 20)
                    screen.blit(coordinates_text, (10, 100))
                    set_star_coordinates_clicked((x, y))
                    break

def draw_status(screen, control_vars):
    # Get the current screen width and height
    screen_width, screen_height = get_size_screen()

    # Set the font size for the status label
    font_size = 24

    # Render the status text
    axis_status = "Axis Shifting Enabled" if control_vars['track_axes_changes'] else "Axis Shifting Disabled"
    status_text = writeText(axis_status, CIndex.WHITE, font_size)

    # Calculate the position to place the text at the top-right corner
    text_width, text_height = status_text.get_size()
    position_x = screen_width - text_width - 75  # 75 pixels padding from the right edge
    position_y = 10  # 10 pixels padding from the top edge

    # Blit the status text onto the screen at the calculated position
    screen.blit(status_text, (position_x, position_y))

    # If axis shifting is enabled, show the current offsets below the status
    if control_vars['track_axes_changes']:
        # Format the offsets to 2 decimal places
        offset_text = f"Offsets - X: {control_vars['shift_x']:.2f}, Y: {control_vars['shift_y']:.2f}, Z: {control_vars['shift_z']:.2f}"
        offsets_text = writeText(offset_text, CIndex.WHITE, font_size)

        # Calculate the position for the offsets text below the axis status
        offset_position_y = position_y + text_height + 5  # 5 pixels padding below the axis status
        screen.blit(offsets_text, (position_x, offset_position_y))


def draw_fps(screen, clock):
    # Set the font size for the FPS counter
    font_size = 36

    # Render the FPS text
    fps_text = writeText(f"FPS: {int(clock.get_fps())}", CIndex.WHITE, font_size)

    # Get the current screen width and height
    screen_width, _ = get_size_screen()

    # Calculate the position to center the FPS text at the top
    text_width, _ = fps_text.get_size()
    position_x = (screen_width - text_width) // 2  # Center horizontally
    position_y = 10  # 10 pixels padding from the top edge

    # Blit the FPS text onto the screen at the calculated position
    screen.blit(fps_text, (position_x, position_y))

def draw_menu(screen, menu_items, font_size=20, color=CIndex.WHITE, start_x=10, start_y=None):
    if start_y is None:
        _, screen_height = get_size_screen()
        start_y = screen_height - len(menu_items) * 30 - 20

    font = pygame.font.Font(None, font_size)
    for index, item in enumerate(menu_items):
        text_surface = font.render(item, True, color)
        screen.blit(text_surface, (start_x, start_y + index * 30))

def draw_placeholder(screen, placeholder_text):
    font_size = 20
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(placeholder_text, True, CIndex.WHITE)

    # Position it at the bottom-left corner
    _, screen_height = get_size_screen()
    position_x = 10  # 10 pixels padding from the left edge
    position_y = screen_height - 30  # 30 pixels padding from the bottom edge

    screen.blit(text_surface, (position_x, position_y))
