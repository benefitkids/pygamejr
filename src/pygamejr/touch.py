import pygame
from .base import screen, get_global_scene, _add_input_update_callback
from .key import _virtual_keys


_DIR_KEYS = {
    'up':    (pygame.K_w, pygame.K_UP),
    'down':  (pygame.K_s, pygame.K_DOWN),
    'left':  (pygame.K_a, pygame.K_LEFT),
    'right': (pygame.K_d, pygame.K_RIGHT),
}


# --- Multi-pointer dispatcher (mouse + multi-touch fingers) ---

_pointers: dict = {}     # id -> {'pos': (x,y), 'down': bool, 'just_pressed': bool, 'just_released': bool, 'owner': control or None}
_controls: list = []     # registered controls (Joystick, ActionButton, ...)
_dispatch_installed = False


def _install_dispatcher():
    global _dispatch_installed
    if _dispatch_installed:
        return
    _dispatch_installed = True
    _add_input_update_callback(_dispatch_input)


def _register_control(c) -> None:
    _install_dispatcher()
    if c not in _controls:
        _controls.append(c)


def _unregister_control(c) -> None:
    if c in _controls:
        _controls.remove(c)


def _dispatch_input(dt: float = 0) -> None:
    pygame.event.pump()

    for p in _pointers.values():
        p['just_pressed'] = False
        p['just_released'] = False

    # Mouse pointer (single, persistent slot keyed 'mouse')
    mp = pygame.mouse.get_pressed()[0]
    mpos = pygame.mouse.get_pos()
    p = _pointers.get('mouse')
    if p is None:
        p = {'pos': mpos, 'down': False, 'just_pressed': False, 'just_released': False, 'owner': None}
        _pointers['mouse'] = p
    if mp and not p['down']:
        p['just_pressed'] = True
        p['down'] = True
        p['owner'] = None
    elif not mp and p['down']:
        p['just_released'] = True
        p['down'] = False
    p['pos'] = mpos

    # Finger events (multi-touch). Consume ONLY finger event types — leave the rest for user code.
    sw, sh = screen.get_size()
    for ev in pygame.event.get([pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP]):
        fid = ('finger', ev.finger_id)
        pos = (int(ev.x * sw), int(ev.y * sh))
        if ev.type == pygame.FINGERDOWN:
            _pointers[fid] = {
                'pos': pos, 'down': True,
                'just_pressed': True, 'just_released': False, 'owner': None,
            }
        elif ev.type == pygame.FINGERMOTION:
            fp = _pointers.get(fid)
            if fp is not None:
                fp['pos'] = pos
        elif ev.type == pygame.FINGERUP:
            fp = _pointers.get(fid)
            if fp is not None:
                fp['just_released'] = True
                fp['down'] = False
                fp['pos'] = pos

    for c in _controls:
        c._process_input()

    # Drop finger pointers that are released (mouse pointer is kept for continuous state).
    for pid in list(_pointers.keys()):
        if pid == 'mouse':
            continue
        if not _pointers[pid]['down']:
            del _pointers[pid]


def _claim_pointer(control, hit_test):
    """Find an unowned pointer that just pressed inside hit_test(pos). Returns id or None."""
    for pid, p in _pointers.items():
        if p['just_pressed'] and p['owner'] is None and hit_test(p['pos']):
            p['owner'] = control
            return pid
    return None


# --- Joystick ---

