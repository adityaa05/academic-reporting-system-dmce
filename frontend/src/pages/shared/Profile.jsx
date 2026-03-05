import { User, Mail, Building2, Briefcase } from 'lucide-react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card } from '../../components/ui/Card';
import { useAuthStore } from '../../store/authStore';

export const Profile = () => {
  const { user } = useAuthStore();

  return (
    <AppLayout>
      <div className="max-w-2xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-primary mb-2">Profile</h1>
          <p className="text-gray-500">Your account information</p>
        </div>

        <Card>
          <div className="flex items-center gap-4 mb-6 pb-6 border-b border-gray-100">
            <div className="w-20 h-20 bg-primary text-white rounded-full flex items-center justify-center text-3xl font-bold">
              {user?.name?.charAt(0)}
            </div>
            <div>
              <h2 className="text-2xl font-bold text-primary">{user?.name}</h2>
              <p className="text-gray-500">{user?.role}</p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl">
              <Mail className="text-gray-400" size={20} />
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">Email</p>
                <p className="text-gray-800 font-medium">{user?.email}</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl">
              <Building2 className="text-gray-400" size={20} />
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">Department</p>
                <p className="text-gray-800 font-medium">{user?.department}</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl">
              <Briefcase className="text-gray-400" size={20} />
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">Role</p>
                <p className="text-gray-800 font-medium">{user?.role}</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl">
              <User className="text-gray-400" size={20} />
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">
                  {user?.role === 'HOD' ? 'HOD ID' : 'Faculty ID'}
                </p>
                <p className="text-gray-800 font-medium">{user?.id}</p>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </AppLayout>
  );
};
