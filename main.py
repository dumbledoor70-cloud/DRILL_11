import os
from pathlib import Path

import pico2d.pico2d as pico2d_core
from pico2d import *

from boy import Boy


class Grass:
    def __init__(self):
        self.image = load_image('grass.png')

    def draw(self):
        self.image.draw(400, 31)


def handle_events(boy):
    for event in get_events():
        if event.type == SDL_QUIT:
            return False
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            return False
        boy.handle_event(event)
    return True


def main():
    os.chdir(Path(__file__).resolve().parent)
    open_canvas(800, 600)
    # SDL may return a null renderer pointer that Pico2D's `is None` check misses.
    if not pico2d_core.renderer:
        pico2d_core.renderer = pico2d_core.SDL_CreateRenderer(
            pico2d_core.window, -1, pico2d_core.SDL_RENDERER_SOFTWARE)
    if not pico2d_core.renderer:
        raise RuntimeError('Pico2D could not create an SDL renderer')
    grass = Grass()
    boy = Boy(canvas_width=800, ground_y=56)
    running = True
    previous_time = get_time()

    try:
        while running:
            running = handle_events(boy)
            current_time = get_time()
            dt = min(current_time - previous_time, 0.05)
            previous_time = current_time

            boy.update(dt)
            clear_canvas()
            grass.draw()
            boy.draw()
            update_canvas()
            delay(0.01)
    finally:
        close_canvas()


if __name__ == '__main__':
    main()
