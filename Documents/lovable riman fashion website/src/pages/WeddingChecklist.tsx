import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { CheckCircle, Circle, ChevronDown, ChevronUp, Mail, Download, Share2 } from "lucide-react";
import Layout from "@/components/Layout";
import { useToast } from "@/hooks/use-toast";

interface ChecklistItem {
  id: string;
  text: string;
  completed: boolean;
}

interface ChecklistCategory {
  id: string;
  title: string;
  monthsBefore: string;
  items: ChecklistItem[];
}

const initialChecklist: ChecklistCategory[] = [
  {
    id: "12-months",
    title: "12 Months Before",
    monthsBefore: "12 months",
    items: [
      { id: "1-1", text: "Set your wedding budget", completed: false },
      { id: "1-2", text: "Create a wedding planning timeline", completed: false },
      { id: "1-3", text: "Start researching wedding venues", completed: false },
      { id: "1-4", text: "Start looking for your wedding dress", completed: false },
      { id: "1-5", text: "Book your wedding planner (if needed)", completed: false },
    ],
  },
  {
    id: "9-months",
    title: "9 Months Before",
    monthsBefore: "9 months",
    items: [
      { id: "2-1", text: "Finalize your venue", completed: false },
      { id: "2-2", text: "Book photographer and videographer", completed: false },
      { id: "2-3", text: "Start dress shopping appointments", completed: false },
      { id: "2-4", text: "Choose your wedding party", completed: false },
      { id: "2-5", text: "Book caterer (if not provided by venue)", completed: false },
    ],
  },
  {
    id: "6-months",
    title: "6 Months Before",
    monthsBefore: "6 months",
    items: [
      { id: "3-1", text: "Order your wedding dress", completed: false },
      { id: "3-2", text: "Book florist", completed: false },
      { id: "3-3", text: "Book DJ or live music", completed: false },
      { id: "3-4", text: "Order wedding invitations", completed: false },
      { id: "3-5", text: "Plan honeymoon", completed: false },
    ],
  },
  {
    id: "3-months",
    title: "3 Months Before",
    monthsBefore: "3 months",
    items: [
      { id: "4-1", text: "Send wedding invitations", completed: false },
      { id: "4-2", text: "Final dress fitting", completed: false },
      { id: "4-3", text: "Book hair and makeup artist", completed: false },
      { id: "4-4", text: "Order wedding cake", completed: false },
      { id: "4-5", text: "Arrange transportation", completed: false },
    ],
  },
  {
    id: "1-month",
    title: "1 Month Before",
    monthsBefore: "1 month",
    items: [
      { id: "5-1", text: "Confirm all vendor details", completed: false },
      { id: "5-2", text: "Final headcount for caterer", completed: false },
      { id: "5-3", text: "Pick up wedding dress", completed: false },
      { id: "5-4", text: "Write wedding vows", completed: false },
      { id: "5-5", text: "Apply for marriage license", completed: false },
    ],
  },
  {
    id: "1-week",
    title: "1 Week Before",
    monthsBefore: "1 week",
    items: [
      { id: "6-1", text: "Confirm timeline with vendors", completed: false },
      { id: "6-2", text: "Pack for honeymoon", completed: false },
      { id: "6-3", text: "Prepare payment envelopes for vendors", completed: false },
      { id: "6-4", text: "Get manicure and pedicure", completed: false },
      { id: "6-5", text: "Break in your wedding shoes", completed: false },
    ],
  },
  {
    id: "wedding-day",
    title: "Wedding Day",
    monthsBefore: "The big day",
    items: [
      { id: "7-1", text: "Eat a good breakfast", completed: false },
      { id: "7-2", text: "Have your hair and makeup done", completed: false },
      { id: "7-3", text: "Get into your dress", completed: false },
      { id: "7-4", text: "Take photos with bridal party", completed: false },
      { id: "7-5", text: "Enjoy your special day!", completed: false },
    ],
  },
];

