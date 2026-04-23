import { motion } from "framer-motion";
import Layout from "@/components/Layout";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";

const blogPosts = [
    {
        id: 1,
        title: "Choosing the Perfect Bridal Gown for Your Body Type",
        excerpt: "Finding the perfect wedding dress is about celebrating your unique silhouette. Learn which styles flatter different body types.",
        video: "/videos/bridal-guide-1.mp4",
        category: "Bridal Tips",
        readTime: "5 min read"
    },
    {
        id: 2,
        title: "The Ultimate Bridal Fitting Guide",
        excerpt: "Everything you need to know about wedding dress fittings, alterations, and achieving the perfect fit for your big day.",
        video: "/videos/bridal-guide-2.mp4",
        category: "Fitting Guide",
        readTime: "7 min read"
    },
    {
        id: 3,
        title: "Bridal Accessories: The Perfect Finishing Touches",
        excerpt: "From veils to jewelry, discover how to choose the right accessories to complement your wedding gown.",
        category: "Accessories",
        readTime: "4 min read"
    },
    {
        id: 4,
        title: "Understanding Bridal Gown Fabrics",
        excerpt: "A comprehensive guide to wedding dress fabrics including lace, tulle, satin, and more.",
        category: "Fabric Guide",
        readTime: "6 min read"
    },
    {
        id: 5,
        title: "Caring for Your Wedding Dress",
        excerpt: "Tips on preserving and storing your wedding dress so it remains perfect for years to come.",
        category: "Care Tips",
        readTime: "3 min read"
    },
    {
        id: 6,
        title: "Destination Wedding Dress Guide",
        excerpt: "Everything you need to consider when choosing a wedding dress for a beach or destination wedding.",
        category: "Destination Weddings",
        readTime: "5 min read"
    }
];

// Newsletter Form Component
const NewsletterForm = () => {
    const [email, setEmail] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);
    const { toast } = useToast();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);

        // Save to localStorage (until backend is connected)
        localStorage.setItem("riman_newsletter", email);

        // TODO: When Supabase is connected, use:
        // const { error } = await supabase
        //     .from('newsletter_subscribers')
        //     .insert([{ email, created_at: new Date() }]);

        toast({
            title: "Welcome to Riman Fashion! 🎉",
            description: "You've been subscribed. Check your email for 10% off code!",
        });

        setEmail("");
        setIsSubmitting(false);
    };

    return (
        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
            <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                className="flex-1 px-4 py-3 bg-white/10 border border-white/20 text-white placeholder:text-gray-500 focus:outline-none focus:border-gold"
                required
            />
            <button
                type="submit"
                className="btn-luxury whitespace-nowrap disabled:opacity-50"
                disabled={isSubmitting}
            >
                {isSubmitting ? "Subscribing..." : "Subscribe"}
            </button>
        </form>
    );
};

const BlogPage = () => {
    return (
        <Layout>
            {/* Hero Section */}
            <section className="pt-32 pb-16 px-6 text-center bg-champagne">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                >
                    <p className="font-body text-[10px] tracking-[0.4em] uppercase text-muted-foreground mb-4">Bridal Guide</p>
                    <h1 className="heading-display text-4xl md:text-6xl mb-6">Your Complete Wedding Resource</h1>
                    <div className="divider-gold mt-6 mb-4" />
                    <p className="font-body text-muted-foreground max-w-2xl mx-auto">
                        Expert advice, styling tips, and everything you need to know about finding your perfect wedding dress.
                    </p>
                </motion.div>
            </section>

            {/* Featured Video */}
            <section className="py-12 bg-black">
                <div className="max-w-6xl mx-auto px-6">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8 }}
                    >
                        <video
                            autoPlay
                            muted
                            loop
                            playsInline
                            className="w-full h-[600px] object-cover rounded-lg"
                        >
                            <source src="/videos/bridal-guide-1.mp4" type="video/mp4" />
                        </video>
                        <div className="mt-8 text-center">
                            <span className="inline-block px-3 py-1 bg-gold/20 text-gold text-xs tracking-widest uppercase mb-4">
                                Featured
                            </span>
                            <h2 className="font-heading text-3xl text-white mb-4">
                                Choosing the Perfect Bridal Gown for Your Body Type
                            </h2>
                            <p className="font-body text-gray-400 max-w-2xl mx-auto">
                                Finding the perfect wedding dress is about celebrating your unique silhouette.
                                Watch ourStyle experts explain which styles flatter different body types and
                                help you find the gown of your dreams.
                            </p>
                        </div>
                    </motion.div>
                </div>
            </section>

            {/* Blog Grid */}
            <section className="section-padding">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {blogPosts.map((post, index) => (
                            <motion.article
                                key={post.id}
                                initial={{ opacity: 0, y: 30 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ duration: 0.5, delay: index * 0.1 }}
                                className="bg-white border border-border overflow-hidden hover:shadow-lg transition-shadow"
                            >
                                {/* Video thumbnail or placeholder */}
                                <div className="relative aspect-[16/9] bg-gray-100 overflow-hidden">
                                    {post.video ? (
                                        <video
                                            autoPlay
                                            muted
                                            loop
                                            playsInline
                                            className="w-full h-full object-cover"
                                        >
                                            <source src={post.video} type="video/mp4" />
                                        </video>
                                    ) : (
                                        <div className="w-full h-full flex items-center justify-center bg-champagne">
                                            <span className="font-heading text-4xl text-gold/30">R</span>
                                        </div>
                                    )}
                                    <div className="absolute top-4 left-4">
                                        <span className="px-2 py-1 bg-white/90 text-xs tracking-widest uppercase">
                                            {post.category}
                                        </span>
                                    </div>
                                </div>

                                <div className="p-6">
                                    <h3 className="font-heading text-xl mb-3 hover:text-gold transition-colors">
                                        {post.title}
                                    </h3>
                                    <p className="font-body text-sm text-muted-foreground mb-4">
                                        {post.excerpt}
                                    </p>
                                    <div className="flex items-center justify-between">
                                        <span className="font-body text-xs text-muted-foreground">
                                            {post.readTime}
                                        </span>
                                        <button className="font-body text-xs tracking-widest uppercase text-gold hover:text-foreground transition-colors">
                                            Read More →
                                        </button>
                                    </div>
                                </div>
                            </motion.article>
                        ))}
                    </div>
                </div>
            </section>

            {/* Newsletter Section */}
            <section className="py-20 bg-black text-white">
                <div className="max-w-2xl mx-auto px-6 text-center">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8 }}
                    >
                        <h2 className="font-heading text-3xl mb-4">Stay Inspired</h2>
                        <p className="font-body text-gray-400 mb-8">
                            Subscribe to our newsletter for exclusive styling tips, new collection previews, and bridal inspiration.
                        </p>
                        <NewsletterForm />
                    </motion.div>
                </div>
            </section>

            {/* Consultation CTA */}
            <section className="section-padding bg-champagne">
                <div className="max-w-4xl mx-auto text-center">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8 }}
                    >
                        <h2 className="font-heading text-3xl mb-6">Need Personal Guidance?</h2>
                        <p className="font-body text-muted-foreground mb-8">
                            Our experienced stylists are here to help you find the perfect dress.
                            Book a private consultation at our Sharjah atelier.
                        </p>
                        <a href="/contact" className="btn-luxury">
                            Book a Consultation
                        </a>
                    </motion.div>
                </div>
            </section>
        </Layout>
    );
};

export default BlogPage;
