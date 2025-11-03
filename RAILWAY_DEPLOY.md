# 🚂 מדריך העלאה ל-Railway - צעד אחר צעד

## 📋 סקירה כללית

ב-Railway נעלה:
1. **PostgreSQL Database** (מאגר נתונים)
2. **Backend Flask Server** (השרת)

ה-Frontend נעלה לפלטפורמה אחרת (Netlify/Vercel).

---

## שלב 1️⃣: הכנת Git Repository

### 1.1 אתחול Git (אם עדיין לא עשית)

```bash
git init
git add .
git commit -m "Initial commit - Tree Matching project"
```

### 1.2 העלאה ל-GitHub

1. **צור repository חדש ב-GitHub:**
   - גש ל-https://github.com/new
   - שם: `Tree_Matching`
   - **סמן:** Private (פרטי) ✓
   - לחץ "Create repository"

2. **חבר את הפרוייקט:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/Tree_Matching.git
   git branch -M main
   git push -u origin main
   ```

---

## שלב 2️⃣: Railway - Database

### 2.1 יצירת PostgreSQL

1. **גש ל:** https://railway.app/
2. **התחבר עם GitHub**
3. **לחץ:** "New Project"
4. **בחר:** "Provision PostgreSQL"
5. ✅ **Database נוצר!**

### 2.2 שמור את ה-DATABASE_URL

1. **לחץ על ה-PostgreSQL** שנוצר
2. **לשונית "Variables"** או "Connect"
3. **העתק את:** `DATABASE_URL`
   ```
   postgresql://postgres:XXX@containers.railway.app:1234/railway
   ```
4. **שמור בצד** - נצטרך בהמשך

---

## שלב 3️⃣: Railway - Backend Server

### 3.1 הוספת השרת לאותו Project

1. **באותו Project** (עם ה-PostgreSQL), לחץ **"+ New"**
2. **בחר:** "GitHub Repo"
3. **אשר גישה** ל-GitHub (אם צריך)
4. **בחר את הרפוזיטורי:** `Tree_Matching`
5. Railway מזהה אוטומטית שזה Python!

### 3.2 הגדרת Root Directory

⚠️ **חשוב!** השרת נמצא בתיקיית `backend`, לא בשורש:

1. **לחץ על ה-Service** שנוצר
2. **Settings** → **Source**
3. **Root Directory:** הזן `backend`
4. **שמור**

### 3.3 הגדרת משתני סביבה (Environment Variables)

1. **לשונית "Variables"**
2. **הוסף את המשתנים הבאים:**

#### משתנה 1: DATABASE_URL
```
DATABASE_URL
```
**ערך:** הדבק את ה-URL שהעתקת בשלב 2.2

#### משתנה 2: JWT_SECRET_KEY
```
JWT_SECRET_KEY
```
**ערך:** צור סיסמה חזקה, למשל:
```
tree-matching-super-secret-key-2024-production
```

#### משתנה 3: ENCRYPTION_KEY

**תחילה צור את המפתח:**

```bash
cd backend
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**תקבל משהו כמו:**
```
gAAAAABmK9X8_random_string_here_==
```

**הוסף משתנה:**
```
ENCRYPTION_KEY
```
**ערך:** הדבק את המפתח שיצרת

#### משתנה 4: FLASK_ENV
```
FLASK_ENV
```
**ערך:**
```
production
```

#### משתנה 5: FLASK_DEBUG
```
FLASK_DEBUG
```
**ערך:**
```
False
```

### 3.4 חבר את Database ל-Backend (אוטומטי)

Railway אמור לזהות אוטומטית את החיבור. אם לא:
1. **Settings** → **Service Variables**
2. ודא שיש **Reference to PostgreSQL**

### 3.5 Deploy!

1. Railway יתחיל **אוטומטית** לבנות ולהעלות
2. **צפה בלוגים** ב-"Deployments" → "View Logs"
3. **המתן** כ-2-5 דקות
4. ✅ כשהסטטוס **"Success"** - השרת פעיל!

