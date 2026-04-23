import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { AuthProvider } from "@/contexts/AuthContext";
import { CartProvider } from "@/contexts/CartContext";
import { ProductProvider } from "@/contexts/ProductContext";
import { WishlistProvider } from "@/contexts/WishlistContext";
import { LanguageProvider } from "@/contexts/LanguageContext";
import { AvailabilityProvider } from "@/contexts/AvailabilityContext";
import Index from "./pages/Index.tsx";
import CollectionPage from "./pages/CollectionPage.tsx";
import ProductDetail from "./pages/ProductDetail.tsx";
import ContactPage from "./pages/ContactPage.tsx";
import AuthPage from "./pages/Auth.tsx";
import CheckoutPage from "./pages/Checkout.tsx";
import NotFound from "./pages/NotFound.tsx";
import { ProtectedRoute } from "./components/ProtectedRoute.tsx";
import AdminLayout from "./pages/admin/AdminLayout.tsx";
import AdminDashboard from "./pages/admin/AdminDashboard.tsx";
import AdminOrders from "./pages/admin/AdminOrders.tsx";
import AdminProducts from "./pages/admin/AdminProducts.tsx";
import AdminCalendar from "./pages/admin/AdminCalendar.tsx";
import AdminConsultations from "./pages/admin/AdminConsultations.tsx";
import AdminContent from "./pages/admin/AdminContent.tsx";
import ProfilePage from "./pages/ProfilePage.tsx";
import TermsPage from "./pages/TermsPage.tsx";
import PrivacyPage from "./pages/PrivacyPage.tsx";
import AboutPage from "./pages/AboutPage.tsx";
import BlogPage from "./pages/BlogPage.tsx";
import SearchPage from "./pages/SearchPage.tsx";
import WishlistPage from "./pages/WishlistPage.tsx";
import FaqPage from "./pages/FaqPage.tsx";
import AlterationsPage from "./pages/AlterationsPage.tsx";
import WeddingTimeline from "./pages/WeddingTimeline.tsx";
import StylistChat from "./components/StylistChat.tsx";
import AtelierPage from "./pages/AtelierPage.tsx";
import StyleQuiz from "./pages/StyleQuiz.tsx";
import AppointmentReminders from "./pages/AppointmentReminders.tsx";
import GalleryPage from "./pages/GalleryPage.tsx";
import InstagramFeed from "./pages/InstagramFeed.tsx";
import GroupBookingPage from "./pages/GroupBookingPage.tsx";
import WeddingChecklist from "./pages/WeddingChecklist.tsx";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ErrorBoundary>
    <LanguageProvider>
      <AuthProvider>
      <ProductProvider>
        <WishlistProvider>
          <CartProvider>
            <AvailabilityProvider>
              <TooltipProvider>
              <StylistChat />
              <Toaster />
              <Sonner />
              <BrowserRouter>
                <Routes>
                  <Route path="/" element={<Index />} />
                  <Route path="/auth" element={<AuthPage />} />
                  <Route path="/login" element={<AuthPage />} />
                  <Route path="/register" element={<AuthPage />} />
                  <Route path="/collection/:category" element={<CollectionPage />} />
                  <Route path="/product/:id" element={<ProductDetail />} />
                  <Route path="/contact" element={<ContactPage />} />
                  <Route path="/terms" element={<TermsPage />} />
                  <Route path="/privacy" element={<PrivacyPage />} />
                  <Route path="/about" element={<AboutPage />} />
                  <Route path="/atelier" element={<AtelierPage />} />
                  <Route path="/style-quiz" element={<StyleQuiz />} />
                  <Route path="/reminders" element={<AppointmentReminders />} />
                  <Route path="/gallery" element={<GalleryPage />} />
                  <Route path="/instagram" element={<InstagramFeed />} />
                  <Route path="/group-booking" element={<GroupBookingPage />} />
                  <Route path="/checklist" element={<WeddingChecklist />} />
                  <Route path="/blog" element={<BlogPage />} />
                  <Route path="/search" element={<SearchPage />} />
                  <Route path="/wishlist" element={<WishlistPage />} />
                  <Route path="/faq" element={<FaqPage />} />
                  <Route path="/alterations" element={<AlterationsPage />} />
                  <Route path="/timeline" element={<WeddingTimeline />} />
                  <Route path="/checkout" element={<CheckoutPage />} />
                  <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />

                  {/* Admin Routes */}
                  <Route path="/admin" element={<ProtectedRoute requireAdmin={true}><AdminLayout /></ProtectedRoute>}>
                    <Route index element={<AdminDashboard />} />
                    <Route path="orders" element={<AdminOrders />} />
                    <Route path="products" element={<AdminProducts />} />
                    <Route path="calendar" element={<AdminCalendar />} />
                    <Route path="consultations" element={<AdminConsultations />} />
                    <Route path="content" element={<AdminContent />} />
                  </Route>

                  <Route path="*" element={<NotFound />} />
                </Routes>
              </BrowserRouter>
            </TooltipProvider>
          </AvailabilityProvider>
        </CartProvider>
        </WishlistProvider>
      </ProductProvider>
      </AuthProvider>
    </LanguageProvider>
    </ErrorBoundary>
  </QueryClientProvider>
);

export default App;
