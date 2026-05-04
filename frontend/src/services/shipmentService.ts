import api from "./api";
import { Shipment, PaginatedResponse } from "../types";

export const shipmentService = {
  async list(page = 1, size = 20, status?: string): Promise<PaginatedResponse<Shipment>> {
    const params: Record<string, unknown> = { page, size };
    if (status) params.status = status;
    const { data } = await api.get<PaginatedResponse<Shipment>>("/shipments", { params });
    return data;
  },

  async get(id: number): Promise<Shipment> {
    const { data } = await api.get<Shipment>(`/shipments/${id}`);
    return data;
  },

  async track(trackingNumber: string): Promise<Shipment> {
    const { data } = await api.get<Shipment>(`/shipments/track/${trackingNumber}`);
    return data;
  },

  async create(payload: Partial<Shipment>): Promise<Shipment> {
    const { data } = await api.post<Shipment>("/shipments", payload);
    return data;
  },

  async assign(id: number, driverId: number): Promise<Shipment> {
    const { data } = await api.put<Shipment>(`/shipments/${id}/assign`, { driver_id: driverId });
    return data;
  },

  async updateStatus(id: number, status: string, message?: string): Promise<Shipment> {
    const { data } = await api.put<Shipment>(`/shipments/${id}/status`, { status, message });
    return data;
  },
};
