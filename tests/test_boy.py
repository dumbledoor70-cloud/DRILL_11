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
