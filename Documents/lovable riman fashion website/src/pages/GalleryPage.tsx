import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Camera, Heart, X, ChevronLeft, ChevronRight, Upload, Mail, Check } from "lucide-react";
import Layout from "@/components/Layout";
import { useToast } from "@/hooks/use-toast";

interface GalleryPhoto {
  id: string;
  brideName: string;
  weddingDate: string;
  dressType: "bridal" | "evening" | "bridesmaid";
  imageUrl: string;
  testimonial?: string;
  approved: boolean;
}

const initialPhotos: GalleryPhoto[] = [
  {
    id: "1",
    brideName: "Fatima Al Hussein",
    weddingDate: "December 2025",
    dressType: "bridal",
    imageUrl: "/images/gallery/bride-1.jpg",
    testimonial: "Riman Fashion made my dream come true. The dress was absolutely perfect!",
    approved: true,
  },
  {
    id: "2",
    brideName: "Aisha Mohammed",
    weddingDate: "November 2025",
    dressType: "bridal",
    imageUrl: "/images/gallery/bride-2.jpg",
    testimonial: "The attention to detail was incredible. I felt like a princess.",
    approved: true,
  },
  {
    id: "3",
    brideName: "Noor Abdullah",
    weddingDate: "October 2025",
    dressType: "evening",
    imageUrl: "/images/gallery/evening-1.jpg",
    approved: true,
  },
  {
    id: "4",
    brideName: "Mariam Talal",
    weddingDate: "September 2025",
    dressType: "bridesmaid",
    imageUrl: "/images/gallery/bridesmaid-1.jpg",
    approved: true,
  },
  {
    id: "5",
    brideName: "Sara Mahmoud",
    weddingDate: "August 2025",
    dressType: "bridal",
    imageUrl: "/images/gallery/bride-3.jpg",
    testimonial: "Everyone asked about my dress. It was truly unique!",
    approved: true,
  },
  {
    id: "6",
    brideName: "Laila Hassan",
    weddingDate: "July 2025",
    dressType: "evening",
    imageUrl: "/images/gallery/evening-2.jpg",
    approved: true,
  },
];

