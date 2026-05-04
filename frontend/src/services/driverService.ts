import api from "./api";
import { Driver, PaginatedResponse } from "../types";

export const driverService = {
  async list(page = 1, size = 20): Promise<PaginatedResponse<Driver>> {
    const { data } = await api.get<PaginatedResponse<Driver>>("/drivers", { params: { page, size } });
    return data;
  },

  async get(id: number): Promise<Driver> {
    const { data } = await api.get<Driver>(`/drivers/${id}`);
    return data;
  },

  async create(payload: Partial<Driver>): Promise<Driver> {
    const { data } = await api.post<Driver>("/drivers", payload);
    return data;
  },

  async update(id: number, payload: Partial<Driver>): Promise<Driver> {
    const { data } = await api.put<Driver>(`/drivers/${id}`, payload);
    return data;
  },

  async updateLocation(id: number, latitude: number, longitude: number): Promise<Driver> {
    const { data } = await api.put<Driver>(`/drivers/${id}/location`, { latitude, longitude });
    return data;
  },
};