class Joystick(pygame.sprite.Sprite):
    """Floating on-screen joystick. Tap re-centers it under the finger; drag activates W/A/S/D and arrow keys."""

    def __init__(
        self,
        pos: tuple[int, int] | None = None,
        base_radius: int = 70,
        stick_radius: int = 35,
        threshold: float = 0.3,
        scene=None,
    ):
        super().__init__()
        if pos is None:
            sw, sh = screen.get_size()
            pos = (base_radius + 30, sh - base_radius - 30)
        self._default_pos = pos
        self._base_pos = pos
        self._stick_pos = pos
        self._base_radius = base_radius
        self._stick_radius = stick_radius
        self._threshold = threshold
        self._active = False
        self._owned_id = None

        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.visible = 1

        (scene or get_global_scene()).add(self)
        _register_control(self)

    def _hit(self, pos):
        bx, by = self._base_pos
        dx = pos[0] - bx
        dy = pos[1] - by
        return dx * dx + dy * dy <= self._base_radius * self._base_radius

    def _process_input(self) -> None:
        if self._owned_id is not None:
            p = _pointers.get(self._owned_id)
            if p is None or not p['down']:
                self._active = False
                self._base_pos = self._default_pos
                self._stick_pos = self._default_pos
                self._owned_id = None
            else:
                bx, by = self._base_pos
                mx, my = p['pos']
                dx = mx - bx
                dy = my - by
                d2 = dx * dx + dy * dy
                r2 = self._base_radius * self._base_radius
                if d2 > r2 and d2 > 0:
                    k = (r2 / d2) ** 0.5
                    dx *= k
                    dy *= k
                self._stick_pos = (bx + dx, by + dy)
        else:
            # Capture a fresh press inside the base circle (its current screen position).
            pid = _claim_pointer(self, self._hit_default_or_current)
            if pid is not None:
                p = _pointers[pid]
                self._owned_id = pid
                self._active = True
                self._base_pos = p['pos']
                self._stick_pos = p['pos']

        self._update_virtual_keys()

    def _hit_default_or_current(self, pos):
        # When idle, the visible base sits at _default_pos; when active, at _base_pos.
        # _process_input only calls this in the idle branch so use _default_pos.
        bx, by = self._default_pos
        dx = pos[0] - bx
        dy = pos[1] - by
        return dx * dx + dy * dy <= self._base_radius * self._base_radius

    def update(self, dt: float = 0) -> None:
        pass

    def _update_virtual_keys(self):
        for keys in _DIR_KEYS.values():
            for k in keys:
                _virtual_keys.discard(k)
        if not self._active:
            return
        bx, by = self._base_pos
        sx, sy = self._stick_pos
        nx = (sx - bx) / self._base_radius
        ny = (sy - by) / self._base_radius
        if nx > self._threshold:
            _virtual_keys.update(_DIR_KEYS['right'])
        elif nx < -self._threshold:
            _virtual_keys.update(_DIR_KEYS['left'])
        if ny > self._threshold:
            _virtual_keys.update(_DIR_KEYS['down'])
        elif ny < -self._threshold:
            _virtual_keys.update(_DIR_KEYS['up'])

    def draw(self, draw_rect: bool = False) -> None:
        if not self.visible:
            return
        d = self._base_radius * 2
        s = pygame.Surface((d, d), pygame.SRCALPHA)
        pygame.draw.circle(s, (200, 200, 200, 90), (self._base_radius, self._base_radius), self._base_radius)
        pygame.draw.circle(s, (255, 255, 255, 180), (self._base_radius, self._base_radius), self._base_radius, 3)
        screen.blit(s, (self._base_pos[0] - self._base_radius, self._base_pos[1] - self._base_radius))

        sd = self._stick_radius * 2
        st = pygame.Surface((sd, sd), pygame.SRCALPHA)
        pygame.draw.circle(st, (255, 255, 255, 220), (self._stick_radius, self._stick_radius), self._stick_radius)
        screen.blit(st, (self._stick_pos[0] - self._stick_radius, self._stick_pos[1] - self._stick_radius))


def show_joystick(**kwargs) -> Joystick:
    """Add a floating on-screen joystick to the global scene. Returns the Joystick instance."""
    return Joystick(**kwargs)


# --- Action button ---

class ActionButton(pygame.sprite.Sprite):
    """On-screen action button. Maps tap (one frame) or hold (while held) to a virtual key press."""

    _auto_index = 0

    def __init__(
        self,
        key: int,
        label: str = "",
        mode: str = 'tap',
        pos: tuple[int, int] | None = None,
        radius: int = 45,
        scene=None,
    ):
        super().__init__()
        if mode not in ('tap', 'hold'):
            raise ValueError(f"mode must be 'tap' or 'hold', got {mode!r}")
        self._key = key
        self._label = label
        self._mode = mode
        self._radius = radius
        if pos is None:
            sw, sh = screen.get_size()
            pos = (
                sw - radius - 30,
                sh - radius - 30 - ActionButton._auto_index * (radius * 2 + 20),
            )
            ActionButton._auto_index += 1
        self._pos = pos
        self._owned_id = None
        self._tap_pending = False
        self._pressed_visual = False

        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.visible = 1

        if not pygame.font.get_init():
            pygame.font.init()
        self._font = pygame.font.SysFont(None, int(radius * 1.1))
        self._label_surf = self._font.render(label, True, (255, 255, 255)) if label else None

        (scene or get_global_scene()).add(self)
        _register_control(self)

    def _hit(self, pos):
        dx = pos[0] - self._pos[0]
        dy = pos[1] - self._pos[1]
        return dx * dx + dy * dy <= self._radius * self._radius

    def _process_input(self) -> None:
        if self._mode == 'tap' and self._tap_pending:
            _virtual_keys.discard(self._key)
            self._tap_pending = False

        if self._owned_id is not None:
            p = _pointers.get(self._owned_id)
            if p is None or not p['down']:
                if self._mode == 'hold':
                    _virtual_keys.discard(self._key)
                self._owned_id = None
                self._pressed_visual = False
        else:
            pid = _claim_pointer(self, self._hit)
            if pid is not None:
                self._owned_id = pid
                self._pressed_visual = True
                if self._mode == 'tap':
                    _virtual_keys.add(self._key)
                    self._tap_pending = True
                else:
                    _virtual_keys.add(self._key)

    def update(self, dt: float = 0) -> None:
        pass

    def draw(self, draw_rect: bool = False) -> None:
        if not self.visible:
            return
        d = self._radius * 2
        s = pygame.Surface((d, d), pygame.SRCALPHA)
        fill = (255, 200, 100, 200) if self._pressed_visual else (200, 200, 200, 100)
        pygame.draw.circle(s, fill, (self._radius, self._radius), self._radius)
        pygame.draw.circle(s, (255, 255, 255, 200), (self._radius, self._radius), self._radius, 3)
        screen.blit(s, (self._pos[0] - self._radius, self._pos[1] - self._radius))
        if self._label_surf is not None:
            lr = self._label_surf.get_rect(center=self._pos)
            screen.blit(self._label_surf, lr)


def show_action_button(key: int, label: str = "", **kwargs) -> ActionButton:
    """Add an on-screen action button to the global scene. Returns the ActionButton instance."""
    return ActionButton(key=key, label=label, **kwargs)
