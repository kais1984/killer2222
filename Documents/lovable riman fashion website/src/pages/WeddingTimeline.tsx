import { motion } from "framer-motion";
import { useState } from "react";
import { Calendar, Clock, CheckCircle, ChevronRight, Heart } from "lucide-react";
import Layout from "@/components/Layout";

interface TimelineEvent {
  id: string;
  title: string;
  description: string;
  timing: string;
  completed: boolean;
  icon: "consultation" | "selection" | "measurement" | "first-fitting" | "alterations" | "final-fitting" | "pickup" | "wedding";
}

const timelineEvents: TimelineEvent[] = [
  {
    id: "1",
    title: "Book Your Consultation",
    description: "Schedule a private appointment at our atelier to explore our collection.",
    timing: "6-8 months before wedding",
    completed: false,
    icon: "consultation",
  },
  {
    id: "2",
    title: "Bridal Collection Viewing",
    description: "Try on our exclusive designs and find your dream dress.",
    timing: "6-8 months before wedding",
    completed: false,
    icon: "selection",
  },
  {
    id: "3",
    title: "Measurements & Customization",
    description: "Get measured and choose fabrics, colors, and custom details.",
    timing: "5-6 months before wedding",
    completed: false,
    icon: "measurement",
  },
  {
    id: "4",
    title: "First Fitting",
    description: "Try on your dress with initial alterations for preview.",
    timing: "2-3 months before wedding",
    completed: false,
    icon: "first-fitting",
  },
  {
    id: "5",
    title: "Alterations Progress",
    description: "Our artisans work on perfecting your dress.",
    timing: "1-2 months before wedding",
    completed: false,
    icon: "alterations",
  },
  {
    id: "6",
    title: "Final Fitting",
    description: "Ensure your dress is perfectly fitted for the big day.",
    timing: "2 weeks before wedding",
    completed: false,
    icon: "final-fitting",
  },
  {
    id: "7",
    title: "Dress Pickup",
    description: "Take home your ready-to-wear dress or arrange delivery.",
    timing: "1 week before wedding",
    completed: false,
    icon: "pickup",
  },
  {
    id: "8",
    title: "Your Wedding Day",
    description: "Look stunning and feel confident on your special day!",
    timing: "The big day",
    completed: false,
    icon: "wedding",
  },
];

const iconMap = {
  consultation: Calendar,
  selection: Heart,
  measurement: Clock,
  "first-fitting": CheckCircle,
  alterations: CheckCircle,
  "final-fitting": CheckCircle,
  pickup: CheckCircle,
  wedding: Heart,
};

const WeddingTimeline = () => {
  const [weddingDate, setWeddingDate] = useState<string>("");
  const [daysUntil, setDaysUntil] = useState<number | null>(null);

  const calculateDays = () => {
    if (!weddingDate) return;
    const wedding = new Date(weddingDate);
    const today = new Date();
    const diff = Math.ceil((wedding.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    setDaysUntil(diff);
  };

  return (
    <Layout>
      {/* Hero */}
      <section className="pt-32 pb-16 px-6 bg-champagne">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl mx-auto text-center"
        >
          <p className="font-body text-[10px] tracking-[0.4em] uppercase text-muted-foreground mb-4">Your Journey</p>
          <h1 className="heading-display text-4xl md:text-5xl mb-6">Wedding Timeline</h1>
          <p className="font-body text-muted-foreground max-w-2xl mx-auto mb-8">
            Plan your path to the perfect dress. Use our timeline to stay on track for your special day.
          </p>
        </motion.div>
      </section>

      {/* Wedding Date Calculator */}
      <section className="py-12 bg-white border-b border-border">
        <div className="max-w-2xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center"
          >
            <h2 className="font-heading text-2xl mb-6">When is your wedding day?</h2>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <input
                type="date"
                value={weddingDate}
                onChange={(e) => setWeddingDate(e.target.value)}
                className="border border-border px-4 py-3 font-body text-sm focus:outline-none focus:border-gold"
              />
              <button onClick={calculateDays} className="btn-luxury">
                Calculate Timeline
              </button>
            </div>
            {daysUntil !== null && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="mt-8 p-6 bg-gold/10 border border-gold/30 rounded-lg"
              >
                <p className="font-body text-sm text-muted-foreground mb-2">Your special day is in</p>
                <p className="font-heading text-5xl text-gold">{daysUntil}</p>
                <p className="font-body text-sm text-muted-foreground mt-2">days</p>
              </motion.div>
            )}
          </motion.div>
        </div>
      </section>

      {/* Timeline */}
      <section className="section-padding">
        <div className="max-w-4xl mx-auto px-6">
          <div className="relative">
            {/* Vertical Line */}
            <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gold/30 md:left-1/2" />

            <div className="space-y-12">
              {timelineEvents.map((event, index) => {
                const Icon = iconMap[event.icon];
                const isLeft = index % 2 === 0;
                
                return (
                  <motion.div
                    key={event.id}
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                    className={`relative flex items-center ${isLeft ? "md:flex-row" : "md:flex-row-reverse"}`}
                  >
                    {/* Icon */}
                    <div className="absolute left-8 md:left-1/2 transform -translate-x-1/2 z-10">
                      <div className={`w-16 h-16 rounded-full flex items-center justify-center ${
                        event.completed ? "bg-green-500 text-white" : "bg-gold text-white"
                      }`}>
                        <Icon size={24} />
                      </div>
                    </div>

                    {/* Content */}
                    <div className={`ml-24 md:ml-0 md:w-[45%] ${isLeft ? "md:mr-auto md:pr-12" : "md:ml-auto md:pl-12"}`}>
                      <div className="bg-white p-6 border border-border hover:shadow-lg transition-shadow">
                        <p className="font-body text-[10px] tracking-[0.2em] uppercase text-gold mb-2">
                          {event.timing}
                        </p>
                        <h3 className="font-heading text-xl mb-2">{event.title}</h3>
                        <p className="font-body text-sm text-muted-foreground">
                          {event.description}
                        </p>
                        {event.completed && (
                          <div className="mt-4 flex items-center gap-2 text-green-600 text-sm">
                            <CheckCircle size={16} />
                            <span>Completed</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-champagne">
        <div className="max-w-2xl mx-auto px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="font-heading text-3xl mb-6">Ready to Start Your Journey?</h2>
            <p className="font-body text-muted-foreground mb-8">
              Book your private consultation and find your dream dress.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a href="/contact" className="btn-luxury">
                Book Consultation
                <ChevronRight size={18} className="ml-2 inline" />
              </a>
              <a href="/collection/bridal" className="btn-luxury-outline">
                View Collection
              </a>
            </div>
          </motion.div>
        </div>
      </section>
    </Layout>
  );
};

export default WeddingTimeline;