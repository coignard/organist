from datetime import datetime
from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Label, Static

from config import LOG_LEVEL_COLORS, MAX_CONSOLE_LINES, KEYBOARD_NAMES
from models import Stop


class ConsoleWidget(VerticalScroll):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._max_lines = MAX_CONSOLE_LINES

    def write_line(self, text: str, level: str = "INFO") -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = LOG_LEVEL_COLORS.get(level, "#888")
        escaped_text = text.replace("[", r"\[")
        line = Static(f"{timestamp} [{color}]{level:8}[/{color}] {escaped_text}")
        self.mount(line)

        children = list(self.children)
        if len(children) > self._max_lines:
            children[0].remove()

        self.scroll_end(animate=False)


class StopWidget(Static):
    is_open = reactive(False)
    tutti_active = reactive(False)
    has_active_notes = reactive(False)

    def __init__(self, stop: Stop) -> None:
        super().__init__()
        self.stop = stop
        self._active_notes: set[int] = set()

    def watch_is_open(self, is_open: bool) -> None:
        self.set_class(is_open, "open")

    def watch_tutti_active(self, tutti_active: bool) -> None:
        self.set_class(tutti_active, "tutti")

    def watch_has_active_notes(self, has_active_notes: bool) -> None:
        self.set_class(has_active_notes, "flashing")

    def render(self) -> str:
        return self.stop.name

    def add_active_note(self, note: int) -> None:
        self._active_notes.add(note)
        self.has_active_notes = len(self._active_notes) > 0

    def remove_active_note(self, note: int) -> None:
        self._active_notes.discard(note)
        self.has_active_notes = len(self._active_notes) > 0

    def clear_all_notes(self) -> None:
        self._active_notes.clear()
        self.has_active_notes = False


class ParameterWidget(Static):
    is_active = reactive(False)

    def __init__(self, name: str) -> None:
        super().__init__()
        self.param_name = name

    def watch_is_active(self, is_active: bool) -> None:
        self.set_class(is_active, "active")

    def render(self) -> str:
        status = "●" if self.is_active else "○"
        return f"{status} {self.param_name}"


class KeyboardColumn(Vertical):
    def __init__(self, keyboard_num: int, stops: list[Stop]) -> None:
        super().__init__()
        self.keyboard_num = keyboard_num
        self.stops = stops
        self._stop_widgets: dict[str, StopWidget] = {}

    def compose(self) -> ComposeResult:
        keyboard_name = KEYBOARD_NAMES.get(
            self.keyboard_num, f"Keyboard {self.keyboard_num}"
        )
        yield Label(keyboard_name)

        for stop in self.stops:
            widget = StopWidget(stop)
            self._stop_widgets[stop.name] = widget
            yield widget

    def set_stop_open(self, stop_name: str, is_open: bool) -> None:
        widget = self._stop_widgets.get(stop_name)
        if widget:
            widget.is_open = is_open
            widget.stop.is_open = is_open

    def set_tutti_active(self, active: bool) -> None:
        for widget in self._stop_widgets.values():
            widget.tutti_active = active

    def note_on(self, note: int) -> None:
        for widget in self._stop_widgets.values():
            if widget.stop.is_open or widget.tutti_active:
                widget.add_active_note(note)

    def note_off(self, note: int) -> None:
        for widget in self._stop_widgets.values():
            widget.remove_active_note(note)

    def reset_all(self) -> None:
        for widget in self._stop_widgets.values():
            widget.is_open = False
            widget.tutti_active = False
            widget.clear_all_notes()
            widget.stop.is_open = False


class ParameterSection(Vertical):
    def __init__(self, title: str, param_names: list[str]) -> None:
        super().__init__()
        self.title = title
        self.param_names = param_names
        self._widgets: dict[str, ParameterWidget] = {}

    def compose(self) -> ComposeResult:
        for name in self.param_names:
            widget = ParameterWidget(name)
            self._widgets[name] = widget
            yield widget

    def set_parameter_active(self, name: str, is_active: bool) -> None:
        widget = self._widgets.get(name)
        if widget:
            widget.is_active = is_active

    def reset_all(self) -> None:
        for widget in self._widgets.values():
            widget.is_active = False


class ParametersPanel(Vertical):
    def __init__(self) -> None:
        super().__init__()
        self._sections: dict[str, ParameterSection] = {}

    def compose(self) -> ComposeResult:
        sections_data = [
            ("Couplers", [f"Coupler {i}" for i in range(1, 7)]),
            ("Mono Couplers", [f"Mono Coupler {i}" for i in range(1, 5)]),
            ("Tremulants", [f"Tremulant {i}" for i in range(1, 5)]),
            ("Other", ["Tutti"]),
        ]

        for title, param_names in sections_data:
            section = ParameterSection(title, param_names)
            self._sections[title.lower().replace(" ", "_")] = section
            yield section

    def set_parameter_active(self, name: str, is_active: bool) -> None:
        for section in self._sections.values():
            section.set_parameter_active(name, is_active)

    def reset_all(self) -> None:
        for section in self._sections.values():
            section.reset_all()
