# 🛡️ PayGuard — Smart Payroll & Biometric Attendance System

<div align="center">

![PayGuard Banner](https://img.shields.io/badge/PayGuard-Enterprise%20v2.0-blue?style=for-the-badge&logo=shield)
![Python](https://img.shields.io/badge/Python-3.11%2B%20%7C%203.14-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Web%20Backend-black?style=for-the-badge&logo=flask)
![pywebview](https://img.shields.io/badge/GUI-PyWebView%20Desktop-4CAF50?style=for-the-badge)
![Security](https://img.shields.io/badge/Security-PyArmor%20Encrypted-red?style=for-the-badge&logo=security)
![Bilingual](https://img.shields.io/badge/Languages-Arabic%20%7C%20English-emerald?style=for-the-badge)

**نظام ذكي متكامل ومحمي لإدارة كشوف الرواتب، وسجلات الحضور والانصراف، والأرصدة المالية والسلف**

[المميزات](#-key-features) • [هيكل المشروع](#-project-architecture) • [طريقة التشغيل](#-getting-started) • [الأمان والتشفير](#-security--client-distribution)

</div>

---

## 🌟 Overview / نبذة عن النظام

**PayGuard** هو تطبيق مكتبي احترافي متكامل مصمم للشركات والمؤسسات لأتمتة عملية حساب المرتبات الشهرية مباشرة من ملفات البصمة الخام (ZKTeco)، مع تقديم واجهة مستخدم مؤسسية عصرية (SaaS Dashboard)، ورقابة مالية صارمة على سلف الموظفين، وأرشفة تاريخية دائمة لكافة الشهور السابقة، وتوليد تقارير PDF وإكسيل احترافية باللغتين العربية والإنجليزية.

---

## ✨ Key Features / أهم المميزات

### 1. 🔍 Biometric Attendance Engine (محرك قراءة البصمة الذكي)
- قراءة ومعالجة ملفات البصمة الخام (`.txt` / `.log`) الصادرة من ماكينات ZKTeco ومثيلاتها.
- استكشاف تلقائي لاسم الشهر، السنة، وعدد الأيام الفعلية (28، 29، 30، 31).
- احتساب أوقات الحضور والانصراف وساعات العمل اليومية تلقائياً، مع رصد بصمات أيام الجمعة والغياب.

### 2. 💰 Financial & Payroll Precision (دقة الحسابات والأرقام العشرية)
- دعم كامل لكتابة وقراءة الأرقام العشرية والكسور في كافة الحقول المالية (المرتبات، البونص، الخصومات، السلف).
- احتساب دقيق لمعدل اليوم ومعدل الساعة.
- احتساب حافز عمل أيام الجمعة بمعامل مضاعفة مرن (افتراضياً 2X أو ما يحدده المدير).
- احتساب أجر الساعات الإضافية (Overtime) وإضافتها آلياً للصافي.

### 3. 💳 Loan & Advance Balance Control (إدارة ومراقبة رصيد السلف)
- تسجيل رصيد السلفة الإجمالي وترحيل المتبقي شهرياً بشكل تلقائي في بطاقة الموظف.
- **رقابة حاسمة على تجاوز الرصيد (Over-deduction Alert):** إذا تجاوز القسط المطلوب خصمه رصيد السلفة (مثال: سلفة 500 وخصم 600):
  - يظهر تحذير لوني أحمر فوري بالواجهة.
  - رسالة تأكيد إجبارية للمدير لاعتماد الخصم الزائد.
  - تسجيل الرصيد بالسالب كـ (سلفة دائنة للموظف).

### 4. 🗄️ Historical Monthly Archive (أرشيف الشهور وقاعدة البيانات)
- قاعدة بيانات SQLite محلية مدمجة وسريعة (`payroll.db`).
- استعراض أو تعديل أو تصدير أي شهر محفوظ سابقاً بضغطة زر.
- زر مخصص **"💾 حفظ الكشف بالكامل"** لحفظ كافة الموظفين وتعديلاتهم دفعة واحدة.
- إمكانية إضافة موظف يدوياً دون الحاجة لسجل بصمة.

### 5. 📑 Bilingual PDF Payslips & Excel Export (التقارير والمخرجات)
- **قسيمة راتب فردية PDF:** توليد وطباعة ملف PDF منفصل لكل موظف باسمه والشهر (مثل: `مفردات_مرتب_محمد_يوليو 2026.pdf` أو `Salary_Slip_Mohamed_July 2026.pdf`) يتضمن جدول الحضور اليومي والبيانات المالية.
- **كشف إكسيل Excel شامل:** تصدير كشف الشهر بالكامل بتنسيق وألوان محاسبية رسمية مع اتجاه الصفحة المناسب (RTL / LTR).

### 6. 🌐 100% Bilingual Interface (ثنائية اللغة العربية والإنجليزية)
- زر تبديل فوري للغة (`🌐 English` / `🌐 العربية`) في شريط العنوان مع تغيير فوري للاتجاه (RTL / LTR).
- دعم الخطوط الحديثة (`Plus Jakarta Sans` للإنجليزية، و `Cairo` للعربية).
- حفظ تفضيل اللغة تلقائياً في `localStorage`.

### 7. 🔒 Standalone Executable & Obfuscation (التشفير والحماية)
- كود مصدري محمي ومشفر بالكامل عبر **PyArmor** لمنع التعديل أو الهندسة العكسية.
- ملف تنفيذي مستقل واحد (`PayGuard.exe`) يعمل على أجهزة Windows دون الحاجة لتثبيت بايثون أو أي برامج وسيطة.

---

## 📂 Project Architecture / هيكل المشروع

```text
PayGuard/
├── app.py                     # نقطة الانطلاق والخادم المحلي (Flask + pywebview)
├── database.py                # إدارة قاعدة البيانات والجداول SQLite
├── payroll_engine.py          # محرك الحسابات المالية ومعدلات الأجر والسلف
├── zkteco_parser.py           # معالج سجلات بصمة ZKTeco وتحليل الشهور
├── exporter.py                # وحدة تصدير كشوفات الإكسيل (openpyxl)
├── pdf_generator.py           # وحدة إنشاء قسائم الرواتب الفردية A4 PDF
├── test_payroll.py            # حزمة الاختبارات الآلية الشاملة
├── templates/
│   └── index.html             # واجهة المستخدم العصرية (PayGuard Enterprise SPA)
├── build_exe.bat              # سكريبت أتمتة التشفير وبناء ملف EXE للعميل
├── run_app.bat                # سكريبت تشغيل التطبيق في وضع التطوير
├── PayGuard.spec              # إعدادات حزم PyInstaller
├── requirements.txt           # متطلبات ومكتبات بايثون
├── شهر.txt                    # ملف بصمة تجريبي متكامل
├── .gitignore                 # استثناء مخلفات البناء وقواعد البيانات
└── README.md                  # التوثيق الشامل للنظام
```

---

## 🚀 Getting Started / طريقة التشغيل

### 1. وضع المطور (Development Mode)
```bash
# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل الاختبارات الآلية
python test_payroll.py

# تشغيل التطبيق
python app.py
# أو عبر النقر المزدوج على run_app.bat
```

### 2. بناء ملف التشغيل المشفر للعميل (Build Standalone EXE)
```bash
# بناء وتشفير ملف PayGuard.exe
build_exe.bat
```
سيتم إنشاء ملف `PayGuard.exe` محمي ومشفر 100% ووضعه داخل مجلد:
```text
النسخة_المشفرة_للعميل\PayGuard.exe
```

---

## 🛡️ Security & Licensing

- **Code Protection:** All business logic files (`app.py`, `database.py`, `zkteco_parser.py`, `payroll_engine.py`, `exporter.py`, `pdf_generator.py`) are hardened and obfuscated with **PyArmor 9+**.
- **Developer:** Abdelhamed Mohamed
