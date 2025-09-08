<!-- src/layouts/RootLayout.vue -->
<template>
  <div class="root safe-area">
    <!-- Use the global Pinia stores instead of nested providers -->
    <Navbar />

    <div class="mx-auto px-4 pt-16">
      <router-view />
    </div>

    <SessionTimeoutDialog v-if="showWarningDialog" :show="showWarningDialog" @stay-logged-in="stayLoggedIn" />
  </div>
</template>

<script setup lang="ts">
import Navbar from "@/components/NavBar.vue";
import SessionTimeoutDialog from "@/components/SessionTimeoutDialog.vue";
import { useSessionTimeout } from "@/composables/useSessionTimeout";

const { showWarningDialog, stayLoggedIn } = useSessionTimeout();
</script>
