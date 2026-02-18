# LuckyVista Frontend - React Application

Modern, responsive React frontend for the LuckyVista Feedback Intelligence Platform.

## Features

✅ User Authentication (Login/Register)  
✅ Feedback Submission with Star Ratings  
✅ User Feedback History  
✅ Admin Dashboard with Charts  
✅ Real-time Form Validation  
✅ Responsive Design (Mobile-friendly)  
✅ Loading States & Error Handling  
✅ Session Management  
✅ Multi-tenant Support  

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool (faster than CRA)
- **React Router v6** - Navigation
- **Axios** - API calls
- **React Hook Form** - Form validation
- **Recharts** - Data visualization
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The app will run at `http://localhost:3000`

### 3. Make Sure Backend is Running

The frontend expects the Flask backend at `http://localhost:5000`

```bash
# In the root directory
python app.py
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── auth/
│   │   │   ├── LoginForm.jsx          # Login page
│   │   │   └── RegisterForm.jsx       # Registration page
│   │   ├── feedback/
│   │   │   └── FeedbackForm.jsx       # Feedback submission
│   │   └── common/
│   │       ├── Navbar.jsx             # Navigation bar
│   │       ├── Loading.jsx            # Loading spinner
│   │       ├── ErrorMessage.jsx       # Error display
│   │       └── SuccessMessage.jsx     # Success display
│   ├── pages/
│   │   ├── LoginPage.jsx              # Login page wrapper
│   │   ├── RegisterPage.jsx           # Register page wrapper
│   │   ├── FeedbackPage.jsx           # Feedback submission page
│   │   ├── MyFeedbackPage.jsx         # User's feedback history
│   │   └── AdminDashboardPage.jsx     # Admin dashboard
│   ├── services/
│   │   └── api.js                     # API service layer
│   ├── context/
│   │   └── AuthContext.jsx            # Authentication state
│   ├── App.jsx                        # Main app with routing
│   ├── main.jsx                       # Entry point
│   └── index.css                      # Global styles
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## Available Scripts

```bash
# Development server
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Features by Page

### Login Page (`/login`)
- Email and password authentication
- Form validation
- Error handling
- Redirect to dashboard after login
- Demo credentials displayed

### Register Page (`/register`)
- Full registration form
- Real-time validation
- Password strength requirements
- Organization/tenant assignment
- Success message and redirect

### Feedback Page (`/feedback`)
- Star rating inputs (Overall & Experience)
- Required comments field
- Optional fields (Feature satisfaction, UI rating, etc.)
- Recommendation likelihood (1-10)
- Form validation
- Success confirmation

### My Feedback Page (`/my-feedback`)
- List of user's submissions
- Sentiment labels with colors
- Rating display
- Date sorting
- Empty state handling

### Admin Dashboard (`/admin/dashboard`)
- Platform metrics cards
- Sentiment distribution pie chart
- Rating breakdown bar chart
- All feedback table
- Tenant filtering
- Real-time data

## API Integration

The frontend communicates with the Flask backend via REST API:

### Authentication
- `POST /api/auth/signup` - Register
- `POST /api/auth/signin` - Login
- `POST /api/auth/signout` - Logout
- `GET /api/auth/session` - Check session

### Feedback
- `POST /api/feedback` - Submit feedback
- `GET /api/feedback/my-submissions` - Get user's feedback

### Admin
- `GET /api/admin/metrics` - Platform metrics
- `GET /api/admin/sentiment-distribution` - Sentiment data
- `GET /api/admin/rating-breakdown` - Rating data
- `GET /api/admin/feedback` - All feedback

## Authentication Flow

1. User logs in → Session cookie created
2. Cookie sent with all API requests
3. Protected routes check authentication
4. Redirect to login if not authenticated
5. Admin routes check for admin role

## Styling

Uses Tailwind CSS with custom configuration:

- Primary color: Blue (#0ea5e9)
- Responsive breakpoints
- Custom component classes
- Consistent spacing and typography

## Form Validation

React Hook Form provides:
- Real-time validation
- Error messages
- Field-level validation
- Custom validation rules

### Validation Rules

**Email:**
- Required
- Valid email format

**Password:**
- Minimum 8 characters
- Uppercase letter
- Lowercase letter
- Digit
- Special character

**Phone:**
- Valid international format
- Pattern: `+1234567890`

**Organization:**
- Alphanumeric, hyphens, underscores only

## State Management

Uses React Context API for authentication:

```javascript
const { user, isAuthenticated, isAdmin, signin, signout } = useAuth();
```

## Error Handling

- API errors displayed with ErrorMessage component
- Network errors caught and displayed
- 401 errors redirect to login
- Form validation errors shown inline

## Loading States

- Full-page loading spinner
- Button loading states
- Skeleton screens (future enhancement)

## Responsive Design

- Mobile-first approach
- Breakpoints: sm, md, lg, xl
- Touch-friendly buttons
- Collapsible navigation (future)

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Development Tips

### Hot Module Replacement
Vite provides instant HMR - changes reflect immediately

### API Proxy
Vite proxies `/api` requests to `http://localhost:5000`

### Environment Variables
Create `.env.local` for custom config:

```env
VITE_API_URL=http://localhost:5000
```

## Building for Production

```bash
# Build optimized bundle
npm run build

# Preview production build
npm run preview
```

Output in `dist/` directory.

## Deployment

### Option 1: Static Hosting (Netlify, Vercel)
```bash
npm run build
# Deploy dist/ folder
```

### Option 2: Serve with Flask
```bash
npm run build
# Copy dist/ to Flask static folder
```

## Troubleshooting

### CORS Errors
- Ensure Flask backend has CORS enabled
- Check `.env` has correct origins

### API Connection Failed
- Verify backend is running on port 5000
- Check Vite proxy configuration

### Session Not Persisting
- Ensure `withCredentials: true` in axios
- Check cookie settings in Flask

## Future Enhancements

- [ ] Dark mode
- [ ] Real-time notifications
- [ ] Advanced filtering
- [ ] Data export UI
- [ ] Password reset UI
- [ ] User profile page
- [ ] Feedback editing
- [ ] File attachments
- [ ] Email notifications
- [ ] Mobile app (React Native)

## Contributing

Follow React best practices:
- Functional components with hooks
- PropTypes for type checking
- ESLint for code quality
- Consistent naming conventions

## License

Proprietary - All rights reserved

---

**Need Help?** Check the main project README or contact the development team.
