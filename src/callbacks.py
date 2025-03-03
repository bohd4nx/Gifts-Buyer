import asyncio

from pyrogram import Client

import config
from src.notifications import notifications
from utils.utils import buyer

sent_gift_ids = set()


def _is_gift_within_limits(gift_price: float, gift_supply: int) -> bool:
    for min_price, max_price, supply_limit, _ in config.GIFT_RANGES:
        if min_price <= gift_price < max_price and gift_supply <= supply_limit:
            return True
    return False


def _handle_limited_gift(gift_id: int) -> bool:
    if gift_id in sent_gift_ids:
        return False
    sent_gift_ids.add(gift_id)
    return True


def _handle_non_limited_gift(gift_id: int, gift_price: float) -> bool:
    if not config.PURCHASE_NON_LIMITED_GIFTS or gift_price > config.MAX_GIFT_PRICE:
        return False
    if gift_id not in sent_gift_ids:
        sent_gift_ids.add(gift_id)
        return True
    return False


async def new_callback(app: Client, star_gift_raw: dict) -> None:
    gift_price = star_gift_raw.get("price", 0)
    gift_supply = star_gift_raw.get("total_amount", 0)
    gift_id = star_gift_raw['id']
    locale = config.locale

    if not _is_gift_within_limits(gift_price, gift_supply):
        print(f"\033[91m[ WARN ]\033[0m {locale.gift_expensive.format(gift_id, gift_price, gift_supply)}\n")
        await notifications(app, gift_id, gift_price=gift_price, gift_supply=gift_supply)
        return

    if star_gift_raw.get("is_limited", False):
        if not _handle_limited_gift(gift_id):
            return
    elif not _handle_non_limited_gift(gift_id, gift_price):
        print(f"\033[91m[ WARN ]\033[0m {locale.non_limited_gift.format(gift_id)}\n")
        await notifications(app, gift_id, non_limited_error=True)
        return

    for i, chat_id in enumerate(config.USER_ID):
        await buyer(app, chat_id, gift_id)
        if i < len(config.USER_ID) - 1:
            await asyncio.sleep(config.GIFT_DELAY)


async def update_callback(new_gift_raw: dict) -> None:
    if "message_id" not in new_gift_raw:
        return

    message_id = new_gift_raw["message_id"]
