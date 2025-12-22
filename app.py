from typing import Optional
import re

import mido
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Footer, Header
from textual.worker import Worker
from textual import work

from midi_handler import MidiMessageHandler
from models import Stop, StopRegistry
from organteq_client import OrganteqClient
from widgets import ConsoleWidget, KeyboardColumn, ParametersPanel


class OrganistApp(App):
    CSS = """
    * {
        scrollbar-background: #121212;
        scrollbar-color: #333;
    }

    Screen {
        background: #121212;
    }

    Header {
        background: #1a1a1a;
    }

    Footer {
        background: #121212;
    }

    #main-container {
        height: 1fr;
    }

    #console {
        height: 8;
        border-top: solid #333;
        padding: 0 1;
        background: #121212;
        color: #888;
    }

    ConsoleWidget {
        background: #121212;
    }

    ConsoleWidget > Static {
        background: #121212;
        color: #888;
        height: auto;
    }

    KeyboardColumn {
        width: 1fr;
        height: 100%;
        border: solid #333;
        padding: 1 2;
        background: #121212;
    }

    KeyboardColumn Label {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    ParametersPanel {
        width: 1fr;
        height: 100%;
        border: solid #333;
        padding: 0;
        background: #121212;
    }

    ParameterSection {
        border-bottom: solid #333;
        padding: 1 2;
    }

    ParameterSection:last-child {
        border-bottom: none;
    }

    StopWidget {
        height: 1;
        color: #666;
    }

    StopWidget.open {
        color: #00ff00;
    }

    StopWidget.tutti {
        color: #006600;
    }

    StopWidget.open.tutti {
        color: #00ff00;
    }

    StopWidget.flashing {
        color: #ffffff;
    }

    StopWidget.tutti.flashing {
        color: #909090;
    }

    StopWidget.open.tutti.flashing {
        color: white;
    }

    ParameterWidget {
        height: 1;
        color: #666;
    }

    ParameterWidget.active {
        color: #00aaff;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "reset", "Reset"),
        ("s", "sync", "Sync State"),
    ]

    def __init__(
        self, midi_port: str, client: OrganteqClient, stop_registry: StopRegistry
    ) -> None:
        super().__init__()
        self._midi_port = midi_port
        self._client = client
        self._stop_registry = stop_registry
        self._columns: dict[int, KeyboardColumn] = {}
        self._parameters_panel: Optional[ParametersPanel] = None
        self._console: Optional[ConsoleWidget] = None
        self._midi_worker: Optional[Worker] = None
        self._midi_handler = MidiMessageHandler(
            registry=stop_registry,
            on_stop_toggle=self._handle_stop_toggle,
            on_note_event=self._handle_note_event,
            on_parameter_set=self._handle_parameter_set,
            on_parameter_ui_update=self._handle_parameter_ui_update,
            on_tutti_changed=self._handle_tutti_changed,
            on_sync_state=self._handle_sync_state,
            on_reset=self._handle_reset,
            on_warning=self._handle_warning,
            on_info=self._handle_info,
        )

    def compose(self) -> ComposeResult:
        yield Header()

        with Container(id="main-container"):
            with Horizontal():
                parameters_panel = ParametersPanel()
                self._parameters_panel = parameters_panel
                yield parameters_panel

                for keyboard_num in [1, 2, 3, 4]:
                    stops = self._stop_registry.get_stops_by_keyboard(keyboard_num)
                    column = KeyboardColumn(keyboard_num, stops)
                    self._columns[keyboard_num] = column
                    yield column

        console = ConsoleWidget(id="console")
        self._console = console
        yield console

        yield Footer()

    def on_mount(self) -> None:
        self.title = "Organist"
        self.sub_title = f"{self._midi_port}"
        self._write_console(f"Connected to {self._midi_port}")
        self._write_console(f"Loaded {len(self._stop_registry)} stops from Organteq")
        self._start_midi_listener()

    def on_unmount(self) -> None:
        if self._midi_worker and not self._midi_worker.is_finished:
            self._midi_worker.cancel()

    def action_reset(self) -> None:
        for column in self._columns.values():
            column.reset_all()
        if self._parameters_panel:
            self._parameters_panel.reset_all()
        self._write_console("Reset all display")

    def action_sync(self) -> None:
        self._sync_state_from_organteq()

    @work(exclusive=True, thread=True)
    def _start_midi_listener(self) -> None:
        try:
            with mido.open_input(self._midi_port) as input_port:
                for message in input_port:
                    if not self.is_running:
                        break
                    self._midi_handler.process_message(message)
        except OSError:
            self.call_from_thread(
                self._write_console, "MIDI connection lost", "ERROR"
            )

    def _write_console(self, message: str, level: str = "INFO") -> None:
        if self._console:
            self._console.write_line(message, level)

    def _handle_warning(self, message: str) -> None:
        self.call_from_thread(self._write_console, message, "WARNING")

    def _handle_info(self, message: str) -> None:
        self.call_from_thread(self._write_console, message, "INFO")

    def _handle_reset(self) -> None:
        self.call_from_thread(self.action_reset)

    def _handle_sync_state(self) -> None:
        self.call_from_thread(self._sync_state_from_organteq)

    def _sync_state_from_organteq(self) -> None:
        parameters = self._client.get_all_parameters()
        if not parameters:
            self._write_console("Failed to sync state from Organteq", "WARNING")
            return

        stop_pattern = re.compile(r"Stop\[(\d+)\]\[(\d+)\]\.Switch")
        coupler_pattern = re.compile(r"Coupler Switch\[(\d+)\]")
        mono_coupler_pattern = re.compile(r"Mono Coupler Switch\[(\d+)\]")
        tremulant_pattern = re.compile(r"Tremulant Switch\[(\d+)\]")

        synced_stops = 0
        synced_params = 0
        tutti_active = False

        for param in parameters:
            param_id = param.get("id", "")
            is_active = param.get("normalized_value", 0.0) > 0.5

            if param_id == "Tutti":
                tutti_active = is_active
                if self._parameters_panel:
                    self._parameters_panel.set_parameter_active("Tutti", is_active)
                    synced_params += 1
                continue

            stop_match = stop_pattern.match(param_id)
            if stop_match:
                keyboard = int(stop_match.group(1))
                position = int(stop_match.group(2))

                stops = self._stop_registry.get_stops_by_keyboard(keyboard)
                for stop in stops:
                    if stop.position == position:
                        column = self._columns.get(keyboard)
                        if column:
                            column.set_stop_open(stop.name, is_active)
                            stop.is_open = is_active
                            synced_stops += 1
                        break
                continue

            coupler_match = coupler_pattern.match(param_id)
            if coupler_match and self._parameters_panel:
                num = int(coupler_match.group(1))
                name = f"Coupler {num}"
                self._parameters_panel.set_parameter_active(name, is_active)
                synced_params += 1
                continue

            mono_coupler_match = mono_coupler_pattern.match(param_id)
            if mono_coupler_match and self._parameters_panel:
                num = int(mono_coupler_match.group(1))
                name = f"Mono Coupler {num}"
                self._parameters_panel.set_parameter_active(name, is_active)
                synced_params += 1
                continue

            tremulant_match = tremulant_pattern.match(param_id)
            if tremulant_match and self._parameters_panel:
                num = int(tremulant_match.group(1))
                name = f"Tremulant {num}"
                self._parameters_panel.set_parameter_active(name, is_active)
                synced_params += 1
                continue

        for column in self._columns.values():
            column.set_tutti_active(tutti_active)

        self._write_console(f"Synced {synced_stops} stops, {synced_params} parameters")

    def _handle_stop_toggle(self, stop: Stop, is_open: bool) -> None:
        normalized_value = 1.0 if is_open else 0.0
        self._client.set_parameter(stop.parameter_id, normalized_value)

        column = self._columns.get(stop.keyboard)
        if column:
            self.call_from_thread(column.set_stop_open, stop.name, is_open)

    def _handle_parameter_set(self, parameter_id: str, normalized_value: float) -> None:
        self._client.set_parameter(parameter_id, normalized_value)

    def _handle_parameter_ui_update(self, name: str, is_active: bool) -> None:
        if self._parameters_panel:
            self.call_from_thread(self._parameters_panel.set_parameter_active, name, is_active)

    def _handle_tutti_changed(self, is_active: bool) -> None:
        for column in self._columns.values():
            self.call_from_thread(column.set_tutti_active, is_active)

    def _handle_note_event(self, keyboard: int, note: int, is_on: bool) -> None:
        column = self._columns.get(keyboard)
        if column:
            if is_on:
                self.call_from_thread(column.note_on, note)
            else:
                self.call_from_thread(column.note_off, note)
