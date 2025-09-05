<template>
  <div class="container mx-auto px-4 py-8 max-w-4xl">
    <div class="flex justify-center items-center mb-6">
      <h1 class="text-sm sm:text-base md:text-lg lg:text-4xl font-bold">🤖 Train your AI Assistant 🤖</h1>
    </div>
    <h2 class="text-xl font-semibold text-gray-500 mb-4">
      Train your AI Assistant, so that it could identify your remindees more accurately...
    </h2>

    <h2 v-if="errorMsg" class="text-red-500">{{ errorMsg }}</h2>

    <div v-if="infoMsg" class="text-center py-12 bg-gray-50 rounded-lg">
      <p class="text-green-600 font-bold text-l">{{ infoMsg }}</p>
    </div>

    <div class="flex justify-center mt-6">
      <button
        class="flex w-64 justify-center rounded-md bg-orange-500 px-3 py-2 text-sm/6 font-semibold text-white shadow-xs hover:bg-orange-600 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-yellow-600"
        :disabled="isModelUpdated"
        @click="handleTrain"
      >
        Train Your AI Assistant
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watchEffect, watch } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/authStore";
import { useJobStore } from "@/stores/jobStore";
import { trigger_train } from "@/services/upload_train";

const router = useRouter();
const authStore = useAuthStore();
const jobStore = useJobStore();

const infoMsg = ref("");
const errorMsg = ref("");
const isModelUpdated = ref(false);

// Redirect if user is not logged in
watchEffect(() => {
  if (!authStore.user) {
    router.push("/");
  }
});

let timer: ReturnType<typeof setTimeout> | null = null;

watch(
  () => jobStore.jobStatus,
  (newStatus) => {
    if (!timer) {
      // Start timeout when first status is received
      timer = setTimeout(() => {
        errorMsg.value = "Timeout: Training took too long. Please try again.";
        infoMsg.value = "";
        // Optional: trigger abort logic or UI reset
      }, 600000); // 600 seconds
    }

    if (newStatus === "complete") {
      clearTimeout(timer!);
      timer = null;
      infoMsg.value = "Your AI Assistant has finished training. Now you could identify persons.";
      errorMsg.value = "";
    } else if (["abort", "error", "terminate", "cancelled", "timeout"].includes(newStatus)) {
      clearTimeout(timer!);
      timer = null;
      infoMsg.value = "";

      switch (newStatus) {
        case "queued":
          infoMsg.value = "Queue... ⏳";
          break;
        case "start":
          infoMsg.value = "Still processing... ⏳";
          break;
        case "abort":
          errorMsg.value = "Processing failed. Please try again.";
          break;
        case "timeout":
          errorMsg.value = "queueing is too long. The job expires. Please try again.";
          break;
        default:
          errorMsg.value = "Unexpected response. Please try again.";
          break;
      }
    }
  },
  { immediate: true }
);

async function handleTrain() {
  try {
    const jobId = await trigger_train(authStore.token);
    console.log(jobId);
    jobStore.jobId = jobId;
    infoMsg.value = "Your AI Assistant is in training process. Please wait for a while...";
    errorMsg.value = "";
    isModelUpdated.value = true;
  } catch (error) {
    console.error(error);
    errorMsg.value = "An error has occurred. Please try again later.";
    isModelUpdated.value = false;
  }
}
</script>
