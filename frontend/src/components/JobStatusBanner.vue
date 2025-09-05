<template>
  <div
    v-if="jobStore.jobId && jobStore.jobStatus && isVisible && jobStore.jobStatus !== 'Logout'"
    :class="`${bgColor} text-gray-600 py-2 px-4 text-center shadow-md`"
  >
    <div class="flex justify-center items-center gap-2">
      <Loader2 v-if="isInProgress" class="animate-spin w-4 h-4" />
      <span>{{ message }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted, computed } from "vue";
import { useJobStore } from "@/stores/jobStore"; // Vue equivalent of useJob hook
import { Loader2 } from "lucide-vue-next";

const jobStore = useJobStore();
const isVisible = ref(true);

let timer = null;

watch(
  () => jobStore.jobStatus,
  (newStatus) => {
    if (newStatus == "start" || newStatus == "queued") {
      jobStore.isVisible.value = true;
    } else if (newStatus === "complete" || newStatus === "terminate" || newStatus === "abort") {
      jobStore.isVisible.value = true;
      if (timer) clearTimeout(timer);
      timer = setTimeout(() => {
        jobStore.isVisible.value = false;
      }, 5000); // 5 seconds
    }
  }
);

onUnmounted(() => {
  if (timer) clearTimeout(timer);
});

const isInProgress = computed(() => jobStore.jobStatus === "start");
const isCompleted = computed(() => jobStore.jobStatus === "complete");
const isPending = computed(() => jobStore.jobStatus === "queued");

const bgColor = computed(() => {
  if (isInProgress.value) return "bg-yellow-400";
  if (isCompleted.value) return "bg-green-500";
  if (isPending.value) return "bg-orange-300";

  return "bg-red-400";
});

const message = computed(() => {
  if (isInProgress.value) return "Processing your images... Please wait.";
  if (isCompleted.value) return "Job completed successfully!";
  if (isPending.value) return "System is busy. Your job is queueing. Wait for a second.";
  return "Something went wrong with your job. Please try again.";
});
</script>
