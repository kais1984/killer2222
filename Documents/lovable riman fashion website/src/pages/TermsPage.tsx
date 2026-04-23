import Layout from "@/components/Layout";
import { Shield, Star, Clock, Heart } from "lucide-react";

const TermsPage = () => {
    return (
        <Layout>
            <div className="min-h-screen bg-background">
                {/* Hero Section */}
                <div className="relative py-20 bg-gradient-to-b from-background to-card/30">
                    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                        <h1 className="font-heading text-4xl md:text-5xl lg:text-6xl tracking-wide mb-6">
                            Terms & <span className="text-gold">Conditions</span>
                        </h1>
                        <p className="font-body text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
                            Your trust is the foundation of our business. Please review our terms to understand how we serve you with excellence.
                        </p>
                    </div>
                </div>

                {/* Content */}
                <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                    <div className="prose prose-lg max-w-none">

                        {/* Introduction */}
                        <section className="mb-12">
                            <h2 className="font-heading text-2xl mb-4 flex items-center gap-3">
                                <Star className="text-gold" size={24} />
                                Welcome to Riman Fashion
                            </h2>
                            <p className="font-body text-muted-foreground leading-relaxed">
                                Welcome to Riman Fashion, where luxury meets personalization. These Terms & Conditions govern your use of our website and services. By accessing our platform, you agree to be bound by these terms, which reflect our commitment to providing you with an exceptional shopping experience.
                            </p>
                        </section>

                        {/* Our Commitment */}
                        <section className="mb-12">
                            <h2 className="font-heading text-2xl mb-4 flex items-center gap-3">
                                <Heart className="text-gold" size={24} />
                                Our Commitment to You
                            </h2>
                            <div className="space-y-4">
                                <p className="font-body text-muted-foreground leading-relaxed">
                                    At Riman Fashion, we are dedicated to providing the highest quality bridal and evening wear in the UAE. Every piece in our collection is crafted with meticulous attention to detail, ensuring that you receive nothing less than perfection.
                                </p>
                                <ul className="list-disc list-inside space-y-2 font-body text-muted-foreground">
                                    <li>Premium quality materials sourced from the finest suppliers</li>
                                    <li>Handcrafted designs by master artisans</li>
                                    <li>Personalized fittings and consultations</li>
                                    <li>White-glove service from selection to delivery</li>
                                </ul>
                            </div>
                        </section>

                        {/* Ordering Terms */}
                        <section className="mb-12">
                            <h2 className="font-heading text-2xl mb-4">Orders & Purchases</h2>
                            <div className="space-y-4">
                                <h3 className="font-heading text-xl mb-2">Purchase Terms</h3>
                                <p className="font-body text-muted-foreground leading-relaxed">
                                    All purchases are subject to availability and confirmation of the order price. Once you place an order, we will provide a confirmation along with estimated delivery timelines. For custom orders, please allow 4-8 weeks for creation, with priority services available upon request.
                                </p>

                                <h3 className="font-heading text-xl mb-2 mt-6">Rental Terms</h3>
                                <p className="font-body text-muted-foreground leading-relaxed">
                                    Our rental service allows you to experience luxury for your special occasions. Rental periods are typically 3-5 days. A security deposit is required and will be refunded upon safe return of the garment in its original condition.
                                </p>

                                <h3 className="font-heading text-xl mb-2 mt-6">Payment & Pricing</h3>
                                <p className="font-body text-muted-foreground leading-relaxed">
                                    All prices are in UAE Dirhams (AED) and include VAT. We accept major credit cards, bank transfers, and installment plans through our financing partners. Price adjustments may occur based on customization requests.
                                </p>
                            </div>
                        </section>

                        {/* Returns & Exchanges */}
                        <section className="mb-12">
                            <h2 className="font-heading text-2xl mb-4 flex items-center gap-3">
                                <Shield className="text-gold" size={24} />
                                Returns, Exchanges & Refunds
                            </h2>
                            <div className="space-y-4">
                                <h3 className="font-heading text-xl mb-2">For Purchased Items</h3>
                                <p className="font-body text-muted-foreground leading-relaxed">
                                    We want you to love your purchase. Unworn items with tags attached may be returned within 14 days for a full refund or exchange. Custom-made gowns are final sale unless there is a manufacturing defect.
                                </p>

                                <h3 className="font-heading text-xl mb-2 mt-6">For Rentals</h3>
                                <p className="font-body text-muted-foreground leading-relaxed">
                                    Rental items must be returned on time to avoid additional charges. The security deposit is fully refundable provided the garment is returned in its original condition, free from damage or stains.
                                </p>

                                <h3 className="font-heading text-xl mb-2 mt-6">Damage Policy</h3>
                                <p className="font-body text-muted-foreground leading-relaxed">
                                    Normal wear is expected; however, significant damage including tears, stains, or missing embellishments will result in deduction from your security deposit or additional charges. We understand accidents happen and will assess each situation individually.
                                </p>
                            </div>
                        </section>

                        {/* Service Terms */}
                        <section className="mb-12">
                            <h2 className="font-heading text-2xl mb-4 flex items-center gap-3">
                                <Clock className="text-gold" size={24} />
                                Consultations & Fittings
                            </h2>
                            <div className="space-y-4">
                                <p className="font-body text-muted-foreground leading-relaxed">
                                    Our private consultation experience is complimentary for wedding parties. During your appointment, ourStyle Experts will guide you through our collections, help you find your dream dress, and take precise measurements for the perfect fit.
                                </p>
                                <ul className="list-disc list-inside space-y-2 font-body text-muted-foreground">
                                    <li>Private viewing appointments available 7 days a week</li>
                                    <li>Complimentary refreshments and champagne service</li>
                                    <li>Up to 3 guests per appointment</li>
                                    <li>Alterations included with purchase (up to 2 fittings)</li>
                                </ul>
                            </div>
                        </section>

                        {/* Privacy */}
                        <section className="mb-12">
                            <h2 className="font-heading text-2xl mb-4">Privacy & Data Protection</h2>
                            <p className="font-body text-muted-foreground leading-relaxed">
                                Your privacy is paramount to us. We collect only necessary information to process your orders and provide personalized service. Your data is never shared with third parties without explicit consent. All payment information is encrypted and processed securely through certified payment gateways.
                            </p>
                        </section>

                        {/* Intellectual Property */}
                        <section className="mb-12">
                            <h2 className="font-heading text-2xl mb-4">Intellectual Property</h2>
                            <p className="font-body text-muted-foreground leading-relaxed">
                                All designs, images, and content on this website are the exclusive property of Riman Fashion. Unauthorized reproduction, distribution, or use of our intellectual property is strictly prohibited. Our gowns are protected under UAE copyright and design laws.
                            </p>
                        </section>

                        {/* Liability */}
                        <section className="mb-12">
                            <h2 className="font-heading text-2xl mb-4">Limitation of Liability</h2>
                            <p className="font-body text-muted-foreground leading-relaxed">
                                Riman Fashion's liability is limited to the purchase price of the item. We are not responsible for indirect, incidental, or consequential damages. Our total liability shall not exceed the amount paid for the product in question.
                            </p>
                        </section>

                        {/* Contact */}
                        <section className="mb-12">
                            <h2 className="font-heading text-2xl mb-4">Questions? We're Here to Help</h2>
                            <p className="font-body text-muted-foreground leading-relaxed mb-4">
                                If you have any questions about these Terms & Conditions, please don't hesitate to contact us:
                            </p>
                            <div className="bg-card p-6 rounded-lg">
                                <p className="font-body text-foreground"><strong>Phone:</strong> +971 55 373 0792</p>
                                <p className="font-body text-foreground"><strong>Email:</strong> info@rimanfashion.com</p>
                                <p className="font-body text-foreground"><strong>Location:</strong> S130 - Al Jazzat, Sharjah, UAE</p>
                            </div>
                        </section>

                        {/* Last Updated */}
                        <div className="border-t border-border pt-8 mt-12">
                            <p className="font-body text-sm text-muted-foreground">
                                Last updated: March 2026
                            </p>
                        </div>

                    </div>
                </div>
            </div>
        </Layout>
    );
};

export default TermsPage;
