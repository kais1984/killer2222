import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { User, Session } from "@supabase/supabase-js";
import { supabase } from "@/integrations/supabase/client";

const hasSupabase = supabase !== null;

interface AuthUser {
  id: string;
  email: string;
  fullName?: string;
  isDemo?: boolean;
}

interface AuthContextType {
  user: AuthUser | null;
  session: Session | null;
  loading: boolean;
  signOut: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = async () => {
    // If no Supabase, use demo user from localStorage only
    if (!hasSupabase) {
      const demoUser = localStorage.getItem("riman_current_user");
      if (demoUser) {
        const parsed = JSON.parse(demoUser);
        setUser({
          id: "demo",
          email: parsed.email,
          fullName: parsed.fullName,
          isDemo: true,
        });
      } else {
        setUser(null);
      }
      setSession(null);
      setLoading(false);
      return;
    }

    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.user) {
        setSession(session);
        setUser({
          id: session.user.id,
          email: session.user.email || "",
          fullName: session.user.user_metadata?.full_name as string | undefined,
        });
      } else {
        // Check for demo user in localStorage
        const demoUser = localStorage.getItem("riman_current_user");
        if (demoUser) {
          const parsed = JSON.parse(demoUser);
          setUser({
            id: "demo",
            email: parsed.email,
            fullName: parsed.fullName,
            isDemo: true,
          });
        } else {
          setUser(null);
        }
        setSession(null);
      }
    } catch (error) {
      console.error("Error refreshing user:", error);
      // Fallback to local demo user
      const demoUser = localStorage.getItem("riman_current_user");
      if (demoUser) {
        const parsed = JSON.parse(demoUser);
        setUser({
          id: "demo",
          email: parsed.email,
          fullName: parsed.fullName,
          isDemo: true,
        });
      } else {
        setUser(null);
      }
    }
  };

  const signOut = async () => {
    if (supabase) {
      try {
        await supabase.auth.signOut();
      } catch (error) {
        console.error("Error signing out from Supabase:", error);
      }
    }
    // Clear demo user
    localStorage.removeItem("riman_current_user");
    setUser(null);
    setSession(null);
  };

  useEffect(() => {
    // Initial session check
    refreshUser().finally(() => setLoading(false));

    // Listen for auth changes (only if Supabase is configured)
    if (!hasSupabase || !supabase) return;

    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (session?.user) {
        setSession(session);
        setUser({
          id: session.user.id,
          email: session.user.email || "",
          fullName: session.user.user_metadata?.full_name as string | undefined,
        });
      } else if (event === "SIGNED_OUT") {
        // Check for demo user
        const demoUser = localStorage.getItem("riman_current_user");
        if (demoUser) {
          const parsed = JSON.parse(demoUser);
          setUser({
            id: "demo",
            email: parsed.email,
            fullName: parsed.fullName,
            isDemo: true,
          });
        } else {
          setUser(null);
        }
        setSession(null);
      }
    });

    return () => {
      if (subscription) subscription.unsubscribe();
    };
  }, []);

  return (
    <AuthContext.Provider value={{ user, session, loading, signOut, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
