import { useState, useEffect } from "react";
import { Search, Eye, Filter, Download } from "lucide-react";

interface OrderItem {
  productId: string;
  name: string;
  type: string;
  price: number;
  image: string;
  size: string;
  rentalDates?: { from: string; to: string };
}

interface Order {
  id: string;
  userEmail: string;
  items: OrderItem[];
  total: number;
  shippingMethod: string;
  paymentMethod: string;
  address: string;
  phone: string;
  status: string;
  createdAt: string;
}

export default function AdminOrders() {
  const [searchTerm, setSearchTerm] = useState("");
  const [orders, setOrders] = useState<Order[]>([]);

  useEffect(() => {
    // Load all orders from localStorage (admin sees all)
    const allOrders: Order[] = JSON.parse(localStorage.getItem('riman_orders') || '[]');
    setOrders(allOrders);
  }, []);

  const filteredOrders = orders.filter(order =>
    order.userEmail.toLowerCase().includes(searchTerm.toLowerCase()) ||
    order.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    order.items.some(item => item.name.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const formatPrice = (price: number) => `AED ${price.toLocaleString()}`;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getRentalDates = (item: OrderItem) => {
    if (item.rentalDates?.from && item.rentalDates?.to) {
      return `${item.rentalDates.from} - ${item.rentalDates.to}`;
    }
    return '';
  };

  const exportCSV = () => {
    const headers = ["Order ID", "Customer Email", "Type", "Items", "Total", "Status", "Date"];
    const rows = filteredOrders.map(o => [
      o.id,
      o.userEmail,
      o.items.map(i => i.type).join(', '),
      o.items.map(i => i.name).join('; '),
      formatPrice(o.total),
      o.status,
      formatDate(o.createdAt)
    ]);
    const csvContent = [headers, ...rows].map(row => row.map(cell => `"${cell}"`).join(",")).join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `riman-orders-${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-heading font-semibold text-gray-900">Orders & Bookings</h1>
          <p className="text-sm text-gray-500 mt-1">Manage all sales and dress rentals.</p>
        </div>
        <button onClick={exportCSV} className="flex items-center gap-2 px-4 py-2 bg-white border border-border rounded-md text-sm font-medium hover:bg-gray-50 transition-colors">
          <Download size={16} />
          Export CSV
        </button>
      </div>

      <div className="bg-white rounded-xl border border-border shadow-sm overflow-hidden">

        {/* Toolbar */}
        <div className="p-4 border-b border-border flex flex-col sm:flex-row gap-4 justify-between bg-gray-50/50">
          <div className="relative w-full sm:w-80">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              placeholder="Search by ID, customer or item..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-border rounded-md text-sm focus:outline-none focus:border-gold transition-colors"
            />
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-white border border-border rounded-md text-sm font-medium hover:bg-gray-50 transition-colors shrink-0">
            <Filter size={16} />
            Filter
          </button>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-gray-50 text-gray-500 font-medium border-b border-border uppercase tracking-wider text-[11px]">
              <tr>
                <th className="px-6 py-4">Order ID</th>
                <th className="px-6 py-4">Customer</th>
                <th className="px-6 py-4">Type</th>
                <th className="px-6 py-4">Item & Dates</th>
                <th className="px-6 py-4">Total</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filteredOrders.map((order) => (
                <tr key={order.id} className="hover:bg-gray-50/50 transition-colors">
                  <td className="px-6 py-4 font-medium text-gray-900">{order.id}</td>
                  <td className="px-6 py-4">{order.userEmail}</td>
                  <td className="px-6 py-4">
                    {order.items.map((item, idx) => (
                      <span key={idx} className={`px-2 py-1 rounded-sm text-xs mr-1 ${item.type === 'rent' ? 'bg-blush text-gray-800' : 'bg-gray-100 text-gray-800'}`}>
                        {item.type === 'rent' ? 'Rental' : 'Sale'}
                      </span>
                    ))}
                  </td>
                  <td className="px-6 py-4">
                    {order.items.map((item, idx) => (
                      <div key={idx} className="font-medium text-gray-900">
                        {item.name}
                        {item.type === 'rent' && item.rentalDates && (
                          <div className="text-gray-500 text-xs mt-0.5">{getRentalDates(item)}</div>
                        )}
                      </div>
                    ))}
                  </td>
                  <td className="px-6 py-4 text-gray-900">{formatPrice(order.total)}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium 
                      ${order.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
                        order.status === 'Confirmed' ? 'bg-blue-100 text-blue-800' :
                          'bg-green-100 text-green-800'}`}
                    >
                      {order.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button className="text-gray-500 hover:text-gold transition-colors p-1">
                      <Eye size={18} />
                    </button>
                  </td>
                </tr>
              ))}

              {filteredOrders.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                    No orders found. Orders will appear here after customers complete checkout.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination placeholder */}
        <div className="p-4 border-t border-border flex items-center justify-between text-sm text-gray-500 bg-gray-50/50">
          <span>Showing {filteredOrders.length} of {orders.length} orders</span>
          <div className="flex gap-2">
            <button className="px-3 py-1 border border-border rounded-md hover:bg-gray-100 disabled:opacity-50" disabled>Previous</button>
            <button className="px-3 py-1 border border-border rounded-md hover:bg-gray-100 disabled:opacity-50" disabled>Next</button>
          </div>
        </div>
      </div>
    </div>
  );
}
