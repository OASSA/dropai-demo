import api from "./api";
import { Warehouse, PaginatedResponse } from "../types";

export const warehouseService = {
  async list(page = 1, size = 20): Promise<PaginatedResponse<Warehouse>> {
    const { data } = await api.get<PaginatedResponse<Warehouse>>("/warehouses", { params: { page, size } });
    return data;
  },

  async create(payload: Partial<Warehouse>): Promise<Warehouse> {
    const { data } = await api.post<Warehouse>("/warehouses", payload);
    return data;
  },

  async update(id: number, payload: Partial<Warehouse>): Promise<Warehouse> {
    const { data } = await api.put<Warehouse>(`/warehouses/${id}`, payload);
    return data;
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/warehouses/${id}`);
  },
};
