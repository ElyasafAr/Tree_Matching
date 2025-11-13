# איך לראות לוגים - מדריך

## לוגים בדפדפן (Frontend - Console)

### Chrome/Edge:
1. פתח את האתר
2. לחץ `F12` או `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
3. לחץ על הטאב **Console**
4. תראה את כל הלוגים שמתחילים ב-`[PROFILE]`

### Firefox:
1. פתח את האתר
2. לחץ `F12` או `Ctrl+Shift+K` (Windows) / `Cmd+Option+K` (Mac)
3. הטאב Console יפתח אוטומטית
4. תראה את כל הלוגים שמתחילים ב-`[PROFILE]`

### Safari:
1. פתח את האתר
2. לחץ `Cmd+Option+C` כדי לפתוח את Console
3. אם Console לא מופיע, הפעל Developer Menu:
   - Settings > Advanced > Show Develop menu
4. תראה את כל הלוגים שמתחילים ב-`[PROFILE]`

### טיפים:
- לחץ על `Clear console` (הסמל 🚫) כדי לנקות את הלוגים הישנים
- לחץ על `Filter` וכתוב `[PROFILE]` כדי לראות רק את הלוגים של הפרופיל
- לוגים אדומים = שגיאות (❌)
- לוגים כחולים = מידע רגיל

---

## לוגים ב-Railway (Backend)

### דרך 1: דרך ה-Dashboard של Railway
1. היכנס ל-[Railway Dashboard](https://railway.app)
2. בחר את הפרויקט שלך
3. לחץ על השירות (Service) של ה-Backend
4. לחץ על הטאב **Deployments** או **Logs**
5. תראה את כל הלוגים של השרת

### דרך 2: דרך Railway CLI
1. התקן את Railway CLI:
   ```bash
   npm i -g @railway/cli
   ```
2. התחבר:
   ```bash
   railway login
   ```
3. צפה בלוגים:
   ```bash
   railway logs
   ```
4. או לוגים בזמן אמת:
   ```bash
   railway logs --follow
   ```

### דרך 3: דרך ה-API של Railway
1. היכנס ל-Railway Dashboard
2. בחר את הפרויקט
3. לחץ על השירות
4. לחץ על **Settings** > **View Logs**
5. או לחץ על **Metrics** כדי לראות סטטיסטיקות

---

## מה לחפש בלוגים?

### Frontend (Console):
- `[PROFILE] useEffect triggered` - מתי הקומפוננטה מתחילה לטעון
- `[PROFILE] loadUserProfile called` - מתי מתחילה טעינת הפרופיל
- `[PROFILE] API Response received` - התגובה מהשרת
- `[PROFILE] ❌ ERROR` - שגיאות

### Backend (Railway):
- `[GET PROFILE] ========== START ==========` - תחילת בקשה
- `[GET PROFILE] Request received for user_id` - איזה משתמש נדרש
- `[GET PROFILE] User query result` - מה החזיר ה-query
- `[GET PROFILE] ✅ Successfully prepared user data` - הצלחה
- `[GET PROFILE] ❌❌❌ UNEXPECTED ERROR` - שגיאות

---

## פתרון בעיות נפוצות

### אם לא רואים לוגים ב-Console:
1. ודא שהדפדפן לא חוסם את ה-Console
2. נסה לרענן את הדף (`F5`)
3. ודא שאתה לא ב-Incognito/Private mode
4. נסה דפדפן אחר

### אם לא רואים לוגים ב-Railway:
1. ודא שהשרת רץ (Status = Running)
2. נסה לרענן את הדף
3. בדוק שהלוגים לא מסוננים (הסר פילטרים)
4. נסה לחפש `[GET PROFILE]` בחיפוש

### אם רואים שגיאות:
1. העתק את השגיאה המלאה
2. חפש את השגיאה ב-Google
3. בדוק את הקוד במקום שמצוין בשגיאה
4. שלח את השגיאה לפיתוח

---

## דוגמאות ללוגים תקינים:

### Frontend:
```
[PROFILE] useEffect triggered - userId: 123 currentUser?.id: 456 isOwnProfile: false
[PROFILE] Loading other user profile, userId: 123
[PROFILE] loadUserProfile called with userId: 123
[PROFILE] Calling API getProfile for userId: 123
[PROFILE] API Response received: {...}
[PROFILE] ✅ User state updated: {...}
```

### Backend:
```
[GET PROFILE] ========== START ==========
[GET PROFILE] Request received for user_id: 123
[GET PROFILE] Current user ID: 456
[GET PROFILE] User query result: <User 123>
[GET PROFILE] ✅ Successfully prepared user data
[GET PROFILE] ========== END ==========
```

---

## קיצורי דרך שימושיים:

- **Chrome Console**: `Ctrl+Shift+J` (Windows) / `Cmd+Option+J` (Mac)
- **Firefox Console**: `Ctrl+Shift+K` (Windows) / `Cmd+Option+K` (Mac)
- **Safari Console**: `Cmd+Option+C`
- **Clear Console**: `Ctrl+L` (רוב הדפדפנים)

---

**עדכון אחרון**: 2025-11-13

