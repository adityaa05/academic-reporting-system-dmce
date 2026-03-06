import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  "https://academic-reporting-api-573297019071.asia-south1.run.app/api/v1";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("auth_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("auth_token");
      localStorage.removeItem("user_data");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

export const authService = {
  login: async (email, password) => {
    const response = await apiClient.post("/auth/login", {
      email,
      password,
    });
    const { access_token, user } = response.data;
    localStorage.setItem("auth_token", access_token);
    localStorage.setItem("user_data", JSON.stringify(user));
    return { user, token: access_token };
  },

  register: async (
    name,
    email,
    password,
    department = "IT",
    role = "FACULTY",
  ) => {
    const response = await apiClient.post("/auth/register", {
      name,
      email,
      password,
      department,
      role,
    });
    const { access_token, user } = response.data;
    localStorage.setItem("auth_token", access_token);
    localStorage.setItem("user_data", JSON.stringify(user));
    return { user, token: access_token };
  },

  logout: () => {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("user_data");
  },

  getCurrentUser: async () => {
    try {
      const response = await apiClient.get("/auth/me");
      const user = response.data;
      localStorage.setItem("user_data", JSON.stringify(user));
      return user;
    } catch (error) {
      // If token is invalid, clear storage
      localStorage.removeItem("auth_token");
      localStorage.removeItem("user_data");
      return null;
    }
  },

  getCurrentUserSync: () => {
    const userData = localStorage.getItem("user_data");
    return userData ? JSON.parse(userData) : null;
  },
};

export const taskService = {
  logTask: async (rawInput) => {
    const response = await apiClient.post("/tasks/intake", {
      raw_input: rawInput,
    });
    return response.data;
  },
};

export const reportService = {
  generateDraftReport: async () => {
    const response = await apiClient.post("/reports/generate");
    return response.data;
  },

  dispatchFinalReport: async (isApproved, editedSummary = null) => {
    const payload = {
      is_approved: isApproved,
    };
    if (editedSummary) {
      payload.edited_summary = editedSummary;
    }
    const response = await apiClient.post("/reports/dispatch", payload);
    return response.data;
  },

  getReportHistory: async () => {
    const response = await apiClient.get("/reports/history");
    return response.data;
  },

  // Simplified API
  submitSimpleReport: async (tasks) => {
    const response = await apiClient.post("/simple/reports/submit", {
      tasks: tasks,
    });
    return response.data;
  },

  getMyHistory: async () => {
    const response = await apiClient.get("/simple/reports/my-history");
    return response.data;
  },

  getAllFacultyReports: async (days = 30) => {
    const response = await apiClient.get(`/simple/reports/all?days=${days}`);
    return response.data;
  },

  getNewReportsCount: async () => {
    const response = await apiClient.get("/simple/reports/new-count");
    return response.data;
  },

  // AI-powered formatted reports
  generateFormattedReport: async (tasksList) => {
    const response = await apiClient.post("/reports/generate-formatted", {
      tasks: tasksList,
    });
    return response.data;
  },

  dispatchFormattedReport: async (isApproved) => {
    const response = await apiClient.post("/reports/dispatch-formatted", {
      is_approved: isApproved,
    });
    return response.data;
  },
};

export const analyticsService = {
  getDashboardMetrics: async () => {
    const response = await apiClient.get("/dashboard/metrics");
    return response.data;
  },

  getAggregatedReportStream: async () => {
    // For SSE streaming with authentication
    const token = localStorage.getItem("auth_token");
    const response = await fetch(`${API_BASE_URL}/reports/aggregate/stream`, {
      headers: {
        Accept: "text/event-stream",
        Authorization: `Bearer ${token}`,
      },
    });
    return response;
  },

  getDepartmentStats: async () => {
    const response = await apiClient.get("/hod/stats");
    return response.data;
  },
};

export default apiClient;
