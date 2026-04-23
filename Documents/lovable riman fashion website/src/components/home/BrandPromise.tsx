import { motion } from "framer-motion";
import { Gem, Scissors, Sparkles, Award, Heart, Clock } from "lucide-react";

const promises = [
  {
    icon: Gem,
    title: "European Fabrics",
    description: "Sourced from the finest mills in Italy and France, every fabric is selected for its exceptional quality and luminous beauty. From luxurious silk satins to delicate French lace, we spare no effort in sourcing materials that exude elegance.",
  },
  {
    icon: Scissors,
    title: "Handcrafted Excellence",
    description: "Each gown is meticulously crafted by master artisans, with hundreds of hours dedicated to hand-embroidery and beading. Our skilled craftsmen bring decades of expertise to every stitch, ensuring impeccable quality.",
  },
  {
    icon: Sparkles,
    title: "Exclusive Designs",
    description: "Our creations are never repeated. Every Riman gown is as unique as the woman who wears it — a true one-of-a-kind masterpiece designed exclusively for you.",
  },
];

const stats = [
  { number: "15+", label: "Years of Excellence", icon: Award },
  { number: "5000+", label: "Happy Brides", icon: Heart },
  { number: "48h", label: "Quick Consultations", icon: Clock },
];

const BrandPromise = () => {
  return (
    <section className="section-padding bg-ivory">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <p className="font-body text-[10px] tracking-[0.4em] uppercase text-muted-foreground mb-4">The Riman Promise</p>
          <h2 className="heading-display text-4xl md:text-5xl">A Legacy of Excellence</h2>
          <div className="divider-gold mt-6" />
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-12 md:gap-16">
          {promises.map((item, i) => (
            <motion.div
              key={item.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: i * 0.2 }}
              className="text-center"
            >
              <div className="w-16 h-16 mx-auto mb-6 rounded-full border border-gold/30 flex items-center justify-center">
                <item.icon size={24} className="text-gold" />
              </div>
              <h3 className="font-heading text-xl md:text-2xl mb-3 tracking-wide">{item.title}</h3>
              <p className="font-body text-xs leading-relaxed text-muted-foreground">
                {item.description}
              </p>
            </motion.div>
          ))}
        </div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="grid grid-cols-3 gap-8 mt-20 pt-16 border-t border-gold/20"
        >
          {stats.map((stat) => (
            <div key={stat.label} className="text-center">
              <stat.icon size={24} className="text-gold mx-auto mb-3" />
              <div className="font-heading text-3xl md:text-4xl text-gold mb-2">{stat.number}</div>
              <p className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground">{stat.label}</p>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default BrandPromise;
