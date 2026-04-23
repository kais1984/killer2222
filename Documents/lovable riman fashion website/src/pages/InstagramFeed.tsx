import { motion } from "framer-motion";
import { Instagram, Facebook, Mail, MapPin, Phone, Clock } from "lucide-react";
import Layout from "@/components/Layout";

const instagramPosts = [
  { id: 1, imageUrl: "/images/instagram/post-1.jpg", likes: 234 },
  { id: 2, imageUrl: "/images/instagram/post-2.jpg", likes: 189 },
  { id: 3, imageUrl: "/images/instagram/post-3.jpg", likes: 312 },
  { id: 4, imageUrl: "/images/instagram/post-4.jpg", likes: 156 },
  { id: 5, imageUrl: "/images/instagram/post-5.jpg", likes: 278 },
  { id: 6, imageUrl: "/images/instagram/post-6.jpg", likes: 201 },
];

const InstagramFeed = () => {
  return (
    <Layout>
      <section className="pt-32 pb-16 px-6 bg-champagne">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl mx-auto text-center"
        >
          <Instagram className="mx-auto text-gold mb-4" size={32} />
          <p className="font-body text-[10px] tracking-[0.4em] uppercase text-muted-foreground mb-4">Follow Us</p>
          <h1 className="heading-display text-4xl md:text-5xl mb-6">Instagram Feed</h1>
          <p className="font-body text-muted-foreground max-w-2xl mx-auto mb-8">
            Get inspired by our latest designs and real bride moments
          </p>
          <a
            href="https://instagram.com/rimanfashion"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-luxury"
          >
            <Instagram size={18} className="mr-2 inline" />
            Follow @rimanfashion
          </a>
        </motion.div>
      </section>

      <section className="section-padding">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {instagramPosts.map((post, index) => (
              <motion.a
                key={post.id}
                href="https://instagram.com/rimanfashion"
                target="_blank"
                rel="noopener noreferrer"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="group relative aspect-square bg-champagne rounded-lg overflow-hidden cursor-pointer"
              >
                <div className="absolute inset-0 flex items-center justify-center">
                  <Instagram size={32} className="text-gold/30" />
                </div>
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/50 transition-colors flex items-center justify-center">
                  <span className="text-white opacity-0 group-hover:opacity-100 font-body text-sm flex items-center gap-2">
                    <Instagram size={16} /> @rimanfashion
                  </span>
                </div>
              </motion.a>
            ))}
          </div>
        </div>
      </section>

      {/* Contact & Location */}
      <section className="py-20 bg-black text-white">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid md:grid-cols-3 gap-12 text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              <MapPin size={32} className="mx-auto text-gold mb-4" />
              <h3 className="font-heading text-lg mb-2">Visit Our Atelier</h3>
              <p className="font-body text-sm text-white/70">
                Sharjah, United Arab Emirates<br />
                Open by appointment only
              </p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
            >
              <Phone size={32} className="mx-auto text-gold mb-4" />
              <h3 className="font-heading text-lg mb-2">Contact Us</h3>
              <p className="font-body text-sm text-white/70">
                +971 55 373 0792<br />
                info@rimanfashion.com
              </p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
            >
              <Clock size={32} className="mx-auto text-gold mb-4" />
              <h3 className="font-heading text-lg mb-2">Opening Hours</h3>
              <p className="font-body text-sm text-white/70">
                Mon - Sat: 10AM - 8PM<br />
                Sunday: By appointment
              </p>
            </motion.div>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default InstagramFeed;