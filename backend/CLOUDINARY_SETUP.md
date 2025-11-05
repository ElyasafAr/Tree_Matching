# 🔐 הוספת Cloudinary ל-.env

## צעד 1: הירשם ל-Cloudinary

1. לך ל: https://cloudinary.com/users/register/free
2. הירשם עם אימייל וסיסמה (חינמי לחלוטין)
3. אשר את האימייל שתקבל
4. היכנס ל-Dashboard: https://cloudinary.com/console

## צעד 2: העתק את הפרטים

בדף ה-Dashboard תראה:
```
Cloud Name: xxxxxxxxxxxx
API Key: 123456789012345
API Secret: [לחץ על "reveal" כדי לראות]
```

## צעד 3: הוסף ל-backend/.env

פתח את הקובץ `backend/.env` והוסף את השורות הבאות:

```bash
# ============================================
# CLOUDINARY CONFIGURATION
# ============================================
CLOUDINARY_CLOUD_NAME=YOUR_CLOUD_NAME_HERE
CLOUDINARY_API_KEY=YOUR_API_KEY_HERE
CLOUDINARY_API_SECRET=YOUR_API_SECRET_HERE
```

**החלף:**
- `YOUR_CLOUD_NAME_HERE` עם ה-Cloud Name שלך
- `YOUR_API_KEY_HERE` עם ה-API Key שלך
- `YOUR_API_SECRET_HERE` עם ה-API Secret שלך

## דוגמה:

```bash
# אחרי שתחליף - זה צריך להיראות בערך ככה:
CLOUDINARY_CLOUD_NAME=my-dating-site
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=AbCdEfGhIjKlMnOpQrStUvWx
```

## ⚠️ חשוב!

- ✅ **כן**: שמור את ה-.env בשרת שלך
- ❌ **לא**: אל תעלה את ה-.env ל-Git (הוא כבר ב-.gitignore)
- 🔒 **סודי**: המפתחות האלה סודיים - אל תשתף אותם!

## עבור Railway (Production):

אחרי שהכל עובד מקומית, תצטרך להוסיף את המשתנים ב-Railway:

1. לך ל: https://railway.app → הפרויקט שלך → Variables
2. הוסף את 3 המשתנים:
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`
3. Redeploy

---

**מוכן? המשך לקובץ הבא! →**

