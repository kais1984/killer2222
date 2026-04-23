import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Camera, Upload, X, Check, Info, Save, ChevronRight } from "lucide-react";
import { useWishlist } from "@/contexts/WishlistContext";

interface BodyType {
  id: string;
  name: string;
  description: string;
  icon: string;
  recommendations: string[];
  avoid: string[];
}

const bodyTypes: BodyType[] = [
  { 
    id: "hourglass", 
    name: "Hourglass", 
    description: "Balanced bust and hips with a defined waist", 
    icon: "👗",
    recommendations: ["Mermaid", "Trumpet", "Fitted bodice with full skirt"],
    avoid: ["Straight sheath without definition"]
  },
  { 
    id: "pear", 
    name: "Pear", 
    description: "Hips wider than shoulders", 
    icon: "🍐",
    recommendations: ["A-Line", "Ball Gown", "Embellished bodice"],
    avoid: ["Mermaid", "Horizontal details at hip"]
  },
  { 
    id: "apple", 
    name: "Apple", 
    description: "Fuller midsection with slim legs", 
    icon: "🍎",
    recommendations: ["A-Line", "Empire waist", "Flowing skirts"],
    avoid: ["Tight waistband", "Full ball gown"]
  },
  { 
    id: "rectangle", 
    name: "Rectangle", 
    description: "Balanced proportions throughout", 
    icon: "📏",
    recommendations: ["Ball Gown", "Mermaid", "Belted waist"],
    avoid: ["Straight silhouettes without shape"]
  },
  { 
    id: "inverted-triangle", 
    name: "Inverted Triangle", 
    description: "Broader shoulders than hips", 
    icon: "🔺",
    recommendations: ["A-Line", "Ball Gown", "Skirt with volume"],
    avoid: ["Strapless", "Bold shoulder details"]
  },
];

