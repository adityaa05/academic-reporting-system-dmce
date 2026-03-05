// src/services/api.js

import axios from "axios";

// Configure the base HTTP client instance for the local FastAPI server
const apiClient = axios.create({
  baseURL: "http://localhost:8000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

export const reportingService = {
  /**
   * Transmits raw user input to the Task Intake Agent for semantic classification.
   * * @param {string} professorId - The unique identifier for the faculty member.
   * @param {string} rawInput - The unstructured text describing the completed task.
   * @returns {Promise<Object>} The standardized operational domain classification.
   */
  logTask: async (professorId, rawInput) => {
    try {
      const response = await apiClient.post("/tasks/intake", {
        professor_id: professorId,
        raw_input: rawInput,
      });
      return response.data;
    } catch (error) {
      console.error("Task intake failure:", error);
      throw error;
    }
  },

  /**
   * Invokes the Summarization Agent to compile the daily executive draft.
   * Execution pauses at the Human-in-the-Loop checkpoint after returning this draft.
   * * @param {string} professorId - The unique identifier for the faculty member.
   * @returns {Promise<Object>} The structured JSON report draft.
   */
  generateDraftReport: async (professorId) => {
    try {
      const response = await apiClient.post(
        `/reports/generate?professor_id=${professorId}`,
      );
      return response.data;
    } catch (error) {
      console.error("Draft generation failure:", error);
      throw error;
    }
  },

  /**
   * Resumes LangGraph execution post-validation and dispatches data to PostgreSQL.
   * * @param {string} professorId - The unique identifier for the faculty member.
   * @param {boolean} isApproved - Validation boolean confirming factual accuracy.
   * @param {string|null} editedSummary - Optional override if the human modified the AI draft.
   * @returns {Promise<Object>} The database insertion status.
   */
  dispatchFinalReport: async (
    professorId,
    isApproved,
    editedSummary = null,
  ) => {
    try {
      const payload = {
        professor_id: professorId,
        is_approved: isApproved,
      };

      if (editedSummary) {
        payload.edited_summary = editedSummary;
      }

      const response = await apiClient.post("/reports/dispatch", payload);
      return response.data;
    } catch (error) {
      console.error("Report dispatch failure:", error);
      throw error;
    }
  },
};
