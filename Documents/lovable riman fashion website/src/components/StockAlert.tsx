import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bell, X, Mail, Check } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface StockAlertProps {
  productName: string;
  productId: string;
}

const StockAlert = ({ productName, productId }: StockAlertProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const { toast } = useToast();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    
    // Save to localStorage (in production, this would go to a database)
    const alerts = JSON.parse(localStorage.getItem('stockAlerts') || '[]');
    const newAlert = { productId, productName, email, date: new Date().toISOString() };
    localStorage.setItem('stockAlerts', JSON.stringify([...alerts, newAlert]));
    
    setSubmitted(true);
    toast({
      title: "You'll be notified!",
      description: `We'll email you when ${productName} is back in stock.`,
    });
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="w-full py-3 border border-border rounded-lg flex items-center justify-center gap-2 hover:border-gold hover:bg-gold/5 transition-colors"
      >
        <Bell size={18} className="text-gold" />
        <span className="font-body text-xs tracking-[0.2em] uppercase">Notify Me When Available</span>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
            onClick={() => setIsOpen(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl max-w-md w-full p-6"
              onClick={(e) => e.stopPropagation()}
            >
              {!submitted ? (
                <>
                  <div className="flex justify-between items-center mb-6">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-gold/10 rounded-full flex items-center justify-center">
                        <Bell size={24} className="text-gold" />
                      </div>
                      <div>
                        <h3 className="font-heading text-lg">Get Notified</h3>
                        <p className="font-body text-xs text-muted-foreground">We'll let you know when it's back</p>
                      </div>
                    </div>
                    <button onClick={() => setIsOpen(false)}>
                      <X size={20} />
                    </button>
                  </div>

                  <p className="font-body text-sm text-muted-foreground mb-6">
                    <strong>{productName}</strong> is currently out of stock. Enter your email to be notified when it becomes available again.
                  </p>

                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                      <label className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground block mb-2">
                        <Mail size={14} className="inline mr-2" />
                        Email Address
                      </label>
                      <input
                        type="email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full border border-border px-4 py-3 font-body text-sm focus:outline-none focus:border-gold"
                        placeholder="your@email.com"
                      />
                    </div>
                    <button type="submit" className="btn-luxury w-full">
                      Notify Me
                    </button>
                  </form>
                </>
              ) : (
                <div className="text-center py-8">
                  <div className="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
                    <Check size={24} className="text-green-600" />
                  </div>
                  <h4 className="font-heading text-lg mb-2">You're on the list!</h4>
                  <p className="font-body text-sm text-muted-foreground">
                    We'll email you as soon as {productName} is back in stock.
                  </p>
                  <button
                    onClick={() => {
                      setIsOpen(false);
                      setSubmitted(false);
                      setEmail("");
                    }}
                    className="mt-6 text-sm text-gold hover:underline"
                  >
                    Close
                  </button>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default StockAlert;