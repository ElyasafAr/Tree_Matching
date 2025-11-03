# 📖 מדריך התקנה מפורט - Tree Matching

## שלב 1: הגדרת PostgreSQL ב-Railway

1. היכנס ל-[Railway](https://railway.app/)
2. צור פרויקט חדש
3. לחץ על "+ New" → "Database" → "Add PostgreSQL"
4. לאחר היצירה, לחץ על ה-Database
5. עבור ל-"Variables" והעתק את ה-`DATABASE_URL`

## שלב 2: הכנת Backend

### 2.1 התקנת תלויות

```bash
cd backend
pip install -r requirements.txt
```

### 2.2 הגדרת משתני סביבה

צור קובץ `.env` בתיקיית `backend`:

```bash
# Database (מ-Railway)
DATABASE_URL=postgresql://postgres:password@host:port/railway

# JWT Secret - צור סיסמה חזקה
JWT_SECRET_KEY=your-super-secret-jwt-key-here

# Encryption Key - הרץ את הפקודה הבאה:
# python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=your-encryption-key-here

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
```

### 2.3 יצירת Encryption Key

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

העתק את התוצאה ל-`ENCRYPTION_KEY` בקובץ `.env`

### 2.4 אתחול מסד הנתונים

```bash
python init_db.py
```

### 2.5 יצירת משתמש ראשון

```bash
python create_first_user.py
```

עקוב אחר ההוראות והכנס:
- אימייל
- סיסמה
- שם מלא

**שמור את קוד ההמלצה!** תצטרך אותו כדי להירשם כמשתמשים נוספים.

### 2.6 הרצת השרת

```bash
python app.py
```

השרת ירוץ על `http://localhost:5000`

## שלב 3: הכנת Frontend

### 3.1 התקנת תלויות

```bash
cd frontend
npm install
```

### 3.2 הגדרת משתני סביבה

צור קובץ `.env` בתיקיית `frontend`:

```
VITE_API_URL=http://localhost:5000
```

### 3.3 הרצת האתר

```bash
npm run dev
```

האתר יהיה זמין על `http://localhost:5173`

## שלב 4: בדיקה

1. פתח את `http://localhost:5173`
2. לחץ על "הרשם עכשיו"
3. מלא את הטופס והכנס את **קוד ההמלצה** מהמשתמש הראשון
4. התחבר ונסה את התכונות

## 🚀 Deploy ל-Production (Railway)

### Backend Deployment

1. **ב-Railway:**
   - צור Service חדש
   - חבר את ה-GitHub Repository שלך
   - בחר את תיקיית `backend`
   - Railway יזהה אוטומטית שזה Flask

2. **הגדר Variables ב-Railway:**
   ```
   DATABASE_URL=<יתמלא אוטומטית>
   JWT_SECRET_KEY=<סיסמה חזקה>
   ENCRYPTION_KEY=<מה שיצרת>
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

3. **הוסף אתחול:**
   - ב-Settings → Deploy → Start Command:
   ```
   python init_db.py && python app.py
   ```

4. **העתק את ה-URL** של ה-Backend מ-Railway

### Frontend Deployment

#### אופציה 1: Netlify

1. עדכן `frontend/.env`:
   ```
   VITE_API_URL=https://your-backend.railway.app
   ```

2. בנה את הפרויקט:
   ```bash
   cd frontend
   npm run build
   ```

3. גרור את תיקיית `dist` ל-[Netlify Drop](https://app.netlify.com/drop)

#### אופציה 2: Vercel

1. התחבר ל-[Vercel](https://vercel.com)
2. Import את ה-Repository
3. הגדר:
   - Framework: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. הוסף Environment Variable:
   ```
   VITE_API_URL=https://your-backend.railway.app
   ```

## 🔧 פתרון בעיות נפוצות

### Backend לא עולה

**שגיאה:** `ENCRYPTION_KEY not found`
- **פתרון:** ודא שיצרת את ה-encryption key והוספת אותו ל-.env

**שגיאה:** `Connection refused to PostgreSQL`
- **פתרון:** ודא ש-DATABASE_URL נכון ושה-PostgreSQL ב-Railway רץ

### Frontend לא מתחבר ל-Backend

**שגיאה:** `CORS error`
- **פתרון:** ודא ש-Flask-CORS מותקן ופועל (כבר מוגדר ב-app.py)

**שגיאה:** `Network Error`
- **פתרון:** בדוק ש-VITE_API_URL נכון ושה-Backend רץ

### לא יכול להירשם

**שגיאה:** `Invalid referral code`
- **פתרון:** ודא שיש לך משתמש ראשון במערכת והעתקת את קוד ההמלצה הנכון

## 📱 שלבים הבאים

1. הוסף תמונות פרופיל (upload)
2. שדרג לצ'אט בזמן אמת (WebSocket)
3. הוסף התראות
4. בנה אפליקציה ניידת (React Native)
5. הוסף אימות דו-שלבי
6. Analytics ודשבורד אדמין

## 💡 טיפים

- **אבטחה:** החלף את JWT_SECRET_KEY לסיסמה חזקה בייצור
- **Performance:** הוסף Redis לקאשינג
- **Monitoring:** הוסף Sentry לניטור שגיאות
- **Backup:** גבה את מסד הנתונים באופן קבוע

---

**זקוק לעזרה?** פתח issue ב-GitHub או צור קשר.

