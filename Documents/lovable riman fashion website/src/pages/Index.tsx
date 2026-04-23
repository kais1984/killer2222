import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Layout from "@/components/Layout";
import HeroSection from "@/components/home/HeroSection";
import BrandPromise from "@/components/home/BrandPromise";
import CategoryTiles from "@/components/home/CategoryTiles";
import FeaturedCollection from "@/components/home/FeaturedCollection";
import TestimonialsSection from "@/components/home/TestimonialsSection";
import ConsultationBanner from "@/components/home/ConsultationBanner";
import TrustBadges from "@/components/TrustBadges";
import ProductCard from "@/components/ProductCard";

interface RecentlyViewedProduct {
  id: string;
  name: string;
  image: string;
  price: number;
}

const Index = () => {
  const [recentlyViewed, setRecentlyViewed] = useState<RecentlyViewedProduct[]>([]);

  useEffect(() => {
    const viewed = JSON.parse(localStorage.getItem("riman_viewed") || "[]");
    setRecentlyViewed(viewed);
  }, []);

  return (
    <Layout>
      <HeroSection />
      <BrandPromise />
      <CategoryTiles />
      <FeaturedCollection />
      <TestimonialsSection />
      <ConsultationBanner />
      <TrustBadges />

      {/* Recently Viewed Section */}
      {recentlyViewed.length > 0 && (
        <section className="py-16 bg-gray-50">
          <div className="max-w-7xl mx-auto px-6 md:px-12">
            <div className="flex items-center justify-between mb-8">
              <h2 className="font-heading text-2xl md:text-3xl">Recently Viewed</h2>
              <Link to="/collection/all" className="text-sm text-gold hover:underline">
                View All →
              </Link>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {recentlyViewed.slice(0, 4).map((product) => (
                <Link key={product.id} to={`/product/${product.id}`}>
                  <div className="group">
                    <div className="aspect-[3/4] overflow-hidden mb-3">
                      <img
                        src={product.image}
                        alt={product.name}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      />
                    </div>
                    <p className="font-heading text-sm truncate">{product.name}</p>
                    <p className="text-xs text-muted-foreground">AED {product.price?.toLocaleString()}</p>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}
    </Layout>
  );
};

export default Index;
