<!-- <script setup lang="ts">
import { ref, watch, computed, reactive } from "vue";
import type { UploadPayload } from "@/services/upload_train";

interface Props {
  uploadPayload: UploadPayload;
  setUploadPayload: (payload: UploadPayload) => void;
}

const props = defineProps<Props>();
const emit = defineEmits(["update:uploadPayload"]);

const inputRef = ref<HTMLInputElement | null>(null);

const images = ref<File[]>([]);
const summaries = ref<string[]>([]);
const currentIndex = ref(0);

const uploadPayload = reactive({ ...props.uploadPayload });

watch(
  () => props.uploadPayload,
  (newPayload) => {
    Object.assign(uploadPayload, newPayload);
  },
  { deep: true }
);

watch(
  () => uploadPayload,
  (newPayload) => {
    props.setUploadPayload({ ...newPayload });
  },
  { deep: true }
);

const handleClick = () => {
  inputRef.value?.click();
};

const handleImageUpload = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files) {
    const files = Array.from(target.files);
    images.value = files;
    summaries.value = files.map(() => "");
    currentIndex.value = 0;
    uploadPayload.files = files;
    uploadPayload.summary = files.map(() => "");
    props.setUploadPayload({ ...uploadPayload });
  }
};

const handleDeleteImage = (index: number) => {
  images.value = images.value.filter((_, i) => i !== index);
  summaries.value = summaries.value.filter((_, i) => i !== index);

  if (currentIndex.value >= images.value.length) {
    currentIndex.value = Math.max(images.value.length - 1, 0);
  }

  uploadPayload.files = images.value;
  uploadPayload.summary = summaries.value;
  props.setUploadPayload({ ...uploadPayload });
};

const handleSummaryChange = (e: Event) => {
  const target = e.target as HTMLInputElement;
  summaries.value[currentIndex.value] = target.value;
  uploadPayload.summary = summaries.value;
  props.setUploadPayload({ ...uploadPayload });
};

const showPrev = () => {
  currentIndex.value = currentIndex.value === 0 ? images.value.length - 1 : currentIndex.value - 1;
};

const showNext = () => {
  currentIndex.value = currentIndex.value === images.value.length - 1 ? 0 : currentIndex.value + 1;
};

const imageURL = computed(() => {
  if (images.value.length === 0) return "";
  return URL.createObjectURL(images.value[currentIndex.value]);
});
</script> -->

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import type { UploadPayload } from "@/services/upload_train";

// Props + Emit
const props = defineProps<{ modelValue: UploadPayload }>();
const emit = defineEmits<{
  (e: "update:modelValue", value: UploadPayload): void;
}>();

// Internal refs
const inputRef = ref<HTMLInputElement | null>(null);
const currentIndex = ref(0);
const images = ref<File[]>([]);
const summaries = ref<string[]>([]);

// Sync with prop
watch(
  () => props.modelValue,
  (val) => {
    images.value = val.files || [];
    summaries.value = val.summary || [];
  },
  { immediate: true, deep: true }
);

// Emit updated modelValue
function updatePayload(payload: Partial<UploadPayload>) {
  emit("update:modelValue", {
    ...props.modelValue,
    ...payload,
  });
}

function handleClick() {
  inputRef.value?.click();
}

function handleImageUpload(e: Event) {
  console.log("Handling image upload");
  const target = e.target as HTMLInputElement;
  console.log("Target files:", target.files, target.files?.length);
  if (target.files) {
    const files = Array.from(target.files);

    images.value = files;
    summaries.value = files.map(() => "");
    currentIndex.value = 0;
    console.log("Images after upload:", images.value);
    updatePayload({ files: images.value, summary: summaries.value });
    console.log("Updated payload:", props.modelValue);
  }
}

function handleSummaryChange(e: Event) {
  const target = e.target as HTMLInputElement;
  summaries.value[currentIndex.value] = target.value;
  updatePayload({ summary: summaries.value });
}

function handleDeleteImage(index: number) {
  console.log("Deleting image at index:", index);
  images.value.splice(index, 1);
  summaries.value.splice(index, 1);
  if (currentIndex.value >= images.value.length) {
    currentIndex.value = Math.max(images.value.length - 1, 0);
  }
  updatePayload({ files: images.value, summary: summaries.value });
}

function showPrev() {
  currentIndex.value = (currentIndex.value - 1 + images.value.length) % images.value.length;
}
function showNext() {
  currentIndex.value = (currentIndex.value + 1) % images.value.length;
}

const imageURL = computed(() => (images.value.length > 0 ? URL.createObjectURL(images.value[currentIndex.value]) : ""));
</script>

<template>
  <div class="container w-full mx-auto bg-white shadow rounded-xl space-y-6 px-4">
    <!-- Inputs -->
    <div class="flex justify-center pt-10 space-x-6">
      <div class="w-1/2 max-w-sm">
        <label class="block text-sm font-medium text-gray-700 text-left">Remindee Name:</label>
        <input
          type="text"
          v-model="props.modelValue.person_name"
          class="mt-1 w-full border rounded-md px-3 py-2 text-left"
        />
      </div>
      <div class="w-1/2 max-w-sm">
        <label class="block text-sm font-medium text-gray-700 text-left">Relationship:</label>
        <input
          type="text"
          v-model="props.modelValue.relationship"
          class="mt-1 w-full border rounded-md px-3 py-2 text-left"
        />
      </div>
    </div>

    <!-- Upload -->
    <div
      class="cursor-pointer border-2 border-dashed border-gray-400 p-4 rounded text-center hover:bg-gray-100"
      @click="handleClick"
    >
      📁 Click to choose images ...
      <p class="text-sm text-gray-500">(Only image files, multiple allowed)</p>
      <input ref="inputRef" type="file" accept="image/*" multiple class="hidden" @change="handleImageUpload" />
    </div>

    <!-- Image Viewer -->
    <div v-if="images.length > 0" class="relative h-[28rem] flex flex-col items-center space-y-2">
      <div class="relative h-[24rem] w-full flex items-center justify-center">
        <img :src="imageURL" class="h-full object-scale-down" />

        <button
          @click="handleDeleteImage(currentIndex)"
          class="absolute top-0 right-0 bg-orange-500 text-white rounded-full w-8 h-8 text-center flex items-center justify-center"
        >
          x
        </button>
        <button @click="showPrev" class="absolute left-0 bg-orange-400 p-2 rounded-full">◀</button>
        <button @click="showNext" class="absolute right-0 bg-orange-400 p-2 rounded-full">▶</button>
      </div>

      <div class="w-full px-4">
        <label class="block text-sm font-medium text-gray-700">Summary for Image {{ currentIndex + 1 }}</label>
        <input
          type="text"
          :value="summaries[currentIndex]"
          @input="handleSummaryChange"
          class="mt-1 w-full border rounded-md px-3 py-2 text-left"
        />
      </div>
      <br />
    </div>
  </div>
</template>
