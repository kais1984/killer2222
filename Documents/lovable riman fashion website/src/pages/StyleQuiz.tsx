import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronRight, Check, Heart, Sparkles, MessageCircle, ArrowRight } from "lucide-react";
import Layout from "@/components/Layout";
import { products } from "@/data/products";

interface QuizOption {
  id: string;
  label: string;
  description?: string;
}

interface QuizQuestion {
  id: string;
  question: string;
  options: QuizOption[];
}

const quizQuestions: QuizQuestion[] = [
  {
    id: "wedding-style",
    question: "What's your wedding style?",
    options: [
      { id: "classic", label: "Classic & Elegant", description: "Timeless silhouettes with traditional details" },
      { id: "modern", label: "Modern Minimalist", description: "Clean lines and contemporary designs" },
      { id: "boho", label: "Bohemian Free-Spirited", description: "Romantic and relaxed with natural elements" },
      { id: "glam", label: "Glamorous Luxe", description: "Dramatic details and statement pieces" },
    ],
  },
  {
    id: "silhouette",
    question: "Which silhouette do you prefer?",
    options: [
      { id: "ballgown", label: "Ball Gown", description: "Fairytale princess with full skirt" },
      { id: "mermaid", label: "Mermaid", description: "Fitted silhouette with dramatic flare" },
      { id: "a-line", label: "A-Line", description: "Flattering universally, fitted bodice with flowing skirt" },
      { id: "sheath", label: "Sheath", description: "Slim and sophisticated, body-skimming" },
    ],
  },
  {
    id: "neckline",
    question: "What's your ideal neckline?",
    options: [
      { id: "sweetheart", label: "Sweetheart", description: "Romantic heart-shaped neckline" },
      { id: "v-neck", label: "V-Neck", description: "Elongating and elegant" },
      { id: "off-shoulder", label: "Off Shoulder", description: "Romantic and contemporary" },
      { id: "high-neck", label: "High Neck", description: "Sophisticated and modest" },
    ],
  },
  {
    id: "fabric",
    question: "What fabric do you prefer?",
    options: [
      { id: "silk", label: "Silk", description: "Luxurious and lustrous" },
      { id: "lace", label: "Lace", description: "Romantic and feminine" },
      { id: "chiffon", label: "Chiffon", description: "Light and ethereal" },
      { id: "satin", label: "Satin", description: "Structured and elegant" },
    ],
  },
  {
    id: "budget",
    question: "What's your budget range?",
    options: [
      { id: "moderate", label: "AED 2,000 - 5,000", description: "Beautiful options at accessible prices" },
      { id: "mid-luxury", label: "AED 5,000 - 10,000", description: "Premium collection with exceptional quality" },
      { id: "luxury", label: "AED 10,000 - 20,000", description: "Bespoke designs and exclusive pieces" },
      { id: "haute-couture", label: "AED 20,000+", description: "One-of-a-kind custom creations" },
    ],
  },
  {
    id: "wedding-date",
    question: "When is your wedding?",
    options: [
      { id: "soon", label: "Within 3 months", description: "Quick delivery needed" },
      { id: "this-year", label: "3-6 months", description: "Standard timeline" },
      { id: "next-year", label: "6-12 months", description: "Plenty of time for custom work" },
      { id: "exploring", label: "Just exploring", description: "No specific timeline" },
    ],
  },
];

