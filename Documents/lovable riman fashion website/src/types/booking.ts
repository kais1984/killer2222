/**
 * Booking System Types
 * Type definitions for the rental and sales booking system
 */

export type BookingStatus = 'pending' | 'confirmed' | 'active' | 'completed' | 'cancelled' | 'returned_late';
export type OrderStatus = 'pending' | 'processing' | 'confirmed' | 'shipped' | 'delivered' | 'completed' | 'cancelled' | 'refunded';
export type ItemType = 'sale' | 'rent';
export type ShippingMethod = 'delivery' | 'pickup';
export type PaymentMethod = 'card' | 'cod';

export interface Inventory {
  id: string;
  product_id: string;
  total_stock: number;
  available_stock: number;
  is_available_for_rent: boolean;
  is_available_for_sale: boolean;
  cleaning_buffer_days: number;
  rental_period_days: number;
  created_at: string;
  updated_at: string;
}

export interface Booking {
  id: string;
  product_id: string;
  user_id: string | null;
  start_date: string; // ISO date string
  end_date: string; // ISO date string
  status: BookingStatus;
  order_id: string | null;
  size: string | null;
  total_price: number | null;
  security_deposit: number | null;
  actual_return_date: string | null;
  late_fee: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface DateLock {
  id: string;
  product_id: string;
  user_id: string;
  start_date: string;
  end_date: string;
  expires_at: string;
  created_at: string;
}

export interface Order {
  id: string;
  user_id: string | null;
  status: OrderStatus;
  subtotal: number;
  security_deposit_total: number;
  late_fees: number;
  total: number;
  shipping_method: ShippingMethod;
  payment_method: PaymentMethod;
  shipping_address: string | null;
  phone: string | null;
  created_at: string;
  updated_at: string;
  confirmed_at: string | null;
  cancelled_at: string | null;
}

export interface OrderItem {
  id: string;
  order_id: string;
  product_id: string;
  product_name: string;
  item_type: ItemType;
  size: string | null;
  quantity: number;
  unit_price: number;
  rental_days: number | null;
  start_date: string | null;
  end_date: string | null;
  security_deposit: number;
  booking_id: string | null;
  created_at: string;
}

export interface BlockedDateRange {
  blocked_start: string;
  blocked_end: string;
  booking_status: BookingStatus;
}

export interface AvailabilityCheck {
  isAvailable: boolean;
  reason?: string;
  blockedRanges: BlockedDateRange[];
  nextAvailableDate?: string;
}

export interface BookingRequest {
  product_id: string;
  start_date: string;
  end_date: string;
  size: string;
  user_id: string;
}

export interface LockRequest {
  product_id: string;
  start_date: string;
  end_date: string;
  user_id: string;
  duration_minutes?: number;
}

export interface LockResult {
  success: boolean;
  lock_id?: string;
  expires_at?: string;
  reason?: string;
}
