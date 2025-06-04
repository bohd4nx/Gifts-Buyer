import asyncio
from typing import Dict, Tuple, Any

from pyrogram import Client

from app.notifications import send_notification
from app.purchase import buy_gift
from app.utils.logger import warn, info
from data.config import config, t

_skipped_sold_out_gifts = 0
_skipped_non_limited_gifts = 0
_skipped_non_upgradable_gifts = 0
_skipped_excluded_gifts = 0

class GiftFilter:

    @staticmethod
    async def check_gift_eligibility(gift_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        global _skipped_sold_out_gifts, _skipped_non_limited_gifts, _skipped_non_upgradable_gifts, _skipped_excluded_gifts
        gift_price = gift_data.get("price", 0)
        is_limited = gift_data.get("is_limited", False)
        is_sold_out = gift_data.get("is_sold_out", False)
        is_excluded = gift_data.get("id", 0)
        is_upgradable = "upgrade_price" in gift_data
        total_amount = gift_data.get("total_amount", "N/A") if is_limited else "N/A"
        if is_excluded in config.EXCLUDED_GIFTS_IDS:
            _skipped_excluded_gifts += 1
            return False, {}
        
        if is_sold_out:
            _skipped_sold_out_gifts += 1
            return False, {}

        if not is_limited and not config.PURCHASE_NON_LIMITED_GIFTS:
            _skipped_non_limited_gifts += 1
            return False, {}

        if config.PURCHASE_ONLY_UPGRADABLE_GIFTS and not is_upgradable:
            _skipped_non_upgradable_gifts += 1
            return False, {}

        if gift_price < config.MIN_GIFT_PRICE or gift_price > config.MAX_GIFT_PRICE:
            notification_kwargs = {
                "gift_price_error": True,
                "gift_price": gift_price,
                "total_amount": total_amount
            }
            return False, notification_kwargs

        return True, {}


async def new_callback(app: Client, gift_data: Dict[str, Any]) -> None:
    gift_id = gift_data.get("id")

    is_eligible, notification_kwargs = await GiftFilter.check_gift_eligibility(gift_data)

    if not is_eligible and notification_kwargs:
        await send_notification(app, gift_id, **notification_kwargs)
        return

    if is_eligible:
        for user_id in config.USER_ID:
            try:
                await buy_gift(app, user_id, gift_id)
            except Exception as ex:
                warn(t("console.purchase_error", gift_id=gift_id, chat_id=user_id))
                await send_notification(app, gift_id, error_message=str(ex))
            await asyncio.sleep(0.5)


async def process_skipped_gifts(app: Client) -> None:
    global _skipped_sold_out_gifts, _skipped_non_limited_gifts, _skipped_non_upgradable_gifts, _skipped_excluded_gifts

    if _skipped_excluded_gifts > 0:
        info(t("console.excluded_gifts_summary", count=_skipped_excluded_gifts))
        await send_notification(app, 0, excluded_gifts_summary=True, count=_skipped_excluded_gifts)
        _skipped_excluded_gifts = 0

    if _skipped_sold_out_gifts > 0:
        info(t("console.sold_out_gifts_summary", count=_skipped_sold_out_gifts))
        await send_notification(app, 0, sold_out_summary=True, count=_skipped_sold_out_gifts)
        _skipped_sold_out_gifts = 0

    if _skipped_non_limited_gifts > 0:
        info(t("console.non_limited_gifts_summary", count=_skipped_non_limited_gifts))
        await send_notification(app, 0, non_limited_summary=True, count=_skipped_non_limited_gifts)
        _skipped_non_limited_gifts = 0

    if _skipped_non_upgradable_gifts > 0:
        info(t("console.non_upgradable_gifts_summary", count=_skipped_non_upgradable_gifts))
        await send_notification(app, 0, non_upgradable_summary=True, count=_skipped_non_upgradable_gifts)
        _skipped_non_upgradable_gifts = 0

    if _skipped_excluded_gifts > 0:
        info(t("console.non_upgradable_gifts_summary", count=_skipped_non_upgradable_gifts))
        await send_notification(app, 0, non_upgradable_summary=True, count=_skipped_non_upgradable_gifts)
        _skipped_non_upgradable_gifts = 0
