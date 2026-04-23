/**
 * Booking Service Layer
 * Handles all booking logic, date validation, overlap detection, and concurrency management.
 * This service interacts with Supabase for all database operations.
 */

import { createClient } from '@supabase/supabase-js';
import type {
  Booking,
  DateLock,
  Inventory,
  BlockedDateRange,
  AvailabilityCheck,
  BookingRequest,
  LockRequest,
  LockResult,
  BookingStatus,
} from '@/types/booking';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

const supabase = supabaseUrl && supabaseAnonKey 
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null;

// =====================================================
// CONSTANTS
// =====================================================

const DEFAULT_LOCK_DURATION_MINUTES = 10;
const MAX_LOCK_DURATION_MINUTES = 30;
const CLEANING_BUFFER_DEFAULT = 1;
const RENTAL_PERIOD_DEFAULT = 15;

// =====================================================
// INVENTORY OPERATIONS
// =====================================================

/**
 * Get inventory for a specific product
 */
if (!supabase) {
  throw new Error('Supabase is not configured. Please add VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY to your .env file.');
}

export async function getInventory(productId: string): Promise<Inventory | null> {
  const { data, error } = await supabase
    .from('inventory')
    .select('*')
    .eq('product_id', productId)
    .single();

  if (error) {
    if (error.code === 'PGRST116') return null; // Not found
    throw new Error(`Failed to fetch inventory: ${error.message}`);
  }

  return data as Inventory;
}

/**
 * Update inventory for a product (admin only)
 */
export async function updateInventory(
  productId: string,
  updates: Partial<Omit<Inventory, 'id' | 'product_id' | 'created_at' | 'updated_at'>>
): Promise<Inventory> {
  const { data, error } = await supabase
    .from('inventory')
    .update(updates)
    .eq('product_id', productId)
    .select()
    .single();

  if (error) throw new Error(`Failed to update inventory: ${error.message}`);
  return data as Inventory;
}

/**
 * Initialize inventory for a new product
 */
export async function createInventory(productId: string): Promise<Inventory> {
  const { data, error } = await supabase
    .from('inventory')
    .insert({
      product_id: productId,
      total_stock: 1,
      available_stock: 1,
      is_available_for_rent: true,
      is_available_for_sale: true,
      cleaning_buffer_days: CLEANING_BUFFER_DEFAULT,
      rental_period_days: RENTAL_PERIOD_DEFAULT,
    })
    .select()
    .single();

  if (error) throw new Error(`Failed to create inventory: ${error.message}`);
  return data as Inventory;
}

// =====================================================
// AVAILABILITY CHECKING
// =====================================================

/**
 * Check if dates are available for a product
 * Returns detailed availability info including blocked ranges
 */
export async function checkAvailability(
  productId: string,
  startDate: string,
  endDate: string,
  excludeBookingId?: string
): Promise<AvailabilityCheck> {
  // Get blocked date ranges
  const { data: blockedRanges, error } = await supabase
    .rpc('get_blocked_dates', {
      p_product_id: productId,
      p_months_ahead: 12,
    });

  if (error) throw new Error(`Failed to get blocked dates: ${error.message}`);

  const ranges = (blockedRanges || []) as BlockedDateRange[];

  // Check for overlap with active bookings
  const { data: overlaps } = await supabase
    .rpc('check_date_overlap', {
      p_product_id: productId,
      p_start_date: startDate,
      p_end_date: endDate,
      p_exclude_booking_id: excludeBookingId || null,
    });

  const hasBookingOverlap = overlaps === true;

  // Check for overlap with temporary locks
  const { data: lockOverlaps } = await supabase
    .rpc('check_lock_overlap', {
      p_product_id: productId,
      p_start_date: startDate,
      p_end_date: endDate,
      p_exclude_user_id: null,
    });

  const hasLockOverlap = lockOverlaps === true;

  // Get inventory to check stock
  const inventory = await getInventory(productId);

  if (!inventory) {
    return {
      isAvailable: false,
      reason: 'Product inventory not found',
      blockedRanges: ranges,
    };
  }

  if (!inventory.is_available_for_rent && !inventory.is_available_for_sale) {
    return {
      isAvailable: false,
      reason: 'Product is not available for rent or sale',
      blockedRanges: ranges,
    };
  }

  if (inventory.available_stock <= 0) {
    return {
      isAvailable: false,
      reason: 'All units are currently booked',
      blockedRanges: ranges,
    };
  }

  if (hasBookingOverlap) {
    return {
      isAvailable: false,
      reason: 'Selected dates overlap with an existing booking',
      blockedRanges: ranges,
    };
  }

  if (hasLockOverlap) {
    return {
      isAvailable: false,
      reason: 'Selected dates are temporarily held by another user',
      blockedRanges: ranges,
    };
  }

  // Calculate next available date if not available
  let nextAvailableDate: string | undefined;
  if (!hasBookingOverlap && !hasLockOverlap) {
    nextAvailableDate = startDate;
  } else {
    // Find the next available date after all blocked ranges
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const sortedRanges = [...ranges].sort((a, b) =>
      new Date(a.blocked_end).getTime() - new Date(b.blocked_end).getTime()
    );

    for (const range of sortedRanges) {
      const endDate = new Date(range.blocked_end);
      if (endDate >= today) {
        const nextDate = new Date(endDate);
        nextDate.setDate(nextDate.getDate() + (inventory.cleaning_buffer_days || 1) + 1);
        nextAvailableDate = nextDate.toISOString().split('T')[0];
        break;
      }
    }
  }

  return {
    isAvailable: true,
    blockedRanges: ranges,
    nextAvailableDate,
  };
}

