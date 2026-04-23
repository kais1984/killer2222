import { motion } from "framer-motion";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";
import Layout from "@/components/Layout";

const ContactPage = () => {
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);

    const formData = new FormData(e.currentTarget);
    const data = {
      name: formData.get("name") as string,
      email: formData.get("email") as string,
      phone: formData.get("phone") as string,
      preferred_date: formData.get("preferred_date") as string,
      preferred_time: formData.get("preferred_time") as string,
      message: (formData.get("message") as string) || null,
    };

    const { error } = await supabase
      .from("consultation_requests")
      .insert(data);

    setLoading(false);

    if (error) {
      toast({
        title: "Something went wrong",
        description: "Please try again or contact us directly.",
        variant: "destructive",
      });
      return;
    }

    setSubmitted(true);
  };

  return (
    <Layout>
      <section className="pt-32 pb-16 px-6 text-center bg-champagne">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <p className="font-body text-[10px] tracking-[0.4em] uppercase text-muted-foreground mb-4">Get In Touch</p>
          <h1 className="heading-display text-4xl md:text-6xl">Book Your Private Viewing</h1>
          <div className="divider-gold mt-6 mb-4" />
          <p className="font-body text-sm text-muted-foreground max-w-md mx-auto">
            Experience luxury up close. Schedule a private appointment at our Sharjah atelier.
          </p>
        </motion.div>
      </section>

      <section className="section-padding">
        <div className="max-w-2xl mx-auto">
          {submitted ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center py-16"
            >
              <h2 className="heading-display text-3xl mb-4">Thank You</h2>
              <p className="font-body text-sm text-muted-foreground">
                We've received your request and will be in touch within 24 hours to confirm your appointment.
              </p>
            </motion.div>
          ) : (
            <motion.form
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              onSubmit={handleSubmit}
              className="space-y-6"
            >
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div>
                  <label className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground block mb-2">Full Name</label>
                  <input
                    name="name"
                    type="text"
                    required
                    className="w-full border border-border bg-transparent px-4 py-3 font-body text-sm focus:outline-none focus:border-gold transition-colors"
                    placeholder="Your name"
                  />
                </div>
                <div>
                  <label className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground block mb-2">Email</label>
                  <input
                    name="email"
                    type="email"
                    required
                    className="w-full border border-border bg-transparent px-4 py-3 font-body text-sm focus:outline-none focus:border-gold transition-colors"
                    placeholder="your@email.com"
                  />
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div>
                  <label className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground block mb-2">Phone</label>
                  <input
                    name="phone"
                    type="tel"
                    required
                    className="w-full border border-border bg-transparent px-4 py-3 font-body text-sm focus:outline-none focus:border-gold transition-colors"
                    placeholder="055 373 0792"
                  />
                </div>
                <div>
                  <label className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground block mb-2">Preferred Date</label>
                  <input
                    name="preferred_date"
                    type="date"
                    required
                    className="w-full border border-border bg-transparent px-4 py-3 font-body text-sm focus:outline-none focus:border-gold transition-colors"
                  />
                </div>
              </div>
              <div>
                <label className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground block mb-2">Preferred Time</label>
                <select name="preferred_time" className="w-full border border-border bg-transparent px-4 py-3 font-body text-sm focus:outline-none focus:border-gold transition-colors">
                  <option value="Morning (10AM – 12PM)">Morning (10AM – 12PM)</option>
                  <option value="Afternoon (12PM – 4PM)">Afternoon (12PM – 4PM)</option>
                  <option value="Evening (4PM – 8PM)">Evening (4PM – 8PM)</option>
                </select>
              </div>
              <div>
                <label className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground block mb-2">Message (Optional)</label>
                <textarea
                  name="message"
                  rows={4}
                  className="w-full border border-border bg-transparent px-4 py-3 font-body text-sm focus:outline-none focus:border-gold transition-colors resize-none"
                  placeholder="Tell us about your dream dress or occasion..."
                />
              </div>
              <button type="submit" disabled={loading} className="btn-luxury w-full disabled:opacity-50">
                {loading ? "Submitting..." : "Request Appointment"}
              </button>
            </motion.form>
          )}
        </div>
      </section>
    </Layout>
  );
};

export default ContactPage;
