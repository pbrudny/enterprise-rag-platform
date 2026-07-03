"""Classification levels shared across documents, chunks, and users."""

from enum import IntEnum


class Classification(IntEnum):
    PUBLIC = 0
    INTERNAL = 1
    CONFIDENTIAL = 2
    RESTRICTED = 3
