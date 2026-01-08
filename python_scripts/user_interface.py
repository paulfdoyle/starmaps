import pygame
from utils import *
from celestial_mechanics import return_to_home

def handle_key_events(event, keys_config, control_vars):
    if event.type == pygame.QUIT:
        return False
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_c:
            control_vars['draw_constellations'] = not control_vars['draw_constellations']
        elif event.key == pygame.K_r:
            control_vars['rotate'] = not control_vars['rotate']
        elif event.key == pygame.K_LEFT:
            control_vars['current_time'] -= control_vars['time_delta']
        elif event.key == pygame.K_RIGHT:
            control_vars['current_time'] += control_vars['time_delta']
        elif event.key == pygame.K_u:
            control_vars['use_updated_positions'] = not control_vars['use_updated_positions']
            control_vars['track_axes_changes'] = not control_vars['track_axes_changes']
        elif event.key == pygame.K_f:
            reset_view(control_vars)  # Reset the view to default
        elif event.key == pygame.K_g:
            reset_shifts(control_vars)
        elif event.key == pygame.K_m:
            control_vars['show_menu'] = not control_vars['show_menu']
        elif event.key == pygame.K_o:
            control_vars['draw_orion'] = not control_vars['draw_orion']
        elif event.key == pygame.K_h:
            return_to_home(control_vars)  # Trigger the transition back to home
        elif event.key == pygame.K_SPACE:
            control_vars['paused'] = not control_vars['paused']  # Toggle the pause state
            print(f"Paused: {control_vars['paused']}")
    return True



def reset_view(control_vars):
    set_clicked_stars([])
    set_star_coordinates_clicked(None)
    control_vars['x_offset'] = 0
    control_vars['y_offset'] = 0
    control_vars['zoom_factor'] = 1.0

def reset_shifts(control_vars):
    control_vars['shift_x'] = 0
    control_vars['shift_y'] = 0
    control_vars['shift_z'] = 0

def handle_continuous_input(control_vars):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        control_vars['y_offset'] += 100
    if keys[pygame.K_s]:
        control_vars['y_offset'] -= 100
    if keys[pygame.K_a]:
        control_vars['x_offset'] += 100
    if keys[pygame.K_d]:
        control_vars['x_offset'] -= 100
    if keys[pygame.K_y]:
        control_vars['shift_y'] -= 1
    if keys[pygame.K_i]:
        control_vars['shift_y'] += 1
    if keys[pygame.K_x]:
        control_vars['shift_x'] -= 1
    if keys[pygame.K_b]:
        control_vars['shift_x'] += 1
    if keys[pygame.K_z]:
        control_vars['shift_z'] += 1
    if keys[pygame.K_v]:
        control_vars['shift_z'] -= 1
    if keys[pygame.K_PLUS] or keys[pygame.K_EQUALS]:
        control_vars['zoom_factor'] *= 1.1
    if keys[pygame.K_MINUS]:
        control_vars['zoom_factor'] /= 1.1

def draw_menu(screen, menu_items, font_size=20, color=CIndex.WHITE, start_x=10, start_y=350):
    font = pygame.font.Font(None, font_size)
    for index, item in enumerate(menu_items):
        text_surface = font.render(item, True, color)
        screen.blit(text_surface, (start_x, start_y + index * 30))
