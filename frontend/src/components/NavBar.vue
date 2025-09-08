<template>
  <nav class="bg-gray-700 shadow-lg fixed w-full top-5 left-0 z-50 py-1 rounded-b-lg">
    <div class="mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <div class="flex-shrink-0 flex items-center space-x-2">
          <img src="/remind-svgrepo-com.svg" alt="remindMe" class="h-10 w-15 rounded-full object-cover" />
          <RouterLink to="/" class="!text-white font-bold text-3xl">RemindMe</RouterLink>
        </div>

        <!-- Desktop Nav -->
        <div class="hidden md:flex items-center space-x-4">
          <RouterLink
            v-for="link in navLinks"
            :key="link.to"
            :to="link.to"
            :class="{
              'bg-gray-900 text-yellow-300 px-3 py-2 rounded-md text-lg font-medium': $route.path === link.to,
              'text-white hover:text-yellow-300 px-3 py-2 rounded-md text-lg font-medium': $route.path !== link.to,
            }"
          >
            {{ link.label }}
          </RouterLink>
        </div>

        <!-- User Profile -->
        <div class="hidden md:block">
          <div v-if="authStore.user" class="relative" ref="dropdownRef">
            <div @click="toggleDropdown" class="flex items-center text-yellow-300 hover:text-white cursor-pointer">
              <img
                :src="userProfileStore.userProfile?.avatar_url || '/profile.png'"
                class="h-14 w-14 rounded-full object-cover border-2 border-gray-600"
              />
              <ChevronDown class="ml-1 w-4 h-4" />
            </div>
            <div v-if="dropdownOpen" class="absolute right-0 mt-2 w-48 bg-gray-700 rounded-md shadow-lg py-3 z-10">
              <RouterLink
                v-for="item in dropdownItems"
                :key="item.label"
                :to="item.to"
                @click="closeDropdown"
                class="nav-link"
                active-class="bg-gray-900 text-white hover:text-orange-300"
              >
                {{ item.label }}
              </RouterLink>
              <button
                @click="handleLogout"
                class="text-gray-300 bg-gray-700 hover:bg-gray-900 hover:text-yellow-400 justify-center items-center border-none"
              >
                Logout
              </button>
            </div>
          </div>
          <RouterLink v-else to="/" class="text-gray-300 hover:text-white px-3 py-2 rounded-md text-lg font-medium">
            Login
          </RouterLink>
        </div>

        <!-- Mobile toggle -->
        <div class="md:hidden flex items-center">
          <button @click="toggleMenu" class="text-gray-300 hover:text-white focus:outline-none bg-gray-800">
            <component :is="isOpen ? X : Menu" class="w-6 h-6" />
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile Menu -->
    <div v-if="isOpen" class="md:hidden px-4 pt-2 pb-4 space-y-1">
      <RouterLink
        v-for="link in mobileLinks"
        :key="link.to"
        :to="link.to"
        class="mobile-link"
        @click="closeMenu"
        active-class="bg-gray-900 text-white hover:text-organge-300"
      >
        {{ link.label }}
      </RouterLink>

      <RouterLink v-if="authStore.user" to="/profile" class="text-gray-300 block text-center">
        <div class="flex items-center justify-center">
          <img :src="userProfileStore.userProfile?.avatar_url || '/profile.png'" class="h-8 w-8 rounded-full mr-2" />
          My Profile
        </div>
      </RouterLink>

      <button
        v-if="authStore.user"
        @click="logoutAndClose"
        class="bg-gray-700 text-gray-300 hover:text-white justify-center items-center border-none"
      >
        Logout
      </button>

      <RouterLink v-else to="/" @click="closeMenu" class="mobile-link"> Login </RouterLink>
    </div>

    <JobStatusBanner />
  </nav>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from "vue";
import { useAuthStore } from "@/stores/authStore";
import { useUserProfileStore } from "@/stores/UserProfileStore";

import JobStatusBanner from "@/components/JobStatusBanner.vue";
import { Menu, X, ChevronDown } from "lucide-vue-next";
import { useRouter } from "vue-router";

const router = useRouter();
const authStore = useAuthStore();
const userProfileStore = useUserProfileStore();

const isOpen = ref(false);
const dropdownOpen = ref(false);
const dropdownRef = ref<HTMLElement | null>(null);

const navLinks = [
  { to: "/", label: "Home" },
  { to: "/identify", label: "Identify" },
  { to: "/train", label: "Train AI Assistant" },
  { to: "/upload", label: "Upload" },
  { to: "/instruction", label: "Instruction" },
];

const dropdownItems = [
  { to: "/profile", label: "My Profile" },
  { to: "/instruction", label: "Instruction" },
];

const mobileLinks = [...navLinks, { to: "/about", label: "About" }];

function toggleMenu() {
  isOpen.value = !isOpen.value;
}
function closeMenu() {
  isOpen.value = false;
}
function toggleDropdown() {
  dropdownOpen.value = !dropdownOpen.value;
}
function closeDropdown() {
  dropdownOpen.value = false;
}
function handleLogout() {
  authStore.logout();
  dropdownOpen.value = false;
}
function logoutAndClose() {
  closeMenu();
  authStore.logout();
}

function handleClickOutside(event: MouseEvent) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    dropdownOpen.value = false;
  }
}

onMounted(() => {
  document.addEventListener("mousedown", handleClickOutside);
});
onBeforeUnmount(() => {
  document.removeEventListener("mousedown", handleClickOutside);
});
</script>

<style lang="postcss">
.nav-link {
  @apply text-gray-300 bg-gray-700 hover:bg-gray-900 hover:text-yellow-400 block px-3 py-2 rounded-md text-base font-medium;
}
.mobile-link {
  @apply text-gray-300 hover:bg-gray-700 hover:text-white block px-3 py-2 rounded-md text-base font-medium;
}
</style>
