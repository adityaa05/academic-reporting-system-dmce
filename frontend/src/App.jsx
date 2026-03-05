import React, { useState } from "react";
import { Home, BarChart2, User, Plus, Send, X, Loader2 } from "lucide-react";
import { reportingService } from "./services/api";

export default function App() {
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [showInputModal, setShowInputModal] = useState(false);

  const [activeTab, setActiveTab] = useState("Completed");
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSubmittingTask, setIsSubmittingTask] = useState(false);

  const [rawInput, setRawInput] = useState("");
  const [tasks, setTasks] = useState([]);
  const [draftData, setDraftData] = useState(null);

  // Hardcoded identifier mapping to the IT department for development
  const MOCK_PROFESSOR_ID = "prof_dmce_it_001";

  /**
   * Transmits raw text to the AI for classification and updates the local task list.
   */
  const handleAddTask = async () => {
    if (!rawInput.trim()) return;

    setIsSubmittingTask(true);
    try {
      const response = await reportingService.logTask(
        MOCK_PROFESSOR_ID,
        rawInput,
      );
      // The backend returns the accumulated categorized_tasks array
      setTasks(response.categorized_tasks || []);
      setRawInput("");
      setShowInputModal(false);
    } catch (error) {
      alert("Failed to process task. Ensure backend is running.");
    } finally {
      setIsSubmittingTask(false);
    }
  };

  /**
   * Invokes the Summarization Agent to compile the end-of-day draft.
   */
  const handleGenerateReport = async () => {
    if (tasks.length === 0) {
      alert("No completed tasks to summarize.");
      return;
    }

    setIsProcessing(true);
    try {
      const draft =
        await reportingService.generateDraftReport(MOCK_PROFESSOR_ID);
      setDraftData(draft);
      setShowConfirmModal(true);
    } catch (error) {
      alert("Error generating report.");
    } finally {
      setIsProcessing(false);
    }
  };

  /**
   * Approves the draft and dispatches it to the PostgreSQL database.
   */
  const handleFinalDispatch = async () => {
    setIsProcessing(true);
    try {
      await reportingService.dispatchFinalReport(MOCK_PROFESSOR_ID, true);
      setShowConfirmModal(false);
      setDraftData(null);
      setTasks([]); // Clear the local state after successful dispatch
      alert("Report successfully dispatched to the IT Department Head.");
    } catch (error) {
      alert("Error dispatching report to database.");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen flex justify-center bg-gray-200">
      <div className="w-full max-w-md bg-background min-h-screen shadow-2xl relative pb-24 flex flex-col">
        {/* Header Section */}
        <header className="px-6 pt-12 pb-4">
          <h1 className="text-2xl font-bold text-primary">Hey Aditya,</h1>
          <p className="text-gray-500 text-lg italic mt-1">Good morning!</p>
        </header>

        {/* Date Slider Placeholder */}
        <div className="px-6 mb-6">
          <div className="bg-surface rounded-2xl p-4 shadow-sm flex justify-between items-center">
            {/* Keeping the static calendar for UI structure */}
            <div className="text-center text-gray-400">
              <p className="text-xs">Mon</p>
              <p className="font-semibold text-lg">4</p>
            </div>
            <div className="text-center text-gray-400">
              <p className="text-xs">Tue</p>
              <p className="font-semibold text-lg">5</p>
            </div>
            <div className="text-center bg-gray-100 rounded-xl px-3 py-1">
              <p className="text-xs font-medium text-gray-800">Wed</p>
              <p className="font-bold text-lg text-primary">6</p>
            </div>
            <div className="text-center text-gray-400">
              <p className="text-xs">Thu</p>
              <p className="font-semibold text-lg">7</p>
            </div>
            <div className="text-center text-gray-400">
              <p className="text-xs">Fri</p>
              <p className="font-semibold text-lg">8</p>
            </div>
          </div>
        </div>

        {/* Task List Section */}
        <div className="px-6 flex-1 overflow-y-auto">
          <div className="bg-surface rounded-3xl p-5 shadow-sm min-h-[400px]">
            <div className="flex space-x-4 mb-6 text-sm font-medium border-b pb-3">
              <button
                onClick={() => setActiveTab("To do")}
                className={`${activeTab === "To do" ? "text-primary bg-gray-100 px-4 py-1 rounded-full" : "text-gray-400"}`}
              >
                To do
              </button>
              <button
                onClick={() => setActiveTab("Completed")}
                className={`${activeTab === "Completed" ? "text-primary bg-gray-100 px-4 py-1 rounded-full" : "text-gray-400"}`}
              >
                Completed
              </button>
            </div>

            <div className="space-y-4">
              {tasks.length === 0 ? (
                <p className="text-gray-400 text-center text-sm mt-10 italic">
                  No tasks logged yet. Tap + to add.
                </p>
              ) : (
                tasks.map((task, index) => (
                  <div
                    key={index}
                    className="flex items-start space-x-3 group bg-gray-50 p-3 rounded-xl border border-gray-100"
                  >
                    <div className="w-5 h-5 mt-0.5 rounded border-2 border-primary flex items-center justify-center bg-primary text-white shrink-0">
                      <svg
                        className="w-3 h-3"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={3}
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-gray-800 font-medium text-sm">
                        {task.action}
                      </span>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className="text-[10px] uppercase tracking-wider font-bold text-gray-500 bg-gray-200 px-2 py-0.5 rounded">
                          {task.domain}
                        </span>
                        {task.metric && (
                          <span className="text-[10px] text-gray-500">
                            {task.metric}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Floating Send Button */}
        <div className="absolute bottom-24 right-6">
          <button
            onClick={handleGenerateReport}
            disabled={isProcessing || tasks.length === 0}
            className={`px-6 py-3 rounded-full font-semibold shadow-lg flex items-center space-x-2 transition-transform ${isProcessing || tasks.length === 0 ? "bg-gray-400 cursor-not-allowed" : "bg-primary text-white active:scale-95"}`}
          >
            <span>{isProcessing ? "SYNCING..." : "SEND"}</span>
            {!isProcessing && <Send size={18} />}
          </button>
        </div>

        {/* Bottom Navigation */}
        <nav className="absolute bottom-6 left-6 right-6 bg-surface rounded-full shadow-lg p-2 px-6 flex justify-between items-center z-10">
          <button className="flex items-center space-x-2 text-primary font-semibold">
            <Home size={20} />
            <span className="hidden sm:inline">Home</span>
          </button>
          <button className="text-gray-400 hover:text-primary transition-colors">
            <BarChart2 size={24} />
          </button>
          <button className="text-gray-400 hover:text-primary transition-colors">
            <User size={24} />
          </button>
          <button
            onClick={() => setShowInputModal(true)}
            className="bg-primary text-white p-3 rounded-full shadow-md ml-2 active:scale-95 transition-transform"
          >
            <Plus size={24} />
          </button>
        </nav>

        {/* Task Input Modal */}
        {showInputModal && (
          <div className="absolute inset-0 bg-black/40 flex items-end justify-center z-40 rounded-3xl backdrop-blur-sm">
            <div className="bg-surface w-full rounded-t-3xl p-6 shadow-2xl animate-slide-up">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-bold text-primary">Log Activity</h3>
                <button
                  onClick={() => setShowInputModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X size={20} />
                </button>
              </div>

              <textarea
                value={rawInput}
                onChange={(e) => setRawInput(e.target.value)}
                placeholder="E.g., Delivered 2 hour lecture on DBMS for TE students..."
                className="w-full bg-gray-50 border border-gray-200 rounded-xl p-4 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none h-32 mb-4"
                disabled={isSubmittingTask}
              />

              <button
                onClick={handleAddTask}
                disabled={isSubmittingTask || !rawInput.trim()}
                className={`w-full py-3 rounded-xl font-semibold flex justify-center items-center space-x-2 transition-colors ${isSubmittingTask || !rawInput.trim() ? "bg-gray-300 text-gray-500 cursor-not-allowed" : "bg-primary text-white"}`}
              >
                {isSubmittingTask ? (
                  <>
                    <Loader2 className="animate-spin" size={18} />
                    <span>Processing via AI...</span>
                  </>
                ) : (
                  <span>Add to Log</span>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Confirmation Modal */}
        {showConfirmModal && (
          <div className="absolute inset-0 bg-black/40 flex items-center justify-center z-50 rounded-3xl backdrop-blur-sm">
            <div className="bg-surface rounded-3xl p-8 max-w-[85%] shadow-2xl flex flex-col max-h-[80vh]">
              <h3 className="text-xl font-bold text-center mb-4">
                Confirm Daily Report
              </h3>

              {draftData && (
                <div className="mb-6 overflow-y-auto bg-gray-50 p-4 rounded-xl text-sm border border-gray-100">
                  <p className="font-semibold text-gray-800 mb-2">
                    Executive Summary:
                  </p>
                  <p className="text-gray-600 mb-4">
                    {draftData.executive_summary}
                  </p>
                </div>
              )}

              <div className="flex space-x-4 justify-center mt-auto">
                <button
                  onClick={handleFinalDispatch}
                  disabled={isProcessing}
                  className="bg-primary text-white px-8 py-2 rounded-xl font-semibold border-2 border-primary w-full"
                >
                  Submit
                </button>
                <button
                  onClick={() => setShowConfirmModal(false)}
                  disabled={isProcessing}
                  className="bg-white text-primary px-8 py-2 rounded-xl font-semibold border-2 border-gray-200 w-full"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
