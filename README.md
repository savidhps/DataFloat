# LuckyVista - Feedback Intelligence Platform

A multi-tenant SaaS platform for collecting and analyzing user feedback with AI-powered emotion detection using machine learning.

## Features

- **Multi-tenant Architecture**: Secure tenant isolation with role-based access control
- **User Authentication**: Secure signup/signin with bcrypt password hashing
- **Feedback Collection**: Comprehensive feedback forms with ratings and comments
- **AI Emotion Detection**: ML-powered sentiment analysis using 13 emotion categories
- **Admin Dashboard**: Real-time analytics with charts and metrics
- **Responsive Design**: Mobile-first design for all devices
- **RESTful API**: Clean API architecture with Flask backend
- **Modern Frontend**: React with Vite, Tailwind CSS, and React Router

## Tech Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask sessions with bcrypt
- **ML Model**: Scikit-learn (Multinomial Naive Bayes + TF-IDF)
- **Security**: Rate limiting, input validation, audit logging

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Charts**: Recharts
- **Forms**: React Hook Form
- **Icons**: Lucide React

## Project Structure

```
luckyvista/
├── backend/
│   ├── app/
│   │   ├── models.py              # Database models
│   │   ├── routes/                # API endpoints
│   │   └── services/              # Business logic
│   ├── data/                      # Training data
│   ├── models/                    # ML model files
│   ├── app.py                     # Flask application
│   ├── config.py                  # Configuration
│   ├── init_db.py                 # Database initialization
│   ├── train_emotion_model.py     # ML model training
│   └── requirements.txt           # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/            # React components
│   │   ├── pages/                 # Page components
│   │   ├── services/              # API services
│   │   └── context/               # React context
│   ├── package.json               # Node dependencies
│   └── vite.config.js             # Vite configuration
└── README.md
```

## Installation

### Prerequisites

- Python 3.8+
- Node.js 16+
- pip (Python package manager)
- npm or yarn (Node package manager)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd luckyvista
   ```

2. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings (optional)
   ```

5. **Initialize database**
   ```bash
   python init_db.py
   ```
   This creates the database and admin user:
   - Email: `admin@gmail.com`
   - Password: `admin123`

6. **Train ML model** (optional - pre-trained model included)
   ```bash
   python train_emotion_model.py
   ```

7. **Run backend server**
   ```bash
   python app.py
   ```
   Backend runs on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Run development server**
   ```bash
   npm run dev
   ```
   Frontend runs on `http://localhost:5173`

## Usage

### Admin Access

1. Navigate to `http://localhost:5173`
2. Click "Sign in"
3. Use admin credentials:
   - Email: `admin@gmail.com`
   - Password: `admin123`
4. Access admin dashboard to view:
   - User metrics
   - Feedback analytics
   - Emotion distribution charts
   - Rating breakdowns

### User Registration

1. Click "Sign up" on login page
2. Fill in registration form:
   - Full name
   - Email address
   - Phone number
   - Organization name
   - Password (8+ chars with uppercase, lowercase, digit, special char)
3. After registration, login with your credentials

### Submit Feedback

1. Login as a regular user
2. Navigate to "Submit Feedback"
3. Provide ratings and comments
4. Submit feedback
5. View your submissions in "My Feedback"

## AI Emotion Detection

The platform uses a machine learning model trained on 839,555 samples to detect 13 emotions:

### Positive Emotions
- Love, Happiness, Fun, Enthusiasm, Relief

### Negative Emotions
- Anger, Hate

### Concern Emotions
- Sadness, Worry, Empty

### Other Emotions
- Surprise, Boredom, Neutral

**Model Performance**: 92.26% accuracy on test set

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/signin` - User login
- `POST /api/auth/signout` - User logout

### Feedback
- `POST /api/feedback` - Submit feedback
- `GET /api/feedback/my-submissions` - Get user's feedback

### Admin (requires admin role)
- `GET /api/admin/metrics` - Platform metrics
- `GET /api/admin/feedback` - All feedback
- `GET /api/admin/sentiment-distribution` - Emotion distribution
- `GET /api/admin/rating-breakdown` - Rating statistics

## Deployment

### Deploy to Render

**No Docker required!** Render deploys directly from GitHub.

#### Quick Deploy:

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Deploy to Render"
   git push origin master
   ```

2. **Create services on Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml` and create both services

3. **Configure environment variables** (if not using blueprint)
   
   **Backend Service:**
   - Name: `luckyvista-backend`
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt && python init_db.py`
   - Start Command: `gunicorn wsgi:app`
   - Environment Variables:
     - `SECRET_KEY`: (auto-generated)
     - `ADMIN_PASSWORD`: `admin123`
     - `FLASK_ENV`: `production`
   
   **Frontend Service:**
   - Name: `luckyvista-frontend`
   - Environment: `Static Site`
   - Build Command: `npm install && npm run build`
   - Publish Directory: `./dist`
   - Environment Variables:
     - `VITE_API_URL`: `https://your-backend-url.onrender.com/api`

4. **Access your deployed app**
   - Frontend: Your frontend Render URL (shows login page)
   - Backend API: Your backend Render URL + `/api/health` (health check)
   - Admin Login: `admin@gmail.com` / `admin123`

#### Important Notes:

- **Free Tier Sleep**: Services sleep after 15 minutes of inactivity
- **Cold Start**: First request after sleep takes 30-60 seconds
- **Keep-Alive**: GitHub Actions pings services every 13 minutes (6 AM - 11 PM UTC)
- **Branch**: Make sure to use `master` or `main` branch (update `render.yaml` if needed)

### Local Development

See installation instructions above for running locally.

## Configuration

### Backend (.env)
```env
SECRET_KEY=your-secret-key-here
ADMIN_PASSWORD=admin123
DATABASE_URI=sqlite:///instance/luckyvista.db
MODEL_PATH=models/sentiment_model.pkl
VECTORIZER_PATH=models/vectorizer.pkl
```

### Frontend (vite.config.js)
```javascript
server: {
  port: 5173,
  proxy: {
    '/api': 'http://localhost:5000'
  }
}
```

## Security Features

- **Password Hashing**: Bcrypt with salt
- **Session Management**: Secure Flask sessions
- **Rate Limiting**: API endpoint protection
- **Input Validation**: Comprehensive validation on all inputs
- **SQL Injection Prevention**: SQLAlchemy ORM
- **XSS Protection**: React's built-in escaping
- **CORS**: Configured for frontend-backend communication
- **Audit Logging**: Track all critical operations

## Development

### Run Tests
```bash
cd backend
python -m pytest
```

### Build Frontend for Production
```bash
cd frontend
npm run build
```

### Database Migrations
```bash
cd backend
python init_db.py  # Recreates database (WARNING: deletes existing data)
```

## Troubleshooting

### Backend Issues

**Port already in use**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9
```

**Database locked**
- Close all connections to the database
- Restart the backend server

**ML model not loading**
- Ensure `models/sentiment_model.pkl` and `models/vectorizer.pkl` exist
- Run `python train_emotion_model.py` to retrain

### Frontend Issues

**Module not found**
```bash
rm -rf node_modules package-lock.json
npm install
```

**API connection failed**
- Ensure backend is running on port 5000
- Check CORS configuration in backend

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Create an issue on GitHub
- Contact: support@luckyvista.com

## Acknowledgments

- Emotion detection dataset: EmotionDetection.csv (839,555 samples)
- ML framework: Scikit-learn
- UI components: Tailwind CSS, Lucide Icons
- Charts: Recharts library

---

**Built with ❤️ for better feedback intelligence**
