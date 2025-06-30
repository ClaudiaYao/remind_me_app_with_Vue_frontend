<template>
  <div v-if="open" class="fixed inset-0 z-0 flex items-center justify-center bg-black/75">
    <div class="bg-white rounded-lg shadow-lg p-6 w-96">
      <p class="mb-4">
        {{ message || "You have unsaved changes. Are you sure you want to leave?" }}
      </p>
      <div class="flex justify-end space-x-4">
        <button @click="onCancel" class="bg-gray-300 hover:bg-gray-400 text-black font-bold py-2 px-4 rounded">
          Stay
        </button>
        <button @click="onConfirm" class="bg-orange-400 hover:bg-orange-500 text-white font-bold py-2 px-4 rounded">
          Leave
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  open: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  message?: string;
}>();
</script>
