import { useState, useEffect } from 'react';
import { Plus, Send, CheckCircle2, Trash2 } from 'lucide-react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Modal } from '../../components/ui/Modal';
import { useAuthStore } from '../../store/authStore';
import { reportService } from '../../services/api';
import { getGreeting } from '../../utils/helpers';

const STORAGE_KEY = 'faculty_draft_tasks';

export const FacultyDashboard = () => {
  const { user } = useAuthStore();
  const [tasks, setTasks] = useState([]);
  const [showInputModal, setShowInputModal] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [taskInput, setTaskInput] = useState('');
  const [draftReport, setDraftReport] = useState(null);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [isDispatchingReport, setIsDispatchingReport] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Load tasks from localStorage and backend on mount
  useEffect(() => {
    const loadTasks = async () => {
      // Try localStorage first (faster)
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        try {
          setTasks(JSON.parse(stored));
        } catch (e) {
          console.error('Error parsing stored tasks:', e);
        }
      }

      // Then sync with backend
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/simple/tasks/draft/load`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          if (data.tasks && data.tasks.length > 0) {
            const taskTexts = data.tasks.map(t => t.text);
            setTasks(taskTexts);
            localStorage.setItem(STORAGE_KEY, JSON.stringify(taskTexts));
          }
        }
      } catch (error) {
        console.error('Error loading draft tasks from backend:', error);
      }
    };

    loadTasks();
  }, []);

  // Auto-save tasks whenever they change
  useEffect(() => {
    if (tasks.length === 0) return;

    const saveTasks = async () => {
      // Save to localStorage immediately
      localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));

      // Debounced save to backend
      setIsSaving(true);
      try {
        await fetch(`${import.meta.env.VITE_API_URL}/api/v1/simple/tasks/draft/save`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
          body: JSON.stringify({
            tasks: tasks.map(text => ({ text, completed: false })),
          }),
        });
      } catch (error) {
        console.error('Error saving draft tasks to backend:', error);
      } finally {
        setIsSaving(false);
      }
    };

    const timeout = setTimeout(saveTasks, 1000); // Debounce 1 second
    return () => clearTimeout(timeout);
  }, [tasks]);

  const handleAddTask = () => {
    if (!taskInput.trim()) return;

    setTasks([...tasks, taskInput.trim()]);
    setTaskInput('');
    setShowInputModal(false);
  };

  const handleDeleteTask = (index) => {
    setTasks(tasks.filter((_, i) => i !== index));
  };

  const handleGenerateReport = async () => {
    if (tasks.length === 0) {
      alert('No tasks to generate report from.');
      return;
    }

    setIsGeneratingReport(true);
    try {
      const draft = await reportService.generateFormattedReport(tasks);
      setDraftReport(draft);
      setShowConfirmModal(true);
    } catch (error) {
      alert('Error generating report. Please try again.');
      console.error('Report generation error:', error);
    } finally {
      setIsGeneratingReport(false);
    }
  };

  const handleDispatchReport = async () => {
    setIsDispatchingReport(true);
    try {
      await reportService.dispatchFormattedReport(true);
      setShowConfirmModal(false);
      setDraftReport(null);
      setTasks([]);
      // Clear localStorage after successful submission
      localStorage.removeItem(STORAGE_KEY);
      alert('Report submitted successfully!');
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Error submitting report. Please try again.';
      alert(errorMsg);
      console.error('Report dispatch error:', error);
    } finally {
      setIsDispatchingReport(false);
    }
  };

  return (
    <AppLayout>
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Header */}
        <div className="mb-6 sm:mb-8">
          <h1 className="text-2xl sm:text-3xl font-semibold text-gray-900">
            Hey {user?.name?.split(' ')[0]},
          </h1>
          <p className="text-gray-600 text-base sm:text-lg mt-1">{getGreeting()}!</p>
        </div>

        {/* Date Display */}
        <Card className="mb-5 sm:mb-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Today's Date</p>
              <p className="text-base sm:text-lg font-medium text-gray-900 mt-1">
                {new Date().toLocaleDateString('en-US', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg px-3 sm:px-4 py-2 sm:py-3 text-center border border-gray-200">
              <p className="text-xl sm:text-2xl font-semibold text-gray-900">
                {new Date().getDate()}
              </p>
              <p className="text-xs text-gray-500 uppercase tracking-wide">
                {new Date().toLocaleDateString('en-US', { month: 'short' })}
              </p>
            </div>
          </div>
        </Card>

        {/* Task Summary */}
        <div className="grid grid-cols-2 gap-3 sm:gap-4 mb-5 sm:mb-6">
          <Card>
            <p className="text-xs sm:text-sm text-gray-500 mb-1">Tasks Logged</p>
            <p className="text-2xl sm:text-3xl font-semibold text-gray-900">{tasks.length}</p>
          </Card>
          <Card>
            <p className="text-xs sm:text-sm text-gray-500 mb-1">Status</p>
            <div className="flex items-center gap-2 mt-1">
              <div className={`w-2 h-2 rounded-full ${tasks.length > 0 ? 'bg-green-500' : 'bg-gray-300'}`} />
              <p className="text-sm sm:text-base font-medium text-gray-900">
                {tasks.length > 0 ? 'In Progress' : 'No Tasks'}
              </p>
            </div>
          </Card>
        </div>

        {/* Auto-save indicator */}
        {isSaving && (
          <div className="mb-4 text-xs text-gray-500 text-right">
            Saving...
          </div>
        )}

        {/* Tasks List */}
        <Card className="min-h-[350px] sm:min-h-[400px]">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base sm:text-lg font-semibold text-gray-900">Today's Activities</h3>
            <Button
              size="sm"
              onClick={() => setShowInputModal(true)}
              icon={<Plus size={16} />}
              className="text-sm"
            >
              <span className="hidden sm:inline">Add Task</span>
              <span className="sm:hidden">Add</span>
            </Button>
          </div>

          <CardContent className="space-y-2 sm:space-y-3">
            {tasks.length === 0 ? (
              <div className="text-center py-12 sm:py-16">
                <p className="text-gray-400 mb-4 text-sm sm:text-base">No tasks logged yet</p>
                <Button
                  variant="secondary"
                  onClick={() => setShowInputModal(true)}
                  icon={<Plus size={18} />}
                  className="text-sm sm:text-base"
                >
                  Log Your First Task
                </Button>
              </div>
            ) : (
              tasks.map((task, index) => (
                <div
                  key={index}
                  className="flex items-start gap-3 bg-gray-50 p-3 sm:p-4 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors"
                >
                  <div className="flex-shrink-0 mt-0.5">
                    <CheckCircle2 size={18} className="text-green-600" />
                  </div>
                  <p className="flex-1 text-sm text-gray-800 leading-relaxed break-words">{task}</p>
                  <button
                    onClick={() => handleDeleteTask(index)}
                    className="flex-shrink-0 text-gray-400 hover:text-red-600 transition-colors p-1"
                    title="Delete task"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              ))
            )}
          </CardContent>

          {tasks.length > 0 && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <Button
                variant="primary"
                size="lg"
                className="w-full"
                onClick={handleGenerateReport}
                loading={isGeneratingReport}
                icon={<Send size={18} />}
              >
                Generate & Submit Report
              </Button>
            </div>
          )}
        </Card>
      </div>

      {/* Task Input Modal */}
      <Modal
        isOpen={showInputModal}
        onClose={() => setShowInputModal(false)}
        title="Log Your Activity"
      >
        <Input
          label="What did you do?"
          placeholder="E.g., Completed theory lectures"
          value={taskInput}
          onChange={(e) => setTaskInput(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter' && taskInput.trim()) {
              handleAddTask();
            }
          }}
          autoFocus
        />
        <p className="text-xs text-gray-500 mt-2 leading-relaxed">
          Just type a quick note. AI will format it into a proper report when you submit.
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
        {draftReport && (
          <>
            <div className="bg-gray-50 rounded-lg p-4 mb-6 max-h-96 overflow-y-auto border border-gray-200">
              <p className="text-sm font-medium text-gray-700 mb-4">
                AI-Generated Report Preview:
              </p>
              <div className="space-y-3">
                {draftReport.formatted_tasks && draftReport.formatted_tasks.map((task, index) => (
                  <div key={index} className="bg-white p-3 sm:p-4 rounded-lg border border-gray-200">
                    <h4 className="text-sm font-semibold text-gray-900 mb-2">
                      {task.title}
                    </h4>
                    <p className="text-sm text-gray-700 leading-relaxed">
                      {task.description}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <p className="text-sm text-blue-800 leading-relaxed">
                This AI-generated report will be submitted to your HOD. Review it carefully before confirming.
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
          </>
        )}
      </Modal>
    </AppLayout>
  );
};
