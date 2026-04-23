import { useQuery } from "@tanstack/react-query";
import { 
  ShoppingBag, 
  CalendarCheck, 
  DollarSign, 
  Users 
} from "lucide-react";
import { supabase } from "@/integrations/supabase/client";

// MOCK DATA FOR DEMO PURPOSES
const stats = [
  { title: "Total Revenue", value: "AED 124,500", icon: DollarSign, trend: "+12.5%" },
  { title: "Active Rentals", value: "18", icon: CalendarCheck, trend: "+4.2%" },
  { title: "Pending Orders", value: "7", icon: ShoppingBag, trend: "-2.1%" },
  { title: "New Consultations", value: "12", icon: Users, trend: "+8.4%" },
];

export default function AdminDashboard() {
  // Real implementation would fetch these from Supabase edge functions or complex views
  // const { data } = useQuery({ queryKey: ['admin-stats'], queryFn: ... })

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-heading font-semibold text-gray-900">Overview</h1>
        <p className="text-sm text-gray-500 mt-1">Welcome back, Admin. Here's what's happening today.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          const isPositive = stat.trend.startsWith("+");
          return (
            <div key={stat.title} className="bg-white p-6 rounded-xl border border-border shadow-sm">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-sm font-medium text-gray-500">{stat.title}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-2">{stat.value}</p>
                </div>
                <div className="p-2 bg-gray-50 rounded-lg">
                  <Icon size={20} className="text-gold" />
                </div>
              </div>
              <div className="mt-4 flex items-center text-sm">
                <span className={`font-medium ${isPositive ? 'text-green-600' : 'text-red-500'}`}>
                  {stat.trend}
                </span>
                <span className="text-gray-500 ml-2">vs last month</span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
        {/* Recent Bookings Placeholder */}
        <div className="bg-white rounded-xl border border-border shadow-sm p-6 line-clamp-none">
           <h2 className="text-lg font-semibold mb-4">Recent Bookings</h2>
           <div className="space-y-4">
              <div className="flex justify-between items-center py-3 border-b border-gray-100">
                <div>
                  <p className="font-medium text-gray-900">Layla Ahmed - Rosalina Gown</p>
                  <p className="text-sm text-gray-500">Mar 15 - Mar 18</p>
                </div>
                <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-xs font-medium rounded-full">Pending</span>
              </div>
              <div className="flex justify-between items-center py-3 border-b border-gray-100">
                <div>
                  <p className="font-medium text-gray-900">Sarah K - Aurelia Gown</p>
                  <p className="text-sm text-gray-500">Mar 22 - Mar 25</p>
                </div>
                <span className="px-3 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">Confirmed</span>
              </div>
           </div>
        </div>

         {/* Upcoming Consultations Placeholder */}
         <div className="bg-white rounded-xl border border-border shadow-sm p-6 line-clamp-none">
           <h2 className="text-lg font-semibold mb-4">Upcoming Consultations</h2>
           <div className="space-y-4">
              <div className="flex justify-between items-center py-3 border-b border-gray-100">
                <div>
                  <p className="font-medium text-gray-900">Fatima Al-Sayed</p>
                  <p className="text-sm text-gray-500">Bridal Fitting • Mar 12, 11:00 AM</p>
                </div>
              </div>
              <div className="flex justify-between items-center py-3 border-b border-gray-100">
                <div>
                  <p className="font-medium text-gray-900">Nour Hassan</p>
                  <p className="text-sm text-gray-500">Evening Dress Viewing • Mar 13, 2:30 PM</p>
                </div>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
}
