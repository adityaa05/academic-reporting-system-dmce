import { useState, useEffect } from 'react';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardTitle, CardContent } from '../../components/ui/Card';
import { LoadingSpinner } from '../../components/ui/Loading';
import { analyticsService } from '../../services/api';
import { DOMAIN_COLORS } from '../../constants';

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
  const domainData = stats?.top_domains.map(item => ({
    name: item.domain,
    value: item.count,
    percentage: item.percentage,
  })) || [];

  const weeklyData = stats?.weekly_trend || [];

  const COLORS = Object.values(DOMAIN_COLORS);

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
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Domain Distribution Pie Chart */}
        <Card>
          <CardTitle>Activity Domain Distribution</CardTitle>
          <CardContent className="mt-4">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={domainData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percentage }) => `${name} ${percentage}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {domainData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Weekly Trend Bar Chart */}
        <Card>
          <CardTitle>Weekly Submission Trend</CardTitle>
          <CardContent className="mt-4">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={weeklyData}>
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="submissions" fill="#1a1a1a" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Domain Breakdown Table */}
        <Card className="lg:col-span-2">
          <CardTitle>Detailed Activity Breakdown</CardTitle>
          <CardContent className="mt-4">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                      Domain
                    </th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">
                      Task Count
                    </th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">
                      Percentage
                    </th>
                    <th className="py-3 px-4 text-sm font-semibold text-gray-700">
                      Distribution
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {domainData.map((item, idx) => (
                    <tr key={idx} className="border-b border-gray-100">
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <div
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                          />
                          <span className="font-medium text-gray-800">{item.name}</span>
                        </div>
                      </td>
                      <td className="text-right py-3 px-4 text-gray-800 font-medium">
                        {item.value}
                      </td>
                      <td className="text-right py-3 px-4 text-gray-600">
                        {item.percentage}%
                      </td>
                      <td className="py-3 px-4">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="h-2 rounded-full"
                            style={{
                              width: `${item.percentage}%`,
                              backgroundColor: COLORS[idx % COLORS.length],
                            }}
                          />
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
};
