import { useState } from "react";
import { Plus, Edit2, Trash2, Star, X, FileText, MessageSquare } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

// ===================== TESTIMONIALS =====================

interface Testimonial {
  id: string;
  authorName: string;
  authorRole: string;
  content: string;
  rating: number;
}

const INITIAL_TESTIMONIALS: Testimonial[] = [
  { id: "1", authorName: "Fatima Al Rashid", authorRole: "Bride, January 2026", content: "Riman Fashion created the most exquisite wedding gown I could have imagined. The attention to detail and personal service made the entire experience truly magical.", rating: 5 },
  { id: "2", authorName: "Noura Al Maktoum", authorRole: "Evening Event, February 2026", content: "I rented a stunning evening gown for a charity gala. The quality was impeccable and the rental process was seamless. I felt like royalty the entire evening.", rating: 5 },
  { id: "3", authorName: "Layla Hassan", authorRole: "Bride, March 2026", content: "The private viewing experience at Riman was unforgettable. They understood my vision instantly and helped me find the dress of my dreams.", rating: 5 },
];

// ===================== BLOG POSTS =====================

interface BlogPost {
  id: string;
  title: string;
  excerpt: string;
  status: "draft" | "published";
  date: string;
}

const INITIAL_BLOG_POSTS: BlogPost[] = [
  { id: "1", title: "5 Tips for Choosing Your Dream Wedding Dress", excerpt: "Finding the perfect wedding dress is one of the most exciting parts of wedding planning. Here are our expert tips...", status: "published", date: "2026-03-01" },
  { id: "2", title: "The Rise of Dress Rentals in the UAE", excerpt: "Why more brides and fashionistas are choosing to rent luxury gowns instead of buying...", status: "published", date: "2026-02-20" },
  { id: "3", title: "Spring 2026 Bridal Trends", excerpt: "From soft pastels to dramatic sleeves, discover what's trending in bridal fashion this season.", status: "draft", date: "2026-03-10" },
];

