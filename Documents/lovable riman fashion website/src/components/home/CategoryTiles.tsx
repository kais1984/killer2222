import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import bridalImg from "@/assets/bridal-category.jpg";
import eveningImg from "@/assets/evening-category.jpg";
import rentalImg from "@/assets/rental-category.jpg";

const categories = [
  {
    title: "Bridal Gowns",
    subtitle: "For your most precious day",
    image: bridalImg,
    path: "/collection/bridal",
  },
  {
    title: "Evening & Party",
    subtitle: "Unforgettable entrances",
    image: eveningImg,
    path: "/collection/evening",
  },
  {
    title: "Dress Rentals",
    subtitle: "Luxury made accessible",
    image: rentalImg,
    path: "/collection/rentals",
  },
];

const CategoryTiles = () => {
  return (
    <section className="section-padding">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <p className="font-body text-[10px] tracking-[0.4em] uppercase text-muted-foreground mb-4">Shop By Category</p>
          <h2 className="heading-display text-4xl md:text-5xl">Discover Your Style</h2>
          <div className="divider-gold mt-6" />
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {categories.map((cat, i) => (
            <motion.div
              key={cat.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: i * 0.15 }}
            >
              <Link to={cat.path} className="group block relative overflow-hidden aspect-[3/4]">
                <img
                  src={cat.image}
                  alt={cat.title}
                  className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                  loading="lazy"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-foreground/60 via-foreground/10 to-transparent" />
                <div className="absolute bottom-0 left-0 right-0 p-8">
                  <p className="font-body text-[10px] tracking-[0.3em] uppercase text-primary-foreground/70 mb-2">
                    {cat.subtitle}
                  </p>
                  <h3 className="font-heading text-3xl text-primary-foreground tracking-wide">
                    {cat.title}
                  </h3>
                  <div className="mt-4 w-0 group-hover:w-12 h-[1px] bg-gold-light transition-all duration-500" />
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default CategoryTiles;
