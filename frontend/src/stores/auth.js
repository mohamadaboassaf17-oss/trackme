import { defineStore } from "pinia";
import api from "@/utils/api";
import { isValidJSON } from "@/utils/helpers";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: null,
    user: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === "admin",
  },

  actions: {
    initFromStorage() {
      const token = localStorage.getItem("token");
      const userStr = localStorage.getItem("user");

      if (token && !token.trim().startsWith("<") && token !== "undefined") {
        this.token = token;
      } else if (token) {
        localStorage.removeItem("token");
      }

      if (userStr) {
        try {
          const user = JSON.parse(userStr);
          if (user && typeof user === "object") {
            this.user = user;
          } else {
            localStorage.removeItem("user");
          }
        } catch {
          localStorage.removeItem("user");
        }
      }
    },

    async login(username, password) {
      const response = await api.post("/auth/login", { username, password });
      const data = response.data;

      if (typeof data === "string" && data.trim().startsWith("<")) {
        throw new Error("Received HTML instead of JSON — check baseURL configuration");
      }

      if (!data || typeof data !== "object") {
        throw new Error("Invalid server response");
      }

      if (!data.access_token || typeof data.access_token !== "string") {
        throw new Error("No valid token received");
      }

      this.token = data.access_token;
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

    async googleLogin(credential) {
      const response = await api.post("/auth/google", { credential });
      const data = response.data;

      if (typeof data === "string" && data.trim().startsWith("<")) {
        throw new Error("Received HTML instead of JSON — check baseURL configuration");
      }

      if (!data || typeof data !== "object") {
        throw new Error("Invalid server response");
      }

      if (!data.access_token || typeof data.access_token !== "string") {
        throw new Error("No valid token received");
      }

      this.token = data.access_token;
      localStorage.setItem("token", this.token);
      await this.fetchUser();
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
