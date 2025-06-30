<template>
  <div class="container mx-auto px-4 py-8 max-w-4xl">
    <div class="flex justify-center items-center mb-6">
      <h1 class="text-sm sm:text-base md:text-lg lg:text-xl xl:text-4xl font-bold">Do You Know this Person? 🔎</h1>
    </div>

    <Instruction v-if="userProfileStore.isNewUser" />

    <template v-else>
      <TrainAIModel v-if="!isModelExist" />

      <div v-else>
        <h2 class="text-xl font-semibold text-gray-500 mb-4">Ask AI assistant 🤖 to help you identify...</h2>

        <ChooseSingleImage :chosenImage="chosenImage" @update:chosenImage="onImageChange" />

        <div class="flex justify-center mt-6">
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

        <div v-if="identifiedPerson?.image" class="mt-6">
          <h2 class="text-3xl font-bold">This person is:</h2>
          <div class="flex items-center mt-4 space-x-6">
            <img
              :src="identifiedPerson.image"
              :alt="identifiedPerson.person"
              width="300"
              height="300"
              class="rounded-full"
            />
            <div>
              <h3 class="text-2xl font-bold">{{ identifiedPerson.person }}</h3>
              <p>{{ identifiedPerson.summary }}</p>
            </div>
          </div>
        </div>

        <div v-else-if="identifiedPerson" class="mt-4">
          <h3 class="text-3xl font-bold">{{ identifiedPerson.person }}</h3>
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
import { identify, type IdentifyResponse, type RemindeeInfo } from "@/services/identify";
import { check_model_exist } from "@/services/upload_train";

import TrainAIModel from "@/components/TrainAIModel.vue";
import ChooseSingleImage from "@/components/ChooseSingleImage.vue";
import Instruction from "@/pages/Instruction.vue";

// Auth & Profile
const authStore = useAuthStore();
const userProfileStore = useUserProfileStore();
const router = useRouter();

// Local state
const identifiedPerson = ref<RemindeeInfo | null>(null);
const isModelExist = ref(false);
const msg = ref<string | null>(null);
const chosenImage = ref<File | null>(null);

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
  } catch (err) {
    console.error("Error checking model existence:", err);
  }
});

// Update from child image picker
const onImageChange = (file: File | null) => {
  chosenImage.value = file;
};

// Submit image to identify
const handleImageSubmit = async () => {
  try {
    if (chosenImage.value) {
      const response: IdentifyResponse = await identify(authStore.token, chosenImage.value);
      if (response.data) {
        if (response.data.person === "NA") {
          identifiedPerson.value = null;
        } else {
          identifiedPerson.value = response.data;
        }
      } else {
        identifiedPerson.value = null;
      }
      msg.value = null;
    }
  } catch (error) {
    console.error(error);
    msg.value = "There was a problem identifying the image. Please try again.";
  }
};
</script>
