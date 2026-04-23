import { motion } from "framer-motion";
import { Share2, Instagram, Facebook, Twitter, Link as LinkIcon, Check } from "lucide-react";
import { useState } from "react";

interface SocialShareProps {
  productName: string;
  productUrl?: string;
}

const SocialShare = ({ productName, productUrl }: SocialShareProps) => {
  const [copied, setCopied] = useState(false);
  const url = productUrl || window.location.href;

  const shareLinks = {
    facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
    twitter: `https://twitter.com/intent/tweet?text=${encodeURIComponent(`Check out this beautiful ${productName} from Riman Fashion!`)}&url=${encodeURIComponent(url)}`,
    instagram: "https://instagram.com/rimanfashion",
  };

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback
      const textArea = document.createElement('textarea');
      textArea.value = url;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="flex items-center gap-3">
      <span className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground">
        Share
      </span>
      <div className="flex gap-2">
        <a
          href={shareLinks.facebook}
          target="_blank"
          rel="noopener noreferrer"
          className="w-9 h-9 border border-border rounded-full flex items-center justify-center hover:border-gold hover:text-gold transition-colors"
          aria-label="Share on Facebook"
        >
          <Facebook size={16} />
        </a>
        <a
          href={shareLinks.twitter}
          target="_blank"
          rel="noopener noreferrer"
          className="w-9 h-9 border border-border rounded-full flex items-center justify-center hover:border-gold hover:text-gold transition-colors"
          aria-label="Share on Twitter"
        >
          <Twitter size={16} />
        </a>
        <a
          href={shareLinks.instagram}
          target="_blank"
          rel="noopener noreferrer"
          className="w-9 h-9 border border-border rounded-full flex items-center justify-center hover:border-gold hover:text-gold transition-colors"
          aria-label="Follow on Instagram"
        >
          <Instagram size={16} />
        </a>
        <button
          onClick={handleCopyLink}
          className="w-9 h-9 border border-border rounded-full flex items-center justify-center hover:border-gold hover:text-gold transition-colors"
          aria-label="Copy link"
        >
          {copied ? <Check size={16} className="text-green-500" /> : <LinkIcon size={16} />}
        </button>
      </div>
    </div>
  );
};

export default SocialShare;