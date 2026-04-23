import { useState } from "react";
import { Search, Plus, Edit2, Trash2, Package, X, Upload } from "lucide-react";
import { Product } from "@/data/products";
import { useProducts } from "@/contexts/ProductContext";
import { useToast } from "@/hooks/use-toast";

const EMPTY_FORM = {
  name: "",
  description: "",
  productType: "sale" as "sale" | "rent",
  salePrice: "",
  rentalPrice: "",
  securityDeposit: "",
  category: "Bridal Gown" as "Bridal Gown" | "Evening Dress" | "Party Dress",
  style: "",
  color: "",
  fabric: "",
  designer: "",
  sizes: [] as string[],
  imagePreview: "",
};

const ALL_SIZES = ["XS", "S", "M", "L", "XL", "XXL"];

export default function AdminProducts() {
  const [searchTerm, setSearchTerm] = useState("");
  const { products, addProduct, updateProduct, deleteProduct } = useProducts();
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState<string | null>(null);
  const { toast } = useToast();

  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const openAddModal = () => {
    setForm(EMPTY_FORM);
    setEditingId(null);
    setShowModal(true);
  };

  const openEditModal = (product: Product) => {
    setForm({
      name: product.name,
      description: product.description,
      productType: product.productType,
      salePrice: product.salePrice?.toString() || "",
      rentalPrice: product.rentalPrice?.toString() || "",
      securityDeposit: product.securityDeposit?.toString() || "",
      category: product.category,
      style: product.style.join(", "),
      color: product.color.join(", "),
      fabric: product.fabric || "",
      designer: product.designer || "",
      sizes: product.sizes,
      imagePreview: product.images[0] || "",
    });
    setEditingId(product.id);
    setShowModal(true);
  };

  const handleDelete = (id: string) => {
    deleteProduct(id);
    toast({ title: "Product deleted", description: "The product has been removed." });
  };

  const toggleSize = (size: string) => {
    setForm(prev => ({
      ...prev,
      sizes: prev.sizes.includes(size)
        ? prev.sizes.filter(s => s !== size)
        : [...prev.sizes, size]
    }));
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (ev) => {
        setForm(prev => ({ ...prev, imagePreview: ev.target?.result as string }));
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!form.name || !form.description || form.sizes.length === 0) {
      toast({ title: "Missing fields", description: "Please fill in name, description, and select at least one size.", variant: "destructive" });
      return;
    }

    const newProduct: Product = {
      id: editingId || `product-${Date.now()}`,
      name: form.name,
      description: form.description,
      productType: form.productType,
      salePrice: form.salePrice ? Number(form.salePrice) : undefined,
      rentalPrice: form.rentalPrice ? Number(form.rentalPrice) : undefined,
      securityDeposit: form.securityDeposit ? Number(form.securityDeposit) : undefined,
      images: form.imagePreview ? [form.imagePreview] : ["/images/products/placeholder.jpg"],
      category: form.category,
      style: form.style.split(",").map(s => s.trim()).filter(Boolean),
      color: form.color.split(",").map(s => s.trim()).filter(Boolean),
      fabric: form.fabric || undefined,
      designer: form.designer || undefined,
      sizes: form.sizes,
      isNew: !editingId,
    };

    if (editingId) {
      updateProduct(editingId, newProduct);
      toast({ title: "Product updated", description: `${form.name} has been updated successfully.` });
    } else {
      addProduct(newProduct);
      toast({ title: "Product added", description: `${form.name} has been added to the catalog.` });
    }

    setShowModal(false);
    setForm(EMPTY_FORM);
    setEditingId(null);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-heading font-semibold text-gray-900">Products Inventory</h1>
          <p className="text-sm text-gray-500 mt-1">Manage your catalog of dresses for rent and sale.</p>
        </div>
        <button
          onClick={openAddModal}
          className="flex items-center gap-2 px-5 py-2.5 bg-gold text-white rounded-md text-sm font-medium shadow-sm hover:bg-gold-dark transition-colors"
        >
          <Plus size={16} />
          Add Product
        </button>
      </div>

      {/* Toolbar */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
          <input
            type="text"
            placeholder="Search products by name or category..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-border rounded-md text-sm focus:outline-none focus:border-gold transition-colors shadow-sm"
          />
        </div>
      </div>

      {/* Products Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {filteredProducts.map((product) => (
          <div key={product.id} className="bg-white border border-border rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-shadow group">
            <div className="relative aspect-[3/4] overflow-hidden bg-gray-100">
              <img
                src={product.images[0]}
                alt={product.name}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              />
              <div className="absolute top-3 left-3 flex gap-2">
                <span className={`px-2 py-1 text-[10px] uppercase tracking-wider font-semibold rounded-sm bg-white/90 backdrop-blur-sm shadow-sm ${
                  product.productType === 'sale' ? 'text-gray-800' : 'text-gold'
                }`}>
                  {product.productType === 'sale' ? 'Sale' : 'Rent'}
                </span>
              </div>

              {/* Overlay Actions */}
              <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/60 to-transparent p-4 translate-y-full group-hover:translate-y-0 transition-transform duration-300 flex justify-end gap-2">
                <button onClick={() => openEditModal(product)} className="p-2 bg-white rounded-full text-gray-700 hover:text-gold transition-colors" title="Edit">
                  <Edit2 size={16} />
                </button>
                <button onClick={() => handleDelete(product.id)} className="p-2 bg-white rounded-full text-red-600 hover:bg-red-50 transition-colors" title="Delete">
                  <Trash2 size={16} />
                </button>
              </div>
            </div>

            <div className="p-4">
              <p className="text-[10px] text-gray-500 uppercase tracking-widest mb-1">{product.category}</p>
              <h3 className="font-heading text-lg text-gray-900 truncate">{product.name}</h3>

              <div className="mt-4 flex items-center justify-between">
                <p className="font-semibold text-gray-900">
                  AED {product.productType === 'sale' ? product.salePrice?.toLocaleString() : product.rentalPrice?.toLocaleString()}
                  {product.productType === 'rent' && <span className="text-xs text-gray-500 font-normal"> /day</span>}
                </p>
                <div className="text-xs text-gray-500 px-2 py-1 border border-border rounded-md">
                  {product.sizes.length} sizes
                </div>
              </div>
            </div>
          </div>
        ))}

        {filteredProducts.length === 0 && (
          <div className="col-span-full py-20 text-center text-gray-500 border-2 border-dashed border-gray-200 rounded-xl">
            <Package size={48} className="mx-auto text-gray-300 mb-4" />
            <p className="text-lg font-medium text-gray-900">No products found</p>
            <p className="mt-1">Try adjusting your search or filters.</p>
          </div>
        )}
      </div>

      {/* =================== ADD / EDIT PRODUCT MODAL =================== */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm px-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-border sticky top-0 bg-white rounded-t-2xl z-10">
              <h2 className="font-heading text-2xl font-semibold text-gray-900">
                {editingId ? "Edit Product" : "Add New Product"}
              </h2>
              <button onClick={() => setShowModal(false)} className="p-2 hover:bg-gray-100 rounded-full transition-colors">
                <X size={20} />
              </button>
            </div>

            {/* Modal Form */}
            <form onSubmit={handleSubmit} className="p-6 space-y-6">
              {/* Image Upload */}
              <div>
                <label className="block text-[10px] font-semibold uppercase tracking-widest text-gray-500 mb-2">Product Image</label>
                <div className="flex items-center gap-4">
                  {form.imagePreview ? (
                    <img src={form.imagePreview} alt="Preview" className="w-24 h-32 object-cover rounded-lg border border-border" />
                  ) : (
                    <div className="w-24 h-32 bg-gray-100 rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center">
                      <Upload size={24} className="text-gray-400" />
                    </div>
                  )}
                  <div>
                    <label className="cursor-pointer inline-flex items-center gap-2 px-4 py-2 border border-border rounded-md text-sm font-medium hover:bg-gray-50 transition-colors">
                      <Upload size={14} />
                      Upload Image
                      <input type="file" accept="image/*" onChange={handleImageUpload} className="hidden" />
                    </label>
                    <p className="text-xs text-gray-400 mt-1">JPG, PNG — max 5MB</p>
                  </div>
                </div>
              </div>

              {/* Name & Category */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-semibold uppercase tracking-widest text-gray-500 mb-2">Product Name *</label>
                  <input
                    type="text"
                    required
                    value={form.name}
                    onChange={(e) => setForm(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="e.g., Rosalina Gown"
                    className="w-full px-4 py-2.5 border border-border rounded-md text-sm focus:outline-none focus:border-gold transition-colors"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-semibold uppercase tracking-widest text-gray-500 mb-2">Category *</label>
                  <select
                    value={form.category}
                    onChange={(e) => setForm(prev => ({ ...prev, category: e.target.value as "Bridal Gown" | "Evening Dress" | "Party Dress" }))}
                    className="w-full px-4 py-2.5 border border-border rounded-md text-sm focus:outline-none focus:border-gold transition-colors bg-white"
                  >
                    <option value="Bridal Gown">Bridal Gown</option>
                    <option value="Evening Dress">Evening Dress</option>
                    <option value="Party Dress">Party Dress</option>
                  </select>
                </div>
              </div>

              {/* Description */}
              <div>
                <label className="block text-[10px] font-semibold uppercase tracking-widest text-gray-500 mb-2">Description *</label>
                <textarea
                  required
                  rows={3}
                  value={form.description}
                  onChange={(e) => setForm(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Describe the dress, its fabric, and special features..."
                  className="w-full px-4 py-2.5 border border-border rounded-md text-sm focus:outline-none focus:border-gold transition-colors resize-none"
                />
              </div>

              {/* Product Type & Pricing */}
              <div>
                <label className="block text-[10px] font-semibold uppercase tracking-widest text-gray-500 mb-2">Product Type *</label>
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => setForm(prev => ({ ...prev, productType: "sale" }))}
                    className={`flex-1 py-2.5 rounded-md text-sm font-medium border transition-colors ${
                      form.productType === "sale"
                        ? "bg-gray-900 text-white border-gray-900"
                        : "bg-white text-gray-700 border-border hover:bg-gray-50"
                    }`}
                  >
                    For Sale
                  </button>
                  <button
                    type="button"
                    onClick={() => setForm(prev => ({ ...prev, productType: "rent" }))}
                    className={`flex-1 py-2.5 rounded-md text-sm font-medium border transition-colors ${
                      form.productType === "rent"
                        ? "bg-gold text-white border-gold"
                        : "bg-white text-gray-700 border-border hover:bg-gray-50"
                    }`}
                  >
                    For Rent
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {form.productType === "sale" ? (
                  <div>
                    <label className="block text-[10px] font-semibold uppercase tracking-widest text-gray-500 mb-2">Sale Price (AED) *</label>
                    <input
                      type="number"
                      required
                      value={form.salePrice}
                      onChange={(e) => setForm(prev => ({ ...prev, salePrice: e.target.value }))}
                      placeholder="28500"
                      className="w-full px-4 py-2.5 border border-border rounded-md text-sm focus:outline-none focus:border-gold transition-colors"
                    />
                  </div>
                ) : (
                  <>
                    <div>
                      <label className="block text-[10px] font-semibold uppercase tracking-widest text-gray-500 mb-2">Rental Price / Day (AED) *</label>
                      <input
                        type="number"
                        required
                        value={form.rentalPrice}
                        onChange={(e) => setForm(prev => ({ ...prev, rentalPrice: e.target.value }))}
                        placeholder="3500"
                        className="w-full px-4 py-2.5 border border-border rounded-md text-sm focus:outline-none focus:border-gold transition-colors"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-semibold uppercase tracking-widest text-gray-500 mb-2">Security Deposit (AED)</label>
                      <input
                        type="number"
                        value={form.securityDeposit}
                        onChange={(e) => setForm(prev => ({ ...prev, securityDeposit: e.target.value }))}
                        placeholder="5000"
                        className="w-full px-4 py-2.5 border border-border rounded-md text-sm focus:outline-none focus:border-gold transition-colors"
                      />
                    </div>
                  </>
                )}
              </div>

              {/* Sizes */}
              <div>
                <label className="block text-[10px] font-semibold uppercase tracking-widest text-gray-500 mb-2">Available Sizes *</label>
                <div className="flex flex-wrap gap-2">
                  {ALL_SIZES.map(size => (
                    <button
                      key={size}
                      type="button"
                      onClick={() => toggleSize(size)}
                      className={`w-12 h-10 rounded-md text-sm font-medium border transition-colors ${
                        form.sizes.includes(size)
                          ? "bg-gold text-white border-gold"
                          : "bg-white text-gray-700 border-border hover:bg-gray-50"
                      }`}
                    >
                      {size}
                    </button>
                  ))}
                </div>
              </div>

              {/* Style, Color, Fabric, Designer */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-semibold uppercase tracking-widest text-gray-500 mb-2">Style</label>
                  <input
                    type="text"
                    value={form.style}
                    onChange={(e) => setForm(prev => ({ ...prev, style: e.target.value }))}
                    placeholder="e.g., Mermaid, A-Line"
                    className="w-full px-4 py-2.5 border border-border rounded-md text-sm focus:outline-none focus:border-gold transition-colors"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-semibold uppercase tracking-widest text-gray-500 mb-2">Color</label>
                  <input
                    type="text"
                    value={form.color}
                    onChange={(e) => setForm(prev => ({ ...prev, color: e.target.value }))}
                    placeholder="e.g., Ivory, Champagne"
                    className="w-full px-4 py-2.5 border border-border rounded-md text-sm focus:outline-none focus:border-gold transition-colors"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-semibold uppercase tracking-widest text-gray-500 mb-2">Fabric</label>
                  <input
                    type="text"
                    value={form.fabric}
                    onChange={(e) => setForm(prev => ({ ...prev, fabric: e.target.value }))}
                    placeholder="e.g., French Lace, Tulle"
                    className="w-full px-4 py-2.5 border border-border rounded-md text-sm focus:outline-none focus:border-gold transition-colors"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-semibold uppercase tracking-widest text-gray-500 mb-2">Designer</label>
                  <input
                    type="text"
                    value={form.designer}
                    onChange={(e) => setForm(prev => ({ ...prev, designer: e.target.value }))}
                    placeholder="e.g., Riman Atelier"
                    className="w-full px-4 py-2.5 border border-border rounded-md text-sm focus:outline-none focus:border-gold transition-colors"
                  />
                </div>
              </div>

              {/* Actions */}
              <div className="flex justify-end gap-3 pt-4 border-t border-border">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-6 py-2.5 border border-border rounded-md text-sm font-medium hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-6 py-2.5 bg-gold text-white rounded-md text-sm font-medium shadow-sm hover:bg-gold-dark transition-colors"
                >
                  {editingId ? "Save Changes" : "Add Product"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
