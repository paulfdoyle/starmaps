import pyglet
from pyglet.gl import *
from pyglet import shapes
from line_profiler import profile

@profile
def main():
    screen = pyglet.canvas.get_display().get_default_screen()
    window = pyglet.window.Window(screen.width, screen.height)
    # window = pyglet.window.Window(800, 600)

    # Create a batch to draw the circles
    batch = pyglet.graphics.Batch()

    # Define the radius and spacing of the circles
    radius = 10
    spacing = 5

    # Calculate the total width of a single row of circles
    circle_diameter = 2 * radius
    total_circle_width = circle_diameter + spacing

    # Calculate the number of circles per row and the number of rows needed
    circles_per_row = screen.width // total_circle_width
    rows_needed = 9003 // circles_per_row + 1

    # Create the circles
    circles = []
    for row in range(rows_needed):
        for col in range(circles_per_row):
            x = col * total_circle_width + radius
            y = screen.height - (row * total_circle_width + radius)
            if len(circles) < 9003:
                circle = shapes.Circle(x, y, radius, color=(255, 255, 255), batch=batch)
                circles.append(circle)

    @window.event
    @profile
    def on_draw():
        window.clear()
        batch.draw()  # Draw the circles

    pyglet.app.run()



if __name__ == "__main__":
    main()