/**
 * Get all blocked dates for a product (for calendar display)
 */
export async function getBlockedDates(productId: string, monthsAhead = 6): Promise<BlockedDateRange[]> {
  const { data, error } = await supabase
    .rpc('get_blocked_dates', {
      p_product_id: productId,
      p_months_ahead: monthsAhead,
    });

  if (error) throw new Error(`Failed to get blocked dates: ${error.message}`);
  return (data || []) as BlockedDateRange[];
}

// =====================================================
// DATE LOCKING (Concurrency Prevention)
// =====================================================

/**
 * Create a temporary date lock during checkout
 * Prevents other users from booking the same dates
 * Locks auto-expire after duration (default 10 minutes)
 */
export async function createDateLock(request: LockRequest): Promise<LockResult> {
  const durationMinutes = Math.min(
    request.duration_minutes || DEFAULT_LOCK_DURATION_MINUTES,
    MAX_LOCK_DURATION_MINUTES
  );

  // Check for existing locks first
  const { data: hasOverlap } = await supabase
    .rpc('check_lock_overlap', {
      p_product_id: request.product_id,
      p_start_date: request.start_date,
      p_end_date: request.end_date,
      p_exclude_user_id: request.user_id,
    });

  if (hasOverlap === true) {
    return {
      success: false,
      reason: 'These dates are temporarily held by another user. Please try again in a few minutes.',
    };
  }

  // Check for existing bookings
  const { data: hasBookingOverlap } = await supabase
    .rpc('check_date_overlap', {
      p_product_id: request.product_id,
      p_start_date: request.start_date,
      p_end_date: request.end_date,
    });

  if (hasBookingOverlap === true) {
    return {
      success: false,
      reason: 'These dates are already booked.',
    };
  }

  // Create the lock
  const expiresAt = new Date(Date.now() + durationMinutes * 60 * 1000).toISOString();

  const { data, error } = await supabase
    .from('date_locks')
    .insert({
      product_id: request.product_id,
      user_id: request.user_id,
      start_date: request.start_date,
      end_date: request.end_date,
      expires_at: expiresAt,
    })
    .select()
    .single();

  if (error) {
    // Check if it's a unique constraint violation (race condition)
    if (error.code === '23505') {
      return {
        success: false,
        reason: 'Another user just booked these dates. Please select different dates.',
      };
    }
    throw new Error(`Failed to create date lock: ${error.message}`);
  }

  const lock = data as DateLock;

  return {
    success: true,
    lock_id: lock.id,
    expires_at: lock.expires_at,
  };
}

/**
 * Release a date lock (when checkout completes or is cancelled)
 */
export async function releaseDateLock(lockId: string, userId: string): Promise<void> {
  const { error } = await supabase
    .from('date_locks')
    .delete()
    .eq('id', lockId)
    .eq('user_id', userId);

  if (error) throw new Error(`Failed to release date lock: ${error.message}`);
}

/**
 * Release all locks for a user
 */
export async function releaseAllUserLocks(userId: string): Promise<void> {
  const { error } = await supabase
    .from('date_locks')
    .delete()
    .eq('user_id', userId);

  if (error) throw new Error(`Failed to release user locks: ${error.message}`);
}

/**
 * Clean up expired locks (should be called periodically)
 */
export async function cleanupExpiredLocks(): Promise<number> {
  const { data, error } = await supabase
    .rpc('cleanup_expired_locks');

  if (error) throw new Error(`Failed to cleanup locks: ${error.message}`);
  return data as number;
}

