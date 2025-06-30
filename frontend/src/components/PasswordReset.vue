<template>
  <div class="login-container flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8">
    <div class="login-box sm:mx-auto sm:w-full sm:max-w-sm">
      <h2 class="mt-10 text-center text-2xl/9 font-bold tracking-tight text-gray-900">🚀 Reset Password</h2>
      <br />

      <form @submit.prevent="requestPasswordReset">
        <div class="form-group">
          <template v-if="step === 1">
            <label for="email" class="block text-sm/6 font-medium text-gray-900"> Email address: </label>
            <div class="mt-2">
              <input
                id="email"
                name="email"
                type="email"
                required
                autocomplete="email"
                v-model="email"
                class="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-yellow-500 sm:text-sm/6"
              />
            </div>
            <p class="login-error">{{ msg }}</p>
            <div class="buttons-default">
              <button
                type="submit"
                class="app_button flex w-full justify-center rounded-md bg-yellow-600 px-3 py-1.5 text-sm/6 font-semibold text-white shadow-xs hover:bg-yellow-400 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-yellow-600"
              >
                Send Reset Email
              </button>
            </div>
          </template>

          <template v-else>
            <input
              type="text"
              placeholder="Enter verification code"
              v-model="code"
              class="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-yellow-500 sm:text-sm/6 mb-2"
            />
            <input
              type="password"
              placeholder="Enter new password"
              v-model="newPassword"
              class="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-yellow-500 sm:text-sm/6"
            />
            <br />
            <p class="login-error">{{ msg }}</p>
            <div class="buttons-default">
              <button
                type="submit"
                class="flex w-full justify-center rounded-md bg-yellow-600 px-3 py-1.5 text-sm/6 font-semibold text-white shadow-xs hover:bg-yellow-400 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-yellow-600"
              >
                Reset Password
              </button>
            </div>
          </template>
        </div>
      </form>

      <div class="mt-10 text-center text-sm/6 text-black">
        <RouterLink to="/" class="font-medium !text-yellow-800 dark:text-yellow-500 hover:underline">
          Back to login
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { CognitoUser } from "amazon-cognito-identity-js";
import { userPool } from "@/services/userpool";

const router = useRouter();

const step = ref(1);
const email = ref("");
const code = ref("");
const newPassword = ref("");
const msg = ref("");

const requestPasswordReset = async () => {
  msg.value = "";

  if (!email.value) {
    msg.value = "Email is required.";
    return;
  }

  const user = new CognitoUser({ Username: email.value, Pool: userPool });

  if (step.value === 1) {
    user.forgotPassword({
      onSuccess: () => {
        msg.value = "Verification code sent to email.";
        step.value = 2;
      },
      onFailure: () => {
        msg.value = "Enter a valid email address.";
      },
    });
  } else if (step.value === 2) {
    if (!code.value || !newPassword.value) {
      msg.value = "Code and new password are required.";
      return;
    }

    user.confirmPassword(code.value, newPassword.value, {
      onSuccess: () => {
        msg.value = "Password reset successful. You can now log in.";
        setTimeout(() => {
          router.push("/login");
        }, 4000);
      },
      onFailure: () => {
        msg.value = "Invalid code or password.";
      },
    });
  }
};
</script>

<style scoped>
.login-error {
  color: red;
  margin-top: 0.5rem;
}
</style>
