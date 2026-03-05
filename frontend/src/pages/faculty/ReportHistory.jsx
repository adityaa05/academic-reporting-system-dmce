import { useState, useEffect } from 'react';
import { FileText, Calendar, ChevronRight, ChevronDown, ChevronUp } from 'lucide-react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card } from '../../components/ui/Card';
import { LoadingSpinner } from '../../components/ui/Loading';
import { reportService } from '../../services/api';

export const ReportHistory = () => {
  const [reports, setReports] = useState([]);
  const [expandedReports, setExpandedReports] = useState(new Set());
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    setIsLoading(true);
    try {
      const data = await reportService.getMyHistory();
      setReports(data || []);
    } catch (error) {
      console.error('Error fetching reports:', error);
    } finally {
      setIsLoading(false);
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
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-primary mb-2">My Report History</h1>
          <p className="text-gray-500">View all your submitted daily reports</p>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : reports.length === 0 ? (
          <Card>
            <div className="text-center py-12">
              <FileText size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-500">No reports submitted yet</p>
              <p className="text-sm text-gray-400 mt-2">Start logging tasks to create your first report</p>
            </div>
          </Card>
        ) : (
          <div className="space-y-4">
            {reports.map((report) => {
              const isExpanded = expandedReports.has(report.id);

              return (
                <Card key={report.id}>
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
                        <p className="text-sm font-semibold text-gray-800 mb-1">
                          {formatDate(report.date_submitted)}
                        </p>
                        <p className="text-sm text-gray-600">
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
      </div>
    </AppLayout>
  );
};
