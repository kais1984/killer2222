import { useState } from "react";
import { motion } from "framer-motion";
import { Check, Palette, Sparkles } from "lucide-react";

interface FabricOption {
  id: string;
  name: string;
  description: string;
  premium?: boolean;
}

interface ColorOption {
  id: string;
  name: string;
  hex: string;
}

const fabrics: FabricOption[] = [
  { id: "silk", name: "Pure Silk", description: "Luxurious natural silk with beautiful drape", premium: true },
  { id: "chiffon", name: "Silk Chiffon", description: "Lightweight and ethereal flow", premium: false },
  { id: "lace", name: "French Lace", description: "Delicate intricate lace patterns", premium: true },
  { id: "satin", name: "Mikado Satin", description: "Structured and elegant shine", premium: false },
  { id: "tulle", name: "Soft Tulle", description: "Romantic and airy layers", premium: false },
  { id: "organza", name: "Embroidery Organza", description: "Detailed embroidery on sheer fabric", premium: true },
];

const colors: ColorOption[] = [
  { id: "ivory", name: "Ivory", hex: "#FFFFF0" },
  { id: "white", name: "Pure White", hex: "#FFFFFF" },
  { id: "champagne", name: "Champagne", hex: "#F7E7CE" },
  { id: "blush", name: "Blush Pink", hex: "#DE5D83" },
  { id: "nude", name: "Nude", hex: "#E3BC9A" },
  { id: "silver", name: "Silver", hex: "#C0C0C0" },
  { id: "gold", name: "Gold", hex: "#FFD700" },
  { id: "black", name: "Black", hex: "#000000" },
  { id: "red", name: "Ruby Red", hex: "#9B111E" },
  { id: "navy", name: "Navy", hex: "#000080" },
  { id: "burgundy", name: "Burgundy", hex: "#800020" },
  { id: "sage", name: "Sage Green", hex: "#9DC183" },
];

interface FabricCustomizationProps {
  productName?: string;
  onCustomizationChange?: (fabric: string, color: string) => void;
}

const FabricCustomization = ({ productName, onCustomizationChange }: FabricCustomizationProps) => {
  const [selectedFabric, setSelectedFabric] = useState<string | null>(null);
  const [selectedColor, setSelectedColor] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"fabric" | "color">("fabric");

  const handleFabricSelect = (fabricId: string) => {
    setSelectedFabric(fabricId);
    onCustomizationChange?.(fabricId, selectedColor || "");
  };

  const handleColorSelect = (colorId: string) => {
    setSelectedColor(colorId);
    onCustomizationChange?.(selectedFabric || "", colorId);
  };

  const selectedFabricData = fabrics.find(f => f.id === selectedFabric);
  const selectedColorData = colors.find(c => c.id === selectedColor);

  return (
    <div className="bg-white border border-border rounded-lg overflow-hidden">
      <div className="flex border-b border-border">
        <button
          onClick={() => setActiveTab("fabric")}
          className={`flex-1 py-4 px-6 font-body text-xs tracking-[0.2em] uppercase transition-colors ${
            activeTab === "fabric" 
              ? "bg-gold text-white" 
              : "bg-gray-50 text-muted-foreground hover:text-foreground"
          }`}
        >
          <Palette size={16} className="inline mr-2" />
          Fabric
        </button>
        <button
          onClick={() => setActiveTab("color")}
          className={`flex-1 py-4 px-6 font-body text-xs tracking-[0.2em] uppercase transition-colors ${
            activeTab === "color" 
              ? "bg-gold text-white" 
              : "bg-gray-50 text-muted-foreground hover:text-foreground"
          }`}
        >
          <Sparkles size={16} className="inline mr-2" />
          Color
        </button>
      </div>

      <div className="p-6">
        {activeTab === "fabric" ? (
          <div className="space-y-3">
            <p className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground mb-4">
              Select your preferred fabric
            </p>
            {fabrics.map((fabric) => (
              <motion.button
                key={fabric.id}
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                onClick={() => handleFabricSelect(fabric.id)}
                className={`w-full p-4 border rounded-lg text-left transition-all ${
                  selectedFabric === fabric.id
                    ? "border-gold bg-gold/5"
                    : "border-border hover:border-gold/50"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-heading text-sm">{fabric.name}</span>
                      {fabric.premium && (
                        <span className="px-2 py-0.5 bg-gold/20 text-gold text-[10px] font-medium rounded">
                          Premium
                        </span>
                      )}
                    </div>
                    <p className="font-body text-xs text-muted-foreground mt-1">
                      {fabric.description}
                    </p>
                  </div>
                  {selectedFabric === fabric.id && (
                    <Check size={20} className="text-gold" />
                  )}
                </div>
              </motion.button>
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            <p className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground mb-4">
              Select your preferred color
            </p>
            <div className="grid grid-cols-4 gap-3">
              {colors.map((color) => (
                <motion.button
                  key={color.id}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => handleColorSelect(color.id)}
                  className={`relative aspect-square rounded-lg border-2 transition-all ${
                    selectedColor === color.id
                      ? "border-gold shadow-lg"
                      : "border-transparent hover:border-gold/50"
                  }`}
                  style={{ backgroundColor: color.hex }}
                  title={color.name}
                >
                  {selectedColor === color.id && (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Check 
                        size={20} 
                        className={color.hex === "#FFFFFF" || color.hex === "#FFFFF0" ? "text-gray-800" : "text-white"} 
                        style={{ 
                          filter: "drop-shadow(0 1px 2px rgba(0,0,0,0.3))" 
                        }} 
                      />
                    </div>
                  )}
                </motion.button>
              ))}
            </div>
            {selectedColorData && (
              <motion.p 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="font-body text-sm text-center mt-4 text-gold"
              >
                Selected: {selectedColorData.name}
              </motion.p>
            )}
          </div>
        )}
      </div>

      {/* Summary */}
      {(selectedFabricData || selectedColorData) && (
        <div className="p-4 bg-champagne/30 border-t border-border">
          <p className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground mb-2">
            Your Customization
          </p>
          <div className="flex flex-wrap gap-2">
            {selectedFabricData && (
              <span className="px-3 py-1 bg-white border border-border rounded-full text-xs">
                {selectedFabricData.name}
              </span>
            )}
            {selectedColorData && (
              <span className="px-3 py-1 bg-white border border-border rounded-full text-xs flex items-center gap-2">
                <span 
                  className="w-3 h-3 rounded-full border border-border" 
                  style={{ backgroundColor: selectedColorData.hex }}
                />
                {selectedColorData.name}
              </span>
            )}
          </div>
          <p className="font-body text-[10px] text-muted-foreground mt-3">
            * Custom fabric and color selections may require additional production time.
            Our team will contact you to confirm details after ordering.
          </p>
        </div>
      )}
    </div>
  );
};

export default FabricCustomization;