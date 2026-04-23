import { Shield, Truck, RefreshCcw, CreditCard } from "lucide-react";

const TrustBadges = () => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-6 py-12 bg-gray-50">
      <div className="text-center">
        <Shield size={40} className="mx-auto mb-3 text-gold" />
        <p className="font-heading text-sm mb-1">Secure Payment</p>
        <p className="text-xs text-muted-foreground">Encrypted transactions</p>
      </div>
      <div className="text-center">
        <Truck size={40} className="mx-auto mb-3 text-gold" />
        <p className="font-heading text-sm mb-1">Free Shipping</p>
        <p className="text-xs text-muted-foreground">On orders over AED 500</p>
      </div>
      <div className="text-center">
        <RefreshCcw size={40} className="mx-auto mb-3 text-gold" />
        <p className="font-heading text-sm mb-1">Easy Returns</p>
        <p className="text-xs text-muted-foreground">7-day return policy</p>
      </div>
      <div className="text-center">
        <CreditCard size={40} className="mx-auto mb-3 text-gold" />
        <p className="font-heading text-sm mb-1">Flexible Rental</p>
        <p className="text-xs text-muted-foreground">Rent or buy options</p>
      </div>
    </div>
  );
};

export default TrustBadges;