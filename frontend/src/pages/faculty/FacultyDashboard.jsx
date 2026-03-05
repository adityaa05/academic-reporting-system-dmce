import { useState } from 'react';
import { Plus, Send, CheckCircle2, Trash2 } from 'lucide-react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Modal } from '../../components/ui/Modal';
import { useAuthStore } from '../../store/authStore';
import { reportService } from '../../services/api';
import { getGreeting } from '../../utils/helpers';

export const FacultyDashboard = () => {
  const { user } = useAuthStore();
  const [tasks, setTasks] = useState([]);
  const [showInputModal, setShowInputModal] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [taskInput, setTaskInput] = useState('');
  const [draftReport, setDraftReport] = useState(null);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [isDispatchingReport, setIsDispatchingReport] = useState(false);

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
      // Send tasks to backend to generate formatted report using Gemini
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
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-primary">
            Hey {user?.name?.split(' ')[1]},
          </h1>
          <p className="text-gray-500 text-lg mt-1">{getGreeting()}!</p>
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
            <div className="bg-gray-100 rounded-xl px-4 py-3 text-center">
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

        {/* Tasks List */}
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
                  className="flex items-center gap-3 bg-gray-50 p-4 rounded-xl border border-gray-100"
                >
                  <div className="flex-shrink-0">
                    <CheckCircle2 size={20} className="text-primary" />
                  </div>
                  <p className="flex-1 text-sm text-gray-800">{task}</p>
                  <button
                    onClick={() => handleDeleteTask(index)}
                    className="flex-shrink-0 text-red-500 hover:text-red-700 transition-colors"
                    title="Delete task"
                  >
                    <Trash2 size={16} />
                  </button>
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
      </div>

      {/* Task Input Modal */}
      <Modal
        isOpen={showInputModal}
        onClose={() => setShowInputModal(false)}
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
            <div className="bg-gray-50 rounded-xl p-4 mb-6 max-h-96 overflow-y-auto">
              <p className="text-sm font-semibold text-gray-700 mb-4">
                AI-Generated Report Preview:
              </p>
              <div className="space-y-4">
                {draftReport.formatted_tasks && draftReport.formatted_tasks.map((task, index) => (
                  <div key={index} className="bg-white p-3 rounded-lg border border-gray-200">
                    <h4 className="text-sm font-semibold text-primary mb-2">
                      {task.title}
                    </h4>
                    <p className="text-sm text-gray-700 leading-relaxed">
                      {task.description}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
              <p className="text-sm text-blue-800">
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
