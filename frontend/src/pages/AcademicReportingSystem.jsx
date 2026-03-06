import { useState } from 'react';
import { Plus, Send, Trash2, TrendingUp, Users, FileText, Clock } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Modal } from '../components/ui/Modal';

// Sample data for HOD view
const SAMPLE_WEEKLY_DATA = [
  { day: 'Mon', submissions: 12 },
  { day: 'Tue', submissions: 19 },
  { day: 'Wed', submissions: 15 },
  { day: 'Thu', submissions: 22 },
  { day: 'Fri', submissions: 18 },
];

const SAMPLE_FACULTY_REPORTS = [
  {
    id: 1,
    facultyName: 'Dr. Rajesh Kumar',
    email: 'rajesh.kumar@dmce.edu',
    submissionTime: '10:30 AM',
    isNew: true,
    tasks: [
      'Task 01: Conducted a session on Database Management Systems with emphasis on normalization and query optimization.',
      'Task 02: Evaluated assignments from 40 students covering SQL programming and data manipulation.',
      'Task 03: Prepared course materials for the upcoming unit on transaction management and ACID properties.',
    ],
  },
  {
    id: 2,
    facultyName: 'Prof. Anjali Singh',
    email: 'anjali.singh@dmce.edu',
    submissionTime: '09:45 AM',
    isNew: true,
    tasks: [
      'Task 01: Delivered lecture on web development frameworks with practical demonstrations.',
      'Task 02: Mentored 5 students on their semester projects related to full-stack development.',
    ],
  },
  {
    id: 3,
    facultyName: 'Dr. Priya Patel',
    email: 'priya.patel@dmce.edu',
    submissionTime: 'Yesterday',
    isNew: false,
    tasks: [
      'Task 01: Conducted advanced algorithms session covering graph theory and dynamic programming.',
      'Task 02: Reviewed and graded mid-term examination papers for 45 students.',
    ],
  },
];

