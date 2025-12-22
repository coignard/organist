from dataclasses import dataclass
from typing import Optional


@dataclass
class Stop:
    name: str
    keyboard: int
    position: int
    is_open: bool = False

    @property
    def parameter_id(self) -> str:
        return f"Stop[{self.keyboard}][{self.position}].Switch"


class StopRegistry:
    def __init__(self) -> None:
        self._stops: dict[tuple[int, str], Stop] = {}

    def add_stop(self, stop: Stop) -> None:
        key = (stop.keyboard, stop.name.lower())
        self._stops[key] = stop

    def find_stop(self, stop_name: str, keyboard: int) -> Optional[Stop]:
        stop_name_lower = stop_name.lower()
        for (kbd, name), stop in self._stops.items():
            if kbd == keyboard and stop_name_lower in name:
                return stop
        return None

    def get_stops_by_keyboard(self, keyboard: int) -> list[Stop]:
        return [
            stop
            for (kbd, _), stop in self._stops.items()
            if kbd == keyboard
        ]

    def __len__(self) -> int:
        return len(self._stops)
