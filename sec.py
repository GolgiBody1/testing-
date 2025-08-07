import re
import random
import json
from pyrogram import Client, filters
from pyrogram.types import Message

# Config
API_ID = 26014459
API_HASH = "34b8791089c72367a5088f96d925f989"
STRING_SESSION = "BQGM8vsAJVppG5SfjCvycz5l9o_UIsYpj3bvjYYF7qxZijHTM8_7mx8HlI2NVksjHXC3o31_QhFdq3VQGp510kRTE8CP0lYNSxQoM7A00-Wa56JNH1R2cNWTDuUGTYXqbif1B4z96_vPRJvPysL-R-6YMO7BDrI39Poyxv-IieogpMorJKUiQEgn1DjbeQTQNkpbJNwa2l-sbXumBfw5zwMCCZo4-iW_cNULOJLR_hw9-cRC64tMvegiJUUxmpweOThIJdz4ElEl7_qWV1HJSuTkPHyO_RaAIem-GwqQEi5RUlfpKXkCcOZYkPzZpMyrymLzcD0c-cGjPY7lqvFatJnNxF__VwAAAAGx20OoAA"
DATA_FILE = "data.json"
LOG_CHANNEL_ID = -1002330347621  # Change if needed

app = Client(name="escrow_userbot", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)

# Load / Save JSON
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"groups": {}, "global": {"total_deals": 0, "total_volume": 0, "total_fee": 0.0, "escrowers": {}}}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()

# Helpers
async def is_admin(msg: Message) -> bool:
    try:
        member = await app.get_chat_member(msg.chat.id, msg.from_user.id)
        return member.status in ("administrator", "creator")
    except:
        return False

def init_group(chat_id: str):
    if chat_id not in data["groups"]:
        data["groups"][chat_id] = {
            "deals": {},
            "total_deals": 0,
            "total_volume": 0,
            "total_fee": 0.0,
            "escrowers": {}
        }

def update_escrower_stats(group_id: str, escrower: str, amount: float, fee: float):
    g = data["groups"][group_id]
    g["total_deals"] += 1
    g["total_volume"] += amount
    g["total_fee"] += fee
    g["escrowers"][escrower] = g["escrowers"].get(escrower, 0) + amount

    data["global"]["total_deals"] += 1
    data["global"]["total_volume"] += amount
    data["global"]["total_fee"] += fee
    data["global"]["escrowers"][escrower] = data["global"]["escrowers"].get(escrower, 0) + amount

    save_data()

# /start
@app.on_message(filters.command("start"))
async def start(_, msg: Message):
    await msg.reply_text(
        "✨ Welcome to Userbot Escrow!\n"
        "• /add – Reply to a deal to escrow it\n"
        "• /complete – Reply to complete deal\n"
        "• /stats – Group stats\n"
        "• /gstats – Global stats (admin only)"
    )

# /add
@app.on_message(filters.command("add"))
async def add_deal(_, msg: Message):
    if not await is_admin(msg): return

    try: await msg.delete()
    except: pass

    if not msg.reply_to_message:
        await msg.reply("❌ Please reply to the DEAL INFO form!")
        return

    form = msg.reply_to_message.text
    chat_id = str(msg.chat.id)
    reply_id = str(msg.reply_to_message.id)
    init_group(chat_id)

    buyer = re.search(r"BUYER\s*:\s*(@\w+)", form, re.IGNORECASE)
    seller = re.search(r"SELLER\s*:\s*(@\w+)", form, re.IGNORECASE)
    amount = re.search(r"DEAL AMOUNT\s*:\s*₹?\s*([\d.]+)", form, re.IGNORECASE)

    buyer = buyer.group(1) if buyer else "Unknown"
    seller = seller.group(1) if seller else "Unknown"
    if not amount:
        await msg.reply("❌ Amount not found!")
        return

    amount = float(amount.group(1))
    group = data["groups"][chat_id]

    if reply_id not in group["deals"]:
        tid = f"TID{random.randint(100000, 999999)}"
        fee = round(amount * 0.02, 2)
        release = round(amount - fee, 2)
        group["deals"][reply_id] = {"trade_id": tid, "release_amount": release, "completed": False}
    else:
        d = group["deals"][reply_id]
        tid = d["trade_id"]
        release = d["release_amount"]
        fee = round(amount - release, 2)

    esc = f"@{msg.from_user.username}" if msg.from_user.username else msg.from_user.first_name
    update_escrower_stats(chat_id, esc, amount, fee)

    await msg.chat.send_message(
        f"✅ Amount Received!\n"
        f"👤 Buyer  : {buyer}\n"
        f"👤 Seller : {seller}\n"
        f"💰 Amount : ₹{amount}\n"
        f"💸 Release: ₹{release}\n"
        f"⚖️ Fee    : ₹{fee}\n"
        f"🆔 Trade ID: #{tid}\n"
        f"🛡️ Escrowed by {esc}",
        reply_to_message_id=msg.reply_to_message.id
    )

    save_data()

