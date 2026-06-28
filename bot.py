import os
import json
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from openai import OpenAI
from collections import defaultdict

# ================== الإعدادات ==================
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not TELEGRAM_TOKEN or not DEEPSEEK_API_KEY:
    raise ValueError("❌ المفاتيح غير موجودة! تأكد من ملف .env")

# ================== العميل ==================
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

# ================== بياناتك ==================
MY_WORKS = {
    "تصميم": "🎨 أقدم تصاميم جرافيك احترافية (شعارات - هويات - بوسترات)",
    "برمجة": "💻 أبني بوتات ومواقع ويب وتطبيقات ذكية",
    "تسويق": "📈 أدير حملات تسويقية وإعلانات مدفوعة",
    "استشارات": "🧠 استشارات تقنية ورقمية"
}

PAYMENT_METHODS = """
💳 **طرق الدفع المتاحة:**
• باي بال: example@paypal.com
• IBAN: SA1234567890123
• جوال: 0501234567 (تحويل سريع)
• عملات رقمية: USDT (TRC20)
"""

CONTACT_INFO = """
📩 **للتواصل:**
• واتساب: 0501234567
• تويتر: @yourhandle
• تيلغرام: @yourusername
• البريد الإلكتروني: example@email.com
"""

ABOUT_TEXT = """
🌟 **مرحباً بك في بوت خدمات شهاب!**

أنا بوت ذكي يجمع بين الخدمات الاحترافية والذكاء الاصطناعي.
أستطيع:
✅ عرض خدماتي
✅ الرد على استفساراتك
✅ مساعدتك في اختيار الخدمة المناسبة
✅ توجيهك لطرق الدفع والتواصل

استخدم الأوامر:
/start - للترحيب
/works - عرض الخدمات
/payment - طرق الدفع
/contact - معلومات التواصل
/about - عن البوت
/clear - مسح المحادثة
"""

# ================== الذاكرة ==================
sessions = defaultdict(list)
MAX_HISTORY = 10

# ================== الأوامر ==================
async def start(update: Update, context):
    await update.message.reply_text(ABOUT_TEXT)

async def works(update: Update, context):
    text = "🛠️ **خدماتي:**\n\n"
    for k, v in MY_WORKS.items():
        text += f"• **{k}**: {v}\n"
    text += "\n💡 أرسل سؤالك وسأساعدك في اختيار الخدمة المناسبة!"
    await update.message.reply_text(text)

async def payment(update: Update, context):
    await update.message.reply_text(PAYMENT_METHODS)

async def contact(update: Update, context):
    await update.message.reply_text(CONTACT_INFO)

async def about(update: Update, context):
    await update.message.reply_text(ABOUT_TEXT)

async def clear(update: Update, context):
    uid = update.effective_user.id
    sessions[uid] = []
    await update.message.reply_text("🧹 تم مسح المحادثة بنجاح!")

# ================== الرد الذكي ==================
async def reply(update: Update, context):
    uid = update.effective_user.id
    msg = update.message.text
    msg_lower = msg.lower()

    # ===== 1. حفظ الطلب في ملف =====
    try:
        with open("requests.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} | @{update.effective_user.username or 'مجهول'} | {msg}\n")
    except:
        pass

    # ===== 2. الكلمات المفتاحية (أولوية قصوى) =====
    if any(word in msg_lower for word in ["سعر", "تكلفة", "كم", "بكم"]):
        await update.message.reply_text(
            "💰 **الأسعار حسب الخدمة:**\n"
            "• التصميم: يبدأ من 200 ريال\n"
            "• البرمجة: يبدأ من 500 ريال\n"
            "• التسويق: يبدأ من 300 ريال\n"
            "• الاستشارات: 150 ريال/ساعة\n\n"
            "📩 أرسل /contact للتفاصيل الدقيقة"
        )
        return

    if any(word in msg_lower for word in ["دفع", "حساب", "تحويل", "باي بال"]):
        await update.message.reply_text(PAYMENT_METHODS)
        return

    if any(word in msg_lower for word in ["شكرا", "ممتاز", "جميل", "رائع"]):
        await update.message.reply_text("🙏 **العفو!** نحن في خدمتك دائماً.\nهل تحتاج مساعدة إضافية؟")
        return

    if any(word in msg_lower for word in ["خدمات", "شغلات", "تقدم"]):
        await update.message.reply_text(
            "🛠️ **خدماتي:**\n"
            "• تصميم جرافيك\n"
            "• برمجة وتطوير\n"
            "• تسويق وإعلانات\n"
            "• استشارات تقنية\n\n"
            "📌 أرسل /works للتفاصيل"
        )
        return

    # ===== 3. الذكاء الاصطناعي (DeepSeek) =====
    try:
        # حفظ تاريخ المحادثة
        sessions[uid].append({"role": "user", "content": msg})
        sessions[uid] = sessions[uid][-MAX_HISTORY:]

        # إرسال الطلب
        res = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[
                {"role": "system", "content": (
                    "أنت مساعد خدمة عملاء ذكي لرجل أعمال يقدم خدمات (تصميم، برمجة، تسويق، استشارات).\n"
                    "رد باختصار ومفيد، بلغة عربية فصحى أو عامية مفهومة.\n"
                    "إذا سأل عن الأسعار، قل أن الأسعار تبدأ من 200 ريال حسب الخدمة.\n"
                    "إذا سأل عن التواصل، وجهه لأمر /contact."
                )}
            ] + sessions[uid]
        )

        reply_text = res.choices[0].message.content
        sessions[uid].append({"role": "assistant", "content": reply_text})
        await update.message.reply_text(reply_text)

    except Exception as e:
        error_msg = str(e)
        if "402" in error_msg or "Insufficient Balance" in error_msg:
            await update.message.reply_text(
                "⚠️ **رصيد API غير كافٍ!**\n"
                "الرجاء شحن الرصيد من منصة DeepSeek.\n"
                "للتواصل المباشر أرسل /contact"
            )
        else:
            await update.message.reply_text(
                "📩 **شكراً لتواصلك!**\n"
                "سأرد عليك قريباً يدوياً.\n"
                "للتواصل المباشر: /contact"
            )

# ================== تشغيل البوت ==================
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("works", works))
    app.add_handler(CommandHandler("payment", payment))
    app.add_handler(CommandHandler("contact", contact))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("clear", clear))

    # الردود
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

    print("🤖 البوت شغال...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
