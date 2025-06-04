from pyrogram import Client
from pyrogram.errors import RPCError

from app.utils.helper import get_user_balance, format_user_reference
from app.utils.logger import error
from data.config import config, t


async def send_message(app: Client, message: str, disable_web_page_preview: bool = True) -> None:
    if not config.CHANNEL_ID:
        return

    try:
        await app.send_message(
            config.CHANNEL_ID,
            message,
            disable_web_page_preview=disable_web_page_preview
        )
    except RPCError as ex:
        error(f'Failed to send notification: {str(ex)}')


async def send_notification(app: Client, gift_id: int, **kwargs) -> None:
    num = config.GIFT_QUANTITY

    supply_text = ""
    if 'total_amount' in kwargs and kwargs['total_amount'] != "N/A":
        supply_text = f" | {t('telegram.available')}: {kwargs.get('total_amount')}"

    message_types = {
        'peer_id_error': lambda: t("telegram.peer_id_error"),
        'error_message': lambda: t("telegram.error_message", error=kwargs.get('error_message')),
        'balance_error': lambda: t("telegram.balance_error", gift_id=gift_id,
                                   gift_price=kwargs.get('gift_price', 0),
                                   current_balance=kwargs.get('current_balance', 0)),
        'sold_out': lambda: t("telegram.sold_out_error", gift_id=gift_id),
        'sold_out_summary': lambda: t("telegram.sold_out_summary", count=kwargs.get('count', 0)),
        'non_limited_summary': lambda: t("telegram.non_limited_summary", count=kwargs.get('count', 0)),
        'non_upgradable_summary': lambda: t("telegram.non_upgradable_summary", count=kwargs.get('count', 0)),
        'excluded_gifts_summary': lambda: t("telegram.excluded_gifts_summary", count=kwargs.get('count', 0)),
        'gift_price_error': lambda: t("telegram.gift_price", gift_id=gift_id,
                                      price=kwargs.get('gift_price'),
                                      supply_text=supply_text),
        'success_message': lambda: t("telegram.success_message", current=kwargs.get('current_gift'), total=num,
                                     gift_id=gift_id, recipient='') +
                                   format_user_reference(kwargs.get('user_id'), kwargs.get('username'))
    }

    for key, value in kwargs.items():
        if value and key in message_types:
            await send_message(app, message_types[key]().strip())
            return


async def send_start_message(client: Client) -> None:
    balance = await get_user_balance(client)
    message = t("telegram.start_message",
                language=config.LANGUAGE_DISPLAY,
                locale=config.LANGUAGE,
                balance=balance,
                min_price=config.MIN_GIFT_PRICE,
                max_price=config.MAX_GIFT_PRICE,
                quantity=config.GIFT_QUANTITY,
                excluded_gifts=config.EXCLUDED_GIFTS_IDS)
    await send_message(client, message)
