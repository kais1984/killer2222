import { useState } from "react";
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { 
  LayoutDashboard, 
  ShoppingBag, 
  Calendar, 
  Package, 
  MessageSquare, 
  FileText, 
  LogOut,
  Menu,
  X
} from "lucide-react";
import logo from "@/assets/logo.png";
import { useAuth } from "@/contexts/AuthContext";

const adminLinks = [
  { icon: LayoutDashboard, label: "Overview", path: "/admin" },
  { icon: Calendar, label: "Rental Calendar", path: "/admin/calendar" },
  { icon: ShoppingBag, label: "Orders", path: "/admin/orders" },
  { icon: Package, label: "Products", path: "/admin/products" },
  { icon: MessageSquare, label: "Consultations", path: "/admin/consultations" },
  { icon: FileText, label: "Content", path: "/admin/content" },
];

export default function AdminLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { signOut } = useAuth();

  const handleLogout = async () => {
    await signOut();
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Mobile sidebar toggle */}
      <button 
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-white rounded-md shadow-sm border border-border"
        onClick={() => setSidebarOpen(!sidebarOpen)}
      >
        {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Sidebar */}
      <aside 
        className={`fixed inset-y-0 left-0 z-40 w-64 bg-white border-r border-border transform transition-transform duration-300 lg:translate-x-0 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="h-full flex flex-col">
          <div className="p-6 flex justify-center items-center border-b border-border">
            <Link to="/">
              <img src={logo} alt="Riman Fashion" className="h-12 md:h-16 w-auto object-contain drop-shadow-sm" />
            </Link>
          </div>

          <div className="flex-1 overflow-y-auto py-6 px-4 space-y-2">
            <p className="px-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-4">
              Dashboard
            </p>
            {adminLinks.map((link) => {
              const Icon = link.icon;
              const isActive = location.pathname === link.path || 
                               (link.path !== "/admin" && location.pathname.startsWith(link.path));
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  onClick={() => setSidebarOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-md text-sm transition-colors ${
                    isActive 
                      ? "bg-gold text-white font-medium shadow-sm" 
                      : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                  }`}
                >
                  <Icon size={18} />
                  {link.label}
                </Link>
              );
            })}
          </div>

          <div className="p-4 border-t border-border">
            <button 
              onClick={handleLogout}
              className="flex items-center gap-3 px-4 py-2 w-full text-left text-sm text-red-600 hover:bg-red-50 rounded-md transition-colors"
            >
              <LogOut size={18} />
              Sign Out
            </button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 lg:ml-64 min-h-screen">
        <div className="p-6 md:p-10 max-w-7xl mx-auto mt-12 lg:mt-0">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <Outlet />
          </motion.div>
        </div>
      </main>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/20 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
}
