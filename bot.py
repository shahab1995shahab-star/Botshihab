import os
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

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

# ================== ذاكرة المحادثة ==================
sessions = defaultdict(list)
MAX_HISTORY = 10

# ================== بيانات متجر الرياض التعليمي ==================

STORE_NAME = "🏫 متجر الرياض التعليمي"

ABOUT_TEXT = f"""
🌟 **{STORE_NAME}**

متجر الرياض التعليمي هو منصة رائدة ومتخصصة في تقديم الحلول التعليمية الجاهزة للمعلمين والمعلمات والمشرفين التربويين في المملكة العربية السعودية والوطن العربي.

نؤمن بأن التعليم هو أساس نهضة الأمم، ونسعى من خلال خدماتنا إلى تمكين الكوادر التعليمية من أداء رسالتهم النبيلة بكفاءة واحترافية.

📌 **رؤيتنا:**
أن نكون الشريك الأول والأكثر ثقة للمعلمين والمعلمات في رحلتهم التعليمية.

📚 **رسالتنا:**
تقديم ملفات تعليمية جاهزة ومتكاملة، مصممة بأعلى معايير الجودة والاحترافية.

🤍 **شعارنا:**
"نوفر وقتك.. ننفذ طلبك.. بجودة تحترم تعبك"

📞 للتواصل: /contact
🛒 لمعرفة الخدمات: /services
💰 للأسعار: /prices
"""

SERVICES_TEXT = """
🛒 **منتجاتنا وخدماتنا:**

1️⃣ 📋 **ملفات الأداء الوظيفي**
   · نماذج إلكترونية وورقية متكاملة
   · ملفات الأداء الوظيفي الإلكترونية والورقية
   · أدوات تقويم الأداء وفق أحدث الأنظمة

2️⃣ 📊 **اختبارات نافس**
   · نماذج محاكية لاختبارات نافس الوطنية
   · تغطي جميع المراحل (الابتدائي والمتوسط)
   · لجميع المواد (عربي، رياضيات، علوم)

3️⃣ 🩺 **الخطط العلاجية والإثرائية**
   · خطط علاجية لمعالجة الفاقد التعليمي
   · خطط إثرائية لتنمية مهارات المتميزين
   · تغطي جميع المراحل والمواد

4️⃣ 📑 **عروض بوربوينت بالذكاء الاصطناعي**
   · عروض احترافية وجذابة
   · تفاعلية ومصممة بأحدث التقنيات
   · تغطي المنهج كاملاً أو حسب الطلب

5️⃣ 📄 **أوراق عمل احترافية**
   · مميزة ومتنوعة
   · وفق معايير التعلم النشط
   · قابلة للتعديل لتناسب جميع المستويات

6️⃣ 📻 **الإذاعة المدرسية بالذكاء الاصطناعي**
   · نصوص إذاعية جاهزة ومخصصة
   · محتوى إذاعي كامل لـ 12 شهراً

📩 للطلب: /order
💰 للأسعار: /prices
📞 للتواصل: /contact
"""

PRICES_TEXT = """
💰 **أسعارنا التنافسية:**

📋 ملفات الأداء الوظيفي: **١٢٠ ريال**
📊 اختبارات نافس (لكل مادة): **٧٠ ريال**
🩺 خطط علاجية وإثرائية (لكل مادة): **٧٠ ريال**
📑 عروض بوربوينت (لكل درس): **٢٥ ريال**
📄 أوراق عمل (لكل ورقة): **١٠ ريال**
📻 الإذاعة المدرسية (شهر كامل): **١٠٠ ريال**

🎁 **عروض خاصة:**
· حزمة المواد الثلاث (نافس + علاجي + إثرائي): **١٨٠ ريال**
· حزمة الفصل الدراسي كاملاً: **٥٠٠ ريال**

📩 للطلب: /order
"""

CONTACT_TEXT = """
📞 **طرق التواصل معنا:**

📧 البريد الإلكتروني: shahab1995shahab@gmail.com

📱 واتساب: [اضغط هنا للتواصل](https://wa.me/966578371223)

📲 تليجرام: @alryadplay

📍 الموقع: الرياض – المملكة العربية السعودية
نخدم جميع مناطق المملكة عبر التواصل الإلكتروني.

🕐 الدعم الفني متاح على مدار الساعة.
"""

ORDER_TEXT = """
📝 **لطلب ملفاتك التعليمية:**

يرجى إرسال المعلومات التالية على واتساب:
https://wa.me/966578371223

📌 البيانات المطلوبة:
1. اسم الملف المطلوب
2. المرحلة الدراسية
3. المادة
4. الصف
5. الفصل الدراسي
6. أي تفاصيل إضافية

📞 أو تواصل معنا مباشرة على تليجرام: @alryadplay

✅ سيتم الرد عليك في أقرب وقت ممكن.
"""