const VirtualTryOn = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [step, setStep] = useState<"select" | "upload" | "result">("select");
  const [selectedBodyType, setSelectedBodyType] = useState<string | null>(null);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [savedMeasurements, setSavedMeasurements] = useState<Record<string, string>>({});
  const [showSaveSuccess, setShowSaveSuccess] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load saved body type from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('bodyType');
    if (saved) {
      setSelectedBodyType(saved);
      setSavedMeasurements({ bodyType: saved });
    }
  }, []);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setUploadedImage(event.target?.result as string);
        setStep("result");
      };
      reader.readAsDataURL(file);
    }
  };

  const handleBodyTypeSelect = (bodyTypeId: string) => {
    setSelectedBodyType(bodyTypeId);
    setStep("upload");
  };

  const saveToProfile = () => {
    if (selectedBodyType) {
      localStorage.setItem('bodyType', selectedBodyType);
      localStorage.setItem('bodyMeasurements', JSON.stringify({
        bodyType: selectedBodyType,
        savedAt: new Date().toISOString()
      }));
      setSavedMeasurements({ bodyType: selectedBodyType });
      setShowSaveSuccess(true);
      setTimeout(() => setShowSaveSuccess(false), 2000);
    }
  };

  const resetTryOn = () => {
    setStep("select");
    setSelectedBodyType(null);
    setUploadedImage(null);
  };

  const selectedBody = bodyTypes.find(b => b.id === selectedBodyType);

  return (
    <>
      {/* Button to Open Try-On */}
      <button
        onClick={() => setIsOpen(true)}
        className="w-full py-3 border border-border rounded-lg flex items-center justify-center gap-2 hover:border-gold hover:bg-gold/5 transition-colors mb-4"
      >
        <Camera size={18} className="text-gold" />
        <span className="font-body text-xs tracking-[0.2em] uppercase">Virtual Try-On</span>
      </button>

      {/* Modal */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
            onClick={() => setIsOpen(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl max-w-lg w-full max-h-[90vh] overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="p-6 border-b border-border flex items-center justify-between">
                <div>
                  <h3 className="font-heading text-xl">Virtual Try-On</h3>
                  <p className="font-body text-xs text-muted-foreground">See how the dress fits your style</p>
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                >
                  <X size={20} />
                </button>
              </div>

              {/* Content */}
              <div className="p-6">
                {step === "select" && (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                    <div className="flex items-center gap-2 mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <Info size={18} className="text-blue-500" />
                      <p className="text-sm text-blue-700">Select your body type for personalized fit recommendations</p>
                    </div>
                    
                    <p className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground mb-4">
                      Select Your Body Type
                    </p>
                    
                    <div className="grid grid-cols-2 gap-3">
                      {bodyTypes.map((body) => (
                        <button
                          key={body.id}
                          onClick={() => handleBodyTypeSelect(body.id)}
                          className={`p-4 border rounded-lg text-left transition-all hover:border-gold ${
                            selectedBodyType === body.id ? "border-gold bg-gold/5" : "border-border"
                          }`}
                        >
                          <span className="text-2xl block mb-2">{body.icon}</span>
                          <p className="font-heading text-sm">{body.name}</p>
                          <p className="font-body text-xs text-muted-foreground mt-1">{body.description}</p>
                        </button>
                      ))}
                    </div>
                  </motion.div>
                )}

                {step === "upload" && (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                    <p className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground mb-4">
                      Upload Your Photo (Optional)
                    </p>
                    
                    <div
                      onClick={() => fileInputRef.current?.click()}
                      className="border-2 border-dashed border-border rounded-xl p-8 text-center cursor-pointer hover:border-gold transition-colors"
                    >
                      <Upload size={32} className="mx-auto text-muted-foreground mb-3" />
                      <p className="font-body text-sm text-muted-foreground">
                        Click to upload a full-body photo
                      </p>
                      <p className="font-body text-xs text-muted-foreground mt-2">
                        or skip to see body type recommendations
                      </p>
                    </div>
                    
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/*"
                      onChange={handleImageUpload}
                      className="hidden"
                    />
                    
                    <button
                      onClick={() => setStep("result")}
                      className="w-full mt-4 py-3 bg-gray-100 hover:bg-gray-200 rounded-lg font-body text-sm transition-colors"
                    >
                      Skip & Continue
                    </button>
                  </motion.div>
                )}

                {step === "result" && (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                    <div className="text-center mb-6">
                      <div className="w-20 h-20 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
                        <Check size={32} className="text-green-600" />
                      </div>
                      <h4 className="font-heading text-lg mb-2">Recommendations Ready!</h4>
                      <p className="font-body text-sm text-muted-foreground">
                        Based on your {selectedBody?.name || "selected"} body type, 
                        this style will accentuate your best features.
                      </p>
                    </div>

                    {selectedBody && (
                      <div className="space-y-4">
                        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                          <p className="font-body text-[10px] tracking-[0.2em] uppercase text-green-700 mb-2">Perfect For You</p>
                          <ul className="font-body text-sm text-green-800 space-y-1">
                            {selectedBody.recommendations.map((rec, i) => (
                              <li key={i} className="flex items-center gap-2">
                                <Check size={14} className="text-green-600" />
                                {rec}
                              </li>
                            ))}
                          </ul>
                        </div>

                        <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                          <p className="font-body text-[10px] tracking-[0.2em] uppercase text-red-700 mb-2">Best Avoided</p>
                          <ul className="font-body text-sm text-red-800 space-y-1">
                            {selectedBody.avoid.map((item, i) => (
                              <li key={i} className="flex items-center gap-2">
                                <X size={14} className="text-red-500" />
                                {item}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    )}

                    {uploadedImage && (
                      <div className="mt-4">
                        <p className="font-body text-xs text-muted-foreground mb-2">Your uploaded photo:</p>
                        <img 
                          src={uploadedImage} 
                          alt="Uploaded" 
                          className="w-32 h-32 object-cover rounded-lg mx-auto"
                        />
                      </div>
                    )}

                    {/* Save to Profile */}
                    <div className="mt-6 space-y-3">
                      <button
                        onClick={saveToProfile}
                        className="w-full py-3 bg-gold text-white rounded-lg flex items-center justify-center gap-2 hover:bg-gold/90 transition-colors"
                      >
                        <Save size={18} />
                        Save to My Profile
                      </button>
                      
                      {showSaveSuccess && (
                        <p className="text-center text-sm text-green-600 flex items-center justify-center gap-2">
                          <Check size={14} /> Saved successfully!
                        </p>
                      )}
                      
                      <button
                        onClick={resetTryOn}
                        className="w-full py-3 border border-border rounded-lg hover:border-gold transition-colors"
                      >
                        Try Again
                      </button>
                    </div>
                  </motion.div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default VirtualTryOn;