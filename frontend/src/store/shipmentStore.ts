import { create } from "zustand";
import { Shipment, PaginatedResponse } from "../types";
import { shipmentService } from "../services/shipmentService";

interface ShipmentState {
  shipments: Shipment[];
  total: number;
  page: number;
  isLoading: boolean;
  selectedShipment: Shipment | null;
  fetchShipments: (page?: number, status?: string) => Promise<void>;
  selectShipment: (id: number) => Promise<void>;
  createShipment: (payload: Partial<Shipment>) => Promise<Shipment>;
  assignDriver: (id: number, driverId: number) => Promise<void>;
}

export const useShipmentStore = create<ShipmentState>((set, get) => ({
  shipments: [],
  total: 0,
  page: 1,
  isLoading: false,
  selectedShipment: null,

  fetchShipments: async (page = 1, status?: string) => {
    set({ isLoading: true });
    try {
      const data: PaginatedResponse<Shipment> = await shipmentService.list(page, 20, status);
      set({ shipments: data.items, total: data.total, page, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },

  selectShipment: async (id) => {
    const shipment = await shipmentService.get(id);
    set({ selectedShipment: shipment });
  },

  createShipment: async (payload) => {
    const newShipment = await shipmentService.create(payload);
    set((state) => ({ shipments: [newShipment, ...state.shipments], total: state.total + 1 }));
    return newShipment;
  },

  assignDriver: async (id, driverId) => {
    const updated = await shipmentService.assign(id, driverId);
    set((state) => ({
      shipments: state.shipments.map((s) => (s.id === id ? updated : s)),
      selectedShipment: state.selectedShipment?.id === id ? updated : state.selectedShipment,
    }));
  },
}));
