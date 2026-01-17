import math
import time

import pyautogui
from obsws_python import ReqClient

CONFIG = {
    "obs_host": "localhost",
    "obs_port": 4455,
    "obs_password": "",
    "scene_name": "Scene",
    "source_name": "Character",
    "canvas_width": 1920,
    "canvas_height": 1080,
    "head_anchor_x": 960,
    "head_anchor_y": 540,
    "rotation_offset_deg": 0.0,
    "rotation_limit_deg": 35.0,
    "update_fps": 30,
}


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


def get_scale(canvas_width: int, canvas_height: int) -> tuple[float, float]:
    screen_width, screen_height = pyautogui.size()
    return canvas_width / screen_width, canvas_height / screen_height


def cursor_in_canvas(scale_x: float, scale_y: float) -> tuple[float, float]:
    cursor_x, cursor_y = pyautogui.position()
    return cursor_x * scale_x, cursor_y * scale_y


def calculate_rotation(
    head_anchor: tuple[float, float],
    cursor_pos: tuple[float, float],
    offset_deg: float,
    limit_deg: float,
) -> float:
    dx = cursor_pos[0] - head_anchor[0]
    dy = cursor_pos[1] - head_anchor[1]
    angle_deg = math.degrees(math.atan2(dy, dx)) + offset_deg
    return clamp(angle_deg, -limit_deg, limit_deg)


def create_client() -> ReqClient:
    return ReqClient(
        host=CONFIG["obs_host"],
        port=CONFIG["obs_port"],
        password=CONFIG["obs_password"],
    )


def main() -> None:
    try:
        client = create_client()
    except OSError as exc:
        print("Не удалось подключиться к OBS WebSocket.")
        print(
            "Проверьте, что OBS запущен, WebSocket включен, порт не заблокирован, "
            "и пароль совпадает с CONFIG."
        )
        print(f"Детали ошибки: {exc}")
        return

    scene_item_id = client.get_scene_item_id(
        scene_name=CONFIG["scene_name"],
        source_name=CONFIG["source_name"],
    )

    scale_x, scale_y = get_scale(CONFIG["canvas_width"], CONFIG["canvas_height"])
    head_anchor = (CONFIG["head_anchor_x"], CONFIG["head_anchor_y"])
    delay = 1 / CONFIG["update_fps"]

    while True:
        cursor_pos = cursor_in_canvas(scale_x, scale_y)
        rotation = calculate_rotation(
            head_anchor,
            cursor_pos,
            CONFIG["rotation_offset_deg"],
            CONFIG["rotation_limit_deg"],
        )
        client.set_scene_item_transform(
            scene_name=CONFIG["scene_name"],
            item_id=scene_item_id,
            scene_item_transform={"rotation": rotation},
        )
        time.sleep(delay)


if __name__ == "__main__":
    main()
