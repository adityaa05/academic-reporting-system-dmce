# Academic Reporting System - Frontend

A modern, responsive web application for managing daily faculty reports with AI-powered task categorization and analytics.

## Features

### Faculty Features
- **Task Logging**: Natural language input for daily activities
- **AI Categorization**: Automatic task classification into operational domains
- **Report Generation**: AI-generated executive summaries
- **Human-in-the-Loop**: Review and approve reports before submission
- **Report History**: View all submitted reports with detailed breakdowns

### HOD Features
- **Dashboard Analytics**: Real-time department metrics and trends
- **Activity Distribution**: Visual breakdown of faculty activities by domain
- **Submission Tracking**: Monitor faculty report submissions
- **Aggregated Reports**: AI-powered synthesis of multiple faculty reports (SSE streaming)
- **Advanced Analytics**: Charts and visualizations for data-driven insights

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **TanStack Query** - Data fetching and caching
- **Zustand** - State management
- **Axios** - HTTP client
- **Recharts** - Data visualization
- **Lucide React** - Icons
- **TailwindCSS** - Styling
- **date-fns** - Date formatting

## Project Structure

```
src/
├── components/
│   ├── ui/              # Reusable UI components
│   │   ├── Button.jsx
│   │   ├── Card.jsx
│   │   ├── Input.jsx
│   │   ├── Badge.jsx
│   │   ├── Loading.jsx
│   │   └── Modal.jsx
│   ├── layout/          # Layout components
│   │   ├── AppLayout.jsx
│   │   └── Navigation.jsx
│   └── ProtectedRoute.jsx
├── pages/
│   ├── auth/
│   │   └── Login.jsx
│   ├── faculty/
│   │   ├── FacultyDashboard.jsx
│   │   └── ReportHistory.jsx
│   ├── hod/
│   │   ├── HODDashboard.jsx
│   │   ├── AggregatedReports.jsx
│   │   └── Analytics.jsx
│   └── shared/
│       └── Profile.jsx
├── services/
│   └── api.js           # API client and service methods
├── store/
│   └── authStore.js     # Zustand auth store
├── utils/
│   └── helpers.js       # Utility functions
├── constants/
│   └── index.js         # App constants
├── App.jsx              # Main app with routing
└── main.jsx             # Entry point
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

Build output will be in the `dist/` directory.

## Demo Credentials

### Faculty Account
- Email: `faculty@dmce.ac.in`
- Password: `demo123`

### HOD Account
- Email: `hod@dmce.ac.in`
- Password: `demo123`

## Key Features Explained

### Authentication
- JWT-based authentication (mock implementation)
- Role-based access control (FACULTY, HOD)
- Protected routes with automatic redirects
- Persistent login via localStorage

### Task Management
1. Faculty inputs tasks in natural language
2. Backend AI categorizes tasks into domains:
   - PEDAGOGY (Teaching)
   - RESEARCH
   - ADMINISTRATION
   - EVALUATION
   - OTHER
3. Tasks accumulate throughout the day
4. Generate report creates AI summary
5. Faculty reviews and approves
6. Report dispatched to database

### HOD Analytics
- **Dashboard**: Overview with key metrics
- **Activity Distribution**: Domain breakdown with progress bars
- **Weekly Trends**: Bar chart of submission patterns
- **Recent Submissions**: Real-time faculty activity feed
- **Aggregated Reports**: Stream AI-powered department overview

### Responsive Design
- Mobile-first approach
- Bottom navigation on mobile
- Sidebar navigation on desktop
- Adaptive layouts for all screen sizes
- Touch-friendly interactions

## Design System

### Color Palette
- **Primary**: `#1a1a1a` (Dark gray/black)
- **Background**: `#f8f9fa` (Light gray)
- **Surface**: `#ffffff` (White)
- **Domain Colors**:
  - PEDAGOGY: Blue (`#3B82F6`)
  - RESEARCH: Purple (`#8B5CF6`)
  - ADMINISTRATION: Amber (`#F59E0B`)
  - EVALUATION: Green (`#10B981`)
  - OTHER: Gray (`#6B7280`)

### UI Components
- Rounded corners (xl: 0.75rem, 2xl: 1rem, 3xl: 1.5rem)
- Subtle shadows for depth
- Clean, minimal aesthetic
- Consistent spacing
- Active state animations

## API Integration

### Endpoints Used
- `POST /api/v1/tasks/intake` - Log tasks
- `POST /api/v1/reports/generate` - Generate draft report
- `POST /api/v1/reports/dispatch` - Submit final report
- `GET /api/v1/dashboard/metrics` - Get dashboard metrics
- `GET /api/v1/reports/aggregate/stream` - Stream aggregated report (SSE)

### Error Handling
- Automatic token refresh
- 401 redirects to login
- User-friendly error messages
- Loading states for all async operations

## State Management

### Auth Store (Zustand)
```javascript
{
  user: { id, name, email, role, department },
  isAuthenticated: boolean,
  isLoading: boolean,
  error: string | null,
  login: (email, password) => Promise,
  logout: () => void
}
```

## Environment Variables

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Development Tips

### Running with Backend
1. Start backend server: `cd backend && uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Navigate to `http://localhost:5173`

### Code Organization
- Keep components small and focused
- Use custom hooks for reusable logic
- Maintain consistent naming conventions
- Follow React best practices

### Adding New Pages
1. Create page component in `src/pages/`
2. Add route in `src/App.jsx`
3. Update constants in `src/constants/index.js`
4. Add navigation item in `src/components/layout/Navigation.jsx`

## Performance Optimization

- Code splitting with dynamic imports (recommended for production)
- React Query for efficient data caching
- Minimal re-renders with proper state management
- Lazy loading for images and heavy components

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

When adding features:
1. Follow existing code patterns
2. Maintain responsive design
3. Add proper error handling
4. Test on mobile and desktop
5. Update this README if needed

## License

MIT
