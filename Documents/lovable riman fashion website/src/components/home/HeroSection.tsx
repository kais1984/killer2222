import { motion, useMotionValue, useTransform, useSpring } from "framer-motion";
import { Link } from "react-router-dom";
import logo from "@/assets/logo.png";

const HeroSection = () => {
  // Mouse position values
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  // Smooth spring animation for mouse movement
  const springConfig = { damping: 20, stiffness: 300 };
  const smoothX = useSpring(mouseX, springConfig);
  const smoothY = useSpring(mouseY, springConfig);

  // Transform mouse position to parallax offsets
  const x1 = useTransform(smoothX, [-500, 500], [30, -30]);
  const y1 = useTransform(smoothY, [-500, 500], [20, -20]);
  const x2 = useTransform(smoothX, [-500, 500], [-20, 20]);
  const y2 = useTransform(smoothY, [-500, 500], [-15, 15]);
  const x3 = useTransform(smoothX, [-500, 500], [15, -15]);
  const y3 = useTransform(smoothY, [-500, 500], [10, -10]);
  const x4 = useTransform(smoothX, [-500, 500], [-10, 10]);
  const y4 = useTransform(smoothY, [-500, 500], [-20, 20]);
  const x5 = useTransform(smoothX, [-500, 500], [25, -25]);
  const y5 = useTransform(smoothY, [-500, 500], [15, -15]);

  const handleMouseMove = (e: React.MouseEvent) => {
    const { left, top, width, height } = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - left - width / 2;
    const y = e.clientY - top - height / 2;
    mouseX.set(x);
    mouseY.set(y);
  };

  const handleMouseLeave = () => {
    mouseX.set(0);
    mouseY.set(0);
  };

  return (
    <section
      className="relative h-screen overflow-hidden bg-foreground cursor-default"
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      {/* Background - Your Boutique Showroom */}
      <div className="absolute inset-0">
        <motion.div
          className="absolute inset-0 overflow-hidden"
          style={{ x: x1, y: y1 }}
        >
          <img
            src="/images/boutique-1.jpeg"
            alt="Riman Fashion Boutique"
            className="w-full h-full object-cover scale-110"
          />
        </motion.div>
        <div className="absolute inset-0 bg-gradient-to-b from-foreground/60 via-foreground/30 to-foreground/70" />
      </div>

      {/* Floating Product Cards with Parallax - Simplified */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="relative w-full max-w-6xl h-[80vh]">
          {/* Center large card - main feature */}
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 1, delay: 0.5 }}
            className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[40%] h-[60%] rounded-xl overflow-hidden shadow-2xl border-2 border-primary-foreground/20 pointer-events-auto"
            style={{ x: x4, y: y4 }}
          >
            <img src="/images/boutique-2.jpeg" alt="" className="w-full h-full object-cover" />
            <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent" />
          </motion.div>

          {/* Small accent card - bottom left */}
          <motion.div
            initial={{ opacity: 0, rotate: -5, scale: 0.7 }}
            animate={{ opacity: 1, rotate: -5, scale: 1 }}
            transition={{ duration: 1, delay: 0.65 }}
            className="absolute left-10 bottom-20 w-[20%] h-[28%] rounded-xl overflow-hidden shadow-2xl border border-primary-foreground/30 pointer-events-auto"
            style={{ x: x5, y: y5 }}
          >
            <img src="/images/boutique-3.jpeg" alt="" className="w-full h-full object-cover" />
          </motion.div>

          {/* Small accent card - bottom right */}
          <motion.div
            initial={{ opacity: 0, rotate: 8, scale: 0.7 }}
            animate={{ opacity: 1, rotate: 8, scale: 1 }}
            transition={{ duration: 1, delay: 0.8 }}
            className="absolute right-10 bottom-24 w-[18%] h-[26%] rounded-xl overflow-hidden shadow-2xl border border-primary-foreground/30 pointer-events-auto"
            style={{ x: useTransform(smoothX, [-500, 500], [-15, 15]), y: useTransform(smoothY, [-500, 500], [20, -20]) }}
          >
            <img src="/images/boutique-4.jpeg" alt="" className="w-full h-full object-cover" />
          </motion.div>
        </div>
      </div>

      {/* Content Overlay */}
      <div className="relative z-20 h-full flex flex-col items-center justify-end pb-20 md:pb-24 text-center px-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8 }}
          className="mb-4"
        >
          <img src={logo} alt="Riman Fashion" className="h-20 md:h-28 lg:h-32 w-auto object-contain drop-shadow-xl" />
        </motion.div>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="font-body text-[10px] md:text-xs tracking-[0.4em] uppercase text-primary-foreground/90 mb-4"
        >
          Sharjah's Premier Bridal Atelier
        </motion.p>

        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.5 }}
          className="font-heading text-4xl md:text-6xl lg:text-7xl text-primary-foreground font-light tracking-wide leading-tight drop-shadow-lg"
        >
          Your Dream Dress
          <br />
          <span className="italic">Awaits</span>
        </motion.h1>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          className="mt-3 mb-6"
        >
          <div className="w-12 h-[1px] bg-gold-light mx-auto" />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 1 }}
          className="flex flex-col sm:flex-row gap-3"
        >
          <Link to="/collection/bridal" className="btn-luxury">
            Explore Collection
          </Link>
          <Link to="/contact" className="btn-luxury-outline border-primary-foreground/50 text-primary-foreground hover:bg-primary-foreground/15">
            Book Private Viewing
          </Link>
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5, duration: 1 }}
        className="absolute bottom-6 left-1/2 -translate-x-1/2 z-20"
      >
        <motion.div
          animate={{ y: [0, 8, 0] }}
          transition={{ repeat: Infinity, duration: 2 }}
          className="w-[1px] h-8 bg-primary-foreground/50"
        />
      </motion.div>
    </section>
  );
};

export default HeroSection;
