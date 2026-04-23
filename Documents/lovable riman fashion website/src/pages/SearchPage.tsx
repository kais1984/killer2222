import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import { Search as SearchIcon, X } from "lucide-react";
import Layout from "@/components/Layout";
import ProductCard from "@/components/ProductCard";
import { useProducts } from "@/contexts/ProductContext";

const SearchPage = () => {
    const [searchParams, setSearchParams] = useSearchParams();
    const initialQuery = searchParams.get("q") || "";
    const [query, setQuery] = useState(initialQuery);
    const { products } = useProducts();

    const searchResults = query.trim()
        ? products.filter(p =>
            p.name.toLowerCase().includes(query.toLowerCase()) ||
            p.description.toLowerCase().includes(query.toLowerCase()) ||
            p.category.toLowerCase().includes(query.toLowerCase()) ||
            p.color.some(c => c.toLowerCase().includes(query.toLowerCase())) ||
            p.style.some(s => s.toLowerCase().includes(query.toLowerCase())) ||
            p.fabric?.toLowerCase().includes(query.toLowerCase())
        )
        : [];

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        if (query.trim()) {
            setSearchParams({ q: query });
        }
    };

    const clearSearch = () => {
        setQuery("");
        setSearchParams({});
    };

    return (
        <Layout>
            <section className="pt-32 pb-16 px-6 bg-champagne">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    className="max-w-4xl mx-auto"
                >
                    <p className="font-body text-[10px] tracking-[0.4em] uppercase text-muted-foreground mb-4 text-center">Search</p>
                    <h1 className="heading-display text-4xl md:text-5xl text-center mb-8">Find Your Perfect Dress</h1>

                    {/* Search Form */}
                    <form onSubmit={handleSearch} className="relative max-w-2xl mx-auto">
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Search by name, category, color, style..."
                            className="w-full h-16 pl-6 pr-16 bg-white border border-border text-lg focus:border-gold focus:outline-none"
                        />
                        <button
                            type="submit"
                            className="absolute right-2 top-1/2 -translate-y-1/2 w-12 h-12 bg-gold text-white flex items-center justify-center hover:bg-gold/90 transition-colors"
                        >
                            <SearchIcon size={20} />
                        </button>
                    </form>

                    {query && (
                        <button
                            onClick={clearSearch}
                            className="flex items-center gap-2 mx-auto mt-4 text-muted-foreground hover:text-foreground transition-colors"
                        >
                            <X size={16} />
                            <span className="font-body text-sm">Clear search</span>
                        </button>
                    )}
                </motion.div>
            </section>

            <section className="section-padding">
                <div className="max-w-7xl mx-auto px-6">
                    {query.trim() === "" ? (
                        <div className="text-center py-20">
                            <p className="font-body text-muted-foreground">
                                Enter a search term to find your perfect dress
                            </p>
                        </div>
                    ) : searchResults.length === 0 ? (
                        <div className="text-center py-20">
                            <h2 className="font-heading text-2xl mb-4">No results found</h2>
                            <p className="font-body text-muted-foreground">
                                Try different keywords or browse our collections
                            </p>
                            <div className="flex flex-wrap justify-center gap-4 mt-8">
                                <a href="/collection/bridal" className="btn-luxury-outline">Bridal Gowns</a>
                                <a href="/collection/evening" className="btn-luxury-outline">Evening Dresses</a>
                                <a href="/collection/rentals" className="btn-luxury-outline">Rentals</a>
                            </div>
                        </div>
                    ) : (
                        <>
                            <p className="font-body text-sm text-muted-foreground mb-8">
                                Found {searchResults.length} result{searchResults.length !== 1 ? "s" : ""} for "{query}"
                            </p>
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
                                {searchResults.map((product, i) => (
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
                        </>
                    )}
                </div>
            </section>
        </Layout>
    );
};

export default SearchPage;
