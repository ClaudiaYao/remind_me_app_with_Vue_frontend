<template>
  <div v-if="!authStore.user">
    <Login />
  </div>

  <div v-else class="container mx-auto px-4 py-8 max-w-4xl">
    <div v-if="loading" class="flex justify-center items-center h-screen">
      <p class="text-gray-500 text-lg">Loading remindee details...</p>
    </div>

    <div v-else-if="error" class="flex justify-center items-center h-screen">
      <p class="text-red-500 text-lg">{{ error }}</p>
    </div>

    <div v-else-if="!remindeeInfoAll" class="flex justify-center items-center h-screen">
      <p class="text-red-500 text-lg">Fail to load the remindee information.</p>
    </div>

    <div v-else class="flex flex-col md:flex-row h-full p-4 space-y-4 md:space-y-0 md:space-x-6">
      <!-- Left Pane -->
      <div class="w-full md:w-1/4 bg-white shadow rounded-xl p-4 flex flex-col items-center">
        <img :src="profileImageURL" alt="Profile" class="w-32 h-32 rounded-full object-cover" />
        <h2 class="mt-4 text-xl font-bold">{{ personName }}</h2>
        <p class="text-gray-500">{{ relationship }}</p>
      </div>

      <!-- Right Pane -->
      <div class="w-full md:w-3/4 bg-white shadow rounded-xl p-4 space-y-6">
        <!-- Summary -->
        <div>
          <h3 class="!text-3xl font-semibold text-gray-700">✨ AI Assistant's Summary ✨</h3>
          <br />
          <p class="mt-2 text-gray-700 !text-left">{{ remindeeInfoAll.ai_summary }}</p>
        </div>
        <br />

        <p v-if="msg" class="font-medium !text-yellow-800 dark:text-yellow-500">{{ msg }}</p>

        <button
          :disabled="!hasUnsavedChanges"
          @click="handleSubmitChange"
          class="mt-2 px-3 py-2 bg-orange-500 text-white rounded-md hover:bg-orange-600 transition-colors duration-200 inline-flex items-center text-sm"
        >
          Submit Change of Remindee Information
        </button>

        <h2 class="mt-4 text-xl font-bold !text-left">Images of {{ personName }}</h2>

        <!-- Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div
            v-for="(item, index) in remindeeRecords"
            :key="index"
            class="bg-white shadow-md rounded-xl p-4 flex flex-col space-y-2"
          >
            <img
              :src="remindeeInfoAll.image_presigned_url[item.image_object_key]"
              :alt="`Card image ${index}`"
              :class="['w-full h-40 object-cover rounded-lg', { 'opacity-60': deletedItems[index] }]"
            />

            <label for="summary" class="block text-sm/6 font-medium text-gray-900">Image Summary:</label>
            <input
              :value="remindeeRecords[index].summary"
              @input="(e) => handleUpdate((e.target as HTMLInputElement).value, index)"
              :disabled="deletedItems[index]"
              class="border border-gray-300 rounded px-2 w-full"
            />

            <div class="mt-2 flex justify-end space-x-2">
              <button class="px-3 py-1 bg-orange-500 text-sm rounded hover:bg-orange-600" @click="handleDelete(index)">
                {{ deletedItems[index] ? "Undo Delete" : "Delete" }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <PromptDialog
        v-if="showPrompt"
        :open="showPrompt"
        :message="'You have unsaved changes for the remindee. Proceed to leave the page?'"
        @confirm="confirmLeave"
        @cancel="cancelLeave"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/authStore";
import { useUserProfileStore } from "@/stores/UserProfileStore";
import Login from "@/components/Login.vue";
import PromptDialog from "@/components/PromptDialog.vue";
import { fetchRemindeeDetails, updateRemindeeDetails } from "@/services/profile";
import type { RemindeeInfoAll, RemindeeUpdate, RemindeeUpdatePayload } from "@/services/profile";
import type { RemindeeSingleRecord } from "@/types/remindee";
import { useNavigationGuard } from "@/composables/useNavigationGuard";

const authStore = useAuthStore();
const userProfileStore = useUserProfileStore();

const route = useRoute();
const router = useRouter();

const personName = route.query.person_name as string | undefined;
if (!personName) {
  throw new Error("Missing person_name in URL parameters");
}

const profileImageURL = ref<string | undefined>();
const relationship = ref<string | undefined>();
const remindeeInfoAll = ref<RemindeeInfoAll | null>(null);
const remindeeRecords = ref<RemindeeSingleRecord[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);
const msg = ref<string | null>(null);

const deletedItems = reactive<boolean[]>([]);
const updatedItems = reactive<boolean[]>([]);
const hasUnsavedChanges = ref(false);
const { showPrompt, confirmLeave, cancelLeave } = useNavigationGuard(() => hasUnsavedChanges.value);

onMounted(async () => {
  loading.value = true;

  try {
    const response = await fetchRemindeeDetails(authStore.token, personName);
    remindeeInfoAll.value = response;

    const relationsSet = new Set(response.records.map((item) => item.relationship));
    relationship.value = Array.from(relationsSet).join(", ");

    const randomRecord = response.records[Math.floor(Math.random() * response.records.length)];
    profileImageURL.value = response.image_presigned_url[randomRecord.image_object_key];

    remindeeRecords.value = response.records;

    deletedItems.splice(0, deletedItems.length, ...new Array(response.records.length).fill(false));
    updatedItems.splice(0, updatedItems.length, ...new Array(response.records.length).fill(false));
    hasUnsavedChanges.value = false;
    error.value = null;
  } catch (err) {
    console.error("Failed to fetch remindee details:", err);
    error.value = "Failed to load data. Please try again later.";
  } finally {
    loading.value = false;
  }
});

// watch(
//   remindeeRecords,
//   () => {
//     for (let i = 0; i < remindeeRecords.value.length; i++) {
//       updatedItems[i] = true;
//     }
//     console.log("remindeeRecords changed:", remindeeRecords.value);
//     console.log("in watch, hasUnsavedChanges.value:", hasUnsavedChanges.value);
//     hasUnsavedChanges.value = true;
//   },
//   { deep: true }
// );

function handleDelete(index: number) {
  deletedItems.splice(index, 1, !deletedItems[index]);
  hasUnsavedChanges.value = deletedItems.some((item) => item === true) || updatedItems.some((item) => item === true);
}

function handleUpdate(value: string, index: number) {
  remindeeRecords.value[index].summary = value;
  updatedItems[index] = true;
  hasUnsavedChanges.value = true;
}

async function handleSubmitChange() {
  const allUpdateRecords: RemindeeUpdate[] = [];

  for (let i = 0; i < deletedItems.length; i++) {
    if (deletedItems[i] === true) {
      allUpdateRecords.push({
        image_object_url: remindeeRecords.value[i].image_object_key,
        image_summary: remindeeRecords.value[i].summary,
        action: "delete",
      });
    }
  }

  for (let i = 0; i < updatedItems.length; i++) {
    if (updatedItems[i] === true && deletedItems[i] === false) {
      allUpdateRecords.push({
        image_object_url: remindeeRecords.value[i].image_object_key,
        image_summary: remindeeRecords.value[i].summary,
        action: "update",
      });
    }
  }

  const personName = route.query.person_name as string | undefined;
  if (!personName) {
    throw new Error("Missing person_name in URL parameters");
  }

  const updatePayload: RemindeeUpdatePayload = {
    person_name: personName,
    items: allUpdateRecords,
  };

  const response = await updateRemindeeDetails(updatePayload, authStore.token);
  if (response.success === true) {
    msg.value = "Remindee info has been updated.";
  }

  remindeeRecords.value = remindeeRecords.value.filter((_, index) => !deletedItems[index]);

  deletedItems.splice(0, deletedItems.length, ...new Array(remindeeRecords.value.length).fill(false));
  updatedItems.splice(0, updatedItems.length, ...new Array(remindeeRecords.value.length).fill(false));
  hasUnsavedChanges.value = false;
  console.log("showPrompt.value:", showPrompt.value);
  console.log("hasUnsavedChanges.value:", hasUnsavedChanges.value);
}
</script>
