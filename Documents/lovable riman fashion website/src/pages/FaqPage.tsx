import { useState } from "react";
import { motion } from "framer-motion";
import { ChevronDown } from "lucide-react";
import Layout from "@/components/Layout";

const faqCategories = [
    {
        title: "Orders & Purchases",
        questions: [
            {
                q: "How do I place an order?",
                a: "Simply browse our collection, select your desired dress, choose your preferred option (Buy or Rent), select your size, and proceed to checkout. You'll receive a confirmation email with order details."
            },
            {
                q: "Can I buy and rent the same dress?",
                a: "Yes! All our dresses are available for both purchase and rental. You can choose whichever option suits your needs at the time of checkout."
            },
            {
                q: "What payment methods do you accept?",
                a: "We accept all major credit cards, debit cards, and cash on delivery. For rental orders, we also require a security deposit which is refundable upon return of the dress in good condition."
            },
            {
                q: "How long does it take to process an order?",
                a: "Purchase orders are typically processed within 3-5 business days. Rental orders are confirmed once availability is checked for your selected dates."
            }
        ]
    },
    {
        title: "Rentals",
        questions: [
            {
                q: "How does the rental process work?",
                a: "Select your dress, choose your rental dates, and pay the rental fee plus a refundable security deposit. The dress will be delivered to your address on the start date and picked up on the return date."
            },
            {
                q: "What is the security deposit?",
                a: "The security deposit is a refundable amount held to ensure the dress is returned in good condition. It will be fully refunded within 7-10 business days after the dress is returned, minus any damages if applicable."
            },
            {
                q: "Can I extend my rental period?",
                a: "Yes, extensions are subject to availability. Please contact us at least 48 hours before your scheduled return date to request an extension."
            },
            {
                q: "What happens if the dress is damaged?",
                a: "Normal wear is expected. However, significant damage such as tears, stains, or missing accessories may result in deductions from your security deposit. We'll assess any damage and contact you within 3 business days."
            }
        ]
    },
    {
        title: "Alterations",
        questions: [
            {
                q: "Do you offer alterations?",
                a: "Yes! At Riman Fashion, we offer complimentary alterations for both purchased and rented dresses. Our expert tailors will ensure the perfect fit for your special day."
            },
            {
                q: "Are alterations included in the price?",
                a: "Basic alterations (hemming, taking in/letting out) are complimentary for all our dresses. More complex alterations may incur additional charges based on the work required."
            },
            {
                q: "How long do alterations take?",
                a: "Standard alterations take 3-5 business days. For rush orders, please contact us to discuss availability. We recommend allowing at least 1 week before your event for alterations."
            },
            {
                q: "Can I get alterations for rental dresses?",
                a: "Absolutely! We offer same-day alterations for rental dresses to ensure the perfect fit. Please schedule your fitting at least 2 days before your rental period begins."
            }
        ]
    },
    {
        title: "Shipping & Delivery",
        questions: [
            {
                q: "Do you offer international shipping?",
                a: "Currently, we deliver within the UAE and GCC countries. Contact us for international shipping inquiries."
            },
            {
                q: "How long does delivery take?",
                a: "Standard delivery within the UAE takes 3-5 business days. Same-day delivery is available in Dubai for orders placed before 12 PM."
            },
            {
                q: "Is delivery free?",
                a: "Delivery is free for all orders within Sharjah and Dubai. A delivery fee of AED 50 applies to other emirates."
            }
        ]
    },
    {
        title: "Returns & Cancellations",
        questions: [
            {
                q: "What is your return policy?",
                a: "We want you to love your dress. If you're not completely satisfied, you can return unworn dresses within 7 days for a full refund. Rental orders can be cancelled up to 48 hours before the rental period."
            },
            {
                q: "How do I cancel my order?",
                a: "Contact us immediately at +971 55 373 0792 or email info@rimanfashion.com. Cancellations requested within 24 hours of order placement receive a full refund."
            }
        ]
    }
];

const FaqPage = () => {
    const [openIndex, setOpenIndex] = useState<number | null>(null);

    return (
        <Layout>
            <section className="pt-32 pb-16 px-6 bg-champagne">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    className="max-w-4xl mx-auto text-center"
                >
                    <p className="font-body text-[10px] tracking-[0.4em] uppercase text-muted-foreground mb-4">Help</p>
                    <h1 className="heading-display text-4xl md:text-5xl mb-6">Frequently Asked Questions</h1>
                    <div className="divider-gold mt-6 mb-4" />
                </motion.div>
            </section>

            <section className="section-padding">
                <div className="max-w-4xl mx-auto px-6">
                    {faqCategories.map((category, catIndex) => (
                        <div key={category.title} className="mb-12">
                            <h2 className="font-heading text-2xl mb-6 text-gold">{category.title}</h2>
                            <div className="space-y-4">
                                {category.questions.map((item, qIndex) => {
                                    const index = catIndex * 100 + qIndex;
                                    return (
                                        <motion.div
                                            key={index}
                                            initial={{ opacity: 0, y: 10 }}
                                            whileInView={{ opacity: 1, y: 0 }}
                                            viewport={{ once: true }}
                                            transition={{ duration: 0.3, delay: qIndex * 0.1 }}
                                            className="border border-border bg-white"
                                        >
                                            <button
                                                onClick={() => setOpenIndex(openIndex === index ? null : index)}
                                                className="w-full px-6 py-4 flex items-center justify-between text-left"
                                            >
                                                <span className="font-heading text-lg">{item.q}</span>
                                                <ChevronDown
                                                    size={20}
                                                    className={`transition-transform ${openIndex === index ? "rotate-180" : ""}`}
                                                />
                                            </button>
                                            {openIndex === index && (
                                                <motion.div
                                                    initial={{ height: 0, opacity: 0 }}
                                                    animate={{ height: "auto", opacity: 1 }}
                                                    className="px-6 pb-4"
                                                >
                                                    <p className="font-body text-muted-foreground">{item.a}</p>
                                                </motion.div>
                                            )}
                                        </motion.div>
                                    );
                                })}
                            </div>
                        </div>
                    ))}
                </div>
            </section>

            <section className="py-16 bg-black text-white">
                <div className="max-w-2xl mx-auto px-6 text-center">
                    <h2 className="font-heading text-3xl mb-4">Still Have Questions?</h2>
                    <p className="font-body text-gray-400 mb-8">
                        Our team is here to help. Contact us for personalized assistance.
                    </p>
                    <a href="/contact" className="btn-luxury">
                        Contact Us
                    </a>
                </div>
            </section>
        </Layout>
    );
};

export default FaqPage;
