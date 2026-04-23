import { format } from "date-fns";
import { ShoppingBag, X, Trash2 } from "lucide-react";
import { Link } from "react-router-dom";
import { useCart } from "@/contexts/CartContext";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";

export function CartDrawer() {
  const { items, removeItem, totalItems, subtotal, securityDepositTotal } = useCart();

  return (
    <Sheet>
      <SheetTrigger asChild>
        <button aria-label="Cart" className="hover:text-gold transition-colors relative">
          <ShoppingBag size={18} />
          {totalItems > 0 && (
            <span className="absolute -top-2 -right-2 bg-gold text-white text-[10px] w-4 h-4 rounded-full flex items-center justify-center font-bold">
              {totalItems}
            </span>
          )}
        </button>
      </SheetTrigger>
      <SheetContent className="w-full sm:max-w-md bg-white flex flex-col pt-12">
        <SheetHeader>
          <SheetTitle className="font-heading text-2xl tracking-wide font-normal">Your Bag</SheetTitle>
        </SheetHeader>

        <div className="flex-1 overflow-y-auto py-6 flex flex-col gap-6">
          {items.length === 0 ? (
            <div className="text-center text-muted-foreground mt-12">
              <p className="font-body text-sm mb-4">Your bag is currently empty.</p>
              <SheetTrigger asChild>
                <Link to="/collection/bridal" className="btn-luxury inline-block">Continue Shopping</Link>
              </SheetTrigger>
            </div>
          ) : (
            items.map((item) => (
              <div key={item.id} className="flex gap-4 items-start border-b border-border pb-6">
                <div className="w-20 h-24 bg-blush/20 overflow-hidden shrink-0">
                  <img src={item.product.images[0]} alt={item.product.name} className="w-full h-full object-cover" />
                </div>
                
                <div className="flex-1 flex flex-col justify-between h-full">
                  <div>
                    <div className="flex justify-between items-start">
                      <h4 className="font-heading text-lg">{item.product.name}</h4>
                      <button onClick={() => removeItem(item.id)} className="text-muted-foreground hover:text-destructive">
                        <Trash2 size={16} />
                      </button>
                    </div>
                    
                    <p className="font-body text-[10px] uppercase tracking-widest text-muted-foreground mt-1">
                      {item.type === "sale" ? "Purchase" : "Rental"} • Size: {item.size}
                    </p>

                    {item.type === "rent" && item.dateRange?.from && item.dateRange?.to && (
                      <p className="font-body text-[11px] text-muted-foreground mt-2 bg-blush/30 px-2 py-1 inline-block rounded">
                        {format(item.dateRange.from, "MMM d")} - {format(item.dateRange.to, "MMM d, yyyy")}
                      </p>
                    )}
                  </div>

                  <div className="flex justify-between items-end mt-4">
                    <p className="font-body text-xs text-muted-foreground">Qty: {item.quantity || 1}</p>
                    <p className="font-heading text-gold">
                      AED {item.type === "rent" 
                          ? ((item.product.rentalPrice || 0) * (item.rentalDays || 1)).toLocaleString() 
                          : ((item.product.salePrice || 0) * (item.quantity || 1)).toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {items.length > 0 && (
          <div className="border-t border-border pt-6 pb-6 lg:pb-0">
            <div className="flex justify-between items-center mb-2 font-body text-sm text-foreground">
              <span>Subtotal</span>
              <span>AED {subtotal.toLocaleString()}</span>
            </div>
            {securityDepositTotal > 0 && (
              <div className="flex justify-between items-center mb-4 font-body text-sm text-muted-foreground">
                <span>Security Deposit (Refundable)</span>
                <span>AED {securityDepositTotal.toLocaleString()}</span>
              </div>
            )}
            <div className="flex justify-between items-center mb-6 font-heading text-lg">
              <span>Total</span>
              <span className="text-gold">AED {(subtotal + securityDepositTotal).toLocaleString()}</span>
            </div>
            
            <SheetTrigger asChild>
              <Link to="/checkout" className="btn-luxury w-full flex justify-center">
                Checkout
              </Link>
            </SheetTrigger>
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}
