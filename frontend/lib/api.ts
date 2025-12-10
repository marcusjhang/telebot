import axios from 'axios';
import { authLib } from './auth';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
});

// Add JWT token to requests
api.interceptors.request.use((config) => {
  const token = authLib.getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors (redirect to login)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      authLib.removeToken();
      if (typeof window !== 'undefined') {
        window.location.href = '/';
      }
    }
    return Promise.reject(error);
  }
);

// Type definitions
export interface GoalInput {
  daily_water_bottles: number;
  daily_carb_max_portions: number;
  weekly_exercise_sessions: number;
  effective_from?: string;
}

export interface GoalResponse {
  id: number;
  user_id: number;
  daily_water_bottles: number;
  daily_carb_max_portions: number;
  weekly_exercise_sessions: number;
  effective_from: string;
  created_at: string;
}

export interface TodayProgress {
  date: string;
  water: {
    current: number;
    goal: number;
    achieved: boolean;
  };
  carbs: {
    current: number;
    goal: number;
    within_limit: boolean;
  };
  exercise: {
    weekly_total: number;
    weekly_goal: number;
    week_start: string;
    week_end: string;
  };
  streaks: {
    water_streak: number;
    carbs_streak: number;
    exercise_streak: number;
  };
}

export interface UserResponse {
  id: number;
  telegram_user_id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  recap_enabled: boolean;
  created_at: string;
}

export interface UserPreferences {
  recap_enabled?: boolean;
}

// API client
export const apiClient = {
  // Goals
  getGoals: () => api.get<GoalResponse[]>('/api/v1/goals'),
  getCurrentGoal: () => api.get<GoalResponse>('/api/v1/goals'),
  getGoalHistory: () => api.get<GoalResponse[]>('/api/v1/goals/history'),
  createGoal: (data: GoalInput) => api.post<GoalResponse>('/api/v1/goals', data),

  // Progress
  getTodayProgress: () => api.get<TodayProgress>('/api/v1/progress/today'),

  // User
  getMe: () => api.get<UserResponse>('/api/v1/users/me'),
  updatePreferences: (data: UserPreferences) => api.patch<UserResponse>('/api/v1/users/me', data),
};

export default api;

