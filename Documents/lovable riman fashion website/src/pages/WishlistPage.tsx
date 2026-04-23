import { motion } from "framer-motion";
import { Heart, Trash2, Share2, Copy, Mail, Link as LinkIcon, Check } from "lucide-react";
import { useState } from "react";
import Layout from "@/components/Layout";
import ProductCard from "@/components/ProductCard";
import { useWishlist } from "@/contexts/WishlistContext";

const WishlistPage = () => {
    const { wishlist, clearWishlist, removeFromWishlist } = useWishlist();
    const [showShareModal, setShowShareModal] = useState(false);
    const [copied, setCopied] = useState(false);

    const generateShareLink = () => {
        const wishlistData = wishlist.map(p => p.id).join(',');
        return `${window.location.origin}/wishlist?items=${wishlistData}`;
    };

    const handleCopyLink = async () => {
        const link = generateShareLink();
        try {
            await navigator.clipboard.writeText(link);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch {
            // Fallback
            const textArea = document.createElement('textarea');
            textArea.value = link;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    const handleEmailShare = () => {
        const link = generateShareLink();
        const subject = encodeURIComponent('My Favorite Dresses from Riman Fashion');
        const body = encodeURIComponent(`Hi! These are my favorite dresses from Riman Fashion:\n\n${link}`);
        window.location.href = `mailto:?subject=${subject}&body=${body}`;
    };

    return (
        <Layout>
            <section className="pt-32 pb-16 px-6 bg-champagne">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    className="max-w-4xl mx-auto text-center"
                >
                    <p className="font-body text-[10px] tracking-[0.4em] uppercase text-muted-foreground mb-4">Wishlist</p>
                    <h1 className="heading-display text-4xl md:text-5xl mb-6">My Favorites</h1>
                    <div className="divider-gold mt-6 mb-4" />
                </motion.div>
            </section>

            <section className="section-padding">
                <div className="max-w-7xl mx-auto px-6">
                    {wishlist.length === 0 ? (
                        <div className="text-center py-20">
                            <Heart size={48} className="mx-auto text-muted-foreground/30 mb-6" />
                            <h2 className="font-heading text-2xl mb-4">Your wishlist is empty</h2>
                            <p className="font-body text-muted-foreground mb-8">
                                Save your favorite dresses to purchase or rent later
                            </p>
                            <a href="/collection/bridal" className="btn-luxury">
                                Browse Collection
                            </a>
                        </div>
                    ) : (
                        <>
                            <div className="flex justify-between items-center mb-8">
                                <p className="font-body text-sm text-muted-foreground">
                                    {wishlist.length} item{wishlist.length !== 1 ? "s" : ""} in your wishlist
                                </p>
                                <div className="flex gap-3">
                                    <button
                                        onClick={() => setShowShareModal(true)}
                                        className="flex items-center gap-2 text-sm text-muted-foreground hover:text-gold transition-colors"
                                    >
                                        <Share2 size={16} />
                                        Share
                                    </button>
                                    <button
                                        onClick={clearWishlist}
                                        className="flex items-center gap-2 text-sm text-muted-foreground hover:text-red-500 transition-colors"
                                    >
                                        <Trash2 size={16} />
                                        Clear All
                                    </button>
                                </div>
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
                                {wishlist.map((product, i) => (
                                    <motion.div
                                        key={product.id}
                                        initial={{ opacity: 0, y: 30 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ duration: 0.5, delay: i * 0.1 }}
                                        className="relative"
                                    >
                                        <button
                                            onClick={() => removeFromWishlist(product.id)}
                                            className="absolute top-4 right-4 z-10 w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-md hover:bg-red-50 hover:text-red-500 transition-colors"
                                        >
                                            <Heart size={18} className="fill-current" />
                                        </button>
                                        <ProductCard product={product} />
                                    </motion.div>
                                ))}
                            </div>
                        </>
                    )}
                </div>

                {/* Share Modal */}
                {showShareModal && (
                    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="bg-white rounded-2xl p-6 max-w-md w-full"
                        >
                            <h3 className="font-heading text-xl mb-4">Share Your Wishlist</h3>
                            <p className="font-body text-sm text-muted-foreground mb-6">
                                Share your favorite dresses with friends and family
                            </p>
                            
                            <div className="space-y-3">
                                <button
                                    onClick={handleCopyLink}
                                    className="w-full flex items-center justify-center gap-2 py-3 border border-border rounded-lg hover:border-gold hover:bg-gold/5 transition-colors"
                                >
                                    {copied ? <Check size={18} className="text-green-500" /> : <Copy size={18} />}
                                    {copied ? "Link Copied!" : "Copy Link"}
                                </button>
                                <button
                                    onClick={handleEmailShare}
                                    className="w-full flex items-center justify-center gap-2 py-3 border border-border rounded-lg hover:border-gold hover:bg-gold/5 transition-colors"
                                >
                                    <Mail size={18} />
                                    Share via Email
                                </button>
                            </div>
                            
                            <button
                                onClick={() => setShowShareModal(false)}
                                className="w-full mt-4 py-2 text-sm text-muted-foreground hover:text-foreground"
                            >
                                Cancel
                            </button>
                        </motion.div>
                    </div>
                )}
            </section>
        </Layout>
    );
};

export default WishlistPage;
