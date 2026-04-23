import { motion } from "framer-motion";
import { Star } from "lucide-react";
import { testimonials } from "@/data/products";

const TestimonialsSection = () => {
  return (
    <section className="section-padding">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <p className="font-body text-[10px] tracking-[0.4em] uppercase text-muted-foreground mb-4">Testimonials</p>
          <h2 className="heading-display text-4xl md:text-5xl italic">Client Love</h2>
          <div className="divider-gold mt-6" />
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
          {testimonials.map((t, i) => (
            <motion.div
              key={t.id}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: i * 0.15 }}
              className="text-center"
            >
              <div className="flex justify-center gap-1 mb-6">
                {Array.from({ length: t.rating }).map((_, j) => (
                  <Star key={j} size={14} className="fill-gold text-gold" />
                ))}
              </div>
              <p className="font-heading text-lg italic leading-relaxed mb-6 text-foreground/80">
                "{t.content}"
              </p>
              <div className="divider-gold mb-4" />
              <p className="font-body text-xs tracking-[0.15em] uppercase">{t.authorName}</p>
              <p className="font-body text-[10px] text-muted-foreground mt-1">{t.authorRole}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default TestimonialsSection;
