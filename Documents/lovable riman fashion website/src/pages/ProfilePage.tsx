import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Calendar, Package, User, MapPin, Phone, Mail } from "lucide-react";
import Layout from "@/components/Layout";
import { useAuth } from "@/contexts/AuthContext";

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

const ProfilePage = () => {
  const [activeTab, setActiveTab] = useState<"orders" | "rentals" | "settings">("orders");
  const [orders, setOrders] = useState<Order[]>([]);
  const [rentals, setRentals] = useState<Order[]>([]);
  const { user } = useAuth();

  useEffect(() => {
    // Load orders from localStorage and filter by current user
    const allOrders: Order[] = JSON.parse(localStorage.getItem('riman_orders') || '[]');

    if (user?.email) {
      // Filter orders for current user
      const userOrders = allOrders.filter(order => order.userEmail === user.email);
      setOrders(userOrders);

      // Filter rentals (type === 'rent')
      const userRentals = userOrders.filter(order =>
        order.items.some(item => item.type === 'rent')
      );
      setRentals(userRentals);
    }
  }, [user?.email]);

  // Format price to AED
  const formatPrice = (price: number) => `AED ${price.toLocaleString()}`;

  // Format date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  return (
    <Layout>
      <section className="pt-32 pb-16 px-6 bg-champagne">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl mx-auto"
        >
          <p className="font-body text-[10px] tracking-[0.4em] uppercase text-muted-foreground mb-4 text-center">My Account</p>
          <h1 className="heading-display text-4xl md:text-5xl text-center">Welcome Back{user?.fullName ? `, ${user.fullName}` : ''}</h1>
          <div className="divider-gold mt-6 mb-4" />
        </motion.div>
      </section>

      <section className="section-padding">
        <div className="max-w-4xl mx-auto">
          {/* Tabs */}
          <div className="flex gap-1 border-b border-border mb-8">
            {([
              { key: "orders", label: "Order History", icon: Package },
              { key: "rentals", label: "My Rentals", icon: Calendar },
              { key: "settings", label: "Account Settings", icon: User },
            ] as const).map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`flex items-center gap-2 px-6 py-3 font-body text-xs uppercase tracking-widest transition-colors border-b-2 -mb-px ${activeTab === tab.key
                      ? "border-gold text-foreground"
                      : "border-transparent text-muted-foreground hover:text-foreground"
                    }`}
                >
                  <Icon size={14} />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* Order History */}
          {activeTab === "orders" && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
              {orders.length === 0 ? (
                <p className="text-center text-muted-foreground py-12">No orders yet. Start shopping to see your orders here.</p>
              ) : (
                orders.map((order) => (
                  <div key={order.id} className="flex items-center justify-between p-5 border border-border bg-white hover:shadow-sm transition-shadow">
                    <div>
                      <p className="font-heading text-lg">{order.items[0]?.name || 'Order'}</p>
                      <p className="font-body text-xs text-muted-foreground mt-1">
                        {order.id} · {order.items.map(i => i.type === 'rent' ? 'Rental' : 'Sale').join(', ')} · {formatDate(order.createdAt)}
                      </p>
                      <p className="font-body text-xs text-muted-foreground">
                        {order.items.length > 1 && `+${order.items.length - 1} more item(s)`}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold">{formatPrice(order.total)}</p>
                      <span className={`inline-block mt-1 px-2.5 py-0.5 rounded-full text-[10px] font-medium uppercase tracking-wider ${order.status === "Confirmed" ? "bg-blue-100 text-blue-800" : "bg-green-100 text-green-800"
                        }`}>{order.status}</span>
                    </div>
                  </div>
                ))
              )}
            </motion.div>
          )}

          {/* My Rentals */}
          {activeTab === "rentals" && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
              {rentals.length === 0 ? (
                <p className="text-center text-muted-foreground py-12">No rentals yet. Rent a dress to see your rentals here.</p>
              ) : (
                rentals.map((rental) => (
                  <div key={rental.id} className="flex items-center justify-between p-5 border border-border bg-white">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-gold/10 rounded-full flex items-center justify-center">
                        <Calendar size={20} className="text-gold" />
                      </div>
                      <div>
                        <p className="font-heading text-lg">{rental.items[0]?.name}</p>
                        <p className="font-body text-xs text-muted-foreground mt-1">
                          {rental.items[0]?.rentalDates?.from && rental.items[0]?.rentalDates?.to
                            ? `${rental.items[0].rentalDates.from} - ${rental.items[0].rentalDates.to}`
                            : 'Rental period not specified'}
                        </p>
                        <p className="font-body text-xs text-muted-foreground">
                          Order: {rental.id}
                        </p>
                      </div>
                    </div>
                    <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-[10px] font-medium uppercase tracking-wider rounded-full">
                      {rental.status}
                    </span>
                  </div>
                ))
              )}
            </motion.div>
          )}

          {/* Account Settings */}
          {activeTab === "settings" && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
              <div className="bg-white border border-border p-6 space-y-4">
                <h3 className="font-heading text-xl">Personal Information</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="font-body text-[10px] tracking-widest uppercase text-foreground/80 block mb-2">Full Name</label>
                    <input
                      type="text"
                      defaultValue={user?.fullName || ''}
                      className="w-full h-12 bg-transparent border-b border-border text-sm focus:border-gold focus:outline-none transition-colors px-0"
                    />
                  </div>
                  <div>
                    <label className="font-body text-[10px] tracking-widest uppercase text-foreground/80 block mb-2">Email</label>
                    <input
                      type="email"
                      defaultValue={user?.email || ''}
                      className="w-full h-12 bg-transparent border-b border-border text-sm focus:border-gold focus:outline-none transition-colors px-0"
                      disabled
                    />
                  </div>
                  <div>
                    <label className="font-body text-[10px] tracking-widest uppercase text-foreground/80 block mb-2">Phone</label>
                    <div className="flex items-center gap-2">
                      <Phone size={14} className="text-muted-foreground" />
                      <input type="tel" placeholder="Enter your phone" className="w-full h-12 bg-transparent border-b border-border text-sm focus:border-gold focus:outline-none transition-colors px-0" />
                    </div>
                  </div>
                  <div>
                    <label className="font-body text-[10px] tracking-widest uppercase text-foreground/80 block mb-2">Address</label>
                    <div className="flex items-center gap-2">
                      <MapPin size={14} className="text-muted-foreground" />
                      <input type="text" placeholder="Enter your address" className="w-full h-12 bg-transparent border-b border-border text-sm focus:border-gold focus:outline-none transition-colors px-0" />
                    </div>
                  </div>
                </div>
                <button className="btn-luxury mt-4">Save Changes</button>
              </div>
            </motion.div>
          )}
        </div>
      </section>
    </Layout>
  );
};

export default ProfilePage;
