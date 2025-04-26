import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "8136762541:AAHoXifsCDi0Ny3-yovirnTRPfIIPmr1ZtU"
SALDO_FILE = "saldo.json"
ADMIN_USER_IDS = [5368878847, 1316596937]

def get_saldo(user_id):
    try:
        with open(SALDO_FILE, "r") as f:
            data = json.load(f)
        return int(data.get(str(user_id), 0))
    except (FileNotFoundError, ValueError, TypeError):
        return 0

def tambah_saldo_json(user_id, jumlah):
    try:
        with open(SALDO_FILE, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    lama = int(data.get(str(user_id), 0))
    baru = lama + jumlah
    data[str(user_id)] = baru
    with open(SALDO_FILE, "w") as f:
        json.dump(data, f, indent=2)

def kurangi_saldo_json(user_id, jumlah):
    try:
        with open(SALDO_FILE, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    lama = int(data.get(str(user_id), 0))
    baru = max(lama - jumlah, 0)
    data[str(user_id)] = baru
    with open(SALDO_FILE, "w") as f:
        json.dump(data, f, indent=2)
    return lama, baru

def build_main_menu():
    keyboard = [
        [InlineKeyboardButton("BEKASAN", callback_data="bekasan")],
        [
            InlineKeyboardButton("SUPERMINI", callback_data="supermini"),
            InlineKeyboardButton("SUPERBIG", callback_data="superbig")
        ],
        [
            InlineKeyboardButton("MEGAMINI", callback_data="megamini"),
            InlineKeyboardButton("SM V2", callback_data="smv2")
        ],
        [
            InlineKeyboardButton("MINI/L REW", callback_data="mini_l_rew"),
            InlineKeyboardButton("BIG", callback_data="big")
        ],
        [
            InlineKeyboardButton("LITE", callback_data="lite"),
            InlineKeyboardButton("JUMBO", callback_data="jumbo")
        ],
        [InlineKeyboardButton("CEK STOK", callback_data="cekstok")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Untuk melanjutkan bot,\nberikan command /menu")

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    nama = user.username or user.full_name or "-"
    user_id = user.id
    saldo = get_saldo(user_id)

    message_text = (
        "╔══════════════════════════╗\n"
        "             *SELAMAT BERTRANSAKSI*\n"
        "╚══════════════════════════╝\n"
        "╔══════════════════════════╗\n"
        f" *NAMA*  : {nama}\n"
        f" *ID*          : {user_id}\n"
        f" *SALDO* : Rp{saldo:,}\n"
        "╚══════════════════════════╝"
    )

    await update.message.reply_text(message_text, reply_markup=build_main_menu(), parse_mode="Markdown")

async def add_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_USER_IDS:
        await update.message.reply_text("Anda tidak memiliki akses untuk menambah saldo.")
        return

    try:
        user_id = int(context.args[0])
        jumlah = int(context.args[1])
    except (IndexError, ValueError):
        await update.message.reply_text("Format salah. Gunakan: /add {user_id} {jumlah}.")
        return

    saldo_awal = get_saldo(user_id)
    tambah_saldo_json(user_id, jumlah)
    saldo_akhir = get_saldo(user_id)

    user = await context.bot.get_chat(user_id)
    username = user.username or user.full_name

    admin_msg = (
        "✅SUCCESSFULLY✅\n"
        f"ID   : {user_id}\n"
        f"JUMLAH : Rp {jumlah:,}"
    )
    await update.message.reply_text(admin_msg)

    deposit_msg = (
        "╭──────────────────────\n"
        "│              ✅DEPOSIT SALDO✅   \n"
        "├──────────────────────\n"
        f"│ ID Tele       : {user_id}\n"
        f"│ Status        : Saldo Bertambah\n"
        f"│ Username  : {username}\n"
        f"│ Saldo awal  : Rp {saldo_awal:,}\n"
        f"│ Bertambah : Rp {jumlah:,}\n"
        f"│ Saldo akhir : Rp {saldo_akhir:,}\n"
        "╰──────────────────────"
    )
    await context.bot.send_message(user_id, deposit_msg)

async def kurangi_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_USER_IDS:
        await update.message.reply_text("Anda tidak memiliki akses untuk mengurangi saldo.")
        return

    try:
        user_id = int(context.args[0])
        jumlah = int(context.args[1])
    except (IndexError, ValueError):
        await update.message.reply_text("Format salah. Gunakan: /kurangi {user_id} {jumlah}.")
        return

    saldo_awal, saldo_akhir = kurangi_saldo_json(user_id, jumlah)
    user = await context.bot.get_chat(user_id)
    username = user.username or user.full_name

    notif = (
        "╭──────────────────────\n"
        "│      ❗PENGURANGAN SALDO ❗    \n"
        "├──────────────────────\n"
        f"│ ID Tele            : {user_id}\n"
        f"│ Status             : Saldo Terpotong !\n"
        f"│ Username       : {username}\n"
        f"│ Saldo awal      : Rp {saldo_awal:,}\n"
        f"│ Saldo akhir     : Rp {saldo_akhir:,}\n"
        f"│ Total Ditarik   : Rp {saldo_awal - saldo_akhir:,}\n"
        "╰──────────────────────"
    )
    await context.bot.send_message(user_id, notif)
    await update.message.reply_text(f"Saldo pengguna {user_id} berhasil dikurangi Rp{jumlah:,}.")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    reply_msgs = {
        "supermini": "~ AREA 1 : 13 GB\n~ AREA 2 : 15 GB\n~ AREA 3 : 20 GB\n~ AREA 4 : 30 GB\n\nHARGA : Rp.xx.xxxx\nSTOK : KOSONG.",
        "superbig": "~ AREA 1 : 26 GB\n~ AREA 2 : 31 GB\n~ AREA 3 : 44 GB\n~ AREA 4 : 84 GB\n\nHARGA : Rp.xx.xxxx\nSTOK : KOSONG.",
        "megamini": "~ AREA 1 : 15,5 GB\n~ AREA 2 : 18,5 GB\n~ AREA 3 : 29 GB\n~ AREA 4 : 53 GB\n\nHARGA : Rp.xx.xxxx\nSTOK : KOSONG.",
        "smv2": "~ AREA 1 : 31 GB\n~ AREA 2 : 34 GB\n~ AREA 3 : 39 GB\n~ AREA 4 : 48 GB\n\nHARGA : Rp.xx.xxxx\nSTOK : KOSONG.",
        "mini_l_rew": "~ AREA 1 : 38 GB\n~ AREA 2 : 40 GB\n~ AREA 3 : 45 GB\n~ AREA 4 : 55 GB\n\nHARGA : Rp.xx.xxxx\nSTOK : KOSONG.",
        "big": "~ AREA 1 : 35 GB\n~ AREA 2 : 38 GB\n~ AREA 3 : 49 GB\n~ AREA 4 : 73 GB\n\nHARGA : Rp.xx.xxxx\nSTOK : KOSONG.",
        "lite": "~ AREA 1 : 47 GB\n~ AREA 2 : 52 GB\n~ AREA 3 : 65 GB\n~ AREA 4 : 105 GB\n\nHARGA : Rp.xx.xxxx\nSTOK : KOSONG.",
        "jumbo": "~ AREA 1 : 65 GB\n~ AREA 2 : 70 GB\n~ AREA 3 : 83 GB\n~ AREA 4 : 123 GB\n\nHARGA : Rp.xx.xxxx\nSTOK : KOSONG."
    }

    if query.data == "cekstok":
        teks_alert = (
            "Stok:\n"
            "BEKASAN : 0    | SUPERBIG : 0\n"
            "MEGAMINI : 0   | SM V2 : 0\n"
            "MINI_L_REW : 0 | BIG : 0\n"
            "LITE : 0       | JUMBO : 0"
        )
        await query.answer(text=teks_alert, show_alert=True)

    elif query.data in reply_msgs:
        await query.edit_message_text(
            text=reply_msgs[query.data],
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("KEMBALI", callback_data="back"),
                    InlineKeyboardButton("LANJUT BELI", callback_data="lanjut_beli")
                ]
            ])
        )

    elif query.data == "bekasan":
        bekasan_menu = InlineKeyboardMarkup([
            [InlineKeyboardButton("5 HARI", callback_data="bekasan_5")],
            [InlineKeyboardButton("7 HARI", callback_data="bekasan_7")],
            [InlineKeyboardButton("10 HARI", callback_data="bekasan_10")],
            [InlineKeyboardButton("15 HARI", callback_data="bekasan_15")],
            [InlineKeyboardButton("KEMBALI", callback_data="back")]
        ])
        await query.edit_message_text(text="PILIH DURASI BEKASAN:", reply_markup=bekasan_menu)

    elif query.data.startswith("bekasan_"):
        durasi = query.data.split('_')[1]
        await query.edit_message_text(
            text=f"Stok BEKASAN {durasi} HARI: KOSONG.",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("KEMBALI", callback_data="bekasan"),
                    InlineKeyboardButton("LANJUT BELI", callback_data="lanjut_beli")
                ]
            ])
        )

    elif query.data == "lanjut_beli":
        await query.edit_message_text(text="Pembelian segera diproses... (kayaknya🗿).")

    elif query.data == "back":
        user = query.from_user
        nama = user.username or user.full_name or "-"
        user_id = user.id
        saldo = get_saldo(user_id)
        message_text = (
            "╔══════════════════════════╗\n"
            "           *SELAMAT BERTRANSAKSI*\n"
            "╚══════════════════════════╝\n"
            "╔══════════════════════════╗\n"
            f"        *NAMA*  : {nama}\n"
            f"        *ID*    : {user_id}\n"
            f"        *SALDO* : Rp{saldo:,}\n"
            "╚══════════════════════════╝"
        )
        await query.edit_message_text(text=message_text, reply_markup=build_main_menu(), parse_mode="Markdown")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.bot.set_my_commands([
        BotCommand("start", "Mulai"),
        BotCommand("menu", "Menu"),
        BotCommand("add", "Tambah saldo"),
        BotCommand("kurangi", "Kurangi saldo")
    ])

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("add", add_saldo))
    app.add_handler(CommandHandler("kurangi", kurangi_saldo))
    app.add_handler(CallbackQueryHandler(button_click))

    print("\033[92mBOT BERHASIL DI JALANKAN.\033[0m")
    app.run_polling()


if __name__ == "__main__":
    main()


