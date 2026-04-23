import { useParams } from "react-router-dom";
import { useEffect } from "react";
import { motion } from "framer-motion";
import Layout from "@/components/Layout";
import ProductCard from "@/components/ProductCard";
import { useProducts } from "@/contexts/ProductContext";
import type { Product } from "@/data/products";

const categoryMap: Record<string, { title: string; subtitle: string; filter: (p: Product) => boolean }> = {
  bridal: {
    title: "Bridal Gowns",
    subtitle: "Discover our exquisite collection of handcrafted wedding dresses",
    filter: (p) => p.category === "Bridal Gown",
  },
  evening: {
    title: "Evening & Party Dresses",
    subtitle: "Stunning gowns for every unforgettable occasion",
    filter: (p) => p.category === "Evening Dress" || p.category === "Party Dress",
  },
  rentals: {
    title: "Dress Rentals",
    subtitle: "Experience luxury with our curated rental collection",
    filter: (p) => p.productType === "rent" || p.productType === "both",
  },
  sales: {
    title: "Dresses for Sale",
    subtitle: "Own your dream dress from our exclusive collection",
    filter: (p) => p.productType === "sale" || p.productType === "both",
  },
  rental: {
    title: "Dress Rentals",
    subtitle: "Experience luxury with our curated rental collection",
    filter: (p) => p.productType === "rent" || p.productType === "both",
  },
  all: {
    title: "All Dresses",
    subtitle: "Browse our complete collection",
    filter: () => true,
  },
};

const CollectionPage = () => {
  const { category } = useParams<{ category: string }>();
  const { products } = useProducts();
  
  // Scroll to top when page loads
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [category]);
  
  const cat = categoryMap[category || "all"] || categoryMap.all;
  const filtered = products.filter(cat.filter);

  return (
    <Layout>
      {/* Hero Banner */}
      <section className="pt-32 pb-16 px-6 text-center bg-champagne">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <p className="font-body text-[10px] tracking-[0.4em] uppercase text-muted-foreground mb-4">Collection</p>
          <h1 className="heading-display text-4xl md:text-6xl">{cat.title}</h1>
          <div className="divider-gold mt-6 mb-4" />
          <p className="font-body text-sm text-muted-foreground max-w-md mx-auto">{cat.subtitle}</p>
        </motion.div>
      </section>

      {/* Products Grid */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          {filtered.length === 0 ? (
            <p className="text-center text-muted-foreground font-body">No dresses found in this collection yet.</p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
              {filtered.map((product, i) => (
                <motion.div
                  key={product.id}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: i * 0.1 }}
                >
                  <ProductCard product={product} />
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </section>
    </Layout>
  );
};

export default CollectionPage;
