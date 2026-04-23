import { useLanguage } from "@/contexts/LanguageContext";
import { Globe } from "lucide-react";

const LanguageSwitcher = () => {
  const { language, setLanguage } = useLanguage();

  return (
    <button
      onClick={() => setLanguage(language === "en" ? "ar" : "en")}
      className="flex items-center gap-2 px-3 py-1.5 border border-border rounded-full hover:border-gold transition-colors"
      aria-label="Switch language"
    >
      <Globe size={14} />
      <span className="text-xs font-body uppercase">{language}</span>
    </button>
  );
};

export default LanguageSwitcher;