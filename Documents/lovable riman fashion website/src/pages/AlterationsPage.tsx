import { motion } from "framer-motion";
import { Scissors, Ruler, Calendar, Check } from "lucide-react";
import Layout from "@/components/Layout";

const alterationServices = [
    {
        icon: Scissors,
        title: "Hemming",
        description: "Shorten or lengthen the dress to your perfect length. We match the original hemline exactly.",
        included: true
    },
    {
        icon: Ruler,
        title: "Taking In/Letting Out",
        description: "Adjust the bodice for a snug or relaxed fit. Our expert tailors ensure a seamless finish.",
        included: true
    },
    {
        icon: Calendar,
        title: "Rush Alterations",
        description: "Need alterations quickly? We offer same-day and next-day services for urgent requests.",
        included: true
    }
];

const processSteps = [
    {
        step: 1,
        title: "Book Your Appointment",
        description: "Schedule a fitting at our Sharjah atelier. Walk-ins are welcome but appointments are recommended."
    },
    {
        step: 2,
        title: "Initial Fitting",
        description: "Try on your dress and work with our tailor to mark necessary adjustments."
    },
    {
        step: 3,
        title: "Alterations Begin",
        description: "Our skilled artisans carefully modify your dress to perfection."
    },
    {
        step: 4,
        title: "Final Fitting",
        description: "Try on your altered dress to ensure the perfect fit."
    },
    {
        step: 5,
        title: "Take Home",
        description: "Walk out feeling confident in your perfectly fitted dress!"
    }
];

const AlterationsPage = () => {
    return (
        <Layout>
            {/* Hero */}
            <section className="pt-32 pb-16 px-6 bg-champagne">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    className="max-w-4xl mx-auto text-center"
                >
                    <p className="font-body text-[10px] tracking-[0.4em] uppercase text-muted-foreground mb-4">Fitting Services</p>
                    <h1 className="heading-display text-4xl md:text-5xl mb-6">Complimentary Alterations</h1>
                    <p className="font-body text-muted-foreground max-w-2xl mx-auto mb-8">
                        At Riman Fashion, we believe every woman deserves the perfect fit.
                        All our dresses come with complimentary alterations to ensure you look your absolute best.
                    </p>
                    <div className="divider-gold mt-6 mb-4" />
                </motion.div>
            </section>

            {/* What's Included */}
            <section className="section-padding">
                <div className="max-w-6xl mx-auto px-6">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="text-center mb-12"
                    >
                        <h2 className="font-heading text-3xl mb-4">What's Included</h2>
                        <p className="font-body text-muted-foreground">
                            Basic alterations are complimentary with every dress purchase or rental
                        </p>
                    </motion.div>

                    <div className="grid md:grid-cols-3 gap-8">
                        {alterationServices.map((service, index) => {
                            const Icon = service.icon;
                            return (
                                <motion.div
                                    key={service.title}
                                    initial={{ opacity: 0, y: 30 }}
                                    whileInView={{ opacity: 1, y: 0 }}
                                    viewport={{ once: true }}
                                    transition={{ duration: 0.5, delay: index * 0.1 }}
                                    className="bg-white p-8 border border-border text-center hover:shadow-lg transition-shadow"
                                >
                                    <div className="w-16 h-16 mx-auto mb-6 bg-gold/10 rounded-full flex items-center justify-center">
                                        <Icon size={28} className="text-gold" />
                                    </div>
                                    <h3 className="font-heading text-xl mb-3">{service.title}</h3>
                                    <p className="font-body text-sm text-muted-foreground mb-4">
                                        {service.description}
                                    </p>
                                    {service.included && (
                                        <span className="inline-flex items-center gap-1 text-xs text-green-600 font-medium">
                                            <Check size={14} /> Complimentary
                                        </span>
                                    )}
                                </motion.div>
                            );
                        })}
                    </div>
                </div>
            </section>

            {/* Note about sizes */}
            <section className="py-16 bg-black text-white">
                <div className="max-w-4xl mx-auto px-6">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="text-center"
                    >
                        <h2 className="font-heading text-3xl mb-6">We Don't Do Standard Sizes</h2>
                        <p className="font-body text-gray-300 text-lg leading-relaxed">
                            Every woman is unique, and so is her perfect dress. At Riman Fashion,
                            we don't believe in "standard sizes." Instead, we offer made-to-measure
                            alterations for every customer. When you choose a dress, our expert
                            tailors will customize it to your exact measurements, ensuring a flawless
                            fit that's uniquely yours.
                        </p>
                        <p className="font-body text-gold mt-6">
                            Simply select your closest size, and we'll handle the rest!
                        </p>
                    </motion.div>
                </div>
            </section>

            {/* Process */}
            <section className="section-padding">
                <div className="max-w-6xl mx-auto px-6">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="text-center mb-12"
                    >
                        <h2 className="font-heading text-3xl mb-4">Our Alterations Process</h2>
                        <p className="font-body text-muted-foreground">
                            From your first fitting to the final reveal
                        </p>
                    </motion.div>

                    <div className="grid md:grid-cols-5 gap-4">
                        {processSteps.map((step, index) => (
                            <motion.div
                                key={step.step}
                                initial={{ opacity: 0, y: 30 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ duration: 0.5, delay: index * 0.1 }}
                                className="text-center"
                            >
                                <div className="w-12 h-12 mx-auto mb-4 bg-gold text-white rounded-full flex items-center justify-center font-heading text-xl">
                                    {step.step}
                                </div>
                                <h3 className="font-heading text-lg mb-2">{step.title}</h3>
                                <p className="font-body text-xs text-muted-foreground">{step.description}</p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA */}
            <section className="py-20 bg-champagne">
                <div className="max-w-2xl mx-auto px-6 text-center">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                    >
                        <h2 className="font-heading text-3xl mb-6">Ready for Your Fitting?</h2>
                        <p className="font-body text-muted-foreground mb-8">
                            Book an appointment at our atelier and let our experts work their magic.
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                            <a href="/contact" className="btn-luxury">
                                Book Appointment
                            </a>
                            <a href="/collection/bridal" className="btn-luxury-outline">
                                Browse Dresses
                            </a>
                        </div>
                    </motion.div>
                </div>
            </section>
        </Layout>
    );
};

export default AlterationsPage;
