import { Link } from "react-router-dom";
import { Instagram, MapPin, Phone, Mail, Navigation } from "lucide-react";
import logo from "@/assets/logo.png";

const TikTokIcon = ({ size = 20, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" className={className}>
    <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z" />
  </svg>
);

const WhatsAppIcon = ({ size = 20, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" className={className}>
    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51a12.8 12.8 0 0 0-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347M11.994 22A10 10 0 0 1 2 12A10 10 0 0 1 12 2a10 10 0 0 1 10 10 10 10 0 0 1-10 10z" />
  </svg>
);

const Footer = () => {
  return (
    <footer className="bg-foreground text-primary-foreground">
      <div className="section-padding">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-5 gap-8">
          {/* Brand */}
          <div className="md:col-span-1">
            <img src={logo} alt="Riman Fashion" className="h-14 md:h-16 w-auto object-contain mb-4 drop-shadow-sm" />
            <p className="font-body text-xs leading-relaxed opacity-70 tracking-wide mb-4">
              Crafting exceptional bridal and evening wear for the modern woman.
            </p>
            <div className="flex gap-3">
              <a href="https://www.instagram.com/rimanfashion/" target="_blank" rel="noopener noreferrer" className="opacity-70 hover:opacity-100 transition-opacity" aria-label="Instagram">
                <Instagram size={18} />
              </a>
              <a href="https://wa.me/971553730792" target="_blank" rel="noopener noreferrer" className="opacity-70 hover:opacity-100 transition-opacity" aria-label="WhatsApp">
                <WhatsAppIcon size={18} />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="font-body text-[10px] tracking-[0.25em] uppercase mb-5 opacity-70">Explore</h4>
            <div className="flex flex-col gap-2.5">
              <Link to="/collection/bridal" className="font-body text-xs opacity-70 hover:opacity-100 transition-opacity tracking-wide">Bridal Gowns</Link>
              <Link to="/collection/evening" className="font-body text-xs opacity-70 hover:opacity-100 transition-opacity tracking-wide">Evening Dresses</Link>
              <Link to="/collection/rentals" className="font-body text-xs opacity-70 hover:opacity-100 transition-opacity tracking-wide">Rentals</Link>
              <Link to="/about" className="font-body text-xs opacity-70 hover:opacity-100 transition-opacity tracking-wide">Our Story</Link>
              <Link to="/contact" className="font-body text-xs opacity-70 hover:opacity-100 transition-opacity tracking-wide">Contact</Link>
            </div>
          </div>

          {/* Services */}
          <div>
            <h4 className="font-body text-[10px] tracking-[0.25em] uppercase mb-5 opacity-70">Services</h4>
            <div className="flex flex-col gap-2.5">
              <Link to="/alterations" className="font-body text-xs opacity-70 hover:opacity-100 transition-opacity tracking-wide">Alterations</Link>
              <Link to="/faq" className="font-body text-xs opacity-70 hover:opacity-100 transition-opacity tracking-wide">FAQ</Link>
              <Link to="/privacy" className="font-body text-xs opacity-70 hover:opacity-100 transition-opacity tracking-wide">Privacy Policy</Link>
              <Link to="/terms" className="font-body text-xs opacity-70 hover:opacity-100 transition-opacity tracking-wide">Terms & Conditions</Link>
            </div>
          </div>

          {/* Contact Info */}
          <div>
            <h4 className="font-body text-[10px] tracking-[0.25em] uppercase mb-5 opacity-70">Visit Us</h4>
            <div className="flex flex-col gap-3 text-xs opacity-70">
              <div className="flex items-start gap-2">
                <MapPin size={12} className="mt-0.5 shrink-0 text-gold" />
                <span>S130 - Al Jazzat<br />Sharjah, UAE</span>
              </div>
              <div className="flex items-center gap-2">
                <Phone size={12} className="shrink-0 text-gold" />
                <span>055 373 0792</span>
              </div>
              <div className="flex items-center gap-2">
                <Mail size={12} className="shrink-0 text-gold" />
                <span>info@rimanfashion.com</span>
              </div>
            </div>
          </div>

          {/* Map */}
          <div className="md:col-span-1">
            <h4 className="font-body text-[10px] tracking-[0.25em] uppercase mb-5 opacity-70">Get Directions</h4>
            <div className="rounded-lg overflow-hidden h-32 border border-primary-foreground/20">
              <iframe
                src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3603.543284478935!2d55.43109931547756!3d25.36555683471548!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3e5f59a7ab853595%3A0x96c3beacbace225a!2sRiman%20Fashion!5e0!3m2!1sen!2sae!4v1678456789000!5m2!1sen!2sae"
                width="100%"
                height="100%"
                style={{ border: 0 }}
                allowFullScreen
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
                title="Riman Fashion Location"
              />
            </div>
            <a
              href="https://www.google.com/maps/dir/?api=1&destination=Riman+Fashion+Sharjah"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 mt-3 font-body text-[10px] opacity-70 hover:opacity-100 transition-opacity text-gold hover:text-gold-light"
            >
              <Navigation size={12} />
              Get Directions
            </a>
          </div>
        </div>

        <div className="max-w-7xl mx-auto mt-10 pt-6 border-t border-primary-foreground/10 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="font-body text-[10px] opacity-50 tracking-wider">
            © 2026 Riman Fashion. All rights reserved.
          </p>
          <Link to="/contact" className="btn-luxury-outline border-primary-foreground/30 text-primary-foreground/80 hover:bg-primary-foreground/10 hover:text-primary-foreground text-[10px]">
            Book Your Private Viewing
          </Link>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
