import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Info } from "lucide-react";

interface SizeGuideModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const SizeGuideModal = ({ isOpen, onClose }: SizeGuideModalProps) => {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="font-heading text-2xl">Size Guide</DialogTitle>
        </DialogHeader>
        
        <div className="mt-4">
          <p className="text-sm text-muted-foreground mb-4">
            Measure yourself and compare to the chart below for the best fit.
          </p>

          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="bg-gray-50">
                  <th className="border p-3 text-left">Size</th>
                  <th className="border p-3">Bust (cm)</th>
                  <th className="border p-3">Waist (cm)</th>
                  <th className="border p-3">Hips (cm)</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="border p-3 font-medium">XS</td>
                  <td className="border p-3 text-center">76-81</td>
                  <td className="border p-3 text-center">61-66</td>
                  <td className="border p-3 text-center">86-91</td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="border p-3 font-medium">S</td>
                  <td className="border p-3 text-center">81-86</td>
                  <td className="border p-3 text-center">66-71</td>
                  <td className="border p-3 text-center">91-96</td>
                </tr>
                <tr>
                  <td className="border p-3 font-medium">M</td>
                  <td className="border p-3 text-center">86-91</td>
                  <td className="border p-3 text-center">71-76</td>
                  <td className="border p-3 text-center">96-101</td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="border p-3 font-medium">L</td>
                  <td className="border p-3 text-center">91-97</td>
                  <td className="border p-3 text-center">76-82</td>
                  <td className="border p-3 text-center">101-107</td>
                </tr>
                <tr>
                  <td className="border p-3 font-medium">XL</td>
                  <td className="border p-3 text-center">97-102</td>
                  <td className="border p-3 text-center">82-87</td>
                  <td className="border p-3 text-center">107-112</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="mt-6 p-4 bg-blush/30 border border-gold/30 rounded-md">
            <div className="flex items-start gap-3">
              <Info className="text-gold mt-0.5" size={20} />
              <div className="text-sm">
                <p className="font-medium text-gold mb-1">How to Measure:</p>
                <ul className="text-muted-foreground space-y-1">
                  <li><strong>Bust:</strong> Measure around the fullest part of your chest</li>
                  <li><strong>Waist:</strong> Measure around the narrowest part of your waist</li>
                  <li><strong>Hips:</strong> Measure around the fullest part of your hips</li>
                </ul>
              </div>
            </div>
          </div>

          <p className="text-xs text-muted-foreground mt-4 text-center">
            All measurements are approximate and may vary by 1-2 cm.
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default SizeGuideModal;