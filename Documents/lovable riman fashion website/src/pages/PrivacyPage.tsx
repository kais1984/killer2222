import Layout from "@/components/Layout";
import { Shield, Lock, Eye, Heart } from "lucide-react";

const PrivacyPage = () => {
    return (
        <Layout>
            <div className="min-h-screen bg-background">
                {/* Hero Section */}
                <div className="relative py-20 bg-gradient-to-b from-background to-card/30">
                    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                        <h1 className="font-heading text-4xl md:text-5xl lg:text-6xl tracking-wide mb-6">
                            Privacy <span className="text-gold">Policy</span>
                        </h1>
                        <p className="font-body text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
                            Your privacy is paramount. Learn how we protect and handle your personal information with the utmost care.
                        </p>
                    </div>
                </div>

                {/* Content */}
                <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                    <div className="prose prose-lg max-w-none">

                        {/* Introduction */}
                        <section className="mb-12">
                            <h2 className="font-heading text-2xl mb-4 flex items-center gap-3">
                                <Shield className="text-gold" size={24} />
                                Our Commitment
                            </h2>
                            <p className="font-body text-muted-foreground leading-relaxed">
                                At Riman Fashion, we understand that your trust is earned through transparency and respect. This Privacy Policy outlines how we collect, use, disclose, and safeguard your personal information when you visit our website, engage our services, or purchase our products.
                            </p>
                        </section>

                        {/* Information We Collect */}
                        <section className="mb-12">
                            <h2 className="font-heading text-2xl mb-4">Information We Collect</h2>
                            <div className="space-y-4">
                                <h3 className="font-heading text-xl mb-2">Personal Information</h3>
                                <p className="font-body text-muted-foreground leading-relaxed">
                                    When you create an account, place an order, or schedule a consultation, we collect information such as your name, email address, phone number, shipping address, and payment details. For bridal consultations, we may also collect sizing information and event details.
                                </p>

                                <h3 className="font-heading text-xl mb-2 mt-6">Automatically Collected Information</h3>
                                <p className="font-body text-muted-foreground leading-relaxed">
                                    We automatically collect certain information when you visit our website, including your IP address, browser type, operating system, access times, and pages viewed. This data helps us improve our website and understand customer preferences.
                                </p>
                            </div>
                        </section>

                        {/* How We Use Information */}
                        <section className="mb-12">
                            <h2 className="font-heading text-2xl mb-4 flex items-center gap-3">
                                <Eye className="text-gold" size={24} />
                                How We Use Your Information
                            </h2>
                            <div className="space-y-3">
                                <p className="font-body text-muted-foreground leading-relaxed">
                                    We use your personal information to:
                                </p>
                                <ul className="list-disc list-inside space-y-2 font-body text-muted-foreground">
                                    <li>Process and fulfill your orders, including shipping and delivery</li>
                                    <li>Provide customer service and respond to your inquiries</li>
                                    <li>Schedule and conduct bridal consultations and fittings</li>
                                    <li>Send you updates about your order status</li>
                                    <li>Personalize your shopping experience</li>
                                    <li>Send promotional emails about new collections and special offers (with your consent)</li>
                                    <li>Improve our products and services based on your feedback</li>
                                </ul>
                            </div>
                        </section>

                        {/* Data Protection */}
                        <section className="mb-12">
                            <h2 className="font-heading text-2xl mb-4 flex items-center gap-3">
                                <Lock className="text-gold" size={24} />
                                Data Protection & Security
                            </h2>
                            <div className="space-y-4">
                                <p className="font-body text-muted-foreground leading-relaxed">
                                    We implement industry-standard security measures to protect your personal information. All data transmission is encrypted using Secure Socket Layer (SSL) technology. Payment information is processed through PCI-DSS compliant payment gateways.
                                </p>
                                <ul className="list-disc list-inside space-y-2 font-body text-muted-foreground">
                                    <li>256-bit SSL encryption for all data transmission</li>
                                    <li>Secure, encrypted database storage</li>
                                    <li>Regular security audits and updates</li>
                                    <li>Restricted access to personal data on a need-to-know basis</li>
                                    <li>Employee confidentiality agreements</li>
                                </ul>
                            </div>
                        </section>

                        {/* Sharing Information */}
                        <section className="mb-12">
                            <h2 className="font-heading text-2xl mb-4">Sharing Your Information</h2>
                            <p className="font-body text-muted-foreground leading-relaxed">
                                We do not sell, trade, or otherwise transfer your personal information to outside parties except in the following circumstances:
                            </p>
                            <ul className="list-disc list-inside space-y-2 font-body text-muted-foreground mt-4">
                                <li><strong>Service Providers:</strong> Trusted third parties who assist in operating our website, conducting our business, or servicing you (e.g., shipping companies, payment processors)</li>
                                <li><strong>Legal Requirements:</strong> When required by law or in response to valid requests by public authorities</li>
                                <li><strong>Business Transfers:</strong> In the event of a merger, acquisition, or sale of assets, your information may be transferred</li>
                            </ul>
                        </section>

                        {/* Your Rights */}
                        <section className="mb-12">
                            <h2 className="font-heading text-2xl mb-4 flex items-center gap-3">
                                <Heart className="text-gold" size={24} />
                                Your Rights
                            </h2>
                            <div className="space-y-3">
                                <p className="font-body text-muted-foreground leading-relaxed">
                                    You have the right to:
                                </p>
                                <ul className="list-disc list-inside space-y-2 font-body text-muted-foreground">
                                    <li>Access the personal information we hold about you</li>
                                    <li>Request correction of inaccurate personal data</li>
                                    <li>Request deletion of your personal data (subject to legal requirements)</li>
                                    <li>Opt-out of marketing communications at any time</li>
                                    <li>Request a copy of your personal data in a portable format</li>
                                </ul>
                                <p className="font-body text-muted-foreground leading-relaxed mt-4">
                                    To exercise any of these rights, please contact us at info@rimanfashion.com or call +971 55 373 0792.
                                </p>
                            </div>
                        </section>

                        {/* Cookies */}
                        <section className="mb-12">
                            <h2 className="font-heading text-2xl mb-4">Cookies & Tracking Technologies</h2>
                            <p className="font-body text-muted-foreground leading-relaxed">
                                We use cookies and similar tracking technologies to enhance your browsing experience. Cookies are small files stored on your device that help us understand your preferences and improve our website. You can control cookies through your browser settings. Please note that disabling cookies may affect certain features of our website.
                            </p>
                        </section>

                        {/* Third Party Links */}
                        <section className="mb-12">
                            <h2 className="font-heading text-2xl mb-4">Third-Party Links</h2>
                            <p className="font-body text-muted-foreground leading-relaxed">
                                Our website may contain links to third-party websites. We are not responsible for the privacy practices or content of these external sites. We encourage you to review the privacy policies of any website you visit.
                            </p>
                        </section>

                        {/* Children's Privacy */}
                        <section className="mb-12">
                            <h2 className="font-heading text-2xl mb-4">Children's Privacy</h2>
                            <p className="font-body text-muted-foreground leading-relaxed">
                                Our website and services are not intended for individuals under the age of 18. We do not knowingly collect personal information from children. If we become aware that we have collected data from a minor without parental consent, we will take steps to delete such information promptly.
                            </p>
                        </section>

                        {/* Changes to Policy */}
                        <section className="mb-12">
                            <h2 className="font-heading text-2xl mb-4">Changes to This Policy</h2>
                            <p className="font-body text-muted-foreground leading-relaxed">
                                We may update this Privacy Policy from time to time to reflect changes in our practices or for operational, legal, or regulatory reasons. We will post any changes on this page and update the "Last updated" date at the bottom. We encourage you to review this policy periodically.
                            </p>
                        </section>

                        {/* Contact */}
                        <section className="mb-12">
                            <h2 className="font-heading text-2xl mb-4">Contact Us</h2>
                            <p className="font-body text-muted-foreground leading-relaxed mb-4">
                                If you have any questions about this Privacy Policy, please contact us:
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

export default PrivacyPage;
