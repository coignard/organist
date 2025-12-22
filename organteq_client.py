from typing import Optional

import requests

from config import REQUEST_TIMEOUT_SECONDS
from models import Stop, StopRegistry


class OrganteqClient:
    def __init__(self, url: str) -> None:
        self.url = url

    def call_method(
        self, method: str, params: Optional[dict] = None
    ) -> Optional[dict]:
        payload = {
            "method": method,
            "params": params or [],
            "jsonrpc": "2.0",
            "id": 1,
        }
        try:
            response = requests.post(
                self.url, json=payload, timeout=REQUEST_TIMEOUT_SECONDS
            )
            result = response.json()

            if "error" in result:
                return None

            return result.get("result")
        except (requests.exceptions.RequestException, ValueError):
            return None

    def get_stop_names(self) -> list[list[str]]:
        result = self.call_method("getStopNames")
        return result if result else []

    def get_all_parameters(self) -> list[dict]:
        result = self.call_method("getParameters", {"list": []})
        return result if result else []

    def set_parameter(self, parameter_id: str, normalized_value: float) -> bool:
        result = self.call_method(
            "setParameters",
            {"list": [{"id": parameter_id, "normalized_value": normalized_value}]},
        )
        return result is not None

    def load_stops_into_registry(self, registry: StopRegistry) -> bool:
        names_data = self.get_stop_names()
        if not names_data:
            return False

        for keyboard_idx, stops_list in enumerate(names_data):
            keyboard_num = keyboard_idx + 1
            for stop_idx, name in enumerate(stops_list):
                if name and name.strip():
                    stop_position = stop_idx + 1
                    stop = Stop(
                        name=name,
                        keyboard=keyboard_num,
                        position=stop_position,
                    )
                    registry.add_stop(stop)

        return len(registry) > 0
