import { useNavigate, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { Home, BarChart2, User, FileText, LogOut, Users } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { USER_ROLES, ROUTES } from '../../constants';
import { reportService } from '../../services/api';

export const Navigation = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const [newReportsCount, setNewReportsCount] = useState(0);

  useEffect(() => {
    if (user?.role === USER_ROLES.HOD) {
      fetchNewReportsCount();
      // Refresh count every 30 seconds
      const interval = setInterval(fetchNewReportsCount, 30000);
      return () => clearInterval(interval);
    }
  }, [user]);

  const fetchNewReportsCount = async () => {
    try {
      const data = await reportService.getNewReportsCount();
      setNewReportsCount(data.new_reports || 0);
    } catch (error) {
      console.error('Error fetching new reports count:', error);
    }
  };

  const isActive = (path) => location.pathname === path;

  const handleLogout = () => {
    logout();
    navigate(ROUTES.LOGIN);
  };

  const facultyNavItems = [
    { path: ROUTES.FACULTY_DASHBOARD, icon: Home, label: 'Home' },
    { path: ROUTES.FACULTY_HISTORY, icon: FileText, label: 'History' },
    { path: ROUTES.FACULTY_PROFILE, icon: User, label: 'Profile' },
  ];

  const hodNavItems = [
    { path: ROUTES.HOD_DASHBOARD, icon: Home, label: 'Dashboard' },
    { path: ROUTES.HOD_REPORTS, icon: FileText, label: 'Reports' },
    { path: ROUTES.HOD_ANALYTICS, icon: BarChart2, label: 'Analytics' },
    { path: ROUTES.HOD_USERS, icon: Users, label: 'Users' },
    { path: ROUTES.HOD_PROFILE, icon: User, label: 'Profile' },
  ];

  const navItems = user?.role === USER_ROLES.HOD ? hodNavItems : facultyNavItems;

  return (
    <>
      {/* Mobile Bottom Navigation */}
      <nav className="md:hidden fixed bottom-6 left-6 right-6 bg-surface rounded-full shadow-lg p-2 px-4 flex justify-around items-center z-40">
        {navItems.map(({ path, icon: Icon, label }) => (
          <button
            key={path}
            onClick={() => navigate(path)}
            className={`flex flex-col items-center py-2 px-3 rounded-full transition-all relative ${
              isActive(path)
                ? 'text-primary bg-gray-100'
                : 'text-gray-400 hover:text-primary'
            }`}
          >
            <Icon size={22} />
            <span className="text-xs mt-1 hidden sm:block">{label}</span>
            {path === ROUTES.HOD_REPORTS && newReportsCount > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                {newReportsCount}
              </span>
            )}
          </button>
        ))}
        <button
          onClick={handleLogout}
          className="flex flex-col items-center py-2 px-3 rounded-full text-gray-400 hover:text-red-500 transition-colors"
        >
          <LogOut size={22} />
          <span className="text-xs mt-1 hidden sm:block">Logout</span>
        </button>
      </nav>

      {/* Desktop Sidebar Navigation */}
      <aside className="hidden md:flex md:flex-col md:fixed md:left-0 md:top-0 md:bottom-0 md:w-64 bg-surface shadow-lg z-40">
        <div className="p-6 border-b border-gray-100">
          <h2 className="text-xl font-bold text-primary">Academic Report</h2>
          <p className="text-sm text-gray-500 mt-1">{user?.department} Department</p>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {navItems.map(({ path, icon: Icon, label }) => (
            <button
              key={path}
              onClick={() => navigate(path)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all relative ${
                isActive(path)
                  ? 'bg-gray-100 text-primary font-semibold'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-primary'
              }`}
            >
              <Icon size={20} />
              <span>{label}</span>
              {path === ROUTES.HOD_REPORTS && newReportsCount > 0 && (
                <span className="ml-auto bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center">
                  {newReportsCount}
                </span>
              )}
            </button>
          ))}
        </nav>

        <div className="p-4 border-t border-gray-100">
          <div className="bg-gray-50 rounded-xl p-4 mb-3">
            <p className="text-sm font-semibold text-gray-800">{user?.name}</p>
            <p className="text-xs text-gray-500 mt-1">{user?.email}</p>
            <span className="inline-block mt-2 px-3 py-1 bg-primary text-white text-xs font-semibold rounded-full">
              {user?.role}
            </span>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-red-500 hover:bg-red-50 transition-all"
          >
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </aside>
    </>
  );
};