### 3.6 קבל את ה-URL של השרת

1. **Settings** → **Networking**
2. **לחץ:** "Generate Domain"
3. **העתק את ה-URL**, למשל:
   ```
   https://tree-matching-production.up.railway.app
   ```
4. ✅ **שמור את זה** - הפרונט-אנד יצטרך!

---

## שלב 4️⃣: אתחול Database (פעם אחת)

⚠️ **לאחר ה-Deploy הראשון**, צריך ליצור את המשתמש הראשון.

### אופציה A: דרך Railway CLI (מומלץ)

1. **התקן Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **התחבר:**
   ```bash
   railway login
   ```

3. **קישור לפרויקט:**
   ```bash
   railway link
   ```
   בחר את הפרויקט שלך

4. **הרץ סקריפט:**
   ```bash
   railway run python backend/create_first_user.py
   ```

### אופציה B: דרך Local (פשוט יותר)

1. **בקובץ `backend/.env` שלך LOCAL:**
   ```env
   DATABASE_URL=<ההURL מRailway>
   JWT_SECRET_KEY=<אותו ערך מRailway>
   ENCRYPTION_KEY=<אותו ערך מRailway>
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

2. **הרץ:**
   ```bash
   cd backend
   python init_db.py
   python create_first_user.py
   ```

3. **שמור את קוד ההמלצה!** 🎫

---

## שלב 5️⃣: בדיקה

### בדוק שהשרת עובד:

1. **פתח בדפדפן:**
   ```
   https://YOUR-APP.up.railway.app/
   ```

2. **אמור לראות:**
   ```json
   {
     "status": "ok",
     "message": "Tree Matching API is running"
   }
   ```

3. ✅ **עובד!** השרת חי ב-Railway

---

## שלב 6️⃣: Frontend Setup

עכשיו שיש לך Backend חי, עדכן את הפרונט-אנד:

### 6.1 עדכן את ה-URL

**בקובץ `frontend/.env`:**
```env
VITE_API_URL=https://YOUR-APP.up.railway.app
```

### 6.2 הרץ Locally

```bash
cd frontend
npm run dev
```

### 6.3 בדוק התחברות

1. פתח http://localhost:5173
2. נסה להירשם עם קוד ההמלצה
3. ✅ אמור לעבוד!

---

## 📊 סיכום - מה יש לך עכשיו?

```
┌─────────────────┐
│   Frontend      │ ← localhost:5173 (פיתוח)
│   (React)       │    או Netlify (ייצור)
└────────┬────────┘
         │
         │ API Calls
         │
         ↓
┌─────────────────┐
│   Backend       │ ← Railway
│   (Flask)       │    https://xxx.railway.app
└────────┬────────┘
         │
         │ SQL Queries
         │
         ↓
┌─────────────────┐
│   PostgreSQL    │ ← Railway
│   (Database)    │
└─────────────────┘
```

---

## 🎯 השלב הבא

עכשיו אתה יכול:
1. ✅ לפתח את הפרונט-אנד locally
2. ✅ להעלות את הפרונט-אנד ל-Netlify/Vercel
3. ✅ הכל מחובר ב-Production!

---

## ⚠️ פתרון בעיות

### שגיאה: "Application failed to respond"
- **בדוק:** Logs ב-Railway
- **ודא:** שכל משתני הסביבה נכונים

### שגיאה: "Database connection failed"
- **בדוק:** ש-DATABASE_URL נכון
- **ודא:** ש-PostgreSQL רץ ב-Railway

### שגיאה: "ENCRYPTION_KEY not found"
- **בדוק:** שהמשתנה קיים ב-Railway Variables
- **ודא:** שהפורמט נכון (עם ==)

---

**שאלות? תקוע במקום?** ספר לי היכן ואעזור! 🚀

