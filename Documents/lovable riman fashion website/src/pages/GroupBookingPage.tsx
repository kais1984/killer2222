import { useState } from "react";
import { motion } from "framer-motion";
import { Users, Calendar, Heart, Mail, Phone, Check, ChevronRight, Plus, Minus, Trash2 } from "lucide-react";
import Layout from "@/components/Layout";
import { useToast } from "@/hooks/use-toast";

interface GroupMember {
  id: string;
  name: string;
  size: string;
  color: string;
}

const discountTiers = [
  { min: 5, discount: 10, label: "5+ dresses - 10% off" },
  { min: 10, discount: 15, label: "10+ dresses - 15% off" },
];

const sizes = ["XS", "S", "M", "L", "XL", "XXL"];
const colors = [
  { id: "ivory", name: "Ivory", hex: "#FFFFF0" },
  { id: "white", name: "White", hex: "#FFFFFF" },
  { id: "champagne", name: "Champagne", hex: "#F7E7CE" },
  { id: "blush", name: "Blush", hex: "#DE5D83" },
  { id: "nude", name: "Nude", hex: "#E3BC9A" },
  { id: "silver", name: "Silver", hex: "#C0C0C0" },
];

const GroupBookingPage = () => {
  const [members, setMembers] = useState<GroupMember[]>([
    { id: "1", name: "", size: "", color: "" },
  ]);
  const [contactInfo, setContactInfo] = useState({ name: "", email: "", phone: "", message: "" });
  const [selectedDress, setSelectedDress] = useState("");
  const [step, setStep] = useState(1);
  const { toast } = useToast();

  const addMember = () => {
    setMembers([...members, { id: Date.now().toString(), name: "", size: "", color: "" }]);
  };

  const removeMember = (id: string) => {
    if (members.length > 1) {
      setMembers(members.filter(m => m.id !== id));
    }
  };

  const updateMember = (id: string, field: keyof GroupMember, value: string) => {
    setMembers(members.map(m => m.id === id ? { ...m, [field]: value } : m));
  };

  const getCurrentDiscount = () => {
    const tier = discountTiers.find(t => members.length >= t.min);
    return tier || discountTiers[0];
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    toast({
      title: "Group Booking Request Submitted!",
      description: "We'll contact you within 24 hours to confirm your group booking.",
    });
    setStep(3);
  };

  return (
    <Layout>
      <section className="pt-32 pb-16 px-6 bg-champagne">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl mx-auto text-center"
        >
          <Users className="mx-auto text-gold mb-4" size={32} />
          <p className="font-body text-[10px] tracking-[0.4em] uppercase text-muted-foreground mb-4">Special Packages</p>
          <h1 className="heading-display text-4xl md:text-5xl mb-6">Group Bookings</h1>
          <p className="font-body text-muted-foreground max-w-2xl mx-auto mb-8">
            Planning a wedding or event with bridesmaids? Book together and enjoy exclusive group discounts
          </p>
        </motion.div>
      </section>

      <section className="section-padding">
        <div className="max-w-4xl mx-auto px-6">
          {/* Discount Tiers */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-12"
          >
            <h2 className="font-heading text-2xl text-center mb-6">Group Discounts</h2>
            <div className="grid md:grid-cols-2 gap-4">
              {discountTiers.map((tier) => (
                <div
                  key={tier.min}
                  className={`p-6 rounded-xl border text-center transition-all ${
                    members.length >= tier.min
                      ? "border-gold bg-gold/5"
                      : "border-border"
                  }`}
                >
                  <p className="font-heading text-2xl text-gold mb-2">{tier.discount}% OFF</p>
                  <p className="font-body text-sm text-muted-foreground">{tier.label}</p>
                </div>
              ))}
            </div>
          </motion.div>

          {step === 1 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <h2 className="font-heading text-2xl mb-6">Add Group Members</h2>
              <p className="font-body text-sm text-muted-foreground mb-6">
                Add all bridesmaids or group members who need dresses. Current group size: {members.length}
              </p>

              <div className="space-y-4 mb-8">
                {members.map((member, index) => (
                  <div key={member.id} className="bg-white border border-border rounded-xl p-4">
                    <div className="flex justify-between items-center mb-4">
                      <h3 className="font-heading text-sm">Member {index + 1}</h3>
                      {members.length > 1 && (
                        <button
                          onClick={() => removeMember(member.id)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <Trash2 size={18} />
                        </button>
                      )}
                    </div>
                    <div className="grid md:grid-cols-3 gap-4">
                      <div>
                        <label className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground block mb-2">
                          Name
                        </label>
                        <input
                          type="text"
                          value={member.name}
                          onChange={(e) => updateMember(member.id, "name", e.target.value)}
                          className="w-full border border-border px-4 py-2 font-body text-sm focus:outline-none focus:border-gold"
                          placeholder="Member name"
                        />
                      </div>
                      <div>
                        <label className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground block mb-2">
                          Size
                        </label>
                        <select
                          value={member.size}
                          onChange={(e) => updateMember(member.id, "size", e.target.value)}
                          className="w-full border border-border px-4 py-2 font-body text-sm focus:outline-none focus:border-gold"
                        >
                          <option value="">Select size</option>
                          {sizes.map(s => <option key={s} value={s}>{s}</option>)}
                        </select>
                      </div>
                      <div>
                        <label className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground block mb-2">
                          Color
                        </label>
                        <select
                          value={member.color}
                          onChange={(e) => updateMember(member.id, "color", e.target.value)}
                          className="w-full border border-border px-4 py-2 font-body text-sm focus:outline-none focus:border-gold"
                        >
                          <option value="">Select color</option>
                          {colors.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                        </select>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <button
                onClick={addMember}
                className="w-full py-3 border border-dashed border-border rounded-xl flex items-center justify-center gap-2 hover:border-gold transition-colors mb-8"
              >
                <Plus size={18} />
                Add Another Member
              </button>

              <button
                onClick={() => setStep(2)}
                className="btn-luxury w-full"
              >
                Continue to Contact
                <ChevronRight size={18} className="ml-2 inline" />
              </button>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <h2 className="font-heading text-2xl mb-6">Contact Information</h2>
              
              <div className="bg-gold/10 border border-gold/30 rounded-xl p-4 mb-6">
                <p className="font-body text-sm">
                  <strong>{members.length} members</strong> - <strong>{getCurrentDiscount().discount}% discount</strong> applied!
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground block mb-2">
                    Your Name
                  </label>
                  <input
                    type="text"
                    required
                    value={contactInfo.name}
                    onChange={(e) => setContactInfo({ ...contactInfo, name: e.target.value })}
                    className="w-full border border-border px-4 py-3 font-body text-sm focus:outline-none focus:border-gold"
                    placeholder="Your name"
                  />
                </div>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground block mb-2">
                      <Mail size={14} className="inline mr-2" />
                      Email
                    </label>
                    <input
                      type="email"
                      required
                      value={contactInfo.email}
                      onChange={(e) => setContactInfo({ ...contactInfo, email: e.target.value })}
                      className="w-full border border-border px-4 py-3 font-body text-sm focus:outline-none focus:border-gold"
                      placeholder="your@email.com"
                    />
                  </div>
                  <div>
                    <label className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground block mb-2">
                      <Phone size={14} className="inline mr-2" />
                      Phone
                    </label>
                    <input
                      type="tel"
                      required
                      value={contactInfo.phone}
                      onChange={(e) => setContactInfo({ ...contactInfo, phone: e.target.value })}
                      className="w-full border border-border px-4 py-3 font-body text-sm focus:outline-none focus:border-gold"
                      placeholder="+971 55 123 4567"
                    />
                  </div>
                </div>
                <div>
                  <label className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground block mb-2">
                    Additional Notes
                  </label>
                  <textarea
                    rows={3}
                    value={contactInfo.message}
                    onChange={(e) => setContactInfo({ ...contactInfo, message: e.target.value })}
                    className="w-full border border-border px-4 py-3 font-body text-sm focus:outline-none focus:border-gold resize-none"
                    placeholder="Any special requests or questions..."
                  />
                </div>
                <button type="submit" className="btn-luxury w-full">
                  Submit Group Booking Request
                </button>
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="w-full py-2 text-sm text-muted-foreground hover:text-foreground"
                >
                  Back to Members
                </button>
              </form>
            </motion.div>
          )}

          {step === 3 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center py-12"
            >
              <div className="w-20 h-20 mx-auto mb-6 bg-green-100 rounded-full flex items-center justify-center">
                <Check size={32} className="text-green-600" />
              </div>
              <h2 className="font-heading text-3xl mb-4">Request Submitted!</h2>
              <p className="font-body text-muted-foreground mb-8">
                Thank you for your group booking request. Our team will contact you within 24 hours.
              </p>
              <a href="/contact" className="btn-luxury">
                <Calendar size={18} className="mr-2 inline" />
                Book Consultation
              </a>
            </motion.div>
          )}
        </div>
      </section>
    </Layout>
  );
};

export default GroupBookingPage;