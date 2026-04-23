import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import type { AvailabilityCheck, BlockedDateRange, Inventory } from '@/types/booking';
import * as bookingService from '@/services/bookingService';

interface AvailabilityContextType {
  // Availability state
  availability: AvailabilityCheck | null;
  isLoading: boolean;
  error: string | null;

  // Inventory state
  inventory: Inventory | null;

  // Blocked dates for calendar
  blockedDates: BlockedDateRange[];

  // Actions
  checkAvailability: (productId: string, startDate: string, endDate: string) => Promise<void>;
  loadInventory: (productId: string) => Promise<void>;
  loadBlockedDates: (productId: string, monthsAhead?: number) => Promise<void>;
  refreshAll: (productId: string) => Promise<void>;
  clearAvailability: () => void;
}

const AvailabilityContext = createContext<AvailabilityContextType | undefined>(undefined);

export function AvailabilityProvider({ children }: { children: ReactNode }) {
  const [availability, setAvailability] = useState<AvailabilityCheck | null>(null);
  const [inventory, setInventory] = useState<Inventory | null>(null);
  const [blockedDates, setBlockedDates] = useState<BlockedDateRange[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkAvailability = useCallback(async (productId: string, startDate: string, endDate: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await bookingService.checkAvailability(productId, startDate, endDate);
      setAvailability(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to check availability';
      setError(message);
      setAvailability({
        isAvailable: false,
        reason: message,
        blockedDates: [],
      });
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadInventory = useCallback(async (productId: string) => {
    try {
      const inv = await bookingService.getInventory(productId);
      setInventory(inv);
    } catch (err) {
      console.error('Failed to load inventory:', err);
    }
  }, []);

  const loadBlockedDates = useCallback(async (productId: string, monthsAhead = 6) => {
    try {
      const dates = await bookingService.getBlockedDates(productId, monthsAhead);
      setBlockedDates(dates);
    } catch (err) {
      console.error('Failed to load blocked dates:', err);
    }
  }, []);

  const refreshAll = useCallback(async (productId: string) => {
    setIsLoading(true);
    try {
      await Promise.all([
        loadInventory(productId),
        loadBlockedDates(productId),
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [loadInventory, loadBlockedDates]);

  const clearAvailability = useCallback(() => {
    setAvailability(null);
    setError(null);
  }, []);

  return (
    <AvailabilityContext.Provider
      value={{
        availability,
        isLoading,
        error,
        inventory,
        blockedDates,
        checkAvailability,
        loadInventory,
        loadBlockedDates,
        refreshAll,
        clearAvailability,
      }}
    >
      {children}
    </AvailabilityContext.Provider>
  );
}

export function useAvailability() {
  const context = useContext(AvailabilityContext);
  if (!context) {
    throw new Error('useAvailability must be used within an AvailabilityProvider');
  }
  return context;
}
