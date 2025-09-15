<!-- <template>
  <div
    v-if="jobStore.jobId && jobStore.jobStatus && isVisible && jobStore.jobStatus !== 'Logout'"
    :class="`${bgColor} text-gray-600 py-2 px-4 text-center shadow-md`"
  >
    <div class="flex justify-center items-center gap-2">
      <Loader2 v-if="isInProgress" class="animate-spin w-4 h-4" />
      <span>{{ message }}</span>
    </div>
  </div>
</template> -->

<template>
  <transition name="slide-up">
    <div
      v-if="jobStore.jobId && jobStore.jobStatus && isVisible"
      class="fixed bottom-4 left-1/2 -translate-x-1/2 z-50 px-4 py-3 rounded-lg shadow-lg text-black"
      :class="bgColor"
    >
      <div class="flex items-center gap-2">
        <Loader2 v-if="isInProgress" class="animate-spin w-4 h-4" />
        <span>{{ message }}</span>
      </div>
    </div>
  </transition>
</template>

<style>
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>

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
      isVisible.value = true;
    } else if (
      (newStatus === "complete" || newStatus === "terminate" || newStatus === "abort" || newStatus === "timeout") &&
      isVisible
    ) {
      if (timer) clearTimeout(timer);
      timer = setTimeout(() => {
        isVisible.value = false;
      }, 5000); // 5 seconds
    }
  }
);

onUnmounted(() => {
  if (timer) clearTimeout(timer);
});

const isInProgress = computed(() => jobStore.jobStatus === "start");
const isCompleted = computed(() => jobStore.jobStatus === "complete");
const isPending = computed(() => jobStore.jobStatus === "queued" || jobStore.jobStatus === "idle");
const isFailed = computed(
  () =>
    jobStore.jobStatus === "terminate" ||
    jobStore.jobStatus === "error" ||
    jobStore.jobStatus === "abort" ||
    jobStore.jobStatus === "timeout"
);

const bgColor = computed(() => {
  if (isInProgress.value) return "bg-green-400";
  if (isCompleted.value) return "bg-green-500";
  if (isPending.value) return "bg-yellow-300";
  if (isFailed.value) return "bg-red-300";
});

const message = computed(() => {
  if (isInProgress.value) return "Processing your images... Please wait.";
  if (isCompleted.value) return "Job completed successfully!";
  if (isPending.value) return "Your model training job is queueing. Wait for a second.";
  return "Something went wrong with your job. Please try again.";
});
</script>