const StyleQuiz = () => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [showResults, setShowResults] = useState(false);
  const [recommendedProducts, setRecommendedProducts] = useState<typeof products>([]);

  const question = quizQuestions[currentQuestion];

  const handleAnswer = (optionId: string) => {
    setAnswers({ ...answers, [question.id]: optionId });
    
    if (currentQuestion < quizQuestions.length - 1) {
      setTimeout(() => setCurrentQuestion(currentQuestion + 1), 300);
    } else {
      calculateResults();
    }
  };

  const calculateResults = () => {
    const weddingStyle = answers["wedding-style"];
    const silhouette = answers["silhouette"];
    
    let filtered = [...products];
    
    if (weddingStyle === "classic") {
      filtered = filtered.filter(p => p.category?.toLowerCase().includes("bridal"));
    } else if (weddingStyle === "modern") {
      filtered = filtered.filter(p => p.category?.toLowerCase().includes("evening"));
    } else if (weddingStyle === "boho") {
      filtered = filtered.filter(p => p.productType === "rent" || p.productType === "both");
    }
    
    if (silhouette === "mermaid" || silhouette === "sheath") {
      filtered = filtered.slice(0, 4);
    }
    
    setRecommendedProducts(filtered.slice(0, 6));
    setShowResults(true);
  };

  const progress = ((currentQuestion + 1) / quizQuestions.length) * 100;

  return (
    <Layout>
      <section className="pt-32 pb-16 px-6 bg-champagne">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl mx-auto text-center"
        >
          <Sparkles className="mx-auto text-gold mb-4" size={32} />
          <p className="font-body text-[10px] tracking-[0.4em] uppercase text-muted-foreground mb-4">Find Your Perfect Dress</p>
          <h1 className="heading-display text-4xl md:text-5xl mb-6">Style Quiz</h1>
          <p className="font-body text-muted-foreground max-w-2xl mx-auto mb-8">
            Answer a few questions and we'll help you find your dream dress
          </p>
        </motion.div>
      </section>

      {!showResults ? (
        <section className="section-padding">
          <div className="max-w-2xl mx-auto px-6">
            {/* Progress Bar */}
            <div className="mb-12">
              <div className="flex justify-between items-center mb-3">
                <span className="font-body text-xs tracking-[0.2em] uppercase text-muted-foreground">
                  Question {currentQuestion + 1} of {quizQuestions.length}
                </span>
                <span className="font-body text-xs text-gold">{Math.round(progress)}%</span>
              </div>
              <div className="h-1 bg-gray-200 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  className="h-full bg-gold"
                />
              </div>
            </div>

            {/* Question */}
            <AnimatePresence mode="wait">
              <motion.div
                key={question.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                <h2 className="font-heading text-2xl md:text-3xl mb-8 text-center">{question.question}</h2>

                <div className="space-y-3">
                  {question.options.map((option) => (
                    <motion.button
                      key={option.id}
                      whileHover={{ scale: 1.01 }}
                      whileTap={{ scale: 0.99 }}
                      onClick={() => handleAnswer(option.id)}
                      className={`w-full p-5 border rounded-xl text-left transition-all ${
                        answers[question.id] === option.id
                          ? "border-gold bg-gold/5"
                          : "border-border hover:border-gold hover:bg-gold/5"
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-heading text-lg">{option.label}</p>
                          {option.description && (
                            <p className="font-body text-sm text-muted-foreground mt-1">{option.description}</p>
                          )}
                        </div>
                        {answers[question.id] === option.id && (
                          <Check size={20} className="text-gold" />
                        )}
                      </div>
                    </motion.button>
                  ))}
                </div>
              </motion.div>
            </AnimatePresence>

            {/* Navigation */}
            <div className="flex justify-between mt-8">
              <button
                onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
                disabled={currentQuestion === 0}
                className="text-sm text-muted-foreground hover:text-foreground disabled:opacity-50"
              >
                Back
              </button>
              <button
                onClick={() => setCurrentQuestion(currentQuestion + 1)}
                disabled={!answers[question.id]}
                className="btn-luxury disabled:opacity-50"
              >
                {currentQuestion === quizQuestions.length - 1 ? "See Results" : "Next"}
                <ChevronRight size={16} className="ml-2 inline" />
              </button>
            </div>
          </div>
        </section>
      ) : (
        <section className="section-padding">
          <div className="max-w-6xl mx-auto px-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center mb-12"
            >
              <div className="w-20 h-20 mx-auto mb-6 bg-gold/10 rounded-full flex items-center justify-center">
                <Heart size={32} className="text-gold" />
              </div>
              <h2 className="font-heading text-3xl mb-4">Your Perfect Match!</h2>
              <p className="font-body text-muted-foreground max-w-2xl mx-auto">
                Based on your style preferences, we've curated these recommendations just for you.
              </p>
            </motion.div>

            {/* Results Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
              {recommendedProducts.map((product, index) => (
                <motion.div
                  key={product.id}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="group"
                >
                  <a href={`/product/${product.id}`} className="block">
                    <div className="aspect-[3/4] overflow-hidden rounded-xl mb-4">
                      <img
                        src={product.images?.[0] || "/images/products/placeholder.jpg"}
                        alt={product.name}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      />
                    </div>
                    <h3 className="font-heading text-lg mb-1 group-hover:text-gold transition-colors">{product.name}</h3>
                    <p className="font-body text-sm text-muted-foreground">
                      {product.salePrice ? `AED ${product.salePrice.toLocaleString()}` : `AED ${product.rentalPrice?.toLocaleString()} / day`}
                    </p>
                  </a>
                </motion.div>
              ))}
            </div>

            {/* Actions */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a href="/collection/bridal" className="btn-luxury">
                View Full Collection
                <ArrowRight size={18} className="ml-2 inline" />
              </a>
              <a href="/contact" className="btn-luxury-outline">
                <MessageCircle size={18} className="ml-2 inline" />
                Book Consultation
              </a>
            </div>

            {/* Retake Quiz */}
            <button
              onClick={() => {
                setCurrentQuestion(0);
                setAnswers({});
                setShowResults(false);
              }}
              className="block mx-auto mt-8 text-sm text-muted-foreground hover:text-gold"
            >
              Retake Quiz
            </button>
          </div>
        </section>
      )}
    </Layout>
  );
};

export default StyleQuiz;