WHY_US_TEXT = """
💎 **لماذا تختار متجر الرياض التعليمي؟**

1️⃣ **الجودة والاحترافية**
   · منتجاتنا مصممة بأعلى معايير الجودة من قبل خبراء تربويين

2️⃣ **توفير الوقت والجهد**
   · نوفر عليك ساعات من العمل في إعداد الملفات والخطط

3️⃣ **قابلة للتعديل والتخصيص**
   · جميع الملفات بصيغ قابلة للتعديل (Word، PowerPoint)

4️⃣ **الذكاء الاصطناعي في التعليم**
   · نستخدم أحدث التقنيات لتصميم عروض وألعاب تفاعلية

5️⃣ **التحديث المستمر**
   · نواكب أحدث التغييرات في المناهج والأنظمة

6️⃣ **الدعم الفني المتميز**
   · فريقنا متاح على مدار الساعة

7️⃣ **أسعار تنافسية**
   · منتجاتنا بأسعار مناسبة مع أعلى مستويات الجودة

🤍 **شعارنا:**
"نوفر وقتك.. ننفذ طلبك.. بجودة تحترم تعبك"
"""

# ================== أوامر البوت ==================

async def start(update: Update, context):
    await update.message.reply_text(ABOUT_TEXT)

async def services(update: Update, context):
    await update.message.reply_text(SERVICES_TEXT)

async def prices(update: Update, context):
    await update.message.reply_text(PRICES_TEXT)

async def contact(update: Update, context):
    await update.message.reply_text(CONTACT_TEXT)

async def order(update: Update, context):
    await update.message.reply_text(ORDER_TEXT)

async def why_us(update: Update, context):
    await update.message.reply_text(WHY_US_TEXT)

async def clear(update: Update, context):
    uid = update.effective_user.id
    sessions[uid] = []
    await update.message.reply_text("🧹 تم مسح المحادثة بنجاح!")

async def about(update: Update, context):
    await update.message.reply_text(ABOUT_TEXT)

# ================== الرد الذكي ==================

async def reply(update: Update, context):
    uid = update.effective_user.id
    msg = update.message.text
    msg_lower = msg.lower()

    # تسجيل الطلبات
    try:
        with open("requests.txt", "a", encoding="utf-8") as f:
            username = update.effective_user.username or "مجهول"
            f.write(f"{datetime.now()} | @{username} | {msg}\n")
    except:
        pass

    # ===== كلمات مفتاحية سريعة =====

    if any(w in msg_lower for w in ["سعر", "تكلفة", "بكم", "كم"]):
        await update.message.reply_text(PRICES_TEXT)
        return

    if any(w in msg_lower for w in ["طلب", "اشتري", "شراء", "طلبك", "/order"]):
        await update.message.reply_text(ORDER_TEXT)
        return

    if any(w in msg_lower for w in ["خدمات", "منتجات", "تقدمون", "عندكم"]):
        await update.message.reply_text(SERVICES_TEXT)
        return

    if any(w in msg_lower for w in ["تواصل", "رقم", "جوال", "واتس", "تليجرام"]):
        await update.message.reply_text(CONTACT_TEXT)
        return

    if any(w in msg_lower for w in ["شكرا", "ممتاز", "جميل", "رائع", "الله يبارك"]):
        await update.message.reply_text(
            "🙏 **العفو!** نحن في خدمتك دائماً.\n"
            "هل تحتاج مساعدة إضافية؟\n"
            "📞 للتواصل: /contact"
        )
        return

    if any(w in msg_lower for w in ["من أنتم", "من انتم", "نبذة", "عنكم"]):
        await update.message.reply_text(ABOUT_TEXT)
        return

    # ===== الذكاء الاصطناعي =====

    try:
        sessions[uid].append({"role": "user", "content": msg})
        sessions[uid] = sessions[uid][-MAX_HISTORY:]

        res = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[
                {"role": "system", "content": (
                    "أنت مساعد خدمة عملاء لمتجر الرياض التعليمي.\n"
                    "متجر متخصص في الملفات التعليمية للمعلمين في السعودية.\n"
                    "الخدمات: ملفات أداء وظيفي، اختبارات نافس، خطط علاجية وإثرائية، عروض بوربوينت، أوراق عمل، إذاعة مدرسية.\n"
                    "رد باختصار ومفيد، بلغة عربية فصحى.\n"
                    "إذا سأل عن الأسعار، قل: للأسعار أرسل /prices\n"
                    "إذا سأل عن الطلب، قل: للطلب أرسل /order\n"
                    "إذا سأل عن التواصل، قل: للتواصل أرسل /contact"
                )}
            ] + sessions[uid]
        )

        reply_text = res.choices[0].message.content
        sessions[uid].append({"role": "assistant", "content": reply_text})
        await update.message.reply_text(reply_text)

    except Exception as e:
        if "402" in str(e) or "Insufficient Balance" in str(e):
            await update.message.reply_text(
                "⚠️ **رصيد API غير كافٍ!**\n"
                "الرجاء شحن الرصيد من منصة DeepSeek.\n"
                "📞 للتواصل المباشر: /contact"
            )
        else:
            await update.message.reply_text(
                "📩 **شكراً لتواصلك!**\n"
                "سيتم الرد عليك قريباً.\n"
                "📞 للتواصل المباشر: /contact"
            )

# ================== تشغيل البوت ==================

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("services", services))
    app.add_handler(CommandHandler("prices", prices))
    app.add_handler(CommandHandler("contact", contact))
    app.add_handler(CommandHandler("order", order))
    app.add_handler(CommandHandler("whyus", why_us))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("clear", clear))

    # الردود
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

    print("🤖 بوت متجر الرياض التعليمي شغال...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
