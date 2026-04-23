import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import { useToast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";
import Layout from "@/components/Layout";

// Demo users stored in localStorage
const DEMO_USERS_KEY = "riman_demo_users";

const GoogleIcon = ({ size = 20, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
  </svg>
);

const AuthPage = () => {
  const location = useLocation();
  const [isLogin, setIsLogin] = useState(location.pathname !== "/register");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      if (isLogin) {
        // Try Supabase login first
        const { error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });

        if (!error) {
          toast({ title: "Welcome back!", description: "Successfully logged in." });
          const from = location.state?.from?.pathname || "/";
          navigate(from, { replace: true });
          setIsLoading(false);
          return;
        }

        // If Supabase fails, try local demo login
        console.log("Supabase login failed:", error.message);
        const demoUsers = JSON.parse(localStorage.getItem(DEMO_USERS_KEY) || "[]");
        const user = demoUsers.find((u: { email: string; password: string }) => u.email === email && u.password === password);

        if (user) {
          localStorage.setItem("riman_current_user", JSON.stringify({
            email: user.email,
            fullName: user.fullName
          }));
          toast({ title: "Welcome back!", description: "Logged in successfully (Demo Mode)." });
          const from = location.state?.from?.pathname || "/";
          navigate(from, { replace: true });
        } else {
          throw new Error("Invalid email or password.");
        }
      } else {
        // Try Supabase registration first
        const { error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            data: { full_name: fullName },
          },
        });

        // If Supabase succeeds but requires confirmation
        if (!error) {
          toast({
            title: "Account created!",
            description: "Please check your email to verify your account."
          });
          navigate("/");
          setIsLoading(false);
          return;
        }

        // If Supabase fails, use local demo mode
        console.log("Supabase registration failed:", error.message);
        const demoUsers = JSON.parse(localStorage.getItem(DEMO_USERS_KEY) || "[]");
        const existingUser = demoUsers.find((u: { email: string }) => u.email === email);

        if (existingUser) {
          throw new Error("An account with this email already exists.");
        }

        // Create local demo user (no password stored for security)
        const newUser = {
          email,
          fullName: fullName || email.split('@')[0],
          createdAt: new Date().toISOString()
        };

        demoUsers.push(newUser);
        localStorage.setItem(DEMO_USERS_KEY, JSON.stringify(demoUsers));
        localStorage.setItem("riman_current_user", JSON.stringify({
          email: newUser.email,
          fullName: newUser.fullName
        }));

        toast({
          title: "Account created!",
          description: "Welcome to Riman Fashion! (Demo Mode)"
        });
        navigate("/", { replace: true });
      }
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'An unexpected error occurred';
      toast({
        title: isLogin ? "Login Failed" : "Registration Failed",
        description: message,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleAuth = async () => {
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: window.location.origin
        }
      });
      if (error) throw error;
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Google authentication failed';
      toast({
        title: "Google Login Failed",
        description: message,
        variant: "destructive",
      });
    }
  };

  return (
    <Layout>
      <section className="pt-32 pb-24 md:pt-40 md:pb-32 min-h-screen flex items-center justify-center">
        <div className="w-full max-w-md px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="bg-white p-8 md:p-10 shadow-sm border border-border"
          >
            <div className="text-center mb-8">
              <h1 className="heading-display text-3xl mb-2">
                {isLogin ? "Welcome Back" : "Create Account"}
              </h1>
              <p className="font-body text-xs text-muted-foreground uppercase tracking-widest">
                {isLogin ? "Sign in to your account" : "Join Riman Fashion"}
              </p>
            </div>

            <form onSubmit={handleAuth} className="space-y-5">
              {!isLogin && (
                <div className="space-y-2">
                  <label className="font-body text-[10px] tracking-widest uppercase text-foreground/80">Full Name</label>
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full h-12 bg-transparent border-b border-border text-sm focus:border-gold focus:outline-none transition-colors rounded-none px-0"
                    placeholder="Jane Doe"
                  />
                </div>
              )}

              <div className="space-y-2">
                <label className="font-body text-[10px] tracking-widest uppercase text-foreground/80">Email</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full h-12 bg-transparent border-b border-border text-sm focus:border-gold focus:outline-none transition-colors rounded-none px-0"
                  placeholder="jane@example.com"
                />
              </div>

              <div className="space-y-2">
                <div className="flex justify-between">
                  <label className="font-body text-[10px] tracking-widest uppercase text-foreground/80">Password</label>
                  {isLogin && (
                    <button type="button" onClick={() => toast({ title: "Password Reset", description: "Password reset is not available in demo mode." })} className="font-body text-[10px] tracking-widest uppercase text-gold hover:text-foreground transition-colors">
                      Forgot?
                    </button>
                  )}
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full h-12 bg-transparent border-b border-border text-sm focus:border-gold focus:outline-none transition-colors rounded-none px-0"
                  placeholder="••••••••"
                />
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="btn-luxury w-full mt-8"
              >
                {isLoading ? "Processing..." : isLogin ? "Sign In" : "Register"}
              </button>
            </form>

            <div className="relative mt-8 mb-6">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-border" />
              </div>
              <div className="relative flex justify-center text-[10px] uppercase tracking-[0.2em] font-body">
                <span className="bg-white px-4 text-muted-foreground">Or continue with</span>
              </div>
            </div>

            <button
              type="button"
              onClick={handleGoogleAuth}
              disabled={isLoading}
              className="w-full h-12 flex items-center justify-center gap-3 border border-border hover:bg-gray-50 transition-colors font-body text-sm"
            >
              <GoogleIcon size={18} />
              Google
            </button>

            <div className="mt-8 text-center">
              <p className="font-body text-xs text-muted-foreground">
                {isLogin ? "Don't have an account?" : "Already have an account?"}{" "}
                <button
                  type="button"
                  onClick={() => setIsLogin(!isLogin)}
                  className="text-gold hover:text-foreground transition-colors uppercase tracking-widest font-medium"
                >
                  {isLogin ? "Register" : "Sign In"}
                </button>
              </p>
            </div>
          </motion.div>
        </div>
      </section>
    </Layout>
  );
};

export default AuthPage;
