# 🛠️ Tech Stack - Tree Matching

## Backend

### Framework & Core
- **Flask** 2.3.3 - Web framework
- **Python** 3.8+ - Programming language

### Database
- **PostgreSQL** - Main database (hosted on Railway)
- **SQLAlchemy** - ORM (Object-Relational Mapping)
- **psycopg2-binary** - PostgreSQL adapter

### Authentication & Security
- **Flask-JWT-Extended** - JWT token authentication
- **bcrypt** - Password hashing
- **cryptography** (Fernet) - Field-level encryption for sensitive data

### Other
- **Flask-CORS** - Cross-Origin Resource Sharing
- **python-dotenv** - Environment variables management

## Frontend

### Framework & Build Tool
- **React** 19.1.1 - UI library
- **Vite** 7.1.7 - Build tool and dev server

### Routing & State
- **React Router DOM** 6.21.0 - Client-side routing
- **React Context API** - State management (Authentication)

### HTTP Client
- **Axios** 1.6.2 - HTTP requests to backend API

### Styling
- **CSS3** - Custom styling
- **Modern gradients** - Purple-blue theme

### Development
- **ESLint** - Code linting
- **Vite Plugin React** - React support for Vite

## Database Schema

### Tables

#### Users
```sql
- id (PK)
- email_encrypted (TEXT, UNIQUE) - Encrypted
- full_name_encrypted (TEXT) - Encrypted
- phone_encrypted (TEXT) - Encrypted
- address_encrypted (TEXT) - Encrypted
- password_hash (VARCHAR) - bcrypt hashed
- age (INT)
- gender (VARCHAR)
- location (VARCHAR)
- interests (TEXT)
- bio (TEXT)
- profile_image (VARCHAR)
- referral_code (VARCHAR, UNIQUE)
- created_at (DATETIME)
- last_active (DATETIME)
```

#### Referrals
```sql
- id (PK)
- referrer_id (FK -> Users.id)
- referred_id (FK -> Users.id, UNIQUE)
- referral_code_used (VARCHAR)
- created_at (DATETIME)
```

#### Chats
```sql
- id (PK)
- user1_id (FK -> Users.id)
- user2_id (FK -> Users.id)
- created_at (DATETIME)
- last_message_at (DATETIME)
UNIQUE(user1_id, user2_id)
```

#### Messages
```sql
- id (PK)
- chat_id (FK -> Chats.id)
- sender_id (FK -> Users.id)
- content (TEXT)
- sent_at (DATETIME)
- is_read (BOOLEAN)
```

#### Matches
```sql
- id (PK)
- user_id (FK -> Users.id)
- liked_user_id (FK -> Users.id)
- is_mutual (BOOLEAN)
- created_at (DATETIME)
UNIQUE(user_id, liked_user_id)
```

## API Endpoints

### Authentication (`/auth`)
- `POST /auth/register` - Register new user (requires referral code)
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user info
- `GET /auth/validate-referral/<code>` - Validate referral code

### Users (`/users`)
- `GET /users/profile/<id>` - Get user profile
- `GET /users/search` - Search users with filters
- `POST /users/like/<id>` - Like a user
- `GET /users/matches` - Get mutual matches
- `PUT /users/profile` - Update own profile

### Chat (`/chat`)
- `GET /chat/conversations` - Get all conversations
- `GET /chat/messages/<chat_id>` - Get messages in chat
- `POST /chat/send` - Send message
- `POST /chat/start/<user_id>` - Start chat with user
- `GET /chat/unread-count` - Get unread messages count

### Referrals (`/referrals`)
- `GET /referrals/my-referrals` - Get users I referred
- `GET /referrals/tree` - Get my referral tree
- `GET /referrals/my-referrer` - Get who referred me
- `GET /referrals/chain/<user_id>` - Get referral chain to user
- `GET /referrals/stats` - Get referral statistics

## Security Features

### Data Encryption
- Email, full name, phone, address encrypted at rest
- Fernet symmetric encryption (AES-128)
- Encryption key stored in environment variables

### Password Security
- bcrypt hashing with salt
- Minimum 6 characters (can be increased)
- Never stored or transmitted in plain text

### API Security
- JWT tokens for authentication
- Token expiry (24 hours default)
- Protected routes require valid token
- CORS enabled for frontend domain

### Best Practices
- Environment variables for secrets
- SQL injection prevention (SQLAlchemy ORM)
- XSS prevention (React auto-escaping)
- HTTPS recommended for production

## Development Tools

### Backend Development
- **Flask Debug Mode** - Hot reload during development
- **SQLAlchemy** - Database migrations and queries
- **Python REPL** - Interactive testing

### Frontend Development
- **Vite HMR** - Hot Module Replacement
- **React DevTools** - Component debugging
- **Browser DevTools** - Network and console debugging

## Hosting & Deployment

### Recommended Platforms

#### Backend
- **Railway** ⭐ (Recommended)
- Heroku
- DigitalOcean App Platform
- AWS Elastic Beanstalk

#### Frontend
- **Vercel** ⭐ (Recommended)
- **Netlify** ⭐ (Recommended)
- Cloudflare Pages
- AWS S3 + CloudFront

#### Database
- **Railway PostgreSQL** ⭐ (Recommended)
- Supabase
- AWS RDS
- DigitalOcean Managed Database

## Performance Considerations

### Current
- Basic polling for chat messages (5s interval)
- Server-side rendering not implemented
- No caching layer

### Future Improvements
- WebSocket for real-time chat
- Redis for caching
- CDN for static assets
- Image optimization and lazy loading
- Database indexing optimization
- API rate limiting

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Development Environment

- **Node.js:** 18.x or higher
- **Python:** 3.8 or higher
- **PostgreSQL:** 14.x or higher
- **OS:** Windows 10/11, macOS, Linux

---

**Stack Version:** 1.0.0  
**Last Updated:** November 2025

