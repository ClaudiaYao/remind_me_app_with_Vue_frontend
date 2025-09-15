<template>
  <div class="w-full justify-center mx-auto bg-white shadow rounded-xl space-y-6 px-4">
    <!-- Image Upload -->
    <div
      @click="handleClick"
      class="cursor-pointer border-2 border-dashed border-gray-400 p-4 rounded text-center hover:bg-gray-100"
    >
      📁 Click to choose images ...
      <p class="text-sm text-gray-500">(Only one image file is allowed)</p>
    </div>
    <input type="file" ref="inputRef" @change="handleImageUpload" accept="image/*" class="hidden" />

    <!-- Preview -->
    <div
      v-if="chosenImage"
      class="relative w-full h-[32rem] flex flex-col items-center justify-between rounded-md overflow-hidden space-y-2"
    >
      <div class="relative h-[28rem] w-full flex items-center justify-center">
        <img :src="imageURL" class="w-full h-full object-contain" />
        <button
          @click="handleDeleteImage"
          class="absolute top-0 right-0 bg-red-600 text-white rounded-full w-8 h-8 flex items-center justify-center shadow-md hover:bg-red-700"
          title="Delete Image"
        >
          x
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { Camera, CameraResultType, CameraSource } from "@capacitor/camera";

const props = defineProps({
  chosenImage: File,
});
const emit = defineEmits(["update:chosenImage"]);

const inputRef = ref(null);

const handleClick = async () => {
  inputRef.value?.click();
  try {
    const photo = await Camera.getPhoto({
      quality: 90,
      allowEditing: false,
      resultType: CameraResultType.Uri, // get webPath for <img>
      source: CameraSource.Prompt, // user can choose Camera or Gallery
    });

    if (photo.webPath) {
      imageURL.value = photo.webPath;

      // Convert it to File (so backend can receive it)
      const response = await fetch(photo.webPath);
      const blob = await response.blob();
      const file = new File([blob], "photo.jpg", { type: blob.type });

      emit("update:chosenImage", file);
    }
  } catch (err) {
    console.error("Camera error:", err);
  }
};

const handleImageUpload = (e) => {
  const file = e.target.files?.[0];
  if (file) {
    emit("update:chosenImage", file);
  }
};

const handleDeleteImage = () => {
  emit("update:chosenImage", null);
};

const imageURL = computed(() => {
  return props.chosenImage ? URL.createObjectURL(props.chosenImage) : "";
});

// Cleanup object URL when image changes
watch(
  () => props.chosenImage,
  (newFile, oldFile) => {
    if (oldFile) URL.revokeObjectURL(URL.createObjectURL(oldFile));
  }
);
</script>
