import { Link, useLocation } from "react-router-dom";
import { Home, ShoppingBag, Heart, User } from "lucide-react";
import { useCart } from "@/contexts/CartContext";

const MobileBottomNav = () => {
  const location = useLocation();
  const { totalItems } = useCart();

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t flex justify-around py-3 md:hidden z-40 safe-area-bottom">
      <Link
        to="/"
        className={`flex flex-col items-center text-xs ${location.pathname === "/" ? "text-gold" : "text-muted-foreground"}`}
      >
        <Home size={20} />
        <span className="mt-1">Home</span>
      </Link>
      <Link
        to="/collection/all"
        className={`flex flex-col items-center text-xs relative ${location.pathname.includes("/collection") ? "text-gold" : "text-muted-foreground"}`}
      >
        <div className="relative">
          <ShoppingBag size={20} />
          {totalItems > 0 && (
            <span className="absolute -top-2 -right-2 bg-gold text-white text-[10px] w-5 h-5 rounded-full flex items-center justify-center">
              {totalItems > 9 ? "9+" : totalItems}
            </span>
          )}
        </div>
        <span className="mt-1">Shop</span>
      </Link>
      <Link
        to="/wishlist"
        className={`flex flex-col items-center text-xs ${location.pathname === "/wishlist" ? "text-gold" : "text-muted-foreground"}`}
      >
        <Heart size={20} />
        <span className="mt-1">Wishlist</span>
      </Link>
      <Link
        to="/profile"
        className={`flex flex-col items-center text-xs ${location.pathname === "/profile" ? "text-gold" : "text-muted-foreground"}`}
      >
        <User size={20} />
        <span className="mt-1">Account</span>
      </Link>
    </nav>
  );
};

export default MobileBottomNav;