# /complete
@app.on_message(filters.command("complete"))
async def complete_deal(_, msg: Message):
    if not await is_admin(msg): return

    try: await msg.delete()
    except: pass

    if not msg.reply_to_message:
        await msg.reply("❌ Reply to the original deal form!")
        return

    chat_id = str(msg.chat.id)
    reply_id = str(msg.reply_to_message.id)
    init_group(chat_id)

    group = data["groups"][chat_id]
    deal = group["deals"].get(reply_id)

    if not deal:
        await msg.reply("❌ This deal was never added!")
        return
    if deal["completed"]:
        await msg.reply("❌ Already completed!")
        return

    deal["completed"] = True
    save_data()

    form = msg.reply_to_message.text
    buyer = re.search(r"BUYER\s*:\s*(@\w+)", form, re.IGNORECASE)
    seller = re.search(r"SELLER\s*:\s*(@\w+)", form, re.IGNORECASE)

    buyer = buyer.group(1) if buyer else "Unknown"
    seller = seller.group(1) if seller else "Unknown"
    tid = deal["trade_id"]
    release = deal["release_amount"]
    esc = f"@{msg.from_user.username}" if msg.from_user.username else msg.from_user.first_name

    await msg.chat.send_message(
        f"✅ Deal Completed!\n"
        f"👤 Buyer   : {buyer}\n"
        f"👤 Seller  : {seller}\n"
        f"💸 Released: ₹{release}\n"
        f"🆔 Trade ID: #{tid}\n"
        f"🛡️ Escrowed by {esc}",
        reply_to_message_id=msg.reply_to_message.id
    )

    await app.send_message(
        LOG_CHANNEL_ID,
        f"📜 Deal Completed (Log)\n"
        f"👤 Buyer   : {buyer}\n"
        f"👤 Seller  : {seller}\n"
        f"💸 Released: ₹{release}\n"
        f"🆔 Trade ID: #{tid}\n"
        f"🛡️ Escrowed by {esc}\n"
        f"📌 Group: {msg.chat.title} ({msg.chat.id})"
    )

# /stats
@app.on_message(filters.command("stats"))
async def stats(_, msg: Message):
    chat_id = str(msg.chat.id)
    init_group(chat_id)
    g = data["groups"][chat_id]

    escrowers = "\n".join([f"{k} = ₹{v}" for k, v in g["escrowers"].items()]) or "No deals yet"

    await msg.reply_text(
        f"📊 Group Stats\n\n"
        f"{escrowers}\n\n"
        f"🔹 Total Deals: {g['total_deals']}\n"
        f"💰 Volume: ₹{g['total_volume']}\n"
        f"💸 Fee: ₹{g['total_fee']}"
    )

# /gstats
@app.on_message(filters.command("gstats"))
async def gstats(_, msg: Message):
    if not await is_admin(msg): return

    g = data["global"]
    escrowers = "\n".join([f"{k} = ₹{v}" for k, v in g["escrowers"].items()]) or "No global deals"

    await msg.reply_text(
        f"🌍 Global Stats\n\n"
        f"{escrowers}\n\n"
        f"🔹 Total Deals: {g['total_deals']}\n"
        f"💰 Volume: ₹{g['total_volume']}\n"
        f"💸 Fee: ₹{g['total_fee']}"
    )

print("Userbot running... ✅")
app.run()
