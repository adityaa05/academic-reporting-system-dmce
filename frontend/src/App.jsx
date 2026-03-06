import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from './store/authStore';
import { ProtectedRoute } from './components/ProtectedRoute';
import { ROUTES, USER_ROLES } from './constants';

// Auth Pages
import { Login } from './pages/auth/Login';

// Faculty Pages
import { FacultyDashboard } from './pages/faculty/FacultyDashboard';
import { ReportHistory } from './pages/faculty/ReportHistory';

// HOD Pages
import { HODDashboard } from './pages/hod/HODDashboard';
import { AggregatedReports } from './pages/hod/AggregatedReports';
import { Analytics } from './pages/hod/Analytics';
import { UserManagement } from './pages/hod/UserManagement';

// Shared Pages
import { Profile } from './pages/shared/Profile';
import { AcademicReportingSystem } from './pages/AcademicReportingSystem';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  const { isAuthenticated, user } = useAuthStore();

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route
            path={ROUTES.LOGIN}
            element={
              isAuthenticated ? (
                <Navigate
                  to={
                    user?.role === USER_ROLES.HOD
                      ? ROUTES.HOD_DASHBOARD
                      : ROUTES.FACULTY_DASHBOARD
                  }
                  replace
                />
              ) : (
                <Login />
              )
            }
          />
          <Route path={ROUTES.PREVIEW} element={<AcademicReportingSystem />} />

          {/* Faculty Routes */}
          <Route
            path={ROUTES.FACULTY_DASHBOARD}
            element={
              <ProtectedRoute allowedRoles={[USER_ROLES.FACULTY]}>
                <FacultyDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path={ROUTES.FACULTY_HISTORY}
            element={
              <ProtectedRoute allowedRoles={[USER_ROLES.FACULTY]}>
                <ReportHistory />
              </ProtectedRoute>
            }
          />
          <Route
            path={ROUTES.FACULTY_PROFILE}
            element={
              <ProtectedRoute allowedRoles={[USER_ROLES.FACULTY]}>
                <Profile />
              </ProtectedRoute>
            }
          />

          {/* HOD Routes */}
          <Route
            path={ROUTES.HOD_DASHBOARD}
            element={
              <ProtectedRoute allowedRoles={[USER_ROLES.HOD]}>
                <HODDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path={ROUTES.HOD_REPORTS}
            element={
              <ProtectedRoute allowedRoles={[USER_ROLES.HOD]}>
                <AggregatedReports />
              </ProtectedRoute>
            }
          />
          <Route
            path={ROUTES.HOD_ANALYTICS}
            element={
              <ProtectedRoute allowedRoles={[USER_ROLES.HOD]}>
                <Analytics />
              </ProtectedRoute>
            }
          />
          <Route
            path={ROUTES.HOD_USERS}
            element={
              <ProtectedRoute allowedRoles={[USER_ROLES.HOD]}>
                <UserManagement />
              </ProtectedRoute>
            }
          />
          <Route
            path={ROUTES.HOD_PROFILE}
            element={
              <ProtectedRoute allowedRoles={[USER_ROLES.HOD]}>
                <Profile />
              </ProtectedRoute>
            }
          />

          {/* Default Route */}
          <Route
            path="/"
            element={
              isAuthenticated ? (
                <Navigate
                  to={
                    user?.role === USER_ROLES.HOD
                      ? ROUTES.HOD_DASHBOARD
                      : ROUTES.FACULTY_DASHBOARD
                  }
                  replace
                />
              ) : (
                <Navigate to={ROUTES.LOGIN} replace />
              )
            }
          />

          {/* 404 Route */}
          <Route
            path="*"
            element={
              <Navigate
                to={
                  isAuthenticated
                    ? user?.role === USER_ROLES.HOD
                      ? ROUTES.HOD_DASHBOARD
                      : ROUTES.FACULTY_DASHBOARD
                    : ROUTES.LOGIN
                }
                replace
              />
            }
          />
        </Routes>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
