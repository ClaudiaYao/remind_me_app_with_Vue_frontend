<!-- <template>
  <div>
    <p>You have not trained your AI assistant.</p>
    <button @click="handleTraining" :disabled="isTraining">
      {{ isTraining ? "Training..." : "Train Your AI Assistant Now" }}
    </button>
    <p class="text-gray-500">{{ msg }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { useAuthStore } from "@/stores/authStore";
import { useJobStore } from "@/stores/jobStore";
import { trigger_train } from "@/services/upload_train";

const authStore = useAuthStore();
const isTraining = ref(false);
const msg = ref("");

const jobStore = useJobStore();

const handleTraining = async () => {
  try {
    jobStore.resetJobStatus();
    msg.value = "";
    const jobId = await trigger_train(authStore.token);
    console.log(jobId);
    isTraining.value = true;
    jobStore.jobId = jobId;
  } catch (error) {
    console.error(error);
    isTraining.value = false;
    msg.value = "An error has occurred. Please try again later.";
  }
};

watch(
  () => jobStore.jobStatus,
  (newStatus) => {
    if (newStatus === "Completed") {
      isTraining.value = false;
      msg.value = "Your AI assistant has finished training. You could use it to identify the persons.";
    } else if (newStatus === "Error") {
      isTraining.value = false;
      msg.value = "Training encounters some error. Please try again.";
    }
  }
);
</script> -->
