import { useState, useEffect } from "react";
import { X } from "lucide-react";

const CookieBanner = () => {
  const [accepted, setAccepted] = useState(() => {
    return localStorage.getItem("riman_cookies") === "true";
  });
  const [dismissed, setDismissed] = useState(() => {
    return localStorage.getItem("riman_cookies-dismissed") === "true";
  });
  const [isVisible, setIsVisible] = useState(!accepted && !dismissed);

  useEffect(() => {
    if (!accepted) {
      setIsVisible(true);
    }
  }, [accepted]);

  const handleAccept = () => {
    localStorage.setItem("riman_cookies", "true");
    localStorage.removeItem("riman_cookies-dismissed");
    setAccepted(true);
    setDismissed(false);
    setIsVisible(false);
  };

  if (!isVisible) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t shadow-lg z-[100] md:bottom-4 md:left-4 md:right-auto md:max-w-sm md:rounded-lg">
      <div className="p-4 md:p-5">
        <button
          onClick={() => {
            localStorage.setItem("riman_cookies-dismissed", "true");
            setDismissed(true);
            setIsVisible(false);
          }}
          className="absolute top-2 right-2 text-muted-foreground hover:text-foreground"
          aria-label="Close"
        >
          <X size={18} />
        </button>

        <h4 className="font-heading text-sm mb-2 pr-6">We Value Your Privacy</h4>
        <p className="text-xs text-muted-foreground mb-4 leading-relaxed">
          We use cookies to enhance your browsing experience, analyze site traffic, and personalize content. 
          By continuing to use this site, you consent to our use of cookies.
        </p>

        <div className="flex gap-2">
        <button
          onClick={() => {
            localStorage.setItem("riman_cookies-dismissed", "true");
            setDismissed(true);
            setIsVisible(false);
          }}
          className="absolute top-2 right-2 text-muted-foreground hover:text-foreground"
          aria-label="Close"
        >
            Accept
          </button>
          <a
            href="/privacy"
            className="btn-luxury-outline text-xs py-2 px-4 flex-1 text-center"
          >
            Learn More
          </a>
        </div>
      </div>
    </div>
  );
};

export default CookieBanner;