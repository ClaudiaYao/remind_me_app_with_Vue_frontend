import { defineStore } from "pinia";
import { ref, computed, watch } from "vue";
import type { RemindeeProfile } from "@/types/remindee";
import type { UserProfile } from "@/types/user";
import { fetchRemindeeProfile, fetchUserProfile } from "@/services/profile";
import { useAuthStore } from "@/stores/authStore"; // assumes you have an auth store

const LIMIT = 3;

export const useUserProfileStore = defineStore("userProfileStore", () => {
  const authStore = useAuthStore();
  const token = computed(() => authStore.token);

  const userProfile = ref<UserProfile | null>(null);
  const remindeeList = ref<RemindeeProfile[]>([]);
  const loading = ref(false);
  const skip = ref(0);
  const hasMore = ref(true);

  const isNewUser = computed(() => remindeeList.value.length === 0);
  const isUserProfileComplete = computed(() => {
    return !userProfile.value?.user_summary || !userProfile.value?.avatar_url;
  });

  const updateUserProfile = async () => {
    if (!token.value) return;
    try {
      const profile = await fetchUserProfile(token.value);
      userProfile.value = profile;
    } catch {
      userProfile.value = null;
    }
  };

  const loadMoreRemindees = async () => {
    if (!token.value || !hasMore.value) return;
    loading.value = true;

    try {
      const response = await fetchRemindeeProfile(token.value, skip.value, LIMIT);
      if (response.RemindeeList.length > 0) {
        if (skip.value === 0) {
          remindeeList.value = response.RemindeeList;
        } else {
          remindeeList.value.push(...response.RemindeeList);
        }
        hasMore.value = response.has_more;
        skip.value += LIMIT;
      } else {
        hasMore.value = false;
      }
    } finally {
      loading.value = false;
    }
  };

  // Watch for token change
  watch(
    token,
    async (newToken) => {
      if (!newToken) {
        loading.value = false;
        remindeeList.value = [];
        skip.value = 0;
        hasMore.value = true;
        return;
      }

      await updateUserProfile();
      await loadMoreRemindees();
    },
    { immediate: true }
  );

  return {
    userProfile,
    updateUserProfile,
    isNewUser,
    isUserProfileComplete,
    loading,
    remindeeList,
    loadMoreRemindees,
    hasMore,
  };
});
