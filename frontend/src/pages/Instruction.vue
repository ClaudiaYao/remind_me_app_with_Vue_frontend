<template>
  <div class="intro-container flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8">
    <div class="flex justify-center items-center mb-6">
      <h1 class="text-sm sm:text-base md:text-sm lg:text-lg xl:text-3xl font-bold">Welcome to RemindMe</h1>
    </div>

    <div class="w-full flex flex-col items-center justify-between rounded-md overflow-hidden space-y-2">
      <!-- Image container -->
      <div class="relative w-full flex items-center justify-center bg-gray-100">
        <img :src="'/' + images[currentIndex]" :alt="`Step ${currentIndex}`" class="w-full h-full object-contain" />
      </div>

      <!-- Indicator BELOW the image -->
      <div class="flex gap-2 mt-4">
        <button
          v-for="(_, i) in images"
          :key="i"
          @click="currentIndex = i"
          class="!w-2 !h-2 !bg-gray-100 !rounded-full hover:bg-gray-300 focus:outline-none"
          :class="{
            '!bg-gray-400': i === currentIndex,
            '!bg-gray-200': i !== currentIndex,
          }"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

const currentIndex = ref(0);
const images = ["intro_1.jpg", "intro_2.jpg"];
</script>
