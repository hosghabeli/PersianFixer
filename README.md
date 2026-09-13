# PersianFixer 🇮🇷 🚀

<div align="center">
  <img src="https://files.catbox.moe/is7dtt.png" alt="PersianFixer Logo" width="128" height="128" />
  
  <h3>حل هوشمند مشکل زبان فارسی و فونت وزیرمتن در Google Antigravity و Claude Desktop</h3>
  <p><strong>Smart RTL & Vazirmatn Font Engine for Antigravity & Claude Desktop (Windows)</strong></p>

  [![Version](https://img.shields.io/badge/version-v3.0.0-blue.svg)](https://github.com/hosgh/PersianFixer/releases)
  [![Platform](https://img.shields.io/badge/platform-Windows%2010%20%2F%2011-0078D6.svg?logo=windows)](https://github.com/hosgh/PersianFixer)
  [![Font](https://img.shields.io/badge/font-Google%20Vazirmatn%20(Variable)-green.svg)](https://fonts.google.com/specimen/Vazirmatn)
  [![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)
</div>

---

## 📖 معرفی | Introduction

**PersianFixer** یک ابزار سبک، سریع و کاملاً بومی برای ویندوز است که به طور تخصصی برای حل مشکلات کار با زبان فارسی در نرم‌افزارهای دسکتاپ بر پایه Electron (مانند **Google Antigravity** و **Claude Desktop**) ساخته شده است.

این برنامه به طور خودکار:
1. **فونت رسمی و استاندارد وزیرمتن گوگل (Vazirmatn Variable)** را روی سیستم شما نصب و فعال می‌کند.
2. با یک کلیک فایل‌های برنامه را پچ کرده و **موتور هوشمند تشخیص جهت متن (RTL/LTR)** را فعال می‌سازد.
3. در پس‌زمینه در کنار ساعت ویندوز (System Tray) بی‌صدا می‌نشیند و به کمترین حافظه رم نیاز دارد.

---

## ✨ قابلیت‌های کلیدی | Features

- 🔤 **نصب خودکار فونت وزیرمتن گوگل**: بدون نیاز به دانلود جداگانه، فونت وزیرمتن متغیر (وزن‌های ۱۰۰ تا ۹۰۰) مستقیماً روی ویندوز ثبت و به صورت زنده منتشر می‌شود.
- 📐 **تشخیص خودکار و هوشمند جهت متن (RTL)**:
  - متن‌ها و پاراگراف‌های فارسی به صورت خودکار راست‌چین (`dir="rtl"`) می‌شوند.
  - باکس‌ها، چت‌ها، عناوین و لیست‌ها ظاهر فارسی استاندارد به خود می‌گیرند.
- 💻 **حفظ و تفکیک کدهای برنامه‌نویسی و کلمات انگلیسی (LTR)**:
  - بلاک‌های کد (`pre`, `code`)، مسیرهای فایل، دستورات ترمینال و متون انگلیسی دست‌نخورده و چپ‌چین می‌مانند.
- ⚡ **موتور نسل ۳ (Engine v3.0)**:
  - نفوذ به لایه‌های عمیق Shadow DOM و دیالوگ‌های داینامیک.
  - پیمایش مداوم و پایدار رویدادها (MutationObserver) با مهار خطاهای SVG در چت Antigravity.
  - شکستن Electron Fuses برای نسخه ویندوز Claude و پشتیبانی بی‌نقص از Antigravity.
- 🎨 **رابط کاربری مدرن و فارسی (Fluent Dark GUI)**:
  - نمایش زنده لاگ‌ها، وضعیت اتصال و دکمه‌های ۱-کلیک برای پچ و بازگردانی (Restore).
- 📌 **پشتیبانی از System Tray (کنار ساعت)**:
  - با بستن پنجره، برنامه بسته نمی‌شود بلکه به System Tray منتقل شده و از منوی راست‌کلیک قابل دسترس است.

---

## 📥 دانلود و استفاده سریع | Quick Start

### روش ۱: استفاده از نسخه آماده (پیشنهادی)
به بخش [Releases](https://github.com/hosgh/PersianFixer/releases) مراجعه کرده و آخرین نسخه فشرده را دانلود کنید:
1. فایل زیپ را اکسترکت کنید.
2. روی `PersianFixer.vbs` یا `run.bat` دابل‌کلیک کنید تا برنامه باز شود.
3. روی دکمه **«اعمال پچ فارسی (Patch)»** کلیک کنید!
4. نرم‌افزار Antigravity یا Claude را باز کنید و از تایپ و مطالعه روان فارسی لذت ببرید.

### روش ۲: اجرا از سورس کد (برای توسعه‌دهندگان)
پیش‌نیازها:
- پایتون ۳.۱۰ به بالا
- نود جی‌اس (Node.js) نسخه ۱۸ به بالا

```powershell
# ۱. کلون کردن مخزن
git clone https://github.com/hosgh/PersianFixer.git
cd PersianFixer

# ۲. نصب کتابخانه‌های پایتون
pip install -r requirements.txt

# ۳. نصب پکیج‌های Node.js (برای پچ ASAR)
npm install

# ۴. اجرای برنامه
python gui.py
```

---

## 🛠️ ساختار پروژه | Architecture

```text
PersianFixer/
├── fonts/
│   └── Vazirmatn.ttf       # فونت استاندارد متغیر گوگل
├── font_installer.py       # اسکریپت نصب فونت در رجیستری ویندوز و اطلاع‌رسانی به سیستم
├── persian_engine.js       # موتور تزریق استایل، فونت و MutationObserver هوشمند
├── asar_patcher.js         # پچر آرشیو Electron ASAR و تنظیم Fuses
├── patcher.py              # مدیریت پچ، پشتیبان‌گیری (Backup) و بازگردانی خودکار
├── gui.py                  # رابط گرافیکی تحت Tkinter با پشتیبانی از System Tray
├── update_icon.py          # اسکریپت تبدیل خودکار PNG به ICO و رفرش کش آیکون ویندوز
├── icon.ico / icon.png     # لوگوی برنامه با طراحی Fluent
├── PersianFixer.vbs        # لانچر مخفی بدون کنسول مشکی برای ویندوز
└── run.bat                 # لانچر مستقیم اسکریپت
```

---

## 📋 تاریخچه نسخه‌ها | Changelog

### Version 3.0.0 (پایدار - Stable)
- 🚀 **رفع باگ متوقف شدن راست‌چین**: ایزوله‌سازی المان‌های SVG در تایم‌لاین‌های وضعیت Antigravity (`Worked for 2m >`).
- 🔄 **پیمایش دوره‌ای (Continuous Sweep)**: تضمین راست‌چین شدن پاسخ‌های جریانی استریم بدون هیچ‌گونه پرش یا تاخیر.
- 🛡️ **پشتیبانی کامل از Claude Desktop**: بازنویسی پچر جهت تغییر بایت‌های Fuses در فایل `claude.exe` و حفظ دقیق اندازه هدر ASAR.
- 🖥️ **پشتیبانی از System Tray**: ادغام با `pystray`، دکمه Minimize to Tray و اجرای در پس‌زمینه.
- 🎨 **تغییر آسان آیکون**: ابزار `update_icon.bat` برای تبدیل طرح‌های شخصی‌سازی شده در Photoshop با پاکسازی کش آیکون ویندوز.

### Version 2.0.0
- افزودن رابط گرافیکی مشکی Fluent با پشتیبانی از لاگ زنده.
- اضافه شدن فونت متغیر وزیرمتن با نصب خودکار بدون نیاز به ادمین (Current User Fonts).
- ساخت لانچر بی‌صدا (`.vbs`).

### Version 1.0.0
- نسخه اولیه برای پچ دستی Antigravity `app.asar`.

---

## 🤝 مشارکت | Contributing

پیشنهادات و گزارش مشکلات (Issues) با کمال میل استقبال می‌شود! اگر ویژگی جدیدی مد نظرتان است، خوشحال می‌شویم Pull Request ارسال کنید.

---

## 📄 مجوز | License

این پروژه تحت مجوز [MIT](LICENSE) منتشر شده است. استفاده، تغییر و بازنشر آن برای همگان آزاد است.
