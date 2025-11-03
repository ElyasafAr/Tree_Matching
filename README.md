# 🌳 Tree Matching

אתר היכרויות מבוסס המלצות אישיות - כל משתמש חייב להיות מקושר למשתמש קיים שממליץ עליו.

## 🎯 תכונות

### Backend (Flask + PostgreSQL)
- ✅ מערכת אימות מאובטחת (JWT)
- ✅ הצפנת נתונים רגישים (שם, אימייל, טלפון, כתובת, סיסמה)
- ✅ מערכת המלצות (Referral System) - מבנה עץ
- ✅ חיפוש משתמשים עם סינון
- ✅ מערכת לייקים והתאמות
- ✅ צ'אט בין משתמשים
- ✅ אפשרות ליצירת קשר עם הממליץ

### Frontend (React + Vite)
- ✅ ממשק משתמש מודרני ויפה
- ✅ רישום והתחברות
- ✅ חיפוש משתמשים עם פילטרים
- ✅ פרופיל משתמש (צפייה ועריכה)
- ✅ מערכת צ'אט בסיסית
- ✅ הצגת עץ המלצות
- ✅ רשימת התאמות
- ✅ יצירת קשר עם ממליצים

## 🚀 התקנה והרצה

### דרישות מוקדמות
- Python 3.8+
- Node.js 18+
- PostgreSQL Database (מומלץ על Railway)

### Backend Setup

1. **עבור לתיקיית backend:**
\`\`\`bash
cd backend
\`\`\`

2. **התקן תלויות Python:**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

3. **הגדר משתני סביבה:**
צור קובץ \`.env\` על בסיס \`.env.example\`:
\`\`\`bash
# Database (Railway PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/dbname

# JWT Secret (create random string)
JWT_SECRET_KEY=your-secret-key-here

# Encryption Key (generate using Python)
ENCRYPTION_KEY=your-encryption-key-here

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
\`\`\`

4. **צור Encryption Key:**
\`\`\`python
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
\`\`\`

5. **הרץ את השרת:**
\`\`\`bash
python app.py
\`\`\`

השרת ירוץ על http://localhost:5000

### Frontend Setup

1. **עבור לתיקיית frontend:**
\`\`\`bash
cd frontend
\`\`\`

2. **התקן תלויות:**
\`\`\`bash
npm install
\`\`\`

3. **הגדר משתני סביבה:**
צור קובץ \`.env\` על בסיס \`.env.example\`:
\`\`\`
VITE_API_URL=http://localhost:5000
\`\`\`

4. **הרץ את הפרונט-אנד:**
\`\`\`bash
npm run dev
\`\`\`

האתר יהיה זמין על http://localhost:5173

## 📦 Deploy ל-Railway

### Backend Deployment

1. צור פרויקט חדש ב-Railway
2. הוסף PostgreSQL Database
3. הוסף את ה-Backend כ-Service
4. הגדר את משתני הסביבה:
   - \`DATABASE_URL\` - מתקבל אוטומטית מ-PostgreSQL
   - \`JWT_SECRET_KEY\` - צור סיסמה חזקה
   - \`ENCRYPTION_KEY\` - השתמש בקוד Python שלמעלה
   - \`FLASK_ENV=production\`
   - \`FLASK_DEBUG=False\`

### Frontend Deployment

1. עדכן את \`VITE_API_URL\` ב-.env ל-URL של ה-Backend ב-Railway
2. בנה את הפרויקט:
\`\`\`bash
npm run build
\`\`\`
3. העלה את תיקיית \`dist\` לשירות Hosting (Netlify, Vercel, Railway)

## 🔐 אבטחה

- סיסמאות מוצפנות עם bcrypt
- שדות רגישים (שם, אימייל, טלפון, כתובת) מוצפנים במסד הנתונים
- JWT tokens לאימות
- CORS מוגדר בשרת
- הגנה על routes פרטיים

## 📁 מבנה הפרויקט

\`\`\`
Tree_Matching_webSite/
├── backend/
│   ├── app.py              # Flask app ראשי
│   ├── models.py           # SQLAlchemy models
│   ├── auth.py             # Authentication routes
│   ├── encryption.py       # Encryption service
│   ├── config.py           # Configuration
│   ├── routes/
│   │   ├── users.py        # User management routes
│   │   ├── chat.py         # Chat routes
│   │   └── referrals.py    # Referral system routes
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API calls
│   │   ├── context/       # React Context (Auth)
│   │   ├── utils/         # Utilities
│   │   ├── App.jsx        # Main app with routing
│   │   └── main.jsx       # Entry point
│   └── package.json
│
├── .gitignore
└── README.md
\`\`\`

## 🗄️ מבנה מסד הנתונים

### Users
- פרטים אישיים (מוצפנים)
- קוד המלצה ייחודי
- מידע פומבי (גיל, מגדר, מיקום, bio)

### Referrals
- referrer_id -> referred_id
- מבנה עץ של המלצות

### Chats & Messages
- שיחות בין משתמשים
- הודעות עם timestamp

### Matches
- לייקים בין משתמשים
- סימון התאמות הדדיות

## 🎨 עיצוב

האתר בנוי עם עיצוב מודרני:
- צבעים: גרדיאנט סגול-כחול (#667eea → #764ba2)
- Responsive design
- אנימציות חלקות
- UX אינטואיטיבי

## 📝 רישום משתמש ראשון

כדי ליצור משתמש ראשון (Root) שאין לו ממליץ:
1. הוסף משתמש ידנית למסד הנתונים
2. או צור endpoint מיוחד ל-"bootstrap" של המשתמש הראשון
3. משתמש זה יקבל קוד המלצה שאפשר לשתף

## 🤝 תרומה

הפרויקט פרטי. לשאלות או בעיות, צור קשר עם המפתח.

## 📄 License

This project is private and proprietary.

---

Made with ❤️ by Elyasaf

