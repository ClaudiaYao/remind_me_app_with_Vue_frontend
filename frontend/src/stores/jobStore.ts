import { defineStore } from "pinia";
import { ref, watch } from "vue";
import { isTrainingComplete } from "@/services/upload_train";
import { useAuthStore } from "./authStore"; // assuming you have auth store for token

// export type JobStatus = "pending" | "complete" | "terminate" | "abort" | "start" | "error" | "idle";

export const useJobStore = defineStore("job", () => {
  const jobId = ref<string | null>(null);
  const jobStatus = ref<string>("idle");
  const authStore = useAuthStore();

  let intervalId: ReturnType<typeof setInterval> | null = null;

  async function resetJobStatus() {
    jobStatus.value = "idle";
  }

  async function checkJobStatus() {
    if (!jobId.value || !authStore.token) return;

    try {
      const status = await isTrainingComplete(authStore.token, jobId.value);
      jobStatus.value = status;
    } catch (error) {
      console.error("Error checking job status", error);
      jobStatus.value = "error";
    }
  }

  // Watch jobId and token, setup interval to check status repeatedly
  watch(
    [jobId, () => authStore.token],
    ([newJobId, newToken], [oldJobId, oldToken]) => {
      if (!newJobId || !newToken) {
        jobStatus.value = "idle";
        jobId.value = null;

        if (intervalId) {
          clearInterval(intervalId);
          intervalId = null;
        }

        return;
      }

      checkJobStatus();

      if (intervalId) clearInterval(intervalId);
      intervalId = setInterval(() => {
        checkJobStatus();
      }, 6000);
    },
    { immediate: true }
  );

  return { jobId, jobStatus, resetJobStatus, checkJobStatus };
});
