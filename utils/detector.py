import asyncio
import json
import time
import typing

from pyrogram import Client, types
from pytz import timezone as _timezone

import config
from utils.common import get_time

timezone = _timezone(config.TIMEZONE)


async def _load_old_gifts() -> dict:
    try:
        with config.DATA_FILEPATH.open("r", encoding='utf-8') as file:
            old_gifts_raw = json.load(file)
            return {gift["id"]: gift for gift in old_gifts_raw}
    except FileNotFoundError:
        return {}


async def _save_gifts(gifts: list) -> None:
    with config.DATA_FILEPATH.open("w", encoding='utf-8') as file:
        json.dump(gifts, file, indent=4, default=types.Object.default, ensure_ascii=False)


async def _get_formatted_gifts(app: Client) -> tuple[dict, list]:
    all_gifts = [
        json.loads(json.dumps(gift, indent=4, default=types.Object.default, ensure_ascii=False))
        for gift in await app.get_star_gifts()
    ]

    all_gifts_raw = {gift["id"]: gift for gift in all_gifts}
    all_gifts_ids = list(all_gifts_raw.keys())

    return all_gifts_raw, all_gifts_ids


async def detector(app: Client, new_callback: typing.Callable, connect_every_loop: bool = True) -> None:
    locale = config.locale
    dot = 0

    while True:
        current_time = get_time(timezone)
        dot = (dot + 1) % 4
        print(f"\033[K\033[94m[ INFO ]\033[0m {current_time} \033[1m- {locale.gift_checking}{'.' * dot}\033[0m",
              end="\r")

        time.sleep(0.2)

        if not app.is_connected:
            await app.start()

        old_gifts = await _load_old_gifts()
        all_gifts_raw, all_gifts_ids = await _get_formatted_gifts(app)

        new_star_gifts_raw = {
            key: value for key, value in all_gifts_raw.items()
            if key not in old_gifts
        }

        if new_star_gifts_raw:
            print(f"\n\n\033[92m[ NEW ]\033[0m {locale.new_gifts} {len(new_star_gifts_raw)}\n")

            all_gifts_amount = len(all_gifts_ids)
            for star_gift_id, star_gift_raw in new_star_gifts_raw.items():
                star_gift_raw["number"] = all_gifts_amount - all_gifts_ids.index(star_gift_id)

            for star_gift_id, star_gift_raw in sorted(new_star_gifts_raw.items(), key=lambda it: it[1]["number"]):
                await new_callback(app, star_gift_raw)

        await _save_gifts(list(all_gifts_raw.values()))

        if connect_every_loop:
            await app.stop()

        await asyncio.sleep(config.INTERVAL)
