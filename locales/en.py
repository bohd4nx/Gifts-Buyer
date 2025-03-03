# -----------------------------
# Language Info (English)
# -----------------------------
LANG = "🇺🇸 English"
CODE = "EN-US"

# -----------------------------
# Telegram Messages
# -----------------------------
peer_id_error = (
    "<b>❗Error while sending gift!</b>\n\n"
    "Please make sure the initialization message has been sent successfully, "
    "you have interacted with this user previously, <b><i>and that you are not sending a gift to yourself!</i></b>\n\n"
    "⚠️ If nothing helps, try adding them to your contacts or DM the developer: @bohd4nx"
)

error_message = "<b>❗Error while buying a gift!</b>\n\n<pre>{}</pre>"

balance_error = ("<b>🎁 Gift</b> [<code>{}</code>] could not be sent due to insufficient balance!"
                 "\n\n<b>❗ Please top up your balance to continue sending gifts.</b>")

usage_limited = "<b>❗Limited gift</b> [<code>{}</code>] Out of Stock."

non_limited_error = "<b>❗Gift</b> [<code>{}</code>] is non-limited. Skipping due to user settings..."

gift_price = "<b>🎁 Gift</b> [<code>{}</code>] does not match the user's specified settings\n\nPrice: <b>{} ⭐ | supply: {}</b>. Skipping..."

success_message = "<b>🎁 Gift ({}/{}):</b> [<code>{}</code>] has been successfully sent!\n\n<b>Recipient:{}</b> "

start_message = """
<b>✅ The program has started.
Selected localization:</b> <i>🇺🇸 English</i>

<b>⚙️ Parameters:</b>
<code>Price range | number of gifts | supply limit</code>
<blockquote expandable>{ranges_info}</blockquote>

<b>📝 Gift purchase formula explanation:</b>
<blockquote expandable>For example, with settings:
• Min price = 100⭐
• Max price = 1000⭐
• Supply limit = 5000

The gift will be purchased if:
• Gift price is between 100⭐ and 1000⭐
• Gift supply is less than 5000 units

For non-limited gifts, additional settings apply</blockquote>

<i>❗ If any condition is not met, the gift will be skipped</i>
"""

# -----------------------------
# Console Messages
# -----------------------------
low_balance = "Insufficient stars balance to send gift!"
out_of_stock = "Limited gift: {} Out of Stock."
peer_id = "Please ensure that you have interacted with this user previously or are not sending a gift to yourself!"
gift_send_error = "Failed to send gift: {} to user: {}"
gift_checking = "Checking for new gifts"
new_gifts = "New gifts found:"
gift_expensive = "Gift: \033[1m{}\033[0m does not match the user's specified settings, price: {}★ | supply: {}"
non_limited_gift = "Gift: \033[1m{}\033[0m is non-limited. Skipping..."
purchase_error = "Error while buying a gift \033[1m{}\033[0m for user: \033[1m{}\033[0m"
terminated = "Program terminated"
unexpected_error = "An unexpected error occurred:"

gift_sent = "Gift ({}/{}): \033[1m{}\033[0m successfully sent to {}"
