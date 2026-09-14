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
├── .github/
│   └── workflows/
│       └── build.yml          # مسار البناء التلقائي عبر GitHub Actions (Win/Mac/Linux)
├── build_exe.bat              # سكريبت أتمتة التشفير وبناء ملف EXE للعميل
├── run_app.bat                # سكريبت تشغيل التطبيق في وضع التطوير
├── PayGuard.spec              # إعدادات حزم PyInstaller العابرة للمنصات
├── requirements.txt           # متطلبات ومكتبات بايثون
├── شهر.txt                    # ملف بصمة تجريبي متكامل
├── .gitignore                 # استثناء مخلفات البناء وقواعد البيانات
└── README.md                  # التوثيق الشامل للنظام
```

---

## 📥 تنزيل الإصدارات الجاهزة (Download Ready Releases)

يمكن للمستخدم النهائي تحميل أحدث إصدار تنفيذي جاهز للعمل مباشرة من صفحة **[Releases](../../releases)**:

| المنصة (OS) | الملف القابل للتحميل | طريقة التشغيل |
|---|---|---|
| **Windows (x64)** | `PayGuard-Windows-x64.exe` | تشغيل مباشر (Portable) بدون تثبيت |
| **macOS (Intel & Apple Silicon)** | `PayGuard-macOS-Universal.zip` | فك الضغط ثم فتح `PayGuard.app` |
| **Linux (All Distros)** | `PayGuard-Linux-x86_64.AppImage` | إعطاء صلاحية تشغيل (`chmod +x`) ثم تشغيل مباشر |

> ### 🍎 ملاحظة لمستخدمي macOS (Apple Gatekeeper):
> نظراً لأن التطبيق غير موقّع رسمياً بشهادة Apple Developer مدفوعة، سيظهر لك نظام macOS تنبيهاً يفيد بأن التطبيق من مطور غير معروف (Unidentified Developer) عند الفتح لأول مرة:
> 1. بعد فك الضغط، اضغط بالزر الأيمن (Right-click) على `PayGuard.app` واختر **Open** ثم اضغط **Open** في النافذة.
> 2. أو توجه إلى: **System Settings → Privacy & Security** واضغط على زر **Open Anyway**.

---

## 🚀 طريقة التشغيل والبناء محلياً (Local Build for Developers)

### 1. وضع التطوير السريع (Development Mode)
```bash
# تثبيت المكتبات والمتطلبات
pip install -r requirements.txt

# تشغيل الاختبارات الآلية للتأكد من سلامة النظام
python test_payroll.py

# تشغيل التطبيق محلياً
python app.py
```

### 2. البناء المحلي كملف تنفيذي (Build Locally)

#### على ويندوز (Windows):
```bash
build_exe.bat
# أو مباشرة:
pyinstaller --noconfirm PayGuard.spec
```

#### على ماك (macOS):
```bash
pyinstaller --noconfirm PayGuard.spec
# سيتم إنشاء حزمة PayGuard.app داخل مجلد dist/
```

#### على لينكس (Linux):
```bash
sudo apt-get install -y libgtk-3-dev libgirepository1.0-dev gir1.2-webkit2-4.0
pyinstaller --noconfirm PayGuard.spec
# سيتم إنشاء ملف PayGuard داخل مجلد dist/
```

---

## 🔄 نظام البناء التلقائي (CI/CD via GitHub Actions)

يتضمن المشروع ملف سير عمل تلقائي داخل `.github/workflows/build.yml`:
- **البناء التلقائي عند إطلاق إصدار:** بمجرد عمل `git tag v1.0.0` وعمل `git push origin v1.0.0`، يقوم سير العمل تلقائياً ببناء واختبار حزم Windows و macOS و Linux ورفعها كمرفقات داخل صفحة Releases.
- **التشغيل اليدوي (Manual Dispatch):** يمكنك تجربة البناء في أي وقت بالضغط على **Run workflow** من تبويب **Actions** في GitHub.

---

## 🛡️ Security & Licensing

- **Code Protection:** All business logic files (`app.py`, `database.py`, `zkteco_parser.py`, `payroll_engine.py`, `exporter.py`, `pdf_generator.py`) are hardened and obfuscated with **PyArmor**.
- **Developer:** Abdelhamed Mohamed
