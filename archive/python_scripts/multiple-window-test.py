import multiprocessing
from window_functions import create_and_run_window, draw_window1, draw_window2

def main():
    multiprocessing.set_start_method('spawn')

    # Create two processes for two different windows
    p1 = multiprocessing.Process(target=create_and_run_window, args=("Window 1", 400, 300, (255, 0, 0), draw_window1))
    p2 = multiprocessing.Process(target=create_and_run_window, args=("Window 2", 400, 300, (0, 255, 0), draw_window2))

    # Start the processes
    p1.start()
    p2.start()

    # Wait for the processes to complete
    p1.join()
    p2.join()

if __name__ == "__main__":
    main()

