import React, { createContext, useContext, useState, useEffect } from "react";
import { Product } from "@/data/products";
import { DateRange } from "react-day-picker";
import { checkAvailability } from "@/services/bookingService";

export type CartItemType = "sale" | "rent";

export interface CartItem {
  id: string;
  product: Product;
  type: CartItemType;
  size: string;

  // Sale specific
  quantity?: number;

  // Rent specific
  dateRange?: DateRange;
  rentalDays?: number;
}

interface CartContextType {
  items: CartItem[];
  addItem: (item: Omit<CartItem, "id">) => void;
  removeItem: (id: string) => void;
  updateQuantity: (id: string, quantity: number) => void;
  clearCart: () => void;
  totalItems: number;
  subtotal: number;
  securityDepositTotal: number;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export const CartProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [items, setItems] = useState<CartItem[]>(() => {
    try {
      const saved = localStorage.getItem("riman_cart");
      if (saved) {
        // Parse dates back to Date objects for dateRange
        const parsed = JSON.parse(saved);
        return parsed.map((item: CartItem) => {
          if (item.type === 'rent' && item.dateRange) {
            const fromDate = item.dateRange.from ? new Date(item.dateRange.from) : undefined;
            const toDate = item.dateRange.to ? new Date(item.dateRange.to) : undefined;
            if (fromDate && isNaN(fromDate.getTime())) {
              return { ...item, dateRange: { from: undefined, to: undefined } };
            }
            return {
              ...item,
              dateRange: {
                from: fromDate,
                to: toDate
              }
            };
          }
          return item;
        });
      }
    } catch (e) {
      console.error("Failed to parse cart", e);
    }
    return [];
  });

  useEffect(() => {
    localStorage.setItem("riman_cart", JSON.stringify(items));
  }, [items]);

  const addItem = (newItem: Omit<CartItem, "id">) => {
    setItems((prev) => {
      // For sales, if we already have the item in the same size, increase quantity
      if (newItem.type === "sale") {
        const existing = prev.find(
          (i) => i.type === "sale" && i.product.id === newItem.product.id && i.size === newItem.size
        );
        if (existing) {
          return prev.map((i) =>
            i.id === existing.id
              ? { ...i, quantity: (i.quantity || 1) + (newItem.quantity || 1) }
              : i
          );
        }
      }
      // Otherwise, or if it's a rental (where specific dates matter), add new item
      return [...prev, { ...newItem, id: crypto.randomUUID() }];
    });
  };

  const removeItem = (id: string) => {
    setItems((prev) => prev.filter((i) => i.id !== id));
  };

  const updateQuantity = (id: string, quantity: number) => {
    if (quantity <= 0) {
      removeItem(id);
      return;
    }
    setItems((prev) => prev.map((i) => (i.id === id ? { ...i, quantity } : i)));
  };

  const clearCart = () => setItems([]);

  const totalItems = items.reduce((acc, item) => acc + (item.type === "sale" ? (item.quantity || 1) : 1), 0);

  const subtotal = items.reduce((acc, item) => {
    if (item.type === "sale") {
      return acc + (item.product.salePrice || 0) * (item.quantity || 1);
    } else {
      return acc + (item.product.rentalPrice || 0) * (item.rentalDays || 1);
    }
  }, 0);

  const securityDepositTotal = items.reduce((acc, item) => {
    if (item.type === "rent") {
      return acc + (item.product.securityDeposit || 0);
    }
    return acc;
  }, 0);

  return (
    <CartContext.Provider
      value={{
        items,
        addItem,
        removeItem,
        updateQuantity,
        clearCart,
        totalItems,
        subtotal,
        securityDepositTotal,
      }}
    >
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error("useCart must be used within a CartProvider");
  }
  return context;
};

/**
 * Validate rental dates before adding to cart
 * Returns { valid: true } or { valid: false, reason: string }
 */
export async function validateRentalDates(
  productId: string,
  startDate: Date,
  endDate: Date
): Promise<{ valid: boolean; reason?: string }> {
  try {
    const result = await checkAvailability(
      productId,
      startDate.toISOString().split('T')[0],
      endDate.toISOString().split('T')[0]
    );

    if (!result.isAvailable) {
      return { valid: false, reason: result.reason };
    }

    return { valid: true };
  } catch (err) {
    return {
      valid: false,
      reason: err instanceof Error ? err.message : "Failed to validate dates",
    };
  }
}
