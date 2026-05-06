import pygame

_virtual_keys: set[int] = set()


class _PressedWithVirtual:
    __slots__ = ('_real',)

    def __init__(self, real):
        self._real = real

    def __getitem__(self, key):
        return bool(self._real[key]) or (key in _virtual_keys)

    def __iter__(self):
        return iter(self._real)

    def __len__(self):
        return len(self._real)


def get_pressed():
    """Like pygame.key.get_pressed() but also reflects virtual keys from on-screen controls."""
    real = pygame.key.get_pressed()
    if not _virtual_keys:
        return real
    return _PressedWithVirtual(real)
