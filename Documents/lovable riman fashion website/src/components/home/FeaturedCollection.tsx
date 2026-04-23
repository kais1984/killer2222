import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { useProducts } from "@/contexts/ProductContext";
import ProductCard from "@/components/ProductCard";

const FeaturedCollection = () => {
  const { products } = useProducts();
  const featured = products.filter((p) => p.isFeatured).slice(0, 6);

  return (
    <section className="section-padding bg-champagne">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <p className="font-body text-[10px] tracking-[0.4em] uppercase text-muted-foreground mb-4">Curated Selection</p>
          <h2 className="heading-display text-4xl md:text-5xl italic">The Riman Edit</h2>
          <div className="divider-gold mt-6" />
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {featured.map((product, i) => (
            <motion.div
              key={product.id}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
            >
              <ProductCard product={product} />
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.5 }}
          className="text-center mt-12"
        >
          <Link to="/collection/bridal" className="btn-luxury-outline">
            View All Collections
          </Link>
        </motion.div>
      </div>
    </section>
  );
};

export default FeaturedCollection;
