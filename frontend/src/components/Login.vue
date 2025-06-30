<template>
  <div class="login-container flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8">
    <div class="login-box sm:mx-auto sm:w-full sm:max-w-sm">
      <h2 class="mt-10 text-center text-2xl/9 font-bold tracking-tight text-gray-900">🚀 Sign In</h2>
    </div>

    <div class="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
      <form class="space-y-6" @submit.prevent="handleSubmit">
        <div>
          <label for="email" class="block text-sm/6 font-medium text-gray-900">Email address</label>
          <div class="mt-2">
            <input
              id="email"
              name="email"
              type="email"
              v-model="email"
              required
              autocomplete="email"
              class="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-yellow-500 sm:text-sm/6"
            />
          </div>
        </div>

        <div>
          <label for="password" class="block text-sm/6 font-medium text-gray-900">Password</label>
          <div class="mt-2">
            <input
              id="password"
              name="password"
              type="password"
              v-model="password"
              required
              autocomplete="current-password"
              class="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-yellow-500 sm:text-sm/6"
            />
          </div>
        </div>

        <div class="text-sm">
          <RouterLink to="/reset-password" class="font-medium !text-yellow-800 hover:text-yellow-500">
            Forgot password?
          </RouterLink>
        </div>

        <p>{{ msg }}</p>

        <div>
          <button
            type="submit"
            class="flex w-full justify-center rounded-md bg-orange-500 px-3 py-2 text-sm/6 font-semibold text-white shadow-xs hover:bg-orange-600 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-yellow-600"
          >
            Sign in
          </button>
        </div>
      </form>

      <p class="mt-10 text-center text-sm/6 text-black">
        Not a member?
        <RouterLink to="/register" class="font-medium !text-orange-600 dark:text-yellow-500 hover:underline">
          Sign up
        </RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/authStore";
import { CognitoAuthError, CognitoErrorCode } from "@/services/appExceptions";

const email = ref("");
const password = ref("");
const msg = ref("");

const authStore = useAuthStore();
const router = useRouter();

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

const handleSubmit = async () => {
  msg.value = "";

  if (!email.value || !password.value) {
    msg.value = "Both fields are required.";
    return;
  }

  try {
    console.log("email:", email.value);
    await authStore.login({ email: email.value, password: password.value });
    await sleep(1000);
    router.push("/");
  } catch (error: unknown) {
    if (error instanceof CognitoAuthError) {
      switch (error.code) {
        case CognitoErrorCode.UserNotConfirmed:
        case CognitoErrorCode.EmailNotVerified:
          await sleep(1000);
          router.push({ path: "/verify-email", state: { email: email.value } });
          break;
        case CognitoErrorCode.UserNotFound:
          await sleep(1000);
          msg.value = "Could not find the user. Do you want to register a new account?";
          router.push("/register");
          break;
        case CognitoErrorCode.NotAuthorized:
          msg.value = "Incorrect username or password";
          break;
        default:
          msg.value = "Fail to connect to server. Please try again.";
      }
    } else {
      msg.value = "Unexpected error occurs during login";
    }
  }
};
</script>
