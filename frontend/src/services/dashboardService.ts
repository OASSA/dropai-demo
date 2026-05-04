import api from "./api";
import { DashboardStats } from "../types";

export const dashboardService = {
  async getStats(): Promise<DashboardStats> {
    const { data } = await api.get<DashboardStats>("/dashboard/stats");
    return data;
  },

  async getActivity(limit = 10) {
    const { data } = await api.get("/dashboard/activity", { params: { limit } });
    return data;
  },
};