// =====================================================
// BOOKING OPERATIONS
// =====================================================

/**
 * Create a new booking
 * This should be called after successful payment
 */
export async function createBooking(
  request: BookingRequest,
  orderId: string,
  totalPrice: number,
  securityDeposit: number
): Promise<Booking> {
  // Verify availability one more time (double-check for race conditions)
  const availability = await checkAvailability(
    request.product_id,
    request.start_date,
    request.end_date
  );

  if (!availability.isAvailable) {
    throw new Error(`Cannot create booking: ${availability.reason}`);
  }

  const { data, error } = await supabase
    .from('bookings')
    .insert({
      product_id: request.product_id,
      user_id: request.user_id,
      start_date: request.start_date,
      end_date: request.end_date,
      status: 'confirmed',
      order_id: orderId,
      size: request.size,
      total_price: totalPrice,
      security_deposit: securityDeposit,
    })
    .select()
    .single();

  if (error) throw new Error(`Failed to create booking: ${error.message}`);

  // Update inventory available stock
  await updateInventory(request.product_id, {
    available_stock: supabase.rpc('decrement', { column: 'available_stock' }) as any,
  });

  // Actually, let's do a direct update since we can't use rpc for this
  const inventory = await getInventory(request.product_id);
  if (inventory) {
    await supabase
      .from('inventory')
      .update({ available_stock: inventory.available_stock - 1 })
      .eq('product_id', request.product_id);
  }

  return data as Booking;
}

/**
 * Update booking status
 */
export async function updateBookingStatus(
  bookingId: string,
  status: BookingStatus,
  updates?: { actual_return_date?: string; late_fee?: number; notes?: string }
): Promise<Booking> {
  const updateData: any = { status, ...updates };

  const { data, error } = await supabase
    .from('bookings')
    .update(updateData)
    .eq('id', bookingId)
    .select()
    .single();

  if (error) throw new Error(`Failed to update booking: ${error.message}`);

  // If booking is completed or cancelled, restore inventory
  if (status === 'completed' || status === 'cancelled') {
    const booking = data as Booking;
    const inventory = await getInventory(booking.product_id);
    if (inventory) {
      await supabase
        .from('inventory')
        .update({ available_stock: inventory.available_stock + 1 })
        .eq('product_id', booking.product_id);
    }
  }

  return data as Booking;
}

/**
 * Get bookings for a product
 */
export async function getProductBookings(
  productId: string,
  status?: BookingStatus[]
): Promise<Booking[]> {
  let query = supabase
    .from('bookings')
    .select('*')
    .eq('product_id', productId)
    .order('start_date', { ascending: true });

  if (status && status.length > 0) {
    query = query.in('status', status);
  }

  const { data, error } = await query;
  if (error) throw new Error(`Failed to get bookings: ${error.message}`);
  return data as Booking[];
}

/**
 * Get bookings for a user
 */
export async function getUserBookings(userId: string): Promise<Booking[]> {
  const { data, error } = await supabase
    .from('bookings')
    .select('*')
    .eq('user_id', userId)
    .order('created_at', { ascending: false });

  if (error) throw new Error(`Failed to get user bookings: ${error.message}`);
  return data as Booking[];
}

/**
 * Calculate late fee for a returned-late booking
 */
export function calculateLateFee(
  expectedReturnDate: string,
  actualReturnDate: string,
  dailyRentalRate: number
): number {
  const expected = new Date(expectedReturnDate);
  const actual = new Date(actualReturnDate);
  const daysLate = Math.ceil((actual.getTime() - expected.getTime()) / (1000 * 60 * 60 * 24));

  if (daysLate <= 0) return 0;

  // Late fee: 1.5x daily rate for each late day
  return daysLate * dailyRentalRate * 1.5;
}

// =====================================================
// RENTAL PRICE CALCULATION
// =====================================================

/**
 * Calculate rental price based on dates
 */
export function calculateRentalPrice(
  dailyRate: number,
  startDate: string,
  endDate: string,
  securityDeposit: number = 0
): { rentalDays: number; rentalCost: number; securityDeposit: number; total: number } {
  const start = new Date(startDate);
  const end = new Date(endDate);
  const rentalDays = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));

  if (rentalDays <= 0) {
    throw new Error('End date must be after start date');
  }

  const rentalCost = dailyRate * rentalDays;
  const total = rentalCost + securityDeposit;

  return {
    rentalDays,
    rentalCost,
    securityDeposit,
    total,
  };
}
