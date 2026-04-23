import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Package, Calendar, DollarSign, AlertTriangle, CheckCircle, XCircle, Edit2, Save, X } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import * as bookingService from "@/services/bookingService";
import type { Inventory, Booking, BookingStatus } from "@/types/booking";
import { products } from "@/data/products";

/**
 * AdminInventoryManagement Component
 * 
 * Allows admins to:
 * - View inventory levels for all products
 * - Toggle availability for rent/sale
 * - Adjust stock levels
 * - View and manage bookings
 * - Override availability manually
 */
export default function AdminInventoryManagement() {
  const { toast } = useToast();
  const [inventories, setInventories] = useState<Inventory[]>([]);
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<Partial<Inventory>>({});
  const [activeTab, setActiveTab] = useState<"inventory" | "bookings">("inventory");
  const [bookingFilter, setBookingFilter] = useState<BookingStatus | "all">("all");

  // Load all inventory data
  useEffect(() => {
    loadAllInventory();
    loadAllBookings();
  }, []);

  const loadAllInventory = async () => {
    setIsLoading(true);
    try {
      const inventoryPromises = products.map(p => bookingService.getInventory(p.id));
      const results = await Promise.all(inventoryPromises);
      setInventories(results.filter((inv): inv is Inventory => inv !== null));
    } catch (err) {
      toast({ title: "Failed to load inventory", variant: "destructive" });
    } finally {
      setIsLoading(false);
    }
  };

  const loadAllBookings = async () => {
    try {
      const allBookings: Booking[] = [];
      for (const product of products) {
        const productBookings = await bookingService.getProductBookings(product.id);
        allBookings.push(...productBookings);
      }
      setBookings(allBookings.sort((a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      ));
    } catch (err) {
      console.error("Failed to load bookings:", err);
    }
  };

  const startEdit = (inventory: Inventory) => {
    setEditingId(inventory.product_id);
    setEditForm({
      is_available_for_rent: inventory.is_available_for_rent,
      is_available_for_sale: inventory.is_available_for_sale,
      total_stock: inventory.total_stock,
      available_stock: inventory.available_stock,
      cleaning_buffer_days: inventory.cleaning_buffer_days,
      rental_period_days: inventory.rental_period_days,
    });
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditForm({});
  };

  const saveEdit = async () => {
    if (!editingId) return;

    try {
      await bookingService.updateInventory(editingId, editForm);
      toast({ title: "Inventory updated successfully" });
      setEditingId(null);
      setEditForm({});
      await loadAllInventory();
    } catch (err) {
      toast({ title: "Failed to update inventory", variant: "destructive" });
    }
  };

  const updateBookingStatus = async (bookingId: string, status: BookingStatus) => {
    try {
      await bookingService.updateBookingStatus(bookingId, status);
      toast({ title: `Booking ${status}` });
      await loadAllBookings();
      await loadAllInventory();
    } catch (err) {
      toast({ title: "Failed to update booking", variant: "destructive" });
    }
  };

  const filteredBookings = bookingFilter === "all"
    ? bookings
    : bookings.filter(b => b.status === bookingFilter);

  const getProductInfo = (productId: string) => {
    return products.find(p => p.id === productId);
  };

  const statusColors: Record<string, string> = {
    pending: "bg-amber-100 text-amber-800",
    confirmed: "bg-blue-100 text-blue-800",
    active: "bg-purple-100 text-purple-800",
    completed: "bg-green-100 text-green-800",
    cancelled: "bg-red-100 text-red-800",
    returned_late: "bg-orange-100 text-orange-800",
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gold" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Tabs */}
      <div className="flex gap-4 border-b">
        <button
          onClick={() => setActiveTab("inventory")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === "inventory"
              ? "border-gold text-gold"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <Package size={16} className="inline mr-2" />
          Inventory ({inventories.length})
        </button>
        <button
          onClick={() => setActiveTab("bookings")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === "bookings"
              ? "border-gold text-gold"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <Calendar size={16} className="inline mr-2" />
          Bookings ({bookings.length})
        </button>
      </div>

      {/* Inventory Tab */}
      {activeTab === "inventory" && (
        <div className="space-y-4">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-4 bg-white border rounded-lg">
              <div className="flex items-center gap-2 text-muted-foreground text-sm">
                <Package size={16} />
                <span>Total Products</span>
              </div>
              <p className="text-2xl font-heading mt-1">{inventories.length}</p>
            </div>
            <div className="p-4 bg-white border rounded-lg">
              <div className="flex items-center gap-2 text-green-600 text-sm">
                <CheckCircle size={16} />
                <span>Available</span>
              </div>
              <p className="text-2xl font-heading mt-1">
                {inventories.filter(i => i.available_stock > 0).length}
              </p>
            </div>
            <div className="p-4 bg-white border rounded-lg">
              <div className="flex items-center gap-2 text-amber-600 text-sm">
                <AlertTriangle size={16} />
                <span>Out of Stock</span>
              </div>
              <p className="text-2xl font-heading mt-1">
                {inventories.filter(i => i.available_stock <= 0).length}
              </p>
            </div>
            <div className="p-4 bg-white border rounded-lg">
              <div className="flex items-center gap-2 text-red-600 text-sm">
                <XCircle size={16} />
                <span>Unavailable</span>
              </div>
              <p className="text-2xl font-heading mt-1">
                {inventories.filter(i => !i.is_available_for_rent && !i.is_available_for_sale).length}
              </p>
            </div>
          </div>

          {/* Inventory Table */}
          <div className="bg-white border rounded-lg overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left p-3 font-body text-xs uppercase tracking-wider">Product</th>
                  <th className="text-center p-3 font-body text-xs uppercase tracking-wider">Stock</th>
                  <th className="text-center p-3 font-body text-xs uppercase tracking-wider">For Rent</th>
                  <th className="text-center p-3 font-body text-xs uppercase tracking-wider">For Sale</th>
                  <th className="text-center p-3 font-body text-xs uppercase tracking-wider">Rental Period</th>
                  <th className="text-center p-3 font-body text-xs uppercase tracking-wider">Cleaning Buffer</th>
                  <th className="text-center p-3 font-body text-xs uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody>
                {inventories.map((inv) => {
                  const product = getProductInfo(inv.product_id);
                  const isEditing = editingId === inv.product_id;

                  return (
                    <tr key={inv.product_id} className="border-t hover:bg-muted/20">
                      <td className="p-3">
                        <p className="font-heading">{product?.name || "Unknown"}</p>
                        <p className="text-xs text-muted-foreground">{product?.category}</p>
                      </td>
                      <td className="p-3 text-center">
                        {isEditing ? (
                          <input
                            type="number"
                            value={editForm.available_stock ?? inv.available_stock}
                            onChange={(e) => setEditForm({ ...editForm, available_stock: parseInt(e.target.value) })}
                            className="w-16 text-center border rounded p-1"
                            min={0}
                          />
                        ) : (
                          <span className={inv.available_stock > 0 ? "text-green-600" : "text-red-600"}>
                            {inv.available_stock}/{inv.total_stock}
                          </span>
                        )}
                      </td>
                      <td className="p-3 text-center">
                        {isEditing ? (
                          <input
                            type="checkbox"
                            checked={editForm.is_available_for_rent ?? inv.is_available_for_rent}
                            onChange={(e) => setEditForm({ ...editForm, is_available_for_rent: e.target.checked })}
                            className="w-4 h-4"
                          />
                        ) : (
                          inv.is_available_for_rent ? (
                            <CheckCircle size={16} className="text-green-500 mx-auto" />
                          ) : (
                            <XCircle size={16} className="text-red-500 mx-auto" />
                          )
                        )}
                      </td>
                      <td className="p-3 text-center">
                        {isEditing ? (
                          <input
                            type="checkbox"
                            checked={editForm.is_available_for_sale ?? inv.is_available_for_sale}
                            onChange={(e) => setEditForm({ ...editForm, is_available_for_sale: e.target.checked })}
                            className="w-4 h-4"
                          />
                        ) : (
                          inv.is_available_for_sale ? (
                            <CheckCircle size={16} className="text-green-500 mx-auto" />
                          ) : (
                            <XCircle size={16} className="text-red-500 mx-auto" />
                          )
                        )}
                      </td>
                      <td className="p-3 text-center">
                        {isEditing ? (
                          <input
                            type="number"
                            value={editForm.rental_period_days ?? inv.rental_period_days}
                            onChange={(e) => setEditForm({ ...editForm, rental_period_days: parseInt(e.target.value) })}
                            className="w-16 text-center border rounded p-1"
                            min={1}
                          />
                        ) : (
                          `${inv.rental_period_days} days`
                        )}
                      </td>
                      <td className="p-3 text-center">
                        {isEditing ? (
                          <input
                            type="number"
                            value={editForm.cleaning_buffer_days ?? inv.cleaning_buffer_days}
                            onChange={(e) => setEditForm({ ...editForm, cleaning_buffer_days: parseInt(e.target.value) })}
                            className="w-16 text-center border rounded p-1"
                            min={0}
                          />
                        ) : (
                          `${inv.cleaning_buffer_days} day(s)`
                        )}
                      </td>
                      <td className="p-3 text-center">
                        {isEditing ? (
                          <div className="flex gap-2 justify-center">
                            <button onClick={saveEdit} className="p-1 text-green-600 hover:bg-green-50 rounded">
                              <Save size={16} />
                            </button>
                            <button onClick={cancelEdit} className="p-1 text-red-600 hover:bg-red-50 rounded">
                              <X size={16} />
                            </button>
                          </div>
                        ) : (
                          <button onClick={() => startEdit(inv)} className="p-1 text-gold hover:bg-gold/10 rounded">
                            <Edit2 size={16} />
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Bookings Tab */}
      {activeTab === "bookings" && (
        <div className="space-y-4">
          {/* Filter */}
          <div className="flex gap-2">
            {(["all", "pending", "confirmed", "active", "completed", "cancelled"] as const).map((status) => (
              <button
                key={status}
                onClick={() => setBookingFilter(status)}
                className={`px-3 py-1 text-xs rounded-full border transition-colors ${
                  bookingFilter === status
                    ? "bg-gold text-white border-gold"
                    : "border-border text-muted-foreground hover:border-gold"
                }`}
              >
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </button>
            ))}
          </div>

          {/* Bookings List */}
          {filteredBookings.length === 0 ? (
            <div className="text-center p-12 text-muted-foreground">
              <Calendar size={48} className="mx-auto mb-4 opacity-50" />
              <p>No bookings found</p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredBookings.map((booking) => {
                const product = getProductInfo(booking.product_id);
                return (
                  <div key={booking.id} className="p-4 bg-white border rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-heading">{product?.name || "Unknown Product"}</p>
                        <p className="text-xs text-muted-foreground">
                          {booking.start_date} → {booking.end_date}
                          {booking.size && ` • Size: ${booking.size}`}
                        </p>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className={`px-2 py-1 text-xs rounded-full ${statusColors[booking.status] || "bg-gray-100 text-gray-800"}`}>
                          {booking.status}
                        </span>
                        {booking.status === "pending" && (
                          <div className="flex gap-1">
                            <button
                              onClick={() => updateBookingStatus(booking.id, "confirmed")}
                              className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200"
                            >
                              Confirm
                            </button>
                            <button
                              onClick={() => updateBookingStatus(booking.id, "cancelled")}
                              className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200"
                            >
                              Cancel
                            </button>
                          </div>
                        )}
                        {booking.status === "confirmed" && (
                          <button
                            onClick={() => updateBookingStatus(booking.id, "active")}
                            className="px-2 py-1 text-xs bg-purple-100 text-purple-700 rounded hover:bg-purple-200"
                          >
                            Mark Active
                          </button>
                        )}
                        {booking.status === "active" && (
                          <button
                            onClick={() => updateBookingStatus(booking.id, "completed")}
                            className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200"
                          >
                            Complete
                          </button>
                        )}
                      </div>
                    </div>
                    {booking.total_price && (
                      <div className="mt-2 flex gap-4 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <DollarSign size={12} />
                          AED {booking.total_price.toLocaleString()}
                        </span>
                        {booking.security_deposit && (
                          <span>Deposit: AED {booking.security_deposit.toLocaleString()}</span>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
