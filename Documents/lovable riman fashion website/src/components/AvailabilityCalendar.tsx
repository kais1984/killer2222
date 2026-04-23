import { useMemo } from 'react';
import { Calendar } from '@/components/ui/calendar';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import type { BlockedDateRange } from '@/types/booking';
import { cn } from '@/lib/utils';

interface AvailabilityCalendarProps {
  blockedDates: BlockedDateRange[];
  selected?: { from?: Date; to?: Date };
  onSelect?: (range: { from?: Date; to?: Date } | undefined) => void;
  disabled?: boolean;
  monthsAhead?: number;
  className?: string;
}

/**
 * AvailabilityCalendar Component
 * 
 * Extends the base Calendar component with visual indicators for blocked dates.
 * Shows booked date ranges with distinct styling and tooltips.
 * 
 * Features:
 * - Visual blocking of unavailable dates
 * - Tooltips showing booking status on hover
 * - Support for date range selection
 * - Disabled state when product is unavailable
 */
export function AvailabilityCalendar({
  blockedDates,
  selected,
  onSelect,
  disabled = false,
  monthsAhead = 6,
  className,
}: AvailabilityCalendarProps) {
  // Create a map of blocked dates for quick lookup
  const blockedDateMap = useMemo(() => {
    const map = new Map<string, { status: string; bookingId?: string }>();

    for (const range of blockedDates) {
      const start = new Date(range.blocked_start);
      const end = new Date(range.blocked_end);
      const current = new Date(start);

      while (current <= end) {
        const dateStr = current.toISOString().split('T')[0];
        map.set(dateStr, {
          status: range.booking_status,
        });
        current.setDate(current.getDate() + 1);
      }
    }

    return map;
  }, [blockedDates]);

  // Custom modifier function for react-day-picker
  const modifiers = useMemo(() => {
    const blocked: Date[] = [];
    const pending: Date[] = [];
    const confirmed: Date[] = [];
    const active: Date[] = [];

    for (const [dateStr, info] of blockedDateMap.entries()) {
      const date = new Date(dateStr + 'T00:00:00');
      blocked.push(date);

      if (info.status === 'pending') pending.push(date);
      else if (info.status === 'confirmed') confirmed.push(date);
      else if (info.status === 'active') active.push(date);
    }

    return {
      blocked,
      pending,
      confirmed,
      active,
    };
  }, [blockedDateMap]);

  // Modifier styles
  const modifiersStyles = useMemo(() => ({
    blocked: {
      backgroundColor: 'rgba(239, 68, 68, 0.15)',
      color: 'rgba(239, 68, 68, 0.7)',
      textDecoration: 'line-through',
      cursor: 'not-allowed',
      borderRadius: '4px',
    },
    pending: {
      backgroundColor: 'rgba(245, 158, 11, 0.2)',
      color: 'rgba(245, 158, 11, 0.9)',
      borderRadius: '4px',
    },
    confirmed: {
      backgroundColor: 'rgba(239, 68, 68, 0.2)',
      color: 'rgba(239, 68, 68, 0.9)',
      borderRadius: '4px',
    },
    active: {
      backgroundColor: 'rgba(168, 85, 247, 0.2)',
      color: 'rgba(168, 85, 247, 0.9)',
      borderRadius: '4px',
    },
    selected: {
      backgroundColor: 'rgba(197, 165, 114, 0.3)',
      color: 'inherit',
      borderRadius: '4px',
    },
  }), []);

  // Disable function for blocked dates
  const isDateDisabled = (date: Date) => {
    if (disabled) return true;

    const dateStr = date.toISOString().split('T')[0];
    if (blockedDateMap.has(dateStr)) return true;

    // Disable past dates
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if (date < today) return true;

    return false;
  };

  // Get tooltip content for a date
  const getDateTooltip = (date: Date) => {
    const dateStr = date.toISOString().split('T')[0];
    const info = blockedDateMap.get(dateStr);

    if (!info) return null;

    const statusLabels: Record<string, string> = {
      pending: 'Pending booking',
      confirmed: 'Confirmed booking',
      active: 'Currently rented',
      completed: 'Completed',
      cancelled: 'Cancelled',
    };

    return statusLabels[info.status] || info.status;
  };

  return (
    <div className={cn('space-y-4', className)}>
      {/* Legend */}
      <div className="flex flex-wrap gap-4 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-red-500/20 border border-red-500/30" />
          <span className="text-muted-foreground">Booked</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-amber-500/20 border border-amber-500/30" />
          <span className="text-muted-foreground">Pending</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-purple-500/20 border border-purple-500/30" />
          <span className="text-muted-foreground">Active Rental</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-gold/30 border border-gold/50" />
          <span className="text-muted-foreground">Selected</span>
        </div>
      </div>

      {/* Calendar */}
      <TooltipProvider>
        <Calendar
          mode="range"
          selected={selected}
          onSelect={onSelect}
          disabled={isDateDisabled}
          numberOfMonths={1}
          modifiers={modifiers}
          modifiersStyles={modifiersStyles}
          className="mx-auto"
          components={{
            DayContent: ({ date, ...props }) => {
              const tooltip = getDateTooltip(date);
              const isBlocked = blockedDateMap.has(date.toISOString().split('T')[0]);

              const dayButton = (
                <div
                  {...props}
                  className={cn(
                    'rdp-day h-9 w-9 p-0 font-normal',
                    isBlocked && 'cursor-not-allowed'
                  )}
                >
                  {date.getDate()}
                </div>
              );

              if (tooltip) {
                return (
                  <Tooltip>
                    <TooltipTrigger asChild>{dayButton}</TooltipTrigger>
                    <TooltipContent>
                      <p className="text-xs">{tooltip}</p>
                    </TooltipContent>
                  </Tooltip>
                );
              }

              return dayButton;
            },
          }}
        />
      </TooltipProvider>

      {/* Status message */}
      {disabled && (
        <div className="text-center p-3 bg-muted/50 rounded-lg">
          <p className="text-sm text-muted-foreground">
            This product is currently unavailable for booking.
          </p>
        </div>
      )}
    </div>
  );
}

/**
 * AvailabilityStatus Badge
 * Shows current availability status for a product
 */
export function AvailabilityStatus({
  inventory,
  className,
}: {
  inventory: {
    is_available_for_rent: boolean;
    is_available_for_sale: boolean;
    available_stock: number;
  } | null;
  className?: string;
}) {
  if (!inventory) return null;

  if (!inventory.is_available_for_rent && !inventory.is_available_for_sale) {
    return (
      <Badge variant="destructive" className={className}>
        Not Available
      </Badge>
    );
  }

  if (inventory.available_stock <= 0) {
    return (
      <Badge variant="outline" className={cn('text-amber-600 border-amber-600', className)}>
        Rented Until [date]
      </Badge>
    );
  }

  if (inventory.is_available_for_rent) {
    return (
      <Badge variant="outline" className={cn('text-green-600 border-green-600', className)}>
        Available for Rent
      </Badge>
    );
  }

  return (
    <Badge variant="outline" className={cn('text-blue-600 border-blue-600', className)}>
      Available for Sale Only
    </Badge>
  );
}
