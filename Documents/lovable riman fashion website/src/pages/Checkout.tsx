import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { format } from "date-fns";
import { motion } from "framer-motion";
import { CheckCircle } from "lucide-react";
import { useCart } from "@/contexts/CartContext";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/hooks/use-toast";
import Layout from "@/components/Layout";

const CheckoutPage = () => {
  const { items, subtotal, securityDepositTotal, clearCart } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [shippingMethod, setShippingMethod] = useState<"delivery" | "pickup">("delivery");
  const [paymentMethod, setPaymentMethod] = useState<"card" | "cod">("card");
  const [isProcessing, setIsProcessing] = useState(false);

  // Form states
  const [address, setAddress] = useState("");
  const [phone, setPhone] = useState("");

  const total = subtotal + securityDepositTotal;
  const hasRental = items.some(item => item.type === "rent");

  useEffect(() => {
    if (!user) {
      toast({
        title: "Authentication Required",
        description: "Please sign in or create an account to checkout.",
      });
      navigate("/auth", { state: { from: { pathname: "/checkout" } } });
    } else if (items.length === 0) {
      navigate("/");
    }
  }, [user, items, navigate, toast]);

  const validateForm = (): boolean => {
    if (shippingMethod === "delivery") {
      if (!address.trim()) {
        toast({ title: "Missing address", description: "Please enter your shipping address.", variant: "destructive" });
        return false;
      }
      if (!phone.trim() || phone.trim().length < 8) {
        toast({ title: "Invalid phone", description: "Please enter a valid phone number.", variant: "destructive" });
        return false;
      }
    }
    return true;
  };

  const handleCheckout = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;
    setIsProcessing(true);

    try {
      // In a real app, this would:
      // 1. Create Supabase order record
      // 2. If card payment: create Stripe PaymentIntent on backend, confirm here
      // 3. For rentals: authorize security deposit instead of capturing

      // Simulating network request
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Save order to localStorage for demo mode
      const orderId = `ORD-${Date.now()}`;
      const orderItems = items.map(item => ({
        productId: item.product.id,
        name: item.product.name,
        type: item.type,
        price: item.type === 'rent' ? item.product.rentalPrice : item.product.salePrice,
        image: item.product.images[0],
        size: item.size,
        rentalDates: item.dateRange
      }));

      const newOrder = {
        id: orderId,
        userEmail: user?.email || 'demo@user.com',
        items: orderItems,
        total: total,
        subtotal: subtotal,
        securityDeposit: securityDepositTotal,
        shippingMethod,
        paymentMethod,
        address: shippingMethod === 'delivery' ? address : 'Pickup in Store',
        phone,
        status: 'Confirmed',
        createdAt: new Date().toISOString(),
      };

      // Save to localStorage
      const existingOrders = JSON.parse(localStorage.getItem('riman_orders') || '[]');
      existingOrders.push(newOrder);
      localStorage.setItem('riman_orders', JSON.stringify(existingOrders));

      toast({
        title: "Order Confirmed!",
        description: paymentMethod === "cod"
          ? "Your order has been placed successfully. You will pay upon delivery."
          : "Your payment was successful.",
      });

      clearCart();
      navigate("/profile"); // Redirect to profile to see orders

    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "An unexpected error occurred.";
      toast({
        title: "Checkout failed",
        description: message,
        variant: "destructive"
      });
    } finally {
      setIsProcessing(false);
    }
  };

  if (!user || items.length === 0) return null;

  return (
    <Layout>
      <section className="pt-32 pb-24 md:pt-40 md:pb-32 bg-gray-50 min-h-screen">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-12">
            <h1 className="heading-display text-3xl">Checkout</h1>
            <p className="font-body text-xs text-muted-foreground uppercase tracking-widest mt-2 bg-gradient-to-r from-transparent via-gold to-transparent p-[1px] "></p>
          </div>

          {/* Progress Bar */}
          <div className="flex items-center justify-center mb-12">
            {[
              { step: 1, label: "Cart" },
              { step: 2, label: "Shipping" },
              { step: 3, label: "Payment" },
              { step: 4, label: "Confirmation" }
            ].map((item, i, arr) => (
              <div key={item.step} className="flex items-center">
                <div className="flex flex-col items-center">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center transition-colors ${item.step <= 2 ? 'bg-gold text-white' : 'bg-gray-200 text-gray-500'}`}>
                    {item.step < 2 ? <CheckCircle size={20} /> : item.step}
                  </div>
                  <span className={`text-xs mt-2 ${item.step <= 2 ? 'text-gold' : 'text-muted-foreground'}`}>{item.label}</span>
                </div>
                {i < arr.length - 1 && (
                  <div className={`w-12 md:w-24 h-0.5 mx-2 ${item.step < 2 ? 'bg-gold' : 'bg-gray-200'}`} />
                )}
              </div>
            ))}
          </div>

          <div className="flex flex-col lg:flex-row gap-12">

            {/* Left Column: Forms */}
            <div className="flex-1 space-y-10">

              {/* Shipping Method */}
              <motion.div
                initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                className="bg-white p-8 border border-border"
              >
                <h2 className="font-heading text-xl mb-6 flex items-center gap-3">
                  <span className="flex items-center justify-center w-6 h-6 rounded-full bg-gold text-white text-xs">1</span>
                  Delivery Method
                </h2>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    type="button"
                    onClick={() => setShippingMethod("delivery")}
                    className={`p-4 border text-left transition-colors ${shippingMethod === "delivery" ? "border-gold bg-gold/5" : "border-border"}`}
                  >
                    <p className="font-heading text-lg">Delivery</p>
                    <p className="text-sm text-gray-500 mt-1">Direct to your address</p>
                  </button>
                  <button
                    type="button"
                    onClick={() => setShippingMethod("pickup")}
                    className={`p-4 border text-left transition-colors ${shippingMethod === "pickup" ? "border-gold bg-gold/5" : "border-border"}`}
                  >
                    <p className="font-heading text-lg">Boutique Pickup</p>
                    <p className="text-sm text-gray-500 mt-1">Visit our Sharjah atelier</p>
                  </button>
                </div>

                {shippingMethod === "delivery" && (
                  <div className="mt-6 space-y-4">
                    <div>
                      <label className="font-body text-[10px] tracking-widest uppercase text-foreground/80 mb-2 block">Shipping Address</label>
                      <textarea
                        required
                        value={address}
                        onChange={(e) => setAddress(e.target.value)}
                        className="w-full bg-transparent border border-border p-3 text-sm focus:border-gold focus:outline-none transition-colors"
                        rows={3}
                        placeholder="S130 - Al Jazzat - Sharjah, UAE"
                      />
                    </div>
                    <div>
                      <label className="font-body text-[10px] tracking-widest uppercase text-foreground/80 mb-2 block">Phone Number</label>
                      <input
                        type="tel"
                        required
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        className="w-full h-12 bg-transparent border-b border-border text-sm focus:border-gold focus:outline-none transition-colors px-0"
                        placeholder="055 373 0792"
                      />
                    </div>
                  </div>
                )}
              </motion.div>

              {/* Payment Method */}
              <motion.div
                initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
                className="bg-white p-8 border border-border"
              >
                <h2 className="font-heading text-xl mb-6 flex items-center gap-3">
                  <span className="flex items-center justify-center w-6 h-6 rounded-full bg-gold text-white text-xs">2</span>
                  Payment
                </h2>

                {hasRental && (
                  <div className="mb-6 p-4 bg-blush/30 border border-gold/30 text-sm text-gray-700">
                    <p className="font-medium text-gold mb-1">Security Deposit Required</p>
                    Your bag contains rental items. For Credit Card payments, we will hold {securityDepositTotal.toLocaleString()} AED on your card. For COD, the deposit must be paid in cash upon delivery.
                  </div>
                )}

                <div className="space-y-4">
                  <label className={`flex items-center p-4 border cursor-pointer transition-colors ${paymentMethod === "card" ? "border-gold bg-gold/5" : "border-border"}`}>
                    <input type="radio" name="payment" value="card" checked={paymentMethod === "card"} onChange={() => setPaymentMethod("card")} className="mr-3 text-gold focus:ring-gold" />
                    <div>
                      <p className="font-heading">Credit / Debit Card</p>
                      <p className="text-sm text-gray-500">Secure payment via Stripe</p>
                    </div>
                  </label>
                  <label className={`flex items-center p-4 border cursor-pointer transition-colors ${paymentMethod === "cod" ? "border-gold bg-gold/5" : "border-border"}`}>
                    <input type="radio" name="payment" value="cod" checked={paymentMethod === "cod"} onChange={() => setPaymentMethod("cod")} className="mr-3 text-gold focus:ring-gold" />
                    <div>
                      <p className="font-heading">Cash on Delivery</p>
                      <p className="text-sm text-gray-500">Pay when you receive your order</p>
                    </div>
                  </label>
                </div>

                {paymentMethod === "card" && (
                  <div className="mt-6 p-6 border border-border bg-gray-50/50 flex flex-col items-center justify-center text-center">
                    <p className="text-sm text-muted-foreground mb-4">Stripe payment form will render here.</p>
                    {/* <Elements stripe={stripePromise} options={{ clientSecret }}> <CheckoutForm /> </Elements> */}
                  </div>
                )}
              </motion.div>

              <button
                onClick={handleCheckout}
                disabled={isProcessing}
                className="btn-luxury w-full py-4 text-base"
              >
                {isProcessing ? "Processing..." : `Complete Order • AED ${total.toLocaleString()}`}
              </button>

            </div>

            {/* Right Column: Order Summary */}
            <div className="lg:w-[400px]">
              <motion.div
                initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}
                className="bg-white p-8 border border-border sticky top-32"
              >
                <h3 className="font-heading text-2xl mb-6">Order Summary</h3>

                <div className="space-y-6 mb-8 max-h-[40vh] overflow-y-auto pr-2">
                  {items.map((item) => (
                    <div key={item.id} className="flex gap-4">
                      <div className="w-20 h-24 bg-blush/20 shrink-0">
                        <img src={item.product.images[0]} alt={item.product.name} className="w-full h-full object-cover" />
                      </div>
                      <div className="flex-1 text-sm">
                        <p className="font-heading text-base">{item.product.name}</p>
                        <p className="text-muted-foreground text-xs uppercase tracking-wider mb-2 mt-1">
                          {item.type === "sale" ? "Purchase" : "Rental"} • Size: {item.size}
                        </p>

                        {item.type === "rent" && item.dateRange?.from && item.dateRange?.to && (
                          <p className="text-xs text-muted-foreground mb-2">
                            {format(item.dateRange.from, "MMM d")} - {format(item.dateRange.to, "MMM d, yyyy")}
                          </p>
                        )}

                        <div className="flex justify-between items-center mt-2">
                          <span className="text-gray-500">Qty: {item.quantity || 1}</span>
                          <span className="font-medium text-gold">
                            AED {item.type === "rent"
                              ? ((item.product.rentalPrice || 0) * (item.rentalDays || 1)).toLocaleString()
                              : ((item.product.salePrice || 0) * (item.quantity || 1)).toLocaleString()}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="border-t border-border pt-6 space-y-3 test-sm">
                  <div className="flex justify-between text-gray-600">
                    <span>Subtotal</span>
                    <span>AED {subtotal.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-gray-600">
                    <span>Shipping</span>
                    <span>{shippingMethod === "delivery" ? "Calculated at next step" : "Free"}</span>
                  </div>
                  {securityDepositTotal > 0 && (
                    <div className="flex justify-between text-gray-600">
                      <span>Security Deposit <span className="text-xs text-gray-400">(Refundable)</span></span>
                      <span>AED {securityDepositTotal.toLocaleString()}</span>
                    </div>
                  )}
                  <div className="border-t border-border pt-4 mt-4 flex justify-between font-heading text-xl">
                    <span>Total</span>
                    <span className="text-gold">AED {total.toLocaleString()}</span>
                  </div>
                </div>
              </motion.div>
            </div>

          </div>
        </div>
      </section>
    </Layout>
  );
};

export default CheckoutPage;
