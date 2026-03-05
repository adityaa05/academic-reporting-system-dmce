import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { USER_ROLES, ROUTES } from '../../constants';

export const Login = () => {
  const navigate = useNavigate();
  const { login, isLoading, error } = useAuthStore();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const user = await login(formData.email, formData.password);
      // Redirect based on role
      if (user.role === USER_ROLES.HOD) {
        navigate(ROUTES.HOD_DASHBOARD);
      } else {
        navigate(ROUTES.FACULTY_DASHBOARD);
      }
    } catch (err) {
      console.error('Login failed:', err);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="w-full max-w-md">
        <div className="bg-surface rounded-3xl shadow-lg p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-primary mb-2">Welcome back</h1>
            <p className="text-gray-500">Sign in to your account</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <Input
              label="Email"
              type="email"
              placeholder="faculty@dmce.ac.in"
              icon={<Mail size={20} />}
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
            />

            <Input
              label="Password"
              type="password"
              placeholder="Enter your password"
              icon={<Lock size={20} />}
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required
            />

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm">
                {error}
              </div>
            )}

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full"
              loading={isLoading}
            >
              Sign In
            </Button>
          </form>

          <div className="mt-8 pt-6 border-t border-gray-100">
            <div className="bg-blue-50 rounded-xl p-4 text-sm text-gray-600">
              <p className="font-semibold text-gray-800 mb-2">Demo Credentials:</p>
              <p className="mb-2">Faculty: priya.sharma@dmce.ac.in / academic123</p>
              <p>HOD: rajesh.kumar@dmce.ac.in / academic123</p>
            </div>
          </div>
        </div>

        <p className="text-center text-gray-500 text-sm mt-6">
          Academic Reporting System v1.0 - IT Department
        </p>
      </div>
    </div>
  );
};
