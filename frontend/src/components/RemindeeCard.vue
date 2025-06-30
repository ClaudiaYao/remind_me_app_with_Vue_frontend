<template>
  <div class="bg-white rounded-lg shadow-md p-6 border border-gray-200 hover:shadow-lg transition-shadow duration-300">
    <div class="flex flex-col md:flex-row items-center">
      <div class="flex-shrink-0 mb-4 md:mb-0 md:mr-6">
        <img
          :src="person.image_object_key"
          :alt="person.person_name"
          class="w-24 h-24 rounded-full object-cover border-2 border-gray-200"
        />
      </div>

      <div class="flex-grow text-center md:text-left">
        <h3 class="text-xl font-medium text-gray-800 mb-2">{{ person.person_name }}</h3>
        <p class="text-gray-600 leading-relaxed">{{ person.ai_summary }}</p>
        <div class="space-y-2 text-left">
          <div>
            <span class="font-medium text-gray-700">Relationship:</span>
            <span class="text-gray-600"> {{ person.relationship }} </span>
          </div>
        </div>

        <button
          @click="handleMoreInfoClick"
          class="mt-2 bg-orange-500 text-white px-3 py-2 text-sm/6 font-semibold rounded-md hover:bg-orange-600 transition-colors duration-200 inline-flex items-center"
        >
          <span>Show More</span>
          <svg
            class="ml-2 w-4 h-4 transition-transform duration-200"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import type { RemindeeProfile } from "@/types/remindee";

interface Props {
  person: RemindeeProfile;
  index?: number; // optional if you want
}

const props = defineProps<Props>();
const router = useRouter();

function handleMoreInfoClick() {
  router.push({ path: "/remindee-details", query: { person_name: props.person.person_name } });
}
</script>
