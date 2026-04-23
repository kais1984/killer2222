import { useState, useEffect } from "react";
import { X } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const NewsletterPopup = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [email, setEmail] = useState("");
  const { toast } = useToast();

  useEffect(() => {
    const hasSubscribed = localStorage.getItem("riman_newsletter");
    const timer = setTimeout(() => {
      if (!hasSubscribed) {
        setIsOpen(true);
      }
    }, 5000); // Show after 5 seconds

    return () => clearTimeout(timer);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    localStorage.setItem("riman_newsletter", email);
    toast({
      title: "Welcome to Riman Fashion! 🎉",
      description: "You've been subscribed. Check your email for 10% off code!",
    });
    setIsOpen(false);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white max-w-lg w-full relative">
        <button
          onClick={() => setIsOpen(false)}
          className="absolute top-4 right-4 text-muted-foreground hover:text-foreground"
          aria-label="Close"
        >
          <X size={24} />
        </button>

        <div className="p-8 md:p-12 text-center">
          <h3 className="font-heading text-3xl mb-4">Join Riman Fashion</h3>
          <p className="font-body text-muted-foreground mb-6">
            Subscribe to get 10% off your first rental + exclusive access to new arrivals
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              className="w-full border border-border p-4 text-sm focus:border-gold focus:outline-none"
              required
            />
            <button type="submit" className="btn-luxury w-full">
              Subscribe & Get 10% Off
            </button>
          </form>

          <p className="text-xs text-muted-foreground mt-4">
            By subscribing, you agree to our Privacy Policy. Unsubscribe anytime.
          </p>
        </div>
      </div>
    </div>
  );
};

export default NewsletterPopup;