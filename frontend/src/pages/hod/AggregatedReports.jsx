import { useState, useEffect } from 'react';
import { RefreshCw, ChevronDown, ChevronUp } from 'lucide-react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { LoadingSpinner } from '../../components/ui/Loading';
import { reportService } from '../../services/api';

export const AggregatedReports = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [reports, setReports] = useState([]);
  const [expandedReports, setExpandedReports] = useState(new Set());
  const [lastUpdated, setLastUpdated] = useState(null);
  const [newCount, setNewCount] = useState(0);

  useEffect(() => {
    fetchReports();
    fetchNewCount();

    // Auto-refresh every 60 seconds
    const interval = setInterval(() => {
      fetchReports();
      fetchNewCount();
    }, 60000);

    return () => clearInterval(interval);
  }, []);

  const fetchReports = async () => {
    setIsLoading(true);
    try {
      const data = await reportService.getAllFacultyReports(30);
      setReports(data);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error fetching reports:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchNewCount = async () => {
    try {
      const data = await reportService.getNewReportsCount();
      setNewCount(data.new_reports || 0);
    } catch (error) {
      console.error('Error fetching new count:', error);
    }
  };

  const toggleExpand = (reportId) => {
    const newExpanded = new Set(expandedReports);
    if (newExpanded.has(reportId)) {
      newExpanded.delete(reportId);
    } else {
      newExpanded.add(reportId);
    }
    setExpandedReports(newExpanded);
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <AppLayout>
      <div className="mb-8 flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold text-primary mb-2">Faculty Reports</h1>
          <p className="text-gray-500">View all submitted daily reports</p>
          {newCount > 0 && (
            <span className="inline-block mt-2 px-3 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded-full">
              {newCount} new report{newCount > 1 ? 's' : ''} today
            </span>
          )}
        </div>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => {
            fetchReports();
            fetchNewCount();
          }}
          loading={isLoading}
          icon={<RefreshCw size={16} />}
        >
          Refresh
        </Button>
      </div>

      {lastUpdated && (
        <div className="mb-4 text-sm text-gray-500">
          Last updated: {lastUpdated.toLocaleTimeString()}
        </div>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      ) : reports.length === 0 ? (
        <Card>
          <div className="text-center py-12">
            <p className="text-gray-400 mb-2">No reports submitted yet</p>
            <p className="text-sm text-gray-500">Faculty reports will appear here once submitted</p>
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          {reports.map((report) => {
            const isExpanded = expandedReports.has(report.id);
            const isToday = new Date(report.date_submitted).toDateString() === new Date().toDateString();

            return (
              <Card key={report.id} className={isToday ? 'border-2 border-green-200' : ''}>
                <div
                  className="flex items-center justify-between cursor-pointer hover:bg-gray-50 rounded-lg p-4 -m-4"
                  onClick={() => toggleExpand(report.id)}
                >
                  <div className="flex items-center gap-4 flex-1">
                    <div className="bg-gray-100 rounded-lg p-3 text-center min-w-[60px]">
                      <p className="text-xs text-gray-500 uppercase">
                        {new Date(report.date_submitted).toLocaleDateString('en-US', { month: 'short' })}
                      </p>
                      <p className="text-2xl font-bold text-primary">
                        {new Date(report.date_submitted).getDate()}
                      </p>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1 flex-wrap">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {report.professor_name}
                        </h3>
                        {isToday && (
                          <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded">
                            New
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-500">{formatDate(report.date_submitted)}</p>
                      <p className="text-sm text-gray-600 mt-1">
                        {report.tasks.length} task{report.tasks.length > 1 ? 's' : ''} completed
                      </p>
                    </div>
                  </div>
                  <button className="text-gray-400 hover:text-primary transition-colors p-2">
                    {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                  </button>
                </div>

                {isExpanded && (
                  <div className="mt-4 pt-4 border-t border-gray-100 space-y-3">
                    {report.tasks.map((task, index) => (
                      <div key={index} className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="text-sm font-semibold text-primary mb-2">
                          {task.title}
                        </h4>
                        <p className="text-sm text-gray-700 leading-relaxed">
                          {task.description}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      )}
    </AppLayout>
  );
};
