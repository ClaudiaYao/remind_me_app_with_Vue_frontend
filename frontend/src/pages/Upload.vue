<script setup lang="ts">
import { ref, reactive, watch, onMounted } from "vue";
import { useRouter } from "vue-router";
import UploadRemindeeInfoBox from "@/components/UploadRemindeeInfoBox.vue";
import RemindeeCard from "@/components/RemindeeCard.vue";
import type { UploadPayload } from "@/services/upload_train";
import { trigger_train, upload as uploadImage } from "@/services/upload_train";
import { useAuthStore } from "@/stores/authStore";
import { useJobStore } from "@/stores/jobStore";
import type { RemindeeProfile } from "@/types/remindee";

const router = useRouter();
const authStore = useAuthStore();
const jobStore = useJobStore();

const uploadData = ref<UploadPayload>({
  person_name: "",
  relationship: "",
  files: [],
  summary: [],
});

const infoMsg = ref("");
const errorMsg = ref("");
const uploadedRemindee = ref<RemindeeProfile | null>(null);

const isTrainDisabled = ref(true);
const uploadDisabled = ref(true);

// Redirect if no user
onMounted(() => {
  if (!authStore.user) {
    router.push("/");
  } else {
    isTrainDisabled.value = true;
    uploadDisabled.value = false;
  }
});

// Enable/disable upload button based on form data
watch(
  () => [uploadData.value.person_name, uploadData.value.relationship, uploadData.value.files.length],
  ([personName, relationship, file_length]) => {
    if (file_length) {
      uploadDisabled.value = !(personName !== "" && relationship !== "");
      console.log("uploadedDisabled file_length:", uploadDisabled.value);
    } else {
      uploadDisabled.value = true;
      console.log("uploadedDisabled:", uploadDisabled.value);
    }
  },
  { deep: true }
);

async function handleTrain() {
  try {
    const jobId = await trigger_train(authStore.token);
    jobStore.jobId = jobId;
    infoMsg.value = "Your AI Assistant has finished training. Now you could begin identifying your remindees.";
    errorMsg.value = "";
    isTrainDisabled.value = true;
    uploadDisabled.value = false;
  } catch (error) {
    console.error(error);
    errorMsg.value = "An error has occurred. Please try again later.";
    isTrainDisabled.value = false;
  }
}

async function handleBoxSubmit() {
  if (uploadData.value.files.length > 0) {
    try {
      const remindee_profile = await uploadImage(uploadData.value, authStore.token, (progress: number) => {
        infoMsg.value = `Uploading images... ${progress}%`;
      });

      infoMsg.value = "Successfully uploaded images!";
      errorMsg.value = "";
      uploadedRemindee.value = remindee_profile;

      // Reset form
      uploadData.value.person_name = "";
      uploadData.value.relationship = "";
      uploadData.value.summary = [];
      uploadData.value.files = [];

      isTrainDisabled.value = false;
      uploadDisabled.value = true;
    } catch (error) {
      console.error(error);
    }
  } else {
    console.log("nothing uploaded");
  }
}
</script>

<template>
  <div class="upload-container p-6 bg-white rounded-md min-w-[375px] min-h-[700px] text-black">
    <div class="flex justify-center items-center mb-6">
      <h1 class="text-3xl font-bold">Upload Remindee's Images 👩‍🔧</h1>
    </div>
    <RemindeeCard v-if="uploadedRemindee" :person="uploadedRemindee" :index="0" />

    <h2 v-if="errorMsg" class="text-red-500">{{ errorMsg }}</h2>

    <div v-if="infoMsg" class="text-center py-12 bg-gray-50 rounded-lg">
      <p class="text-gray-700">{{ infoMsg }}</p>
    </div>

    <div class="flex justify-center mt-6">
      <UploadRemindeeInfoBox v-model:model-value="uploadData" />
    </div>

    <div class="flex justify-center mt-6">
      <button
        :class="[
          'flex w-64 justify-center rounded-md px-3 py-2 text-sm/6 font-semibold text-white shadow-xs focus-visible:outline-2 focus-visible:outline-offset-2',
          uploadDisabled
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-orange-500 hover:bg-orange-600 focus-visible:outline-yellow-600',
        ]"
        :disabled="uploadDisabled"
        @click="handleBoxSubmit"
      >
        Upload Images
      </button>
    </div>

    <div class="flex justify-center mt-6">
      <button
        :class="[
          'flex w-64 justify-center rounded-md px-3 py-2 text-sm/6 font-semibold text-white shadow-xs focus-visible:outline-2 focus-visible:outline-offset-2',
          isTrainDisabled
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-orange-500 hover:bg-orange-600 focus-visible:outline-yellow-600',
        ]"
        :disabled="isTrainDisabled"
        @click="handleTrain"
      >
        Train Your AI Assistant
      </button>
    </div>
  </div>
</template>
