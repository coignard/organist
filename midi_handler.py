from typing import Callable, Protocol

from config import (
    CC_TO_STOP_NAME,
    CC_TO_COUPLER,
    CC_TO_MONO_COUPLER,
    CC_TO_TREMULANT,
    CC_TO_TUTTI,
    PC_TO_COMBINATION,
    KEYBOARD_NAMES,
)
from models import Stop, StopRegistry


class MidiMessage(Protocol):
    type: str
    channel: int
    velocity: int
    control: int
    value: int
    program: int
    note: int


class MidiMessageHandler:
    def __init__(
        self,
        registry: StopRegistry,
        on_stop_toggle: Callable[[Stop, bool], None],
        on_note_event: Callable[[int, int, bool], None],
        on_parameter_set: Callable[[str, float], None],
        on_parameter_ui_update: Callable[[str, bool], None],
        on_tutti_changed: Callable[[bool], None],
        on_sync_state: Callable[[], None],
        on_reset: Callable[[], None],
        on_warning: Callable[[str], None],
        on_info: Callable[[str], None],
    ) -> None:
        self._registry = registry
        self._on_stop_toggle = on_stop_toggle
        self._on_note_event = on_note_event
        self._on_parameter_set = on_parameter_set
        self._on_parameter_ui_update = on_parameter_ui_update
        self._on_tutti_changed = on_tutti_changed
        self._on_sync_state = on_sync_state
        self._on_reset = on_reset
        self._on_warning = on_warning
        self._on_info = on_info

    def process_message(self, message: MidiMessage) -> None:
        if message.type == "note_on":
            if message.velocity > 0:
                self._handle_note_on(message)
            else:
                self._handle_note_off(message)
        elif message.type == "note_off":
            self._handle_note_off(message)
        elif message.type == "control_change":
            self._handle_control_change(message)
        elif message.type == "program_change":
            self._handle_program_change(message)

    def _handle_note_on(self, message: MidiMessage) -> None:
        channel = message.channel + 1
        keyboard_name = KEYBOARD_NAMES.get(channel, f"Kbd{channel}")
        self._on_info(f"Note {message.note} vel {message.velocity} [{keyboard_name}]")
        if 1 <= channel <= 4:
            self._on_note_event(channel, message.note, True)

    def _handle_note_off(self, message: MidiMessage) -> None:
        channel = message.channel + 1
        if 1 <= channel <= 4:
            self._on_note_event(channel, message.note, False)

    def _handle_program_change(self, message: MidiMessage) -> None:
        if message.program == 0:
            self._on_info("Received reset command via Program Change 0")
            self._on_reset()
        elif message.program in PC_TO_COMBINATION:
            combination_name = PC_TO_COMBINATION[message.program]
            self._on_info(f"Activated {combination_name} via PC {message.program}")
            self._on_sync_state()

    def _handle_control_change(self, message: MidiMessage) -> None:
        channel = message.channel + 1
        cc_number = message.control
        cc_value = message.value

        if cc_number in CC_TO_STOP_NAME:
            self._handle_stop_cc(channel, cc_number, cc_value)
            return

        if cc_number in CC_TO_COUPLER:
            self._handle_coupler_cc(cc_number, cc_value)
            return

        if cc_number in CC_TO_MONO_COUPLER:
            self._handle_mono_coupler_cc(cc_number, cc_value)
            return

        if cc_number in CC_TO_TREMULANT:
            self._handle_tremulant_cc(cc_number, cc_value)
            return

        if cc_number in CC_TO_TUTTI:
            self._handle_tutti_cc(cc_value)
            return

    def _handle_stop_cc(self, channel: int, cc_number: int, cc_value: int) -> None:
        if not self._is_valid_stop_cc(channel, cc_number, cc_value):
            return

        stop_name = CC_TO_STOP_NAME[cc_number]
        is_open = cc_value == 127

        stop = self._registry.find_stop(stop_name, channel)
        if stop:
            keyboard_name = KEYBOARD_NAMES.get(channel, f"Kbd{channel}")
            action = "Opened" if is_open else "Closed"
            self._on_info(f"{action} {stop_name} [{keyboard_name}]")
            self._on_stop_toggle(stop, is_open)
        else:
            keyboard_name = KEYBOARD_NAMES.get(channel, f"Kbd{channel}")
            action = "open" if is_open else "close"
            message_text = (
                f"Failed to {action} {stop_name} [{keyboard_name}] (not present)"
            )
            self._on_warning(message_text)

    def _handle_coupler_cc(self, cc_number: int, cc_value: int) -> None:
        if cc_value not in (1, 127):
            return

        param_id, name = CC_TO_COUPLER[cc_number]
        is_on = cc_value == 127
        normalized_value = 1.0 if is_on else 0.0

        action = "Enabled" if is_on else "Disabled"
        self._on_info(f"{action} {name}")
        self._on_parameter_set(param_id, normalized_value)
        self._on_parameter_ui_update(name, is_on)

    def _handle_mono_coupler_cc(self, cc_number: int, cc_value: int) -> None:
        if cc_value not in (1, 127):
            return

        param_id, name = CC_TO_MONO_COUPLER[cc_number]
        is_on = cc_value == 127
        normalized_value = 1.0 if is_on else 0.0

        action = "Enabled" if is_on else "Disabled"
        self._on_info(f"{action} {name}")
        self._on_parameter_set(param_id, normalized_value)
        self._on_parameter_ui_update(name, is_on)

    def _handle_tremulant_cc(self, cc_number: int, cc_value: int) -> None:
        if cc_value not in (1, 127):
            return

        param_id, name = CC_TO_TREMULANT[cc_number]
        is_on = cc_value == 127
        normalized_value = 1.0 if is_on else 0.0

        action = "Enabled" if is_on else "Disabled"
        self._on_info(f"{action} {name}")
        self._on_parameter_set(param_id, normalized_value)
        self._on_parameter_ui_update(name, is_on)

    def _handle_tutti_cc(self, cc_value: int) -> None:
        if cc_value not in (1, 127):
            return

        param_id, name = CC_TO_TUTTI[90]
        is_on = cc_value == 127
        normalized_value = 1.0 if is_on else 0.0

        action = "Enabled" if is_on else "Disabled"
        self._on_info(f"{action} {name}")
        self._on_parameter_set(param_id, normalized_value)
        self._on_parameter_ui_update(name, is_on)
        self._on_tutti_changed(is_on)

    def _is_valid_stop_cc(
        self, channel: int, cc_number: int, cc_value: int
    ) -> bool:
        if cc_number not in CC_TO_STOP_NAME:
            return False
        if not (1 <= channel <= 4):
            return False
        if cc_value not in (1, 127):
            return False
        return True