export const AcademicReportingSystem = () => {
  // View State
  const [currentView, setCurrentView] = useState('faculty'); // 'faculty' or 'hod'

  // Faculty View State
  const [tasks, setTasks] = useState([]);
  const [showInputModal, setShowInputModal] = useState(false);
  const [taskInput, setTaskInput] = useState('');
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [isDispatchingReport, setIsDispatchingReport] = useState(false);

  // Faculty Functions
  const handleAddTask = () => {
    if (!taskInput.trim()) return;

    const taskNumber = tasks.length + 1;
    const formattedTask = `Task ${String(taskNumber).padStart(2, '0')}: ${taskInput.trim()}`;
    setTasks([...tasks, formattedTask]);
    setTaskInput('');
    setShowInputModal(false);
  };

  const handleDeleteTask = (index) => {
    const updatedTasks = tasks.filter((_, i) => i !== index);
    // Renumber remaining tasks
    const renumberedTasks = updatedTasks.map((task, idx) => {
      const taskContent = task.substring(task.indexOf(':') + 1).trim();
      return `Task ${String(idx + 1).padStart(2, '0')}: ${taskContent}`;
    });
    setTasks(renumberedTasks);
  };

  const handleGenerateReport = async () => {
    if (tasks.length === 0) {
      alert('No tasks to generate report from.');
      return;
    }
    setIsGeneratingReport(true);
    // Simulate API call
    setTimeout(() => {
      setIsGeneratingReport(false);
      setShowConfirmModal(true);
    }, 1500);
  };

  const handleDispatchReport = async () => {
    setIsDispatchingReport(true);
    // Simulate API call
    setTimeout(() => {
      setIsDispatchingReport(false);
      setShowConfirmModal(false);
      setTasks([]);
      alert('Report submitted successfully!');
    }, 1500);
  };

  // Render Faculty Dashboard
  const renderFacultyDashboard = () => (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-primary">Welcome, Faculty Member</h1>
        <p className="text-gray-500 text-lg mt-1">Document your daily activities and submit your report</p>
      </div>

      {/* Date Display */}
      <Card className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-500">Today's Date</p>
            <p className="text-lg font-semibold text-primary mt-1">
              {new Date().toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </p>
          </div>
          <div className="bg-gray-100 rounded-2xl px-4 py-3 text-center">
            <p className="text-2xl font-bold text-primary">
              {new Date().getDate()}
            </p>
            <p className="text-xs text-gray-500 uppercase">
              {new Date().toLocaleDateString('en-US', { month: 'short' })}
            </p>
          </div>
        </div>
      </Card>

      {/* Task Summary */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <Card>
          <p className="text-sm text-gray-500 mb-1">Tasks Logged</p>
          <p className="text-3xl font-bold text-primary">{tasks.length}</p>
        </Card>
        <Card>
          <p className="text-sm text-gray-500 mb-1">Status</p>
          <p className="text-lg font-semibold text-green-600">
            {tasks.length > 0 ? 'In Progress' : 'No Tasks'}
          </p>
        </Card>
      </div>

      {/* Tasks List Card */}
      <Card className="min-h-[400px]">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-primary">Today's Activities</h3>
          <Button
            size="sm"
            onClick={() => setShowInputModal(true)}
            icon={<Plus size={18} />}
          >
            Add Task
          </Button>
        </div>

        <CardContent className="space-y-3">
          {tasks.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-400 mb-4">No tasks logged yet</p>
              <Button
                variant="secondary"
                onClick={() => setShowInputModal(true)}
                icon={<Plus size={18} />}
              >
                Log Your First Task
              </Button>
            </div>
          ) : (
            tasks.map((task, index) => (
              <div
                key={index}
                className="bg-gray-50 p-4 rounded-2xl border border-gray-100 hover:shadow-md transition-all"
              >
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 mt-1">
                    <div className="w-6 h-6 rounded-full bg-primary text-white flex items-center justify-center text-xs font-bold">
                      {index + 1}
                    </div>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-gray-800 mb-1">
                      {task.substring(0, task.indexOf(':') + 1)}
                    </p>
                    <p className="text-sm text-gray-700">
                      {task.substring(task.indexOf(':') + 1).trim()}
                    </p>
                  </div>
                  <button
                    onClick={() => handleDeleteTask(index)}
                    className="flex-shrink-0 text-red-400 hover:text-red-600 transition-colors p-2"
                    title="Delete task"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
            ))
          )}
        </CardContent>

        {tasks.length > 0 && (
          <div className="mt-6 pt-6 border-t border-gray-100">
            <Button
              variant="primary"
              size="lg"
              className="w-full"
              onClick={handleGenerateReport}
              loading={isGeneratingReport}
              icon={<Send size={20} />}
            >
              Generate & Submit Report
            </Button>
          </div>
        )}
      </Card>

      {/* Task Input Modal */}
      <Modal
        isOpen={showInputModal}
        onClose={() => {
          setShowInputModal(false);
          setTaskInput('');
        }}
        title="Log Your Activity"
      >
        <Input
          label="What did you do?"
          placeholder="E.g., Taught DBMS lecture to TE students"
          value={taskInput}
          onChange={(e) => setTaskInput(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter' && taskInput.trim()) {
              handleAddTask();
            }
          }}
          autoFocus
        />
        <p className="text-xs text-gray-500 mt-2">
          Just type a quick note. Your task will be automatically formatted.
        </p>
        <div className="flex gap-3 mt-6">
          <Button
            variant="primary"
            className="flex-1"
            onClick={handleAddTask}
            disabled={!taskInput.trim()}
          >
            Add to Log
          </Button>
          <Button
            variant="secondary"
            className="flex-1"
            onClick={() => {
              setShowInputModal(false);
              setTaskInput('');
            }}
          >
            Cancel
          </Button>
        </div>
      </Modal>

      {/* Report Confirmation Modal */}
      <Modal
        isOpen={showConfirmModal}
        onClose={() => setShowConfirmModal(false)}
        title="Confirm Daily Report"
        size="lg"
      >
        <div className="bg-gray-50 rounded-2xl p-4 mb-6 max-h-96 overflow-y-auto">
          <p className="text-sm font-semibold text-gray-700 mb-4">
            Report Preview:
          </p>
          <div className="space-y-4">
            {tasks.map((task, index) => (
              <div key={index} className="bg-white p-3 rounded-xl border border-gray-200">
                <p className="text-sm text-gray-700 leading-relaxed">
                  {task}
                </p>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
          <p className="text-sm text-blue-800">
            This report will be submitted to your HOD for review. Please review it carefully before confirming.
          </p>
        </div>

        <div className="flex gap-3">
          <Button
            variant="primary"
            className="flex-1"
            size="lg"
            onClick={handleDispatchReport}
            loading={isDispatchingReport}
          >
            Confirm & Submit
          </Button>
          <Button
            variant="secondary"
            className="flex-1"
            onClick={() => setShowConfirmModal(false)}
            disabled={isDispatchingReport}
          >
            Cancel
          </Button>
        </div>
      </Modal>
    </div>
  );

  // Render HOD Dashboard
  const renderHODDashboard = () => (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-primary">HOD Dashboard</h1>
        <p className="text-gray-500 text-lg mt-1">Review faculty daily reports and analytics</p>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Faculty</p>
              <p className="text-3xl font-bold text-primary mt-1">42</p>
            </div>
            <div className="bg-blue-100 rounded-2xl p-3">
              <Users size={24} className="text-blue-600" />
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Reports Today</p>
              <p className="text-3xl font-bold text-primary mt-1">{SAMPLE_FACULTY_REPORTS.filter(r => r.isNew).length}</p>
            </div>
            <div className="bg-green-100 rounded-2xl p-3">
              <FileText size={24} className="text-green-600" />
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Submission Rate</p>
              <p className="text-3xl font-bold text-primary mt-1">95%</p>
            </div>
            <div className="bg-purple-100 rounded-2xl p-3">
              <TrendingUp size={24} className="text-purple-600" />
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Avg Response</p>
              <p className="text-3xl font-bold text-primary mt-1">15 min</p>
            </div>
            <div className="bg-orange-100 rounded-2xl p-3">
              <Clock size={24} className="text-orange-600" />
            </div>
          </div>
        </Card>
      </div>

      {/* Weekly Trend Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Weekly Submission Trend</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={SAMPLE_WEEKLY_DATA}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="day" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '12px',
                }}
              />
              <Bar dataKey="submissions" fill="#1a1a1a" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Faculty Reports Feed */}
      <div>
        <h2 className="text-2xl font-bold text-primary mb-4">Faculty Reports</h2>
        <div className="space-y-4">
          {SAMPLE_FACULTY_REPORTS.map((report) => (
            <Card
              key={report.id}
              className={`${report.isNew ? 'border-l-4 border-l-green-500 bg-green-50' : ''}`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-bold text-primary">{report.facultyName}</h3>
                    {report.isNew && (
                      <span className="px-2 py-1 bg-green-500 text-white text-xs font-semibold rounded-full">
                        New
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-500">{report.email}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-500">
                    Submitted at {report.submissionTime}
                  </p>
                </div>
              </div>

              {/* Tasks List */}
              <CardContent className="space-y-2 mt-4 border-t border-gray-100 pt-4">
                {report.tasks.map((task, idx) => (
                  <div key={idx} className="text-sm text-gray-700 pl-4 border-l-2 border-gray-200">
                    <p className="font-semibold text-gray-800 mb-1">
                      {task.substring(0, task.indexOf(':') + 1)}
                    </p>
                    <p className="text-gray-600">
                      {task.substring(task.indexOf(':') + 1).trim()}
                    </p>
                  </div>
                ))}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Global College Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between sm:justify-start py-3 sm:py-4 gap-3 sm:gap-4">
            {/* Logo & Title */}
            <div className="flex items-center gap-4 flex-1">
              <div className="flex-shrink-0">
                <img
                  src="/images/dmce-logo.png"
                  alt="DMCE Logo"
                  className="w-12 h-12 sm:w-14 sm:h-14 object-contain"
                  onError={(e) => {
                    e.target.style.display = 'none';
                  }}
                />
              </div>
              <div className="flex flex-col">
                <p className="text-xs sm:text-sm text-gray-600 font-medium">
                  Nagar Yuwak Shikshan Sanstha, Airoli's
                </p>
                <h1 className="text-lg sm:text-xl md:text-2xl font-bold text-gray-900">
                  Datta Meghe College of Engineering
                </h1>
              </div>
            </div>

            {/* View Toggle */}
            <div className="flex gap-2 ml-auto">
              <button
                onClick={() => setCurrentView('faculty')}
                className={`px-4 py-2 rounded-xl font-semibold transition-all ${
                  currentView === 'faculty'
                    ? 'bg-primary text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Faculty View
              </button>
              <button
                onClick={() => setCurrentView('hod')}
                className={`px-4 py-2 rounded-xl font-semibold transition-all ${
                  currentView === 'hod'
                    ? 'bg-primary text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                HOD View
              </button>
            </div>
          </div>
        </div>
        {/* Yellow accent line */}
        <div className="h-1 bg-gradient-to-r from-yellow-400 via-yellow-500 to-yellow-400"></div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'faculty' ? renderFacultyDashboard() : renderHODDashboard()}
      </main>
    </div>
  );
};

export default AcademicReportingSystem;
