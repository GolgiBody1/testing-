import random
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = 26014459
API_HASH = "34b8791089c72367a5088f96d925f989"
SESSION = "BQGM8vsAJVppG5SfjCvycz5l9o_UIsYpj3bvjYYF7qxZijHTM8_7mx8HlI2NVksjHXC3o31_QhFdq3VQGp510kRTE8CP0lYNSxQoM7A00-Wa56JNH1R2cNWTDuUGTYXqbif1B4z96_vPRJvPysL-R-6YMO7BDrI39Poyxv-IieogpMorJKUiQEgn1DjbeQTQNkpbJNwa2l-sbXumBfw5zwMCCZo4-iW_cNULOJLR_hw9-cRC64tMvegiJUUxmpweOThIJdz4ElEl7_qWV1HJSuTkPHyO_RaAIem-GwqQEi5RUlfpKXkCcOZYkPzZpMyrymLzcD0c-cGjPY7lqvFatJnNxF__VwAAAAGx20OoAA"

app = Client(session_name=SESSION, api_id=API_ID, api_hash=API_HASH)

# Helper to generate unique Trade ID
def generate_trade_id():
    return f"#TID{random.randint(100000, 999999)}"

# /add command - marks amount as received
@app.on_message(filters.command("add"))
async def add_deal(client, message: Message):
    try:
        await message.delete()

        if not message.reply_to_message:
            return await message.reply("❌ Please reply to the original deal form.")

        form_text = message.reply_to_message.text
        buyer = seller = "Unknown"
        amount = 0.0

        for line in form_text.splitlines():
            if "BUYER" in line.upper():
                buyer = line.split(":")[1].strip()
            elif "SELLER" in line.upper():
                seller = line.split(":")[1].strip()
            elif "AMOUNT" in line.upper():
                amount = float(line.split(":")[1].replace("rs", "").replace("₹", "").strip())

        fee = round(amount * 0.02, 2)
        release_amount = round(amount - fee, 2)
        trade_id = generate_trade_id()

        reply_text = f"""✅ Amount Received!

──────────────────
👤 Buyer  : {buyer}
👤 Seller : {seller}
💰 Amount : ₹{amount:.2f}
💸 Release: ₹{release_amount:.2f}
⚖️ Fee    : ₹{fee:.2f}
🆔 Trade ID: {trade_id}
──────────────────
🛡️ Escrowed by @{message.from_user.username or 'Unknown'}"""

        await message.reply_to_message.reply(reply_text)

    except Exception as e:
        await message.reply(f"⚠️ Error: {e}")

# /complete command - marks deal as completed
@app.on_message(filters.command("complete"))
async def complete_deal(client, message: Message):
    try:
        await message.delete()

        if not message.reply_to_message:
            return await message.reply("❌ Please reply to the original deal form.")

        form_text = message.reply_to_message.text
        buyer = seller = "Unknown"
        amount = 0.0

        for line in form_text.splitlines():
            if "BUYER" in line.upper():
                buyer = line.split(":")[1].strip()
            elif "SELLER" in line.upper():
                seller = line.split(":")[1].strip()
            elif "AMOUNT" in line.upper():
                amount = float(line.split(":")[1].replace("rs", "").replace("₹", "").strip())

        trade_id = generate_trade_id()

        reply_text = f"""✅ Deal Completed!

──────────────────
👤 Buyer  : {buyer}
👤 Seller : {seller}
💸 Released: ₹{amount:.2f}
🆔 Trade ID: {trade_id}
──────────────────
🛡️ Escrowed by @{message.from_user.username or 'Unknown'}"""

        await message.reply_to_message.reply(reply_text)

    except Exception as e:
        await message.reply(f"⚠️ Error: {e}")

# Start the userbot
app.run()
