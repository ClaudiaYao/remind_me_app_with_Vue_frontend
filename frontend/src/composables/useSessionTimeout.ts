import { ref, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";

const WARNING_TIME_MS = 4 * 60 * 1000; // 4 minutes
const TIMEOUT_AFTER_WARNING_MS = 60 * 1000; // 1 minute

export function useSessionTimeout() {
  const showWarningDialog = ref(false);
  const router = useRouter();

  let warningTimer: ReturnType<typeof setTimeout> | null = null;
  let logoutTimer: ReturnType<typeof setTimeout> | null = null;

  const getLastActiveTime = (): number | null => {
    const value = localStorage.getItem("lastActiveTime");
    return value ? parseInt(value, 10) : null;
  };

  const updateLastActiveTime = () => {
    localStorage.setItem("lastActiveTime", Date.now().toString());
  };

  const clearTimers = () => {
    if (warningTimer) clearTimeout(warningTimer);
    if (logoutTimer) clearTimeout(logoutTimer);
  };

  const startLogoutTimer = () => {
    logoutTimer = setTimeout(() => {
      localStorage.clear();
      router.push("/login");
    }, TIMEOUT_AFTER_WARNING_MS);
  };

  const startTimers = () => {
    clearTimers();
    const lastActive = getLastActiveTime();
    const now = Date.now();
    const inactiveTime = now - (lastActive || now);

    if (inactiveTime >= WARNING_TIME_MS) {
      showWarningDialog.value = true;
      startLogoutTimer();
    } else {
      warningTimer = setTimeout(() => {
        showWarningDialog.value = true;
        startLogoutTimer();
      }, WARNING_TIME_MS - inactiveTime);
    }
  };

  const handleUserActivity = () => {
    updateLastActiveTime();
    if (showWarningDialog.value) {
      showWarningDialog.value = false;
    }
    startTimers();
  };

  const stayLoggedIn = () => {
    updateLastActiveTime();
    showWarningDialog.value = false;
    startTimers();
  };

  onMounted(() => {
    const events = ["click", "mousemove", "keydown", "scroll"];
    events.forEach((event) => window.addEventListener(event, handleUserActivity));
    startTimers();

    onUnmounted(() => {
      clearTimers();
      events.forEach((event) => window.removeEventListener(event, handleUserActivity));
    });
  });

  return { showWarningDialog, stayLoggedIn };
}
