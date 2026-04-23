import { useState } from "react";
import { motion } from "framer-motion";
import { Bell, Mail, Phone, Calendar, Check, Clock, ChevronRight } from "lucide-react";
import Layout from "@/components/Layout";
import { useToast } from "@/hooks/use-toast";

interface Reminder {
  id: string;
  title: string;
  description: string;
  timing: string;
  enabled: boolean;
}

const defaultReminders: Reminder[] = [
  {
    id: "consultation",
    title: "Consultation Reminder",
    description: "Get reminded about your upcoming appointment",
    timing: "24 hours before",
    enabled: true,
  },
  {
    id: "fitting",
    title: "Fitting Appointment",
    description: "Reminder for your fitting sessions",
    timing: "48 hours before",
    enabled: true,
  },
  {
    id: "pickup",
    title: "Dress Pickup",
    description: "Reminder to pick up your finished dress",
    timing: "1 week before",
    enabled: true,
  },
  {
    id: "alterations",
    title: "Alterations Update",
    description: "Get updates on your alterations progress",
    timing: "When status changes",
    enabled: false,
  },
  {
    id: "promotions",
    title: "Special Offers",
    description: "Exclusive promotions and new collection announcements",
    timing: "Monthly",
    enabled: false,
  },
];

const AppointmentReminders = () => {
  const [reminders, setReminders] = useState<Reminder[]>(defaultReminders);
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [isSubscribed, setIsSubscribed] = useState(false);
  const { toast } = useToast();

  const toggleReminder = (id: string) => {
    setReminders(reminders.map(r => 
      r.id === id ? { ...r, enabled: !r.enabled } : r
    ));
  };

  const handleSubscribe = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email && !phone) {
      toast({
        title: "Please enter email or phone",
        variant: "destructive",
      });
      return;
    }
    setIsSubscribed(true);
    toast({
      title: "Subscribed successfully!",
      description: "You'll receive reminders for your appointments.",
    });
  };

  return (
    <Layout>
      <section className="pt-32 pb-16 px-6 bg-champagne">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl mx-auto text-center"
        >
          <Bell className="mx-auto text-gold mb-4" size={32} />
          <p className="font-body text-[10px] tracking-[0.4em] uppercase text-muted-foreground mb-4">Stay Informed</p>
          <h1 className="heading-display text-4xl md:text-5xl mb-6">Appointment Reminders</h1>
          <p className="font-body text-muted-foreground max-w-2xl mx-auto mb-8">
            Never miss an important appointment. Get SMS or email reminders for your consultations, fittings, and dress pickup.
          </p>
        </motion.div>
      </section>

      <section className="section-padding">
        <div className="max-w-4xl mx-auto px-6">
          {/* Subscribe Form */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="bg-white border border-border rounded-2xl p-8 mb-12"
          >
            <h2 className="font-heading text-2xl mb-6">Subscribe to Reminders</h2>
            
            {!isSubscribed ? (
              <form onSubmit={handleSubscribe} className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground block mb-2">
                      <Mail size={14} className="inline mr-2" />
                      Email Address
                    </label>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="your@email.com"
                      className="w-full border border-border px-4 py-3 font-body text-sm focus:outline-none focus:border-gold"
                    />
                  </div>
                  <div>
                    <label className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground block mb-2">
                      <Phone size={14} className="inline mr-2" />
                      Phone Number
                    </label>
                    <input
                      type="tel"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      placeholder="+971 55 123 4567"
                      className="w-full border border-border px-4 py-3 font-body text-sm focus:outline-none focus:border-gold"
                    />
                  </div>
                </div>
                <button type="submit" className="btn-luxury">
                  Subscribe
                  <ChevronRight size={16} className="ml-2 inline" />
                </button>
              </form>
            ) : (
              <div className="text-center py-8">
                <div className="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
                  <Check size={24} className="text-green-600" />
                </div>
                <h3 className="font-heading text-xl mb-2">You're Subscribed!</h3>
                <p className="font-body text-muted-foreground mb-4">
                  You'll receive reminders at {email || phone}
                </p>
                <button
                  onClick={() => setIsSubscribed(false)}
                  className="text-sm text-gold hover:underline"
                >
                  Update preferences
                </button>
              </div>
            )}
          </motion.div>

          {/* Reminder Options */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
          >
            <h2 className="font-heading text-2xl mb-6">Reminder Settings</h2>
            
            <div className="space-y-4">
              {reminders.map((reminder) => (
                <motion.div
                  key={reminder.id}
                  whileHover={{ scale: 1.01 }}
                  className={`bg-white border rounded-xl p-6 transition-all ${
                    reminder.enabled ? "border-gold bg-gold/5" : "border-border"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4">
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                        reminder.enabled ? "bg-gold text-white" : "bg-gray-100 text-gray-400"
                      }`}>
                        {reminder.id === "consultation" && <Calendar size={20} />}
                        {reminder.id === "fitting" && <Clock size={20} />}
                        {reminder.id === "pickup" && <Check size={20} />}
                        {reminder.id === "alterations" && <Bell size={20} />}
                        {reminder.id === "promotions" && <Bell size={20} />}
                      </div>
                      <div>
                        <h3 className="font-heading text-lg">{reminder.title}</h3>
                        <p className="font-body text-sm text-muted-foreground mt-1">{reminder.description}</p>
                        <p className="font-body text-xs text-gold mt-2">
                          <Clock size={12} className="inline mr-1" />
                          {reminder.timing}
                        </p>
                      </div>
                    </div>
                    
                    <button
                      onClick={() => toggleReminder(reminder.id)}
                      className={`relative w-14 h-8 rounded-full transition-colors ${
                        reminder.enabled ? "bg-gold" : "bg-gray-200"
                      }`}
                    >
                      <span className={`absolute top-1 w-6 h-6 bg-white rounded-full shadow transition-transform ${
                        reminder.enabled ? "translate-x-7" : "translate-x-1"
                      }`} />
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Info Box */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3 }}
            className="mt-12 p-6 bg-champagne/50 border border-border rounded-xl"
          >
            <div className="flex items-start gap-4">
              <Bell size={24} className="text-gold mt-1" />
              <div>
                <h3 className="font-heading text-lg mb-2">How it works</h3>
                <ul className="font-body text-sm text-muted-foreground space-y-2">
                  <li>• Book an appointment through our contact form</li>
                  <li>• Subscribe to reminders using your email or phone</li>
                  <li>• Select which reminders you'd like to receive</li>
                  <li>• Get notified before each important appointment</li>
                </ul>
              </div>
            </div>
          </motion.div>
        </div>
      </section>
    </Layout>
  );
};

export default AppointmentReminders;