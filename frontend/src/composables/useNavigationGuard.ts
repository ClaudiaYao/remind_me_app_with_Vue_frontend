// src/composables/useNavigationGuard.ts
import { ref, watch } from "vue";
import { useRouter, useRoute, onBeforeRouteLeave } from "vue-router";

export function useNavigationGuard(shouldBlock: () => boolean) {
  console.log("useNavigationGuard called shouldBlock:", shouldBlock());
  const showPrompt = ref(false);
  const nextLocation = ref<ReturnType<typeof useRoute> | null>(null);
  const router = useRouter();
  const bypassGuard = ref(false);

  const confirmLeave = () => {
    showPrompt.value = false;
    bypassGuard.value = true;
    if (nextLocation.value) {
      router.push(nextLocation.value.fullPath);
    }
  };

  const cancelLeave = () => {
    showPrompt.value = false;
    nextLocation.value = null;
  };

  onBeforeRouteLeave((to, from, next) => {
    if (bypassGuard.value) {
      bypassGuard.value = false; // reset after bypassing
      return next();
    }

    if (shouldBlock()) {
      showPrompt.value = true;
      console.log("Blocking navigation to:", to.fullPath, to);
      nextLocation.value = to;
      next(false); // block navigation
    } else {
      next(); // allow
    }
  });

  return {
    showPrompt,
    nextLocation,
    confirmLeave,
    cancelLeave,
  };
}
