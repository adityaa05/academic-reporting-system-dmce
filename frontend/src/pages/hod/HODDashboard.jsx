import { useState, useEffect } from 'react';
import { Users, FileText, TrendingUp, Clock, RefreshCw } from 'lucide-react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardTitle, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { LoadingSpinner } from '../../components/ui/Loading';
import { analyticsService } from '../../services/api';

export const HODDashboard = () => {
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    fetchStats();

    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchStats(true);
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const fetchStats = async (isAutoRefresh = false) => {
    if (isAutoRefresh) {
      setIsRefreshing(true);
    } else {
      setIsLoading(true);
    }

    try {
      const data = await analyticsService.getDepartmentStats();
      setStats(data);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  const handleManualRefresh = () => {
    fetchStats(true);
  };

  if (isLoading) {
    return (
      <AppLayout>
        <div className="flex justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-primary mb-2">HOD Dashboard</h1>
          <p className="text-gray-500">
            Department overview and analytics
            {lastUpdated && (
              <span className="ml-2 text-xs">
                • Last updated: {lastUpdated.toLocaleTimeString()}
              </span>
            )}
          </p>
        </div>
        <Button
          variant="secondary"
          size="sm"
          onClick={handleManualRefresh}
          disabled={isRefreshing}
          icon={<RefreshCw size={16} className={isRefreshing ? 'animate-spin' : ''} />}
        >
          Refresh
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-gray-500 mb-1">Total Faculty</p>
              <p className="text-3xl font-bold text-primary">{stats?.total_faculty}</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-xl">
              <Users className="text-blue-600" size={24} />
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-gray-500 mb-1">Reports Today</p>
              <p className="text-3xl font-bold text-primary">{stats?.reports_today}</p>
            </div>
            <div className="bg-green-100 p-3 rounded-xl">
              <FileText className="text-green-600" size={24} />
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-gray-500 mb-1">Completion Rate</p>
              <p className="text-3xl font-bold text-primary">{stats?.completion_rate}%</p>
            </div>
            <div className="bg-purple-100 p-3 rounded-xl">
              <TrendingUp className="text-purple-600" size={24} />
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-gray-500 mb-1">Pending</p>
              <p className="text-3xl font-bold text-primary">
                {stats?.total_faculty - stats?.reports_today}
              </p>
            </div>
            <div className="bg-amber-100 p-3 rounded-xl">
              <Clock className="text-amber-600" size={24} />
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Activity Domains */}
        <Card>
          <CardTitle>Activity Distribution</CardTitle>
          <CardContent className="mt-4">
            <div className="space-y-4">
              {stats?.top_domains.map((item) => (
                <div key={item.domain}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">
                      {item.domain}
                    </span>
                    <span className="text-sm text-gray-500">
                      {item.count} tasks ({item.percentage}%)
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary h-2 rounded-full transition-all"
                      style={{ width: `${item.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Submissions */}
        <Card>
          <CardTitle>Recent Submissions</CardTitle>
          <CardContent className="mt-4">
            <div className="space-y-3">
              {stats?.recent_submissions.map((submission, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-xl"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-primary text-white rounded-full flex items-center justify-center font-bold">
                      {submission.professor.charAt(0)}
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-gray-800">
                        {submission.professor}
                      </p>
                      <p className="text-xs text-gray-500">{submission.time}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-primary">
                      {submission.tasks}
                    </p>
                    <p className="text-xs text-gray-500">tasks</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Weekly Trend */}
        <Card className="lg:col-span-2">
          <CardTitle>Weekly Submission Trend</CardTitle>
          <CardContent className="mt-4">
            <div className="flex items-end justify-between gap-4 h-48">
              {stats?.weekly_trend.map((day) => {
                const maxValue = Math.max(...stats.weekly_trend.map(d => d.submissions));
                const height = (day.submissions / maxValue) * 100;

                return (
                  <div key={day.day} className="flex-1 flex flex-col items-center">
                    <div className="w-full flex flex-col items-center justify-end flex-1 mb-2">
                      <span className="text-sm font-semibold text-primary mb-2">
                        {day.submissions}
                      </span>
                      <div
                        className="w-full bg-primary rounded-t-lg transition-all"
                        style={{ height: `${height}%`, minHeight: '20px' }}
                      />
                    </div>
                    <span className="text-xs text-gray-500 font-medium">{day.day}</span>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
};
