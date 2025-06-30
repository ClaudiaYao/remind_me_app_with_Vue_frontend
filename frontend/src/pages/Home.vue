<template>
  <div class="home-container mx-auto px-4 py-8 max-w-4xl">
    <Login v-if="!authStore.user" />
    <Instruction v-else-if="userProfileStore.isNewUser" />
    <template v-else>
      <div class="flex justify-center items-center mb-6">
        <h1 class="text-sm sm:text-base md:text-lg lg:text-xl xl:text-4xl font-bold text-gray-800 mb-6">
          <RouterLink to="/profile" class="!text-gray-800">
            Welcome, {{ userProfileStore.userProfile?.user_summary?.nick_name || "User" }}!
          </RouterLink>
        </h1>
      </div>

      <h2 class="text-xl font-semibold text-gray-500 mb-4">👭🏼👫🏼 People You Know 🧑🏽‍🤝‍🧑🏽👬🏽</h2>

      <div class="space-y-6">
        <RemindeeCard
          v-for="(person, index) in userProfileStore.remindeeList"
          :key="index"
          :person="person"
          :index="index"
        />
      </div>

      <div v-if="userProfileStore.hasMore" style="margin-top: 1rem">
        <span
          @click="handleLoadMore"
          :style="{
            color: 'blue',
            textDecoration: 'underline',
            cursor: 'pointer',
            opacity: userProfileStore.loading ? 0.5 : 1,
            pointerEvents: userProfileStore.loading ? 'none' : 'auto',
          }"
        >
          {{ userProfileStore.loading ? "Loading..." : "Load More..." }}
        </span>
      </div>

      <div v-else class="space-y-1.5">
        <p class="text-3xl font-medium text-gray-500"></p>
        <p class="mt-10 text-center text-sm/6 text-black">
          No more remindees.
          <RouterLink to="/upload" class="font-medium !text-yellow-600 dark:text-yellow-500 hover:underline">
            Add more?
          </RouterLink>
        </p>
      </div>

      <div
        v-if="!userProfileStore.remindeeList || userProfileStore.remindeeList.length === 0"
        class="text-center py-12 bg-gray-50 rounded-lg"
      >
        <p class="text-gray-500">No people added yet. Add someone to get started!</p>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from "@/stores/authStore";
import { useUserProfileStore } from "@/stores/UserProfileStore";
import Login from "@/components/Login.vue";
import Instruction from "@/pages/Instruction.vue";
import RemindeeCard from "@/components/RemindeeCard.vue";
import { RouterLink } from "vue-router";

const authStore = useAuthStore();
const userProfileStore = useUserProfileStore();

const handleLoadMore = async () => {
  if (!authStore.token) return;
  await userProfileStore.loadMoreRemindees();
};
</script>
