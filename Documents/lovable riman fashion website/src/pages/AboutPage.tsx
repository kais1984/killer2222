import { motion } from "framer-motion";
import Layout from "@/components/Layout";

const AboutPage = () => {
    return (
        <Layout>
            {/* Hero Section with Video */}
            <section className="relative h-[70vh] overflow-hidden">
                <video
                    autoPlay
                    muted
                    loop
                    playsInline
                    className="absolute inset-0 w-full h-full object-cover"
                >
                    <source src="/videos/our-story-1.mp4" type="video/mp4" />
                </video>
                <div className="absolute inset-0 bg-black/40" />
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    className="relative z-10 h-full flex flex-col items-center justify-center text-white text-center px-6"
                >
                    <p className="font-body text-xs tracking-[0.4em] uppercase mb-4">Our Story</p>
                    <h1 className="heading-display text-5xl md:text-7xl mb-6">A Legacy of Elegance</h1>
                    <p className="font-body text-sm md:text-base max-w-2xl opacity-90">
                        Crafting dreams into reality since 2015
                    </p>
                </motion.div>
            </section>

            {/* Story Content */}
            <section className="section-padding bg-champagne">
                <div className="max-w-4xl mx-auto">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8 }}
                        className="text-center mb-16"
                    >
                        <h2 className="font-heading text-3xl md:text-4xl mb-6">The Riman Journey</h2>
                        <p className="font-body text-muted-foreground leading-relaxed">
                            Riman Fashion began as a small atelier in the heart of Sharjah, driven by a singular vision:
                            to create exquisite bridal and evening wear that makes every woman feel like royalty.
                            What started as a family business has grown into one of the UAE's most sought-after
                            luxury fashion houses.
                        </p>
                    </motion.div>

                    {/* Video Section */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8 }}
                        className="mb-16"
                    >
                        <video
                            autoPlay
                            muted
                            loop
                            playsInline
                            className="w-full h-[500px] object-cover rounded-lg shadow-lg"
                        >
                            <source src="/videos/our-story-2.mp4" type="video/mp4" />
                        </video>
                    </motion.div>

                    {/* Values */}
                    <div className="grid md:grid-cols-3 gap-12">
                        {[
                            {
                                title: "Craftsmanship",
                                description: "Every piece is meticulously handcrafted by skilled artisans with decades of experience in bridal fashion."
                            },
                            {
                                title: "Quality",
                                description: "We source only the finest fabrics from around the world, ensuring each gown meets our exacting standards."
                            },
                            {
                                title: "Personalization",
                                description: "Our bespoke service ensures every bride gets a dress that's uniquely hers, tailored to perfection."
                            }
                        ].map((value, index) => (
                            <motion.div
                                key={value.title}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ duration: 0.8, delay: index * 0.2 }}
                                className="text-center"
                            >
                                <h3 className="font-heading text-xl mb-4">{value.title}</h3>
                                <p className="font-body text-sm text-muted-foreground">{value.description}</p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Stats Section */}
            <section className="py-20 bg-black text-white">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
                        {[
                            { number: "10+", label: "Years of Excellence" },
                            { number: "5000+", label: "Happy Brides" },
                            { number: "150+", label: "Designer Gowns" },
                            { number: "50+", label: "Expert Stylists" }
                        ].map((stat, index) => (
                            <motion.div
                                key={stat.label}
                                initial={{ opacity: 0, scale: 0.9 }}
                                whileInView={{ opacity: 1, scale: 1 }}
                                viewport={{ once: true }}
                                transition={{ duration: 0.5, delay: index * 0.1 }}
                            >
                                <p className="font-heading text-4xl md:text-5xl text-gold mb-2">{stat.number}</p>
                                <p className="font-body text-xs tracking-widest uppercase">{stat.label}</p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="section-padding">
                <div className="max-w-2xl mx-auto text-center">
                    <h2 className="font-heading text-3xl mb-6">Visit Our Atelier</h2>
                    <p className="font-body text-muted-foreground mb-8">
                        Experience the Riman difference firsthand. Schedule a private consultation
                        with ourStyle experts and discover your dream dress.
                    </p>
                    <a href="/contact" className="btn-luxury">
                        Book Your Appointment
                    </a>
                </div>
            </section>
        </Layout>
    );
};

export default AboutPage;
