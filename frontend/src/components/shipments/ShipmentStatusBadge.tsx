import { ShipmentStatus } from "../../types";

const statusConfig: Record<ShipmentStatus, { label: string; className: string }> = {
  pending:           { label: "Pending",           className: "bg-gray-100 text-gray-700" },
  assigned:          { label: "Assigned",          className: "bg-blue-100 text-blue-700" },
  picked_up:         { label: "Picked Up",         className: "bg-indigo-100 text-indigo-700" },
  in_transit:        { label: "In Transit",        className: "bg-yellow-100 text-yellow-700" },
  out_for_delivery:  { label: "Out for Delivery",  className: "bg-orange-100 text-orange-700" },
  delivered:         { label: "Delivered",         className: "bg-green-100 text-green-700" },
  failed:            { label: "Failed",            className: "bg-red-100 text-red-700" },
  cancelled:         { label: "Cancelled",         className: "bg-gray-100 text-gray-500" },
  returned:          { label: "Returned",          className: "bg-purple-100 text-purple-700" },
};

export function ShipmentStatusBadge({ status }: { status: ShipmentStatus }) {
  const { label, className } = statusConfig[status] ?? { label: status, className: "bg-gray-100 text-gray-700" };
  return <span className={`badge ${className}`}>{label}</span>;
}
