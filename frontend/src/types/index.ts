export type UserRole = "super_admin" | "company_admin" | "warehouse_manager" | "driver" | "customer";

export interface Role {
  id: number;
  name: UserRole;
  description?: string;
}

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  avatar_url?: string;
  is_active: boolean;
  status: string;
  role: Role;
  company_id?: number;
  created_at: string;
  updated_at: string;
}

export type ShipmentStatus =
  | "pending" | "assigned" | "picked_up" | "in_transit"
  | "out_for_delivery" | "delivered" | "failed" | "cancelled" | "returned";

export type ShipmentPriority = "low" | "normal" | "high" | "urgent";

export interface TrackingLog {
  id: number;
  status: ShipmentStatus;
  message?: string;
  location_address?: string;
  latitude?: number;
  longitude?: number;
  created_at: string;
}

export interface Shipment {
  id: number;
  tracking_number: string;
  status: ShipmentStatus;
  priority: ShipmentPriority;
  company_id: number;
  origin_address: string;
  origin_city: string;
  destination_address: string;
  destination_city: string;
  recipient_name: string;
  recipient_phone: string;
  recipient_email?: string;
  weight_kg?: number;
  is_fragile: boolean;
  driver_id?: number;
  assigned_at?: string;
  scheduled_pickup?: string;
  actual_pickup?: string;
  scheduled_delivery?: string;
  actual_delivery?: string;
  predicted_eta?: string;
  predicted_distance_km?: number;
  failure_reason?: string;
  tracking_logs?: TrackingLog[];
  created_at: string;
  updated_at: string;
}

export type DriverStatus = "available" | "on_delivery" | "off_duty" | "suspended";
export type VehicleType = "motorcycle" | "car" | "van" | "truck";

export interface Driver {
  id: number;
  user_id: number;
  company_id: number;
  license_number: string;
  vehicle_type: VehicleType;
  vehicle_plate: string;
  vehicle_model?: string;
  status: DriverStatus;
  current_latitude?: number;
  current_longitude?: number;
  performance_score: number;
  total_deliveries: number;
  successful_deliveries: number;
  average_rating: number;
  success_rate: number;
  created_at: string;
  updated_at: string;
}

export interface Warehouse {
  id: number;
  company_id: number;
  name: string;
  code: string;
  address: string;
  city: string;
  country: string;
  latitude?: number;
  longitude?: number;
  manager_id?: number;
  phone?: string;
  email?: string;
  capacity?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Company {
  id: number;
  name: string;
  email: string;
  phone?: string;
  address?: string;
  city?: string;
  country?: string;
  logo_url?: string;
  is_active: boolean;
  subscription_plan: string;
  created_at: string;
  updated_at: string;
}

export interface ShipmentStats {
  total: number;
  pending: number;
  in_transit: number;
  delivered: number;
  failed: number;
  cancelled: number;
  delivery_success_rate: number;
}

export interface DriverStats {
  total_drivers: number;
  available: number;
  on_delivery: number;
  off_duty: number;
  top_performer_name?: string;
  top_performer_score?: number;
}

export interface DeliveryTrendPoint {
  date: string;
  delivered: number;
  failed: number;
  total: number;
}

export interface DashboardStats {
  shipments: ShipmentStats;
  drivers: DriverStats;
  companies?: {
    total_companies: number;
    active_companies: number;
    new_this_month: number;
  };
  delivery_trend: DeliveryTrendPoint[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
