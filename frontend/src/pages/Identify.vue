<template>
  <div class="container mx-auto px-4 py-8 max-w-4xl">
    <div class="flex justify-center items-center mb-6">
      <h1 class="text-2xl sm:text-base md:text-lg lg:text-xl font-bold">Do You Know this Person? 🔎</h1>
    </div>

    <Instruction v-if="userProfileStore.isNewUser" />

    <template v-else>
      <div>
        <h2 class="text-xl font-semibold text-gray-500 mb-4">Ask AI assistant 🤖 to help you identify...</h2>

        <ChooseSingleImage :chosenImage="chosenImage" @update:chosenImage="onImageChange" />

        <div class="flex justify-center mb-6">
          <button
            class="flex w-64 justify-center rounded-md bg-orange-500 px-3 py-1.5 text-sm/6 font-semibold text-white shadow-xs hover:bg-orange-600 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-yellow-600"
            :disabled="!chosenImage"
            @click="handleImageSubmit"
          >
            Identify This Person
          </button>
        </div>

        <p v-if="msg" class="font-medium !text-yellow-800 dark:text-yellow-500 mt-4">
          {{ msg }}
        </p>

        <div v-if="identifiedPerson?.image" class="mt-4">
          <div class="flex items-center justify-center mb-6 space-x-6">
            <img
              :src="identifiedPerson.image"
              :alt="identifiedPerson.person"
              width="200"
              height="200"
              class="rounded-full"
            />
            <div>
              <h3 class="text-xl font-bold">{{ identifiedPerson.person }}</h3>
              <p>{{ identifiedPerson.summary }}</p>
            </div>
          </div>
        </div>

        <div v-else-if="identifiedPerson" class="mt-4">
          <h3 class="text-xl font-bold">{{ identifiedPerson.person }}</h3>
          <p class="text-2xl font-semibold">{{ identifiedPerson.summary }}</p>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/authStore";
import { useUserProfileStore } from "@/stores/UserProfileStore";
import { identify, isInferenceComplete, type IdentifyResponse, type RemindeeInfo } from "@/services/identify";
import { check_model_exist } from "@/services/upload_train";

// import TrainAIModel from "@/components/TrainAIModel.vue";
import ChooseSingleImage from "@/components/ChooseSingleImage.vue";
import Instruction from "@/pages/Instruction.vue";
import { API_BASE_URL, INFERENCE_TIME_MILSEC } from "@/config/config";
import { convertIfHeic } from "@/composables/userImageConversion";

// Auth & Profile
const authStore = useAuthStore();
const userProfileStore = useUserProfileStore();
const router = useRouter();

// Local state
const identifiedPerson = ref<RemindeeInfo | null>(null);
const isModelExist = ref(false);
const msg = ref<string | null>(null);
const chosenImage = ref<File | null>(null);

// // Watch the value and redirect when false
// watch(
//   isModelExist,
//   (newVal) => {
//     if (!newVal) {
//       router.push("/train"); // <-- route to the page you want
//     }
//   },
//   { immediate: true }
// );

// Watch for image clear
watch(chosenImage, (newVal) => {
  if (!newVal) identifiedPerson.value = null;
});

// Fetch model status on mount
onMounted(async () => {
  if (!authStore.user) {
    router.push("/");
    return;
  }
  try {
    isModelExist.value = await check_model_exist(authStore.token);
    if (!isModelExist.value) router.push("/train");
  } catch (err) {
    console.error("Error checking model existence:", err);
  }
});

// Update from child image picker
const onImageChange = (file: File | null) => {
  chosenImage.value = file;
};

// polling helper
const pollInterval = 3000; // 3 seconds
let startTime = Date.now();
let pollingTimer: number | null = null;

const pollInferenceStatus = async (job_id: string) => {
  if (Date.now() - startTime > INFERENCE_TIME_MILSEC) {
    msg.value = "Timed out. Please try again.";
    return;
  }

  if (pollingTimer) clearTimeout(pollingTimer);

  try {
    const result = await isInferenceComplete(authStore.token, job_id);

    switch (result.status) {
      case "complete":
        if (result.person === "unknown") {
          msg.value = "The person could not be recognized.";
        } else {
          if (result.data) identifiedPerson.value = result.data;
          else identifiedPerson.value = null;
        }
        msg.value = null; // Clear status message
        break;

      case "queued":
        msg.value = "Queue... ⏳";
        pollingTimer = window.setTimeout(() => pollInferenceStatus(job_id), pollInterval);
        break;
      case "start":
        msg.value = "Your AI assistant begins processing... ⏳";
        pollingTimer = window.setTimeout(() => pollInferenceStatus(job_id), pollInterval);
        break;

      case "abort":
        msg.value = "Processing failed. Please try again.";
        break;
      case "timeout":
        msg.value = "queueing is too long. The job expires. Please try again.";
        break;
      default:
        msg.value = "Unexpected response. Please try again.";
        break;
    }
  } catch (error) {
    console.error("Error during polling:", error);
    msg.value = "Error checking status. Please retry.";
  }
};

// Submit image to identify
const handleImageSubmit = async () => {
  identifiedPerson.value = null;
  msg.value = "Sending request to queue...";
  startTime = Date.now();

  try {
    if (!chosenImage.value) return;
    msg.value += "before identify...";

    const finalFile = await convertIfHeic(chosenImage.value);
    console.log("final file:", finalFile);
    console.log("chosenimage.value:", chosenImage.value);
    const response: IdentifyResponse = await identify(authStore.token, finalFile);
    msg.value = "after getting response:" + response;

    if (response.status === "queued" && response.job_id) {
      msg.value = "Queue... Please wait ⏳";
      pollInferenceStatus(response.job_id);
    }
  } catch (err) {
    console.error(err);
    msg.value = msg.value + "There was a problem submitting the image.";
  }
};
</script>
