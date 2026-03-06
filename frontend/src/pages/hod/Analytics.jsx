import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardTitle, CardContent } from '../../components/ui/Card';
import { LoadingSpinner } from '../../components/ui/Loading';
import { analyticsService } from '../../services/api';

export const Analytics = () => {
  const [metrics, setMetrics] = useState(null);
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [metricsData, statsData] = await Promise.all([
        analyticsService.getDashboardMetrics(),
        analyticsService.getDepartmentStats(),
      ]);
      setMetrics(metricsData);
      setStats(statsData);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setIsLoading(false);
    }
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

  // Prepare data for charts
  const weeklyData = stats?.weekly_trend || [];

  return (
    <AppLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-primary mb-2">Analytics</h1>
        <p className="text-gray-500">Detailed department insights and trends</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <p className="text-sm text-gray-500 mb-1">Total Submissions</p>
          <p className="text-4xl font-bold text-primary">{metrics?.total_submissions || 0}</p>
          <p className="text-xs text-gray-400 mt-2">As of {metrics?.date}</p>
        </Card>

        <Card>
          <p className="text-sm text-gray-500 mb-1">Active Faculty</p>
          <p className="text-4xl font-bold text-primary">{stats?.reports_today || 0}</p>
          <p className="text-xs text-gray-400 mt-2">Submitted reports today</p>
        </Card>

        <Card>
          <p className="text-sm text-gray-500 mb-1">Completion Rate</p>
          <p className="text-4xl font-bold text-primary">{stats?.completion_rate || 0}%</p>
          <p className="text-xs text-gray-400 mt-2">
            {stats?.total_faculty - stats?.reports_today} pending
          </p>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-6">
        {/* Weekly Trend Bar Chart */}
        <Card>
          <CardTitle>Weekly Submission Trend</CardTitle>
          <CardContent className="mt-4">
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={weeklyData}>
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="submissions" fill="#111827" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
};
