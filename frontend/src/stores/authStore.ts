import { defineStore } from "pinia";
import { CognitoUser, AuthenticationDetails } from "amazon-cognito-identity-js";
import { userPool } from "@/services/userpool";
import { authenticateUser, notifyBackendLogin, notifyBackendLogout } from "@/services/authentication";
import { CognitoAuthError } from "@/services/appExceptions";
import router from "@/router"; // Assuming you have vue-router setup

interface LoginType {
  email: string;
  password: string;
}

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null as string | null,
    token: "",
  }),
  actions: {
    init() {
      const storedInfo = localStorage.getItem("user");
      const lastActiveTime = parseInt(localStorage.getItem("lastActiveTime") || "0", 10);
      const now = Date.now();
      const sessionTimeout = 5 * 60 * 1000; // 5 minutes

      if (storedInfo && now - lastActiveTime <= sessionTimeout) {
        const parsed = JSON.parse(storedInfo);
        this.user = parsed.email;
        this.token = parsed.token;
      } else {
        this.logout();
      }

      // Activity tracking
      const updateActivity = () => {
        localStorage.setItem("lastActiveTime", Date.now().toString());
      };

      window.addEventListener("mousemove", updateActivity);
      window.addEventListener("keydown", updateActivity);

      window.addEventListener("beforeunload", () => {
        localStorage.setItem("lastActiveTime", Date.now().toString());
      });
    },

    async login(data: LoginType) {
      try {
        localStorage.setItem("lastActiveTime", Date.now().toString());

        const cognitoUser = new CognitoUser({
          Username: data.email,
          Pool: userPool,
        });

        const authenticationDetails = new AuthenticationDetails({
          Username: data.email,
          Password: data.password,
        });

        const CognitoUserSession = await authenticateUser(cognitoUser, authenticationDetails);

        const accessToken = CognitoUserSession.getIdToken().getJwtToken();
        const userId = CognitoUserSession.getIdToken().payload.sub;

        this.user = userId;
        this.token = accessToken;

        localStorage.setItem("user", JSON.stringify({ email: data.email, token: accessToken, userId }));

        await notifyBackendLogin(accessToken);

        // Navigate after login
        router.push("/");
      } catch (error) {
        if (error instanceof CognitoAuthError) {
          throw error;
        }
        console.error("Unknown login error:", error);
        throw new Error("Unexpected login failure");
      }
    },

    async logout() {
      localStorage.removeItem("user");
      localStorage.removeItem("lastActiveTime");

      const user = userPool.getCurrentUser();
      if (user) {
        user.signOut();
        await notifyBackendLogout(this.token);
      }
      this.user = null;
      this.token = "";
      router.push("/login");
    },
  },
});
