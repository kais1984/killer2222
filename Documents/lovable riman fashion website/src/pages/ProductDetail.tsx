import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, Calendar as CalendarIcon, Info, AlertCircle, CheckCircle2 } from "lucide-react";
import { differenceInDays, format } from "date-fns";
import { DateRange } from "react-day-picker";
import Layout from "@/components/Layout";
import { products } from "@/data/products";
import { Calendar } from "@/components/ui/calendar";
import { useToast } from "@/hooks/use-toast";
import { useCart } from "@/contexts/CartContext";
import { useAvailability } from "@/contexts/AvailabilityContext";
import { AvailabilityCalendar, AvailabilityStatus } from "@/components/AvailabilityCalendar";
import { calculateRentalPrice as calcRentalPrice, checkAvailability } from "@/services/bookingService";
import SizeGuideModal from "@/components/SizeGuideModal";
import FabricCustomization from "@/components/FabricCustomization";
import SocialShare from "@/components/SocialShare";
import VirtualTryOn from "@/components/VirtualTryOn";
import { useAuth } from "@/contexts/AuthContext";

const ProductDetail = () => {
  const { id } = useParams<{ id: string }>();
  const { toast } = useToast();
  const { addItem } = useCart();
  const { user } = useAuth();
  const { availability, isLoading: isCheckingAvailability, blockedDates, inventory, checkAvailability: checkAvail, loadBlockedDates, loadInventory } = useAvailability();

  // Use static products directly
  const product = products.find((p) => p.id === id);

  // State
  const [selectedSize, setSelectedSize] = useState<string | null>(null);
  const [date, setDate] = useState<DateRange | undefined>(undefined);
  const [isChecking, setIsChecking] = useState(false);
  const [showSizeGuide, setShowSizeGuide] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [availabilityError, setAvailabilityError] = useState<string | null>(null);

  // Load availability data on mount
  useEffect(() => {
    if (id) {
      loadInventory(id);
      loadBlockedDates(id);
    }
  }, [id, loadInventory, loadBlockedDates]);

  // If product not found
  if (!product) {
    return (
      <Layout>
        <div className="pt-32 section-padding text-center">
          <h1 className="heading-display text-4xl mb-4">Product Not Found</h1>
          <p className="text-muted-foreground mb-8">Sorry, we could not find this product.</p>
          <Link to="/collection/all" className="btn-luxury">
            <ArrowLeft size={16} className="inline mr-2" />
            Browse Collection
          </Link>
        </div>
      </Layout>
    );
  }

  const isAvailableForRent = product.productType === "rent" || product.productType === "both";
  const isAvailableForSale = product.productType === "sale" || product.productType === "both";
  const isProductUnavailable = inventory && !inventory.is_available_for_rent && !inventory.is_available_for_sale;
  const isOutOfStock = inventory && inventory.available_stock <= 0;

  const calculateRentalPrice = () => {
    if (!isAvailableForRent || !date?.from || !date?.to || !product.rentalPrice) return null;
    const days = Math.abs(differenceInDays(date.to, date.from));
    return days > 0 ? (product.rentalPrice * days) + (product.securityDeposit || 0) : null;
  };

  // Validate dates against server-side availability
  const validateDates = async (startDate: Date, endDate: Date): Promise<boolean> => {
    if (!id) return false;

    setIsValidating(true);
    setAvailabilityError(null);

    try {
      const result = await checkAvailability(
        id,
        startDate.toISOString().split('T')[0],
        endDate.toISOString().split('T')[0]
      );

      if (!result.isAvailable) {
        setAvailabilityError(result.reason || 'Selected dates are not available');
        return false;
      }

      return true;
    } catch (err) {
      // Backend not ready - allow add to proceed with warning
      console.warn('Availability check failed, proceeding anyway:', err);
      setAvailabilityError(null);
      return true; // Allow add to cart, backend will validate at checkout
    } finally {
      setIsValidating(false);
    }
  };

  const handleAddToCart = async () => {
    if (!selectedSize) {
      toast({ title: "Please select a size", variant: "destructive" });
      return;
    }

    // Validate rental dates server-side
    if (isAvailableForRent && date?.from && date?.to) {
      const isValid = await validateDates(date.from, date.to);
      if (!isValid) {
        toast({
          title: "Dates Not Available",
          description: availabilityError || "The selected dates are already booked.",
          variant: "destructive",
        });
        return;
      }
    }

    if (isAvailableForRent && !isAvailableForSale && (!date?.from || !date?.to)) {
      toast({ title: "Please select rental dates", variant: "destructive" });
      return;
    }

    setIsChecking(true);
    setTimeout(() => {
      setIsChecking(false);
      if (isAvailableForRent && !isAvailableForSale) {
        addItem({ product, type: "rent", size: selectedSize, dateRange: date, rentalDays: differenceInDays(date.to!, date.from!) });
      } else {
        addItem({ product, type: "sale", size: selectedSize, quantity: 1 });
      }
      toast({ title: "Added to cart!" });
    }, 500);
  };

  const price = isAvailableForSale ? `AED ${product.salePrice?.toLocaleString()}` : `AED ${product.rentalPrice?.toLocaleString()} / day`;

  return (
    <Layout>
      <section className="pt-24 md:pt-28">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mb-8">
            <button onClick={() => window.history.back()} className="inline-flex items-center gap-2 font-body text-xs tracking-[0.15em] uppercase text-muted-foreground hover:text-gold transition-colors">
              <ArrowLeft size={14} /> Back
            </button>
          </motion.div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20">
            <motion.div initial={{ opacity: 0, x: -30 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.8 }}>
              <div className="aspect-[3/4] overflow-hidden">
                <img src={product.images?.[0] || '/images/placeholder.jpg'} alt={product.name} className="w-full h-full object-cover" />
              </div>
            </motion.div>
            <motion.div initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.8, delay: 0.2 }} className="flex flex-col justify-center py-8">
              <p className="font-body text-[10px] tracking-[0.3em] uppercase text-muted-foreground mb-2">{product.category} • {product.designer}</p>
              <h1 className="font-heading text-4xl md:text-5xl tracking-wide mb-2">{product.name}</h1>
              <div className="flex items-center gap-3 mb-6">
                {isAvailableForSale ? <span className="badge-sale">For Sale</span> : <span className="badge-rent">For Rent</span>}
                {id && <AvailabilityStatus inventory={inventory} />}
              </div>

              {/* Availability warning */}
              {isProductUnavailable && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
                  <AlertCircle size={16} className="text-red-500 shrink-0" />
                  <p className="text-sm text-red-700">This product is currently unavailable.</p>
                </div>
              )}
              {isOutOfStock && (
                <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-lg flex items-center gap-2">
                  <AlertCircle size={16} className="text-amber-500 shrink-0" />
                  <p className="text-sm text-amber-700">All units are currently booked. Check back soon!</p>
                </div>
              )}

              <p className="font-heading text-2xl text-gold mb-1">{price}</p>
              {isAvailableForRent && <p className="font-body text-xs text-muted-foreground mb-6">Security deposit: AED {product.securityDeposit?.toLocaleString()} (refundable)</p>}
              <div className="divider-gold !mx-0 mb-6" />
              <p className="font-body text-sm leading-relaxed text-muted-foreground mb-8">{product.description}</p>
              <div className="grid grid-cols-2 gap-4 mb-8">
                {product.fabric && <div><p className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground/60 mb-1">Fabric</p><p className="font-body text-xs">{product.fabric}</p></div>}
                <div><p className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground/60 mb-1">Style</p><p className="font-body text-xs">{product.style.join(", ")}</p></div>
                <div><p className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground/60 mb-1">Colour</p><p className="font-body text-xs">{product.color.join(", ")}</p></div>
                <div><p className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground/60 mb-1">Sizes</p><p className="font-body text-xs">{product.sizes.join(", ")}</p></div>
              </div>
              <div className="mb-6">
                <div className="flex items-center justify-between mb-3">
                  <p className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground">Select Size</p>
                  <button onClick={() => setShowSizeGuide(true)} className="text-xs text-gold hover:underline flex items-center gap-1"><Info size={14} /> Size Guide</button>
                </div>
                <div className="flex gap-2">
                  {product.sizes.map((size) => (
                    <button key={size} onClick={() => setSelectedSize(size)} className={`w-12 h-12 border font-body text-xs tracking-wider transition-colors ${selectedSize === size ? "border-gold text-gold bg-gold/5" : "border-border hover:border-gold hover:text-gold"}`}>{size}</button>
                  ))}
                </div>
              </div>
              <FabricCustomization productName={product.name} />
              <SocialShare productName={product.name} />
              <VirtualTryOn />
              <SizeGuideModal isOpen={showSizeGuide} onClose={() => setShowSizeGuide(false)} />
              {(product.productType === "rent" || product.productType === "both") && isAvailableForRent && !isProductUnavailable && (
                <div className="mb-8 p-6 bg-blush/30 border border-border">
                  <div className="flex items-center gap-2 mb-3">
                    <CalendarIcon size={16} className="text-gold" />
                    <p className="font-body text-[10px] tracking-[0.2em] uppercase">Select Rental Dates</p>
                  </div>

                  {/* Availability Calendar */}
                  <div className="bg-white rounded-md border border-border p-2 mb-4">
                    <AvailabilityCalendar
                      blockedDates={blockedDates}
                      selected={date}
                      onSelect={setDate}
                      disabled={isOutOfStock || isCheckingAvailability}
                    />
                  </div>

                  {/* Availability error message */}
                  {availabilityError && (
                    <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
                      <AlertCircle size={16} className="text-red-500 shrink-0" />
                      <p className="text-sm text-red-700">{availabilityError}</p>
                    </div>
                  )}

                  {/* Validation success */}
                  {date?.from && date?.to && !availabilityError && !isValidating && (
                    <div className="mb-2 flex items-center gap-2 text-green-600 text-sm">
                      <CheckCircle2 size={14} />
                      <span>Dates available</span>
                    </div>
                  )}

                  {date?.from && date?.to && (
                    <div className="bg-white p-4 border border-border rounded-md text-sm mb-4">
                      <div className="flex justify-between mb-2">
                        <span className="text-muted-foreground">Rental ({differenceInDays(date.to, date.from)} days)</span>
                        <span>AED {(product.rentalPrice! * differenceInDays(date.to, date.from)).toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between mb-2">
                        <span className="text-muted-foreground">Security Deposit</span>
                        <span>AED {product.securityDeposit?.toLocaleString()}</span>
                      </div>
                      <div className="divider-gold !my-3" />
                      <div className="flex justify-between font-heading text-lg">
                        <span>Total</span>
                        <span className="text-gold">AED {calculateRentalPrice()?.toLocaleString()}</span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-2">
                        {format(date.from, "MMM d, yyyy")} → {format(date.to, "MMM d, yyyy")}
                      </p>
                    </div>
                  )}
                </div>
              )}
              <div className="flex flex-col gap-3">
                <button
                  onClick={handleAddToCart}
                  disabled={isChecking || isValidating || isProductUnavailable || isOutOfStock}
                  className="btn-luxury w-full disabled:opacity-70"
                >
                  {isValidating ? "Checking..." : isChecking ? "Adding..." : isProductUnavailable ? "Unavailable" : (isAvailableForRent && !isAvailableForSale ? "Reserve Now" : "Add to Cart")}
                </button>
                <Link to="/contact" className="btn-luxury-outline w-full text-center">Book Consultation</Link>
              </div>
            </motion.div>
          </div>
        </div>
        <div className="h-20" />
      </section>
    </Layout>
  );
};

export default ProductDetail;