export default function AdminContent() {
  const [activeTab, setActiveTab] = useState<"testimonials" | "blog">("testimonials");
  const [testimonials, setTestimonials] = useState<Testimonial[]>(INITIAL_TESTIMONIALS);
  const [blogPosts, setBlogPosts] = useState<BlogPost[]>(INITIAL_BLOG_POSTS);
  const { toast } = useToast();

  // Testimonial modal state
  const [showTestimonialModal, setShowTestimonialModal] = useState(false);
  const [editingTestimonial, setEditingTestimonial] = useState<Testimonial | null>(null);
  const [testimonialForm, setTestimonialForm] = useState({ authorName: "", authorRole: "", content: "", rating: 5 });

  // Blog modal state
  const [showBlogModal, setShowBlogModal] = useState(false);
  const [editingBlog, setEditingBlog] = useState<BlogPost | null>(null);
  const [blogForm, setBlogForm] = useState({ title: "", excerpt: "", status: "draft" as "draft" | "published" });

  // ========== TESTIMONIAL HANDLERS ==========
  const openAddTestimonial = () => {
    setTestimonialForm({ authorName: "", authorRole: "", content: "", rating: 5 });
    setEditingTestimonial(null);
    setShowTestimonialModal(true);
  };

  const openEditTestimonial = (t: Testimonial) => {
    setTestimonialForm({ authorName: t.authorName, authorRole: t.authorRole, content: t.content, rating: t.rating });
    setEditingTestimonial(t);
    setShowTestimonialModal(true);
  };

  const saveTestimonial = () => {
    if (!testimonialForm.authorName || !testimonialForm.content) return;
    if (editingTestimonial) {
      setTestimonials(prev => prev.map(t => t.id === editingTestimonial.id ? { ...t, ...testimonialForm } : t));
      toast({ title: "Testimonial updated" });
    } else {
      setTestimonials(prev => [...prev, { id: `t-${Date.now()}`, ...testimonialForm }]);
      toast({ title: "Testimonial added" });
    }
    setShowTestimonialModal(false);
  };

  const deleteTestimonial = (id: string) => {
    setTestimonials(prev => prev.filter(t => t.id !== id));
    toast({ title: "Testimonial deleted" });
  };

  // ========== BLOG HANDLERS ==========
  const openAddBlog = () => {
    setBlogForm({ title: "", excerpt: "", status: "draft" });
    setEditingBlog(null);
    setShowBlogModal(true);
  };

  const openEditBlog = (b: BlogPost) => {
    setBlogForm({ title: b.title, excerpt: b.excerpt, status: b.status });
    setEditingBlog(b);
    setShowBlogModal(true);
  };

  const saveBlog = () => {
    if (!blogForm.title) return;
    if (editingBlog) {
      setBlogPosts(prev => prev.map(b => b.id === editingBlog.id ? { ...b, ...blogForm } : b));
      toast({ title: "Blog post updated" });
    } else {
      setBlogPosts(prev => [...prev, { id: `b-${Date.now()}`, ...blogForm, date: new Date().toISOString().slice(0, 10) }]);
      toast({ title: "Blog post created" });
    }
    setShowBlogModal(false);
  };

  const deleteBlog = (id: string) => {
    setBlogPosts(prev => prev.filter(b => b.id !== id));
    toast({ title: "Blog post deleted" });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-heading font-semibold text-gray-900">Content Manager</h1>
        <p className="text-sm text-gray-500 mt-1">Manage testimonials and blog posts.</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-border">
        <button
          onClick={() => setActiveTab("testimonials")}
          className={`flex items-center gap-2 px-6 py-3 text-sm font-medium border-b-2 -mb-px transition-colors ${
            activeTab === "testimonials" ? "border-gold text-gray-900" : "border-transparent text-gray-500 hover:text-gray-700"
          }`}
        >
          <MessageSquare size={16} /> Testimonials
        </button>
        <button
          onClick={() => setActiveTab("blog")}
          className={`flex items-center gap-2 px-6 py-3 text-sm font-medium border-b-2 -mb-px transition-colors ${
            activeTab === "blog" ? "border-gold text-gray-900" : "border-transparent text-gray-500 hover:text-gray-700"
          }`}
        >
          <FileText size={16} /> Blog Posts
        </button>
      </div>

      {/* ============ TESTIMONIALS TAB ============ */}
      {activeTab === "testimonials" && (
        <div className="space-y-4">
          <div className="flex justify-end">
            <button onClick={openAddTestimonial} className="flex items-center gap-2 px-4 py-2 bg-gold text-white rounded-md text-sm font-medium hover:bg-gold-dark transition-colors">
              <Plus size={16} /> Add Testimonial
            </button>
          </div>

          {testimonials.map(t => (
            <div key={t.id} className="bg-white border border-border rounded-xl p-5 flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-1 mb-2">
                  {Array.from({ length: t.rating }).map((_, i) => (
                    <Star key={i} size={14} className="fill-gold text-gold" />
                  ))}
                </div>
                <p className="text-sm text-gray-700 italic mb-2">"{t.content}"</p>
                <p className="text-xs text-gray-500 font-medium">{t.authorName} — {t.authorRole}</p>
              </div>
              <div className="flex gap-2 shrink-0">
                <button onClick={() => openEditTestimonial(t)} className="p-2 hover:bg-gray-100 rounded-full transition-colors"><Edit2 size={16} className="text-gray-500" /></button>
                <button onClick={() => deleteTestimonial(t.id)} className="p-2 hover:bg-red-50 rounded-full transition-colors"><Trash2 size={16} className="text-red-500" /></button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ============ BLOG TAB ============ */}
      {activeTab === "blog" && (
        <div className="space-y-4">
          <div className="flex justify-end">
            <button onClick={openAddBlog} className="flex items-center gap-2 px-4 py-2 bg-gold text-white rounded-md text-sm font-medium hover:bg-gold-dark transition-colors">
              <Plus size={16} /> New Blog Post
            </button>
          </div>

          {blogPosts.map(b => (
            <div key={b.id} className="bg-white border border-border rounded-xl p-5 flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-1">
                  <h3 className="font-heading text-lg font-semibold text-gray-900">{b.title}</h3>
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium uppercase tracking-wider ${
                    b.status === "published" ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-600"
                  }`}>{b.status}</span>
                </div>
                <p className="text-sm text-gray-600 mb-1">{b.excerpt}</p>
                <p className="text-xs text-gray-400">{b.date}</p>
              </div>
              <div className="flex gap-2 shrink-0">
                <button onClick={() => openEditBlog(b)} className="p-2 hover:bg-gray-100 rounded-full transition-colors"><Edit2 size={16} className="text-gray-500" /></button>
                <button onClick={() => deleteBlog(b.id)} className="p-2 hover:bg-red-50 rounded-full transition-colors"><Trash2 size={16} className="text-red-500" /></button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ============ TESTIMONIAL MODAL ============ */}
      {showTestimonialModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm px-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="font-heading text-xl font-semibold">{editingTestimonial ? "Edit Testimonial" : "Add Testimonial"}</h2>
              <button onClick={() => setShowTestimonialModal(false)}><X size={20} /></button>
            </div>
            <div className="space-y-3">
              <input type="text" placeholder="Author name" value={testimonialForm.authorName} onChange={e => setTestimonialForm(p => ({ ...p, authorName: e.target.value }))} className="w-full px-4 py-2.5 border border-border rounded-md text-sm focus:outline-none focus:border-gold" />
              <input type="text" placeholder="Role (e.g., Bride, January 2026)" value={testimonialForm.authorRole} onChange={e => setTestimonialForm(p => ({ ...p, authorRole: e.target.value }))} className="w-full px-4 py-2.5 border border-border rounded-md text-sm focus:outline-none focus:border-gold" />
              <textarea rows={3} placeholder="Testimonial content..." value={testimonialForm.content} onChange={e => setTestimonialForm(p => ({ ...p, content: e.target.value }))} className="w-full px-4 py-2.5 border border-border rounded-md text-sm focus:outline-none focus:border-gold resize-none" />
              <div>
                <label className="text-xs text-gray-500 uppercase tracking-wider block mb-1">Rating</label>
                <div className="flex gap-1">
                  {[1, 2, 3, 4, 5].map(r => (
                    <button key={r} type="button" onClick={() => setTestimonialForm(p => ({ ...p, rating: r }))}>
                      <Star size={20} className={r <= testimonialForm.rating ? "fill-gold text-gold" : "text-gray-300"} />
                    </button>
                  ))}
                </div>
              </div>
            </div>
            <div className="flex gap-3 pt-2">
              <button onClick={() => setShowTestimonialModal(false)} className="flex-1 py-2.5 border border-border rounded-md text-sm font-medium hover:bg-gray-50">Cancel</button>
              <button onClick={saveTestimonial} className="flex-1 py-2.5 bg-gold text-white rounded-md text-sm font-medium hover:bg-gold-dark">Save</button>
            </div>
          </div>
        </div>
      )}

      {/* ============ BLOG MODAL ============ */}
      {showBlogModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm px-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="font-heading text-xl font-semibold">{editingBlog ? "Edit Blog Post" : "New Blog Post"}</h2>
              <button onClick={() => setShowBlogModal(false)}><X size={20} /></button>
            </div>
            <div className="space-y-3">
              <input type="text" placeholder="Post title" value={blogForm.title} onChange={e => setBlogForm(p => ({ ...p, title: e.target.value }))} className="w-full px-4 py-2.5 border border-border rounded-md text-sm focus:outline-none focus:border-gold" />
              <textarea rows={3} placeholder="Post excerpt / summary..." value={blogForm.excerpt} onChange={e => setBlogForm(p => ({ ...p, excerpt: e.target.value }))} className="w-full px-4 py-2.5 border border-border rounded-md text-sm focus:outline-none focus:border-gold resize-none" />
              <select value={blogForm.status} onChange={e => setBlogForm(p => ({ ...p, status: e.target.value as "draft" | "published" }))} className="w-full px-4 py-2.5 border border-border rounded-md text-sm focus:outline-none focus:border-gold bg-white">
                <option value="draft">Draft</option>
                <option value="published">Published</option>
              </select>
            </div>
            <div className="flex gap-3 pt-2">
              <button onClick={() => setShowBlogModal(false)} className="flex-1 py-2.5 border border-border rounded-md text-sm font-medium hover:bg-gray-50">Cancel</button>
              <button onClick={saveBlog} className="flex-1 py-2.5 bg-gold text-white rounded-md text-sm font-medium hover:bg-gold-dark">Save</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
