import { motion } from "framer-motion";
import { Scissors, PenTool, Palette, Award, Heart, Play } from "lucide-react";
import Layout from "@/components/Layout";

const atelierStories = [
  {
    id: "1",
    title: "The Art of Hand Embroidery",
    description: "Each dress features hours of meticulous hand embroidery by our skilled artisans. Our master embroiders use traditional techniques passed down through generations.",
    image: "/images/atelier/embroidery.jpg",
    icon: PenTool,
  },
  {
    id: "2",
    title: "European Fabric Sourcing",
    description: "We travel to the finest fabric houses in Italy, France, and Spain to source unique silks, laces, and satins for our exclusive collections.",
    image: "/images/atelier/fabrics.jpg",
    icon: Palette,
  },
  {
    id: "3",
    title: "Made to Measure",
    description: "Every bride deserves the perfect fit. Our in-house tailors craft made-to-measure gowns that flatter each unique body shape.",
    image: "/images/atelier/measure.jpg",
    icon: Scissors,
  },
];

const teamMembers = [
  {
    name: "Riman Hassan",
    role: "Founder & Creative Director",
    bio: "With over 20 years of experience in bridal fashion, Riman founded Riman Fashion to create dream dresses for modern brides.",
    image: "/images/team/riman.jpg",
  },
  {
    name: "Fatima Al Mahmoud",
    role: "Head of Alterations",
    bio: "Master tailor with 15 years of experience in bridal alterations, ensuring perfect fits for every bride.",
    image: "/images/team/fatima.jpg",
  },
  {
    name: "Aisha Rahman",
    role: "Lead Designer",
    bio: "Trained at prestigious fashion houses in Paris, Aisha brings contemporary elegance to our bridal collections.",
    image: "/images/team/aisha.jpg",
  },
];

const AtelierPage = () => {
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
          <p className="font-body text-[10px] tracking-[0.4em] uppercase text-muted-foreground mb-4">Behind the Scenes</p>
          <h1 className="heading-display text-4xl md:text-5xl mb-6">Our Atelier</h1>
          <p className="font-body text-muted-foreground max-w-2xl mx-auto mb-8">
            Discover the craftsmanship, passion, and artistry that goes into every dress we create
          </p>
        </motion.div>
      </section>

      {/* Video Section */}
      <section className="py-20 bg-black">
        <div className="max-w-6xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="relative aspect-video rounded-2xl overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent z-10" />
            <div className="w-full h-full bg-gray-900 flex items-center justify-center">
              <div className="text-center z-20">
                <div className="w-20 h-20 mx-auto mb-6 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                  <Play size={32} className="text-white ml-1" />
                </div>
                <h3 className="font-heading text-2xl text-white mb-2">The Art of Bridal Couture</h3>
                <p className="font-body text-white/70">Watch our artisans create magic</p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Craftsmanship Stories */}
      <section className="section-padding">
        <div className="max-w-6xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="font-heading text-3xl md:text-4xl mb-4">Craftsmanship</h2>
            <p className="font-body text-muted-foreground">The art of creating dream dresses</p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {atelierStories.map((story, index) => {
              const Icon = story.icon;
              return (
                <motion.div
                  key={story.id}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="bg-white border border-border rounded-xl overflow-hidden hover:shadow-lg transition-shadow"
                >
                  <div className="aspect-[4/3] bg-gray-200 relative">
                    <div className="absolute inset-0 flex items-center justify-center bg-champagne">
                      <Icon size={48} className="text-gold/50" />
                    </div>
                  </div>
                  <div className="p-6">
                    <div className="w-12 h-12 bg-gold/10 rounded-full flex items-center justify-center mb-4">
                      <Icon size={24} className="text-gold" />
                    </div>
                    <h3 className="font-heading text-lg mb-2">{story.title}</h3>
                    <p className="font-body text-sm text-muted-foreground">{story.description}</p>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-20 bg-black text-white">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {[
              { number: "500+", label: "Bridal Dresses Created" },
              { number: "20+", label: "Years of Experience" },
              { number: "98%", label: "Customer Satisfaction" },
              { number: "50+", label: "Skilled Artisans" },
            ].map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <p className="font-heading text-4xl md:text-5xl text-gold mb-2">{stat.number}</p>
                <p className="font-body text-xs tracking-[0.2em] uppercase text-white/70">{stat.label}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Team */}
      <section className="section-padding">
        <div className="max-w-6xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="font-heading text-3xl md:text-4xl mb-4">Meet Our Team</h2>
            <p className="font-body text-muted-foreground">The talented people behind your dream dress</p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {teamMembers.map((member, index) => (
              <motion.div
                key={member.name}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="text-center"
              >
                <div className="aspect-square bg-gray-200 rounded-full mx-auto mb-6 max-w-[200px] relative overflow-hidden">
                  <div className="absolute inset-0 flex items-center justify-center bg-champagne">
                    <Heart size={48} className="text-gold/30" />
                  </div>
                </div>
                <h3 className="font-heading text-lg">{member.name}</h3>
                <p className="font-body text-xs tracking-[0.2em] uppercase text-gold mb-3">{member.role}</p>
                <p className="font-body text-sm text-muted-foreground max-w-xs mx-auto">{member.bio}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Awards */}
      <section className="py-20 bg-champagne">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <Award size={48} className="mx-auto text-gold mb-6" />
            <h2 className="font-heading text-3xl mb-6">Recognition</h2>
            <p className="font-body text-muted-foreground mb-8">
              We're honored to have received recognition for our work in bridal fashion
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white p-6 rounded-xl border border-border">
                <p className="font-heading text-lg mb-2">Best Bridal Designer</p>
                <p className="font-body text-xs text-muted-foreground">Dubai Fashion Awards 2024</p>
              </div>
              <div className="bg-white p-6 rounded-xl border border-border">
                <p className="font-heading text-lg mb-2">Excellence in Craftsmanship</p>
                <p className="font-body text-xs text-muted-foreground">UAE Luxury Awards 2023</p>
              </div>
              <div className="bg-white p-6 rounded-xl border border-border">
                <p className="font-heading text-lg mb-2">Top Bridal Shop</p>
                <p className="font-body text-xs text-muted-foreground">Sharjah Business Excellence 2023</p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-white">
        <div className="max-w-2xl mx-auto px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="font-heading text-3xl mb-6">Visit Our Atelier</h2>
            <p className="font-body text-muted-foreground mb-8">
              Experience our craftsmanship in person. Book a private consultation today.
            </p>
            <a href="/contact" className="btn-luxury">
              Book Consultation
            </a>
          </motion.div>
        </div>
      </section>
    </Layout>
  );
};

export default AtelierPage;