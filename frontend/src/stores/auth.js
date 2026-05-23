import { defineStore } from "pinia";
import api from "@/utils/api";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem("token") || null,
    user: JSON.parse(localStorage.getItem("user") || "null"),
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === "admin",
  },

  actions: {
    async login(username, password) {
      const response = await api.post("/auth/login", { username, password });
      this.token = response.data.access_token;
      localStorage.setItem("token", this.token);
      await this.fetchUser();
    },

    async register(username, password, salaryType, salaryAmount) {
      const response = await api.post("/auth/register", {
        username,
        password,
        salary_type: salaryType,
        salary_amount: salaryAmount,
      });
      return response.data;
    },

    async fetchUser() {
      try {
        const response = await api.get("/auth/me");
        this.user = response.data;
        localStorage.setItem("user", JSON.stringify(this.user));
      } catch {
        this.logout();
      }
    },

    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem("token");
      localStorage.removeItem("user");
    },
  },
});
