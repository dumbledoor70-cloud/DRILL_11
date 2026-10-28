import types
import unittest
from unittest.mock import patch

import boy
from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDLK_a, SDLK_LEFT, SDLK_RIGHT


class FakeImage:
    def __init__(self):
        self.last_draw = None

    def clip_composite_draw(self, *args):
        self.last_draw = args


class BoyTestCase(unittest.TestCase):
    def setUp(self):
        self.now = [100.0]
        self.image = FakeImage()
        self.loader = patch('pico2d.load_image', return_value=self.image)
        self.clock = patch('boy.get_time', side_effect=lambda: self.now[0])
        self.loader.start()
        self.clock.start()
        self.addCleanup(self.loader.stop)
        self.addCleanup(self.clock.stop)
        self.boy = boy.Boy()

    @staticmethod
    def event(event_type, key):
        return types.SimpleNamespace(type=event_type, key=key)


class IdleAndRunTests(BoyTestCase):
    def test_starts_idle_and_a_starts_autorun(self):
        self.assertEqual(self.boy.state.name, 'Idle')
        self.boy.handle_event(self.event(SDL_KEYDOWN, SDLK_a))
        self.assertEqual(self.boy.state.name, 'AutoRun')

    def test_direction_key_runs_and_release_returns_to_idle(self):
        self.boy.handle_event(self.event(SDL_KEYDOWN, SDLK_LEFT))
        self.assertEqual(self.boy.state.name, 'Run')
        start_x = self.boy.x
        self.boy.update(0.1)
        self.assertLess(self.boy.x, start_x)
        self.boy.handle_event(self.event(SDL_KEYUP, SDLK_LEFT))
        self.assertEqual(self.boy.state.name, 'Idle')

    def test_a_does_not_start_autorun_from_run(self):
        self.boy.handle_event(self.event(SDL_KEYDOWN, SDLK_RIGHT))
        self.boy.handle_event(self.event(SDL_KEYDOWN, SDLK_a))
        self.assertEqual(self.boy.state.name, 'Run')

class AutoRunTimingTests(BoyTestCase):
    def test_auto_run_expires_after_five_seconds_and_resets_scale(self):
        self.boy.handle_event(self.event(SDL_KEYDOWN, SDLK_a))
        self.now[0] = 104.9
        self.boy.update(0.01)
        self.assertEqual(self.boy.state.name, 'AutoRun')
        self.now[0] = 105.0
        self.boy.update(0.01)
        self.assertEqual(self.boy.state.name, 'Idle')
        self.assertEqual(self.boy.scale, 1.0)

class AutoRunGrowthTests(BoyTestCase):
    def test_speed_and_scale_grow_during_auto_run(self):
        self.boy.handle_event(self.event(SDL_KEYDOWN, SDLK_a))
        start_x = self.boy.x
        self.now[0] = 102.5
        self.boy.update(0.1)
        self.assertAlmostEqual(self.boy.scale, 1.25)
        self.assertAlmostEqual(self.boy.x - start_x, 25.0)

class AutoRunBoundaryTests(BoyTestCase):
    def test_right_edge_reverses_auto_run_direction(self):
        self.boy.handle_event(self.event(SDL_KEYDOWN, SDLK_a))
        self.boy.x = 755
        self.now[0] = 101.0
        self.boy.update(0.1)
        self.assertEqual(self.boy.state.direction, -1)
        self.assertLessEqual(self.boy.x + 38 * self.boy.scale, 800.01)

    def test_left_edge_reverses_auto_run_direction(self):
        self.boy.facing = -1
        self.boy.handle_event(self.event(SDL_KEYDOWN, SDLK_a))
        self.boy.x = 45
        self.now[0] = 101.0
        self.boy.update(0.1)
        self.assertEqual(self.boy.state.direction, 1)
        self.assertGreaterEqual(self.boy.x - 38 * self.boy.scale, -0.01)

class AutoRunInputTests(BoyTestCase):
    def test_direction_key_cancels_auto_run_into_normal_size_run(self):
        self.boy.handle_event(self.event(SDL_KEYDOWN, SDLK_a))
        self.now[0] = 102.5
        self.boy.update(0.01)
        self.assertGreater(self.boy.scale, 1.0)
        self.boy.handle_event(self.event(SDL_KEYDOWN, SDLK_LEFT))
        self.assertEqual(self.boy.state.name, 'Run')
        self.assertEqual(self.boy.scale, 1.0)
        start_x = self.boy.x
        self.boy.update(0.1)
        self.assertLess(self.boy.x, start_x)

    def test_each_auto_run_activation_gets_a_fresh_five_second_timer(self):
        self.boy.handle_event(self.event(SDL_KEYDOWN, SDLK_a))
        self.now[0] = 105.0
        self.boy.update(0.01)
        self.assertEqual(self.boy.state.name, 'Idle')
        self.now[0] = 106.0
        self.boy.handle_event(self.event(SDL_KEYDOWN, SDLK_a))
        self.now[0] = 110.9
        self.boy.update(0.01)
        self.assertEqual(self.boy.state.name, 'AutoRun')
        self.now[0] = 111.0
        self.boy.update(0.01)
        self.assertEqual(self.boy.state.name, 'Idle')

    def test_normal_run_stays_inside_canvas(self):
        self.boy.x = 790
        self.boy.handle_event(self.event(SDL_KEYDOWN, SDLK_RIGHT))
        self.boy.update(1.0)
        self.assertLessEqual(self.boy.x + 38 * self.boy.scale, 800)

class RenderingBehaviorTests(BoyTestCase):
    def test_run_animation_advances_on_elapsed_frame_time(self):
        self.boy.handle_event(self.event(SDL_KEYDOWN, SDLK_RIGHT))
        self.assertEqual(self.boy.frame, 0)
        self.boy.update(0.09)
        self.assertEqual(self.boy.frame, 1)

    def test_running_left_flips_sprite_horizontally(self):
        self.boy.handle_event(self.event(SDL_KEYDOWN, SDLK_LEFT))
        self.boy.draw()
        self.assertEqual(self.image.last_draw[5], 'h')
