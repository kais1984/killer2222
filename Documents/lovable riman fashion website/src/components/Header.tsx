import { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Search, User, Menu, X, Heart } from "lucide-react";
import logo from "@/assets/logo.png";
import { CartDrawer } from "./CartDrawer";
import LanguageSwitcher from "./LanguageSwitcher";

const navLinks = [
  { label: "Bridal", path: "/collection/bridal" },
  { label: "Evening", path: "/collection/evening" },
  { label: "Rentals", path: "/collection/rental" },
  { label: "Timeline", path: "/timeline" },
  { label: "Style Quiz", path: "/style-quiz" },
  { label: "Our Story", path: "/about" },
  { label: "Contact", path: "/contact" },
];

const Header = () => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const isHome = location.pathname === "/";

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => setMobileOpen(false), [location]);

  const headerBg = scrolled || !isHome || mobileOpen
    ? "bg-background/95 backdrop-blur-md shadow-sm"
    : "bg-transparent";

  const textColor = scrolled || !isHome
    ? "text-foreground"
    : "text-primary-foreground";

  return (
    <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${headerBg}`}>
      <div className="flex items-center justify-between px-6 md:px-12 py-4">
        {/* Mobile menu button */}
        <button
          className={`md:hidden ${scrolled || !isHome ? 'text-foreground' : 'text-primary-foreground'}`}
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Toggle menu"
          aria-expanded={mobileOpen}
        >
          {mobileOpen ? <X size={24} /> : <Menu size={24} />}
        </button>

        {/* Logo */}
        <Link to="/" className="flex items-center">
          <img src={logo} alt="Riman Fashion" className="h-16 md:h-20 lg:h-24 w-auto object-contain drop-shadow-sm" />
        </Link>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              className={`font-body text-[11px] tracking-[0.2em] uppercase transition-colors duration-300 hover:text-gold ${scrolled || !isHome ? "text-foreground" : "text-primary-foreground"
                }`}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Icons */}
        <div className={`flex items-center gap-5 ${scrolled || !isHome ? "text-foreground" : "text-primary-foreground"}`}>
          <LanguageSwitcher />
          <button aria-label="Search" className="hover:text-gold transition-colors" onClick={() => navigate('/search')}><Search size={18} /></button>
          <Link to="/wishlist" aria-label="Wishlist" className="hover:text-gold transition-colors"><Heart size={18} /></Link>
          <Link to="/profile" aria-label="Account" className="hover:text-gold transition-colors"><User size={18} /></Link>
          <CartDrawer />
        </div>
      </div>

      {/* Mobile Nav */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.nav
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="md:hidden overflow-hidden bg-background"
          >
            <div className="flex flex-col items-center gap-6 py-8">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  className="font-body text-xs tracking-[0.2em] uppercase text-foreground hover:text-gold transition-colors"
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </motion.nav>
        )}
      </AnimatePresence>
    </header>
  );
};

export default Header;
