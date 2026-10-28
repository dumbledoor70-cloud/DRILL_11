from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDLK_a, SDLK_LEFT, SDLK_RIGHT, get_time


class IdleState:
    name = 'Idle'

    def enter(self, boy):
        boy.scale = 1.0
        boy.frame = 3

    def handle_event(self, boy, event):
        if event.type == SDL_KEYDOWN and event.key == SDLK_a:
            boy.change_state(AutoRunState())
        elif event.type == SDL_KEYDOWN and event.key in (SDLK_LEFT, SDLK_RIGHT):
            boy.change_state(RunState())

    def update(self, boy, dt):
        boy.frame = 3


class RunState:
    name = 'Run'

    def enter(self, boy):
        boy.frame = 0
        boy.scale = 1.0
        boy._face_input_direction()

    def handle_event(self, boy, event):
        if event.type == SDL_KEYDOWN and event.key in (SDLK_LEFT, SDLK_RIGHT):
            boy._face_input_direction()
        elif event.type == SDL_KEYUP and not boy.held_directions:
            boy.change_state(IdleState())

    def update(self, boy, dt):
        direction = boy.direction_from_keys()
        if direction == 0:
            boy.change_state(IdleState())
            return
        boy.facing = direction
        boy.x += direction * boy.run_speed * dt
        boy._keep_on_screen()
        boy._animate(dt)


class AutoRunState:
    name = 'AutoRun'
    duration = 5.0
    start_speed = 180.0
    end_speed = 320.0
    end_scale = 1.5

    def enter(self, boy):
        self.started_at = get_time()
        self.direction = boy.facing
        boy.frame = 0
        boy.scale = 1.0

    def handle_event(self, boy, event):
        if event.type == SDL_KEYDOWN and event.key in (SDLK_LEFT, SDLK_RIGHT):
            # Stop autoplay immediately and let the normal Run state own the key.
            boy.change_state(RunState())

    def update(self, boy, dt):
        elapsed = get_time() - self.started_at
        if elapsed >= self.duration:
            boy.change_state(IdleState())
            return

        progress = elapsed / self.duration
        speed = self.start_speed + (self.end_speed - self.start_speed) * progress
        boy.scale = 1.0 + (self.end_scale - 1.0) * progress
        boy.facing = self.direction
        boy.x += self.direction * speed * dt

        half_width = 38 * boy.scale
        if boy.x >= boy.canvas_width - half_width:
            boy.x = boy.canvas_width - half_width
            self.direction = -1
        elif boy.x <= half_width:
            boy.x = half_width
            self.direction = 1

        boy._animate(dt)


class Boy:
    def __init__(self, canvas_width=800, ground_y=62):
        from pico2d import load_image

        self.image = load_image('run_animation.png')
        self.canvas_width = canvas_width
        self.ground_y = ground_y
        self.x = canvas_width / 2
        self.y = ground_y + 50
        self.run_speed = 150.0
        self.facing = 1
        self.frame = 3
        self.scale = 1.0
        self.frame_elapsed = 0.0
        self.held_directions = set()
        self.state = None
        self.change_state(IdleState())

    def change_state(self, state):
        self.state = state
        self.state.enter(self)

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key in (SDLK_LEFT, SDLK_RIGHT):
            self.held_directions.add(event.key)
        elif event.type == SDL_KEYUP and event.key in (SDLK_LEFT, SDLK_RIGHT):
            self.held_directions.discard(event.key)
        self.state.handle_event(self, event)

    def update(self, dt):
        self.state.update(self, dt)

    def draw(self):
        source_x = self.frame * 100
        flip = '' if self.facing > 0 else 'h'
        self.image.clip_composite_draw(
            source_x, 0, 100, 100, 0, flip,
            self.x, self.y, 100 * self.scale, 100 * self.scale,
        )

    def direction_from_keys(self):
        if SDLK_RIGHT in self.held_directions:
            return 1
        if SDLK_LEFT in self.held_directions:
            return -1
        return 0

    def _face_input_direction(self):
        direction = self.direction_from_keys()
        if direction:
            self.facing = direction

    def _keep_on_screen(self):
        half_width = 38 * self.scale
        self.x = max(half_width, min(self.canvas_width - half_width, self.x))

    def _animate(self, dt):
        self.frame_elapsed += dt
        if self.frame_elapsed >= 0.08:
            self.frame = (self.frame + int(self.frame_elapsed / 0.08)) % 8
            self.frame_elapsed %= 0.08