const GalleryPage = () => {
  const [photos] = useState<GalleryPhoto[]>(initialPhotos);
  const [filter, setFilter] = useState<"all" | "bridal" | "evening" | "bridesmaid">("all");
  const [selectedPhoto, setSelectedPhoto] = useState<GalleryPhoto | null>(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadForm, setUploadForm] = useState({ name: "", email: "", message: "" });
  const [uploadSubmitted, setUploadSubmitted] = useState(false);
  const { toast } = useToast();

  const filteredPhotos = filter === "all" ? photos : photos.filter(p => p.dressType === filter);

  const handleSubmitUpload = (e: React.FormEvent) => {
    e.preventDefault();
    setUploadSubmitted(true);
    toast({
      title: "Thank you for sharing!",
      description: "We'll review your photo and get back to you soon.",
    });
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
          <Camera className="mx-auto text-gold mb-4" size={32} />
          <p className="font-body text-[10px] tracking-[0.4em] uppercase text-muted-foreground mb-4">Real Brides</p>
          <h1 className="heading-display text-4xl md:text-5xl mb-6">Photo Gallery</h1>
          <p className="font-body text-muted-foreground max-w-2xl mx-auto mb-8">
            Be inspired by real brides who found their dream dress at Riman Fashion
          </p>
        </motion.div>
      </section>

      <section className="section-padding">
        <div className="max-w-7xl mx-auto px-6">
          {/* Filter Tabs */}
          <div className="flex flex-wrap justify-center gap-4 mb-12">
            {(["all", "bridal", "evening", "bridesmaid"] as const).map((type) => (
              <button
                key={type}
                onClick={() => setFilter(type)}
                className={`px-6 py-2 rounded-full font-body text-xs tracking-[0.2em] uppercase transition-all ${
                  filter === type
                    ? "bg-gold text-white"
                    : "border border-border hover:border-gold"
                }`}
              >
                {type === "all" ? "All" : type.charAt(0).toUpperCase() + type.slice(1)}
              </button>
            ))}
          </div>

          {/* Photo Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <AnimatePresence>
              {filteredPhotos.map((photo, index) => (
                <motion.div
                  key={photo.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="group cursor-pointer"
                  onClick={() => setSelectedPhoto(photo)}
                >
                  <div className="aspect-[3/4] rounded-xl overflow-hidden relative">
                    <div className="absolute inset-0 bg-champagne flex items-center justify-center">
                      <Camera size={48} className="text-gold/30" />
                    </div>
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-colors flex items-center justify-center">
                      <Heart className="text-white opacity-0 group-hover:opacity-100 transition-opacity" size={32} />
                    </div>
                    <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/70 to-transparent">
                      <p className="text-white font-heading text-sm">{photo.brideName}</p>
                      <p className="text-white/70 font-body text-xs">{photo.weddingDate}</p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          {/* Upload CTA */}
          <div className="text-center mt-16">
            <button
              onClick={() => setShowUploadModal(true)}
              className="btn-luxury"
            >
              <Upload size={18} className="mr-2 inline" />
              Share Your Photo
            </button>
          </div>
        </div>
      </section>

      {/* Lightbox */}
      <AnimatePresence>
        {selectedPhoto && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedPhoto(null)}
          >
            <button
              className="absolute top-4 right-4 text-white hover:text-gold"
              onClick={() => setSelectedPhoto(null)}
            >
              <X size={32} />
            </button>
            
            <div className="max-w-4xl w-full flex items-center gap-4">
              <button
                className="text-white hover:text-gold"
                onClick={(e) => {
                  e.stopPropagation();
                  const currentIndex = filteredPhotos.findIndex(p => p.id === selectedPhoto.id);
                  if (currentIndex > 0) {
                    setSelectedPhoto(filteredPhotos[currentIndex - 1]);
                  }
                }}
              >
                <ChevronLeft size={32} />
              </button>
              
              <motion.div
                initial={{ scale: 0.9 }}
                animate={{ scale: 1 }}
                className="flex-1"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="aspect-[3/4] bg-champagne rounded-xl flex items-center justify-center mb-4">
                  <Camera size={64} className="text-gold/30" />
                </div>
                <div className="text-center">
                  <h3 className="font-heading text-xl text-white">{selectedPhoto.brideName}</h3>
                  <p className="text-white/70 font-body text-sm">{selectedPhoto.weddingDate}</p>
                  {selectedPhoto.testimonial && (
                    <p className="text-white/80 font-body text-sm mt-4 italic">"{selectedPhoto.testimonial}"</p>
                  )}
                </div>
              </motion.div>
              
              <button
                className="text-white hover:text-gold"
                onClick={(e) => {
                  e.stopPropagation();
                  const currentIndex = filteredPhotos.findIndex(p => p.id === selectedPhoto.id);
                  if (currentIndex < filteredPhotos.length - 1) {
                    setSelectedPhoto(filteredPhotos[currentIndex + 1]);
                  }
                }}
              >
                <ChevronRight size={32} />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Upload Modal */}
      <AnimatePresence>
        {showUploadModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
            onClick={() => setShowUploadModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.9 }}
              className="bg-white rounded-2xl max-w-md w-full p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex justify-between items-center mb-6">
                <h3 className="font-heading text-xl">Share Your Photo</h3>
                <button onClick={() => setShowUploadModal(false)}>
                  <X size={20} />
                </button>
              </div>

              {!uploadSubmitted ? (
                <form onSubmit={handleSubmitUpload} className="space-y-4">
                  <div>
                    <label className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground block mb-2">
                      Your Name
                    </label>
                    <input
                      type="text"
                      required
                      value={uploadForm.name}
                      onChange={(e) => setUploadForm({ ...uploadForm, name: e.target.value })}
                      className="w-full border border-border px-4 py-3 font-body text-sm focus:outline-none focus:border-gold"
                      placeholder="Your name"
                    />
                  </div>
                  <div>
                    <label className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground block mb-2">
                      <Mail size={14} className="inline mr-2" />
                      Email
                    </label>
                    <input
                      type="email"
                      required
                      value={uploadForm.email}
                      onChange={(e) => setUploadForm({ ...uploadForm, email: e.target.value })}
                      className="w-full border border-border px-4 py-3 font-body text-sm focus:outline-none focus:border-gold"
                      placeholder="your@email.com"
                    />
                  </div>
                  <div>
                    <label className="font-body text-[10px] tracking-[0.2em] uppercase text-muted-foreground block mb-2">
                      Message (Optional)
                    </label>
                    <textarea
                      rows={3}
                      value={uploadForm.message}
                      onChange={(e) => setUploadForm({ ...uploadForm, message: e.target.value })}
                      className="w-full border border-border px-4 py-3 font-body text-sm focus:outline-none focus:border-gold resize-none"
                      placeholder="Tell us about your dress..."
                    />
                  </div>
                  <div className="border-2 border-dashed border-border rounded-xl p-8 text-center cursor-pointer hover:border-gold">
                    <Upload size={32} className="mx-auto text-muted-foreground mb-2" />
                    <p className="font-body text-sm text-muted-foreground">Click to upload your photo</p>
                  </div>
                  <button type="submit" className="btn-luxury w-full">
                    Submit
                  </button>
                </form>
              ) : (
                <div className="text-center py-8">
                  <div className="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
                    <Check size={24} className="text-green-600" />
                  </div>
                  <h4 className="font-heading text-lg mb-2">Thank You!</h4>
                  <p className="font-body text-sm text-muted-foreground">
                    We'll review your photo and add it to our gallery soon.
                  </p>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </Layout>
  );
};

export default GalleryPage;