import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from pdf2docx import Converter

# Loglarni sozlash (xatolarni ko'rish uchun)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- KONFIGURATSIYA ---
# Railway Environment Variable orqali tokenni olamiz
TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi /start bosganda ishlaydi"""
    await update.message.reply_text(
        "Assalomu alaykum! Menga PDF fayl yuboring, men uni DOCX (Word) formatiga o'girib beraman."
    )

async def convert_pdf_to_docx(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """PDF faylni qabul qilib, DOCX ga aylantiradi"""
    user = update.message.from_user
    file_id = update.message.document.file_id
    file_name = update.message.document.file_name

    # Faqat .pdf fayllarni qabul qilish
    if not file_name.lower().endswith('.pdf'):
        await update.message.reply_text("Iltimos, faqat PDF fayl yuboring.")
        return

    status_msg = await update.message.reply_text("Fayl qabul qilindi. Konvertatsiya qilinmoqda, kuting...")

    # Fayl nomlarini tayyorlash
    pdf_path = f"{file_id}.pdf"
    docx_path = f"{os.path.splitext(file_name)[0]}.docx"

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
            caption="Mana sizning Word faylingiz! 📄"
        )
        
        # Xabar yangilash
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=status_msg.message_id)

    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await update.message.reply_text("Kechirasiz, faylni o'girishda xatolik yuz berdi. Fayl buzilgan yoki shifrlangan bo'lishi mumkin.")

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
    
    # Faqat hujjat (Document) va PDF bo'lsa ishlaydi
    app.add_handler(MessageHandler(filters.Document.PDF, convert_pdf_to_docx))

    print("Bot ishga tushdi...")
    app.run_polling()
