import os
import logging
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from pdf2docx import Converter

# Loglarni sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- KONFIGURATSIYA ---
# Environment Variable orqali tokenni olamiz
TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi /start bosganda ishlaydi"""
    await update.message.reply_text(
        "Assalomu alaykum! Menga **PDF** fayl yuboring, men uni **DOCX** (Word) formatiga o'girib beraman. "
        "Iltimos, fayl parollanmagan bo'lishi kerak.",
        parse_mode=constants.ParseMode.MARKDOWN
    )

async def convert_pdf_to_docx(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """PDF faylni qabul qilib, DOCX ga aylantiradi"""
    file_name = update.message.document.file_name
    file_id = update.message.document.file_id

    # Faqat .pdf fayllarni tekshirish (Telegramning o'z filtrlari yetarli bo'lmasa)
    if not file_name.lower().endswith('.pdf'):
        await update.message.reply_text("Iltimos, faqat PDF fayl yuboring.")
        return

    # Foydalanuvchiga jarayon boshlanganini bildiruvchi xabar yuborish
    status_msg = await update.message.reply_text("📥 Fayl qabul qilindi. **Konvertatsiya qilinmoqda...**", 
                                                 parse_mode=constants.ParseMode.MARKDOWN)

    # Fayl nomlarini tayyorlash
    pdf_path = f"{file_id}_in.pdf"
    docx_path = f"{os.path.splitext(file_name)[0]}_out.docx"

    try:
        # 1. Telegramdan faylni yuklab olish
        new_file = await context.bot.get_file(file_id)
        await new_file.download_to_drive(pdf_path)

        # 2. PDF ni DOCX ga o'girish
        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()

        # 3. Tayyor faylni foydalanuvchiga yuborish
        await update.message.reply_document(
            document=open(docx_path, 'rb'),
            caption="✅ Mana sizning Word faylingiz! "
        )
        
        # Jarayon xabarini o'chirish (tozalash)
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=status_msg.message_id)

    except Exception as e:
        # Xatolikni qayd etish
        logging.error(f"Konvertatsiya xatosi: {e}", exc_info=True)
        
        # Haqiqiy xato nomini va xabarini foydalanuvchiga yuborish
        error_name = type(e).__name__
        error_message = str(e)
        
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=status_msg.message_id,
            text=f"❌ **Konvertatsiya bajarilmadi!**\n\n"
                 f"Bu faylni o'girib bo'lmadi. Eng keng tarqalgan sabablar:\n"
                 f"* Parollangan\n* Buzilgan struktura\n* Faqat rasm (skanerlangan)\n\n"
                 f"**Texnik xato turi:** `{error_name}`\n"
                 f"**Batafsil:** `{error_message[:100]}...`",
            parse_mode=constants.ParseMode.MARKDOWN
        )

    finally:
        # 4. Serverni tozalash (vaqtincha fayllarni o'chirish)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        if os.path.exists(docx_path):
            os.remove(docx_path)

if __name__ == '__main__':
    # Token borligini tekshirish
    if not TOKEN:
        print("Xatolik: BOT_TOKEN topilmadi. Iltimos, environment variable qo'shing.")
        exit(1)

    app = ApplicationBuilder().token(TOKEN).build()

    # Handlerlar
    app.add_handler(CommandHandler("start", start))
    
    # Faqat PDF hujjatni qabul qilish
    app.add_handler(MessageHandler(filters.Document.PDF, convert_pdf_to_docx))

    print("Bot ishga tushdi...")
    app.run_polling()
