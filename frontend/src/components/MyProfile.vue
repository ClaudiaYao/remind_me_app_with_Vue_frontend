<script setup lang="ts">
import { ref, watch, computed } from "vue";
import { useAuthStore } from "@/stores/authStore";
import { useUserProfileStore } from "@/stores/UserProfileStore";
import { updateProfile } from "@/services/profile";
import { useRouter } from "vue-router";

const fileInputRef = ref<HTMLInputElement | null>(null);
const preview = ref<string | undefined>();
const selectedFile = ref<File | null>(null);
const errorMessage = ref<string | null>(null);
const isSaving = ref(false);

const authStore = useAuthStore();
const userProfileStore = useUserProfileStore();
const router = useRouter();

// Reactive references
const userSummary = computed(() => userProfileStore.userProfile?.user_summary);
const avatar = computed(() => userProfileStore.userProfile?.avatar_url);

// Local editable copy (used for editing)
const editedSummary = ref({
  nick_name: "",
  age: 0,
  description: "",
  phone_number: "",
});

// Sync with store when it loads
watch(
  userSummary,
  (newSummary) => {
    if (newSummary) {
      editedSummary.value = { ...newSummary };
    }
  },
  { immediate: true }
);

watch(
  avatar,
  (url) => {
    preview.value = url;
  },
  { immediate: true }
);

function handleFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (file) {
    selectedFile.value = file;
    preview.value = URL.createObjectURL(file);
  }
}

async function handleSave() {
  if (!authStore.token) {
    errorMessage.value = "You must be logged in to update your profile.";
    return;
  }

  try {
    isSaving.value = true;
    await updateProfile(authStore.token, editedSummary.value, selectedFile.value);
    await userProfileStore.updateUserProfile(); // <-- sync store with latest info
  } catch (err) {
    console.error("Error updating profile:", err);
    errorMessage.value = "Failed to update profile. Please try again later.";
  } finally {
    isSaving.value = false;
    router.push("/");
  }
}

function handleCancel() {
  if (userSummary.value) {
    editedSummary.value = { ...userSummary.value };
    preview.value = avatar.value;
  }
  selectedFile.value = null;
  router.push("/");
}
</script>

<template>
  <div class="p-6 bg-white shadow-md rounded-md min-w-[375px] min-h-[700px] text-black">
    <h2 class="text-3xl font-bold p-1">My Profile</h2>

    <div class="space-y-4">
      <!-- Avatar -->
      <div class="relative w-32 h-32 group">
        <img
          :src="preview || '/profile.png'"
          alt="Profile"
          class="w-24 h-24 rounded-full object-cover border-2 border-gray-200"
        />
        <div
          class="absolute inset-0 bg-gray-400 bg-opacity-50 w-24 h-24 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
          @click="fileInputRef?.click()"
        >
          <span class="text-sm font-semibold text-white">Edit</span>
        </div>
        <input type="file" accept="image/*" class="hidden" ref="fileInputRef" @change="handleFileChange" />
      </div>

      <!-- Form Fields -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mt-4">Nickname:</label>
        <input class="w-full p-2 border border-gray-300 rounded" type="text" v-model="editedSummary.nick_name" />

        <label class="block text-sm font-medium text-gray-700 mt-4">Age:</label>
        <input class="w-full p-2 border border-gray-300 rounded" type="number" v-model.number="editedSummary.age" />

        <label class="block text-sm font-medium text-gray-700 mt-4">Description:</label>
        <input class="w-full p-2 border border-gray-300 rounded" type="text" v-model="editedSummary.description" />

        <label class="block text-sm font-medium text-gray-700 mt-4">Phone Number:</label>
        <input class="w-full p-2 border border-gray-300 rounded" type="text" v-model="editedSummary.phone_number" />

        <div v-if="errorMessage" class="text-red-500 mt-2">{{ errorMessage }}</div>
      </div>

      <!-- Buttons -->
      <div class="flex justify-end space-x-2 mt-6">
        <button @click="handleCancel" class="text-white bg-orange-400 px-4 py-2 rounded">Cancel</button>
        <button @click="handleSave" class="text-white bg-orange-500 px-4 py-2 rounded">
          {{ isSaving ? "Saving..." : "Save" }}
        </button>
      </div>
    </div>
  </div>
</template>
