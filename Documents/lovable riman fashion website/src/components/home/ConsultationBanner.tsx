import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import consultationBg from "@/assets/consultation-bg.jpg";

const ConsultationBanner = () => {
  return (
    <section className="relative overflow-hidden">
      <div className="absolute inset-0">
        <img
          src={consultationBg}
          alt="Riman Fashion Atelier"
          className="w-full h-full object-cover"
          loading="lazy"
        />
        <div className="absolute inset-0 bg-foreground/50" />
      </div>

      <div className="relative z-10 section-padding text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="max-w-2xl mx-auto"
        >
          <p className="font-body text-[10px] tracking-[0.4em] uppercase text-primary-foreground/70 mb-4">
            Private Appointments Available
          </p>
          <h2 className="font-heading text-4xl md:text-5xl text-primary-foreground font-light tracking-wide leading-tight mb-6">
            Experience the Riman
            <br />
            <span className="italic">Difference</span>
          </h2>
          <p className="font-body text-sm text-primary-foreground/70 leading-relaxed mb-8 max-w-lg mx-auto">
            Visit our atelier in Sharjah for a personalised consultation. Our expert stylists will guide you to discover your perfect gown in an intimate, luxurious setting.
          </p>
          <Link to="/contact" className="btn-luxury">
            Book Your Private Appointment
          </Link>
        </motion.div>
      </div>
    </section>
  );
};

export default ConsultationBanner;
