<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
    <div class="bg-white p-6 rounded shadow max-w-sm w-full">
      <h2 class="text-lg font-semibold mb-2">Session Timeout Warning</h2>
      <p class="mb-4">You’ve been inactive for a while. You will be logged out in 1 minute.</p>
      <div class="flex justify-end space-x-2">
        <button @click="onStayLoggedIn" class="bg-orange-500 text-white px-4 py-2 rounded hover:bg-orange-600">
          Stay Logged In
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  show: boolean;
  onStayLoggedIn: () => void;
}>();
</script>
