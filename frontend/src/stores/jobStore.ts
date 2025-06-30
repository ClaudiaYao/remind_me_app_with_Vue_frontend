import { defineStore } from "pinia";
import { ref, watch } from "vue";
import { isTrainingComplete } from "@/services/upload_train";
import { useAuthStore } from "./authStore"; // assuming you have auth store for token

export type JobStatus = "InProgress" | "Completed" | "Error" | null | "Logout";

export const useJobStore = defineStore("job", () => {
  const jobId = ref<string | null>(null);
  const jobStatus = ref<JobStatus>(null);
  const authStore = useAuthStore();

  let intervalId: ReturnType<typeof setInterval> | null = null;

  async function resetJobStatus() {
    jobStatus.value = null;
  }

  async function checkJobStatus() {
    if (!jobId.value || !authStore.token) return;

    try {
      const status = await isTrainingComplete(authStore.token, jobId.value);
      jobStatus.value = status ? "Completed" : "InProgress";
    } catch (error) {
      console.error("Error checking job status", error);
      jobStatus.value = "Error";
    }
  }

  // Watch jobId and token, setup interval to check status repeatedly
  watch(
    [jobId, () => authStore.token],
    ([newJobId, newToken], [oldJobId, oldToken]) => {
      if (!newJobId || !newToken) {
        jobStatus.value = newToken ? null : "Logout";
        jobId.value = null;

        if (intervalId) {
          clearInterval(intervalId);
          intervalId = null;
        }

        return;
      }

      jobStatus.value = "InProgress";
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