const WeddingChecklist = () => {
  const [checklist, setChecklist] = useState<ChecklistCategory[]>(initialChecklist);
  const [expandedCategories, setExpandedCategories] = useState<string[]>(["12-months"]);
  const [email, setEmail] = useState("");
  const [showEmailModal, setShowEmailModal] = useState(false);
  const { toast } = useToast();

  // Load from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('weddingChecklist');
    if (saved) {
      setChecklist(JSON.parse(saved));
    }
  }, []);

  // Save to localStorage
  useEffect(() => {
    localStorage.setItem('weddingChecklist', JSON.stringify(checklist));
  }, [checklist]);

  const toggleCategory = (id: string) => {
    setExpandedCategories(prev => 
      prev.includes(id) ? prev.filter(c => c !== id) : [...prev, id]
    );
  };

  const toggleItem = (categoryId: string, itemId: string) => {
    setChecklist(prev => prev.map(cat => 
      cat.id === categoryId 
        ? { ...cat, items: cat.items.map(item => 
            item.id === itemId ? { ...item, completed: !item.completed } : item
          )}
        : cat
    ));
  };

  const getProgress = () => {
    const total = checklist.reduce((acc, cat) => acc + cat.items.length, 0);
    const completed = checklist.reduce((acc, cat) => 
      acc + cat.items.filter(item => item.completed).length, 0
    );
    return Math.round((completed / total) * 100);
  };

  const sendChecklist = () => {
    if (!email) return;
    toast({
      title: "Checklist sent!",
      description: `We'll email your checklist to ${email}`,
    });
    setShowEmailModal(false);
    setEmail("");
  };

  const progress = getProgress();

  return (
    <Layout>
      <section className="pt-32 pb-16 px-6 bg-champagne">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl mx-auto text-center"
        >
          <CheckCircle className="mx-auto text-gold mb-4" size={32} />
          <p className="font-body text-[10px] tracking-[0.4em] uppercase text-muted-foreground mb-4">Stay Organized</p>
          <h1 className="heading-display text-4xl md:text-5xl mb-6">Wedding Checklist</h1>
          <p className="font-body text-muted-foreground max-w-2xl mx-auto mb-8">
            Your complete wedding planning guide. Track your progress and stay on top of every detail
          </p>
        </motion.div>
      </section>

      <section className="section-padding">
        <div className="max-w-3xl mx-auto px-6">
          {/* Progress Bar */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="bg-white border border-border rounded-2xl p-6 mb-8"
          >
            <div className="flex justify-between items-center mb-4">
              <h2 className="font-heading text-xl">Your Progress</h2>
              <span className="font-heading text-2xl text-gold">{progress}%</span>
            </div>
            <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                className="h-full bg-gold"
              />
            </div>
            <div className="flex gap-4 mt-4">
              <button
                onClick={() => setShowEmailModal(true)}
                className="flex-1 py-2 border border-border rounded-lg flex items-center justify-center gap-2 hover:border-gold text-sm"
              >
                <Mail size={16} />
                Email Checklist
              </button>
              <button
                onClick={() => {
                  const data = JSON.stringify(checklist, null, 2);
                  const blob = new Blob([data], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = 'wedding-checklist.json';
                  a.click();
                }}
                className="flex-1 py-2 border border-border rounded-lg flex items-center justify-center gap-2 hover:border-gold text-sm"
              >
                <Download size={16} />
                Download
              </button>
            </div>
          </motion.div>

          {/* Categories */}
          <div className="space-y-4">
            {checklist.map((category, catIndex) => {
              const completedCount = category.items.filter(i => i.completed).length;
              const isExpanded = expandedCategories.includes(category.id);
              
              return (
                <motion.div
                  key={category.id}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: catIndex * 0.1 }}
                  className="bg-white border border-border rounded-xl overflow-hidden"
                >
                  <button
                    onClick={() => toggleCategory(category.id)}
                    className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        completedCount === category.items.length
                          ? "bg-green-100 text-green-600"
                          : "bg-gold/10 text-gold"
                      }`}>
                        {completedCount === category.items.length ? (
                          <CheckCircle size={20} />
                        ) : (
                          <span className="font-heading text-sm">{completedCount}/{category.items.length}</span>
                        )}
                      </div>
                      <div className="text-left">
                        <h3 className="font-heading text-lg">{category.title}</h3>
                        <p className="font-body text-xs text-muted-foreground">{category.monthsBefore}</p>
                      </div>
                    </div>
                    {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                  </button>
                  
                  {isExpanded && (
                    <div className="px-4 pb-4 space-y-2">
                      {category.items.map((item) => (
                        <button
                          key={item.id}
                          onClick={() => toggleItem(category.id, item.id)}
                          className="w-full p-3 flex items-center gap-3 hover:bg-gray-50 rounded-lg transition-colors text-left"
                        >
                          {item.completed ? (
                            <CheckCircle size={20} className="text-green-500 shrink-0" />
                          ) : (
                            <Circle size={20} className="text-gray-300 shrink-0" />
                          )}
                          <span className={`font-body text-sm ${
                            item.completed ? "text-muted-foreground line-through" : ""
                          }`}>
                            {item.text}
                          </span>
                        </button>
                      ))}
                    </div>
                  )}
                </motion.div>
              );
            })}
          </div>

          {/* Reset Button */}
          <button
            onClick={() => {
              setChecklist(initialChecklist);
              localStorage.removeItem('weddingChecklist');
            }}
            className="w-full mt-8 py-3 text-sm text-muted-foreground hover:text-red-500"
          >
            Reset Checklist
          </button>
        </div>
      </section>

      {/* Email Modal */}
      {showEmailModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6">
            <h3 className="font-heading text-xl mb-4">Email Your Checklist</h3>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              className="w-full border border-border px-4 py-3 font-body text-sm focus:outline-none focus:border-gold mb-4"
            />
            <div className="flex gap-3">
              <button
                onClick={() => setShowEmailModal(false)}
                className="flex-1 py-2 border border-border rounded-lg"
              >
                Cancel
              </button>
              <button onClick={sendChecklist} className="flex-1 btn-luxury">
                Send
              </button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
};

export default WeddingChecklist;