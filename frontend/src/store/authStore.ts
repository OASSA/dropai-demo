import { create } from "zustand";
import { persist } from "zustand/middleware";
import { User } from "../types";
import { authService } from "../services/authService";

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  fetchMe: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: !!localStorage.getItem("access_token"),
      isLoading: false,

      login: async (email, password) => {
        set({ isLoading: true });
        try {
          await authService.login(email, password);
          const user = await authService.me();
          set({ user, isAuthenticated: true, isLoading: false });
        } catch (err) {
          set({ isLoading: false });
          throw err;
        }
      },

      logout: () => {
        authService.logout();
        set({ user: null, isAuthenticated: false });
      },

      fetchMe: async () => {
        try {
          const user = await authService.me();
          set({ user, isAuthenticated: true });
        } catch {
          authService.logout();
          set({ user: null, isAuthenticated: false });
        }
      },
    }),
    { name: "auth-storage", partialize: (s) => ({ user: s.user, isAuthenticated: s.isAuthenticated }) }
  )
);
