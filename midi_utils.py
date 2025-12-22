from typing import Optional

import mido


def select_midi_port() -> Optional[str]:
    inputs = mido.get_input_names()

    if not inputs:
        print("No MIDI input devices found")
        return None

    auto_selected = _try_auto_select(inputs)
    if auto_selected:
        return auto_selected

    return _prompt_user_selection(inputs)


def _try_auto_select(inputs: list[str]) -> Optional[str]:
    keywords = ["IAC", "Bus", "Dorico"]
    for port in inputs:
        if any(keyword in port for keyword in keywords):
            return port
    return None


def _prompt_user_selection(inputs: list[str]) -> Optional[str]:
    print("\nAvailable MIDI inputs:")
    for i, name in enumerate(inputs, 1):
        print(f"  {i}. {name}")

    try:
        selection = input("\nSelect port number: ").strip()
        idx = int(selection) - 1
        if 0 <= idx < len(inputs):
            return inputs[idx]
    except (ValueError, IndexError):
        pass

    return None
