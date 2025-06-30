<template>
  <div class="login-container flex min-h-full flex-1 flex-col justify-center px-6 py-6 lg:px-8">
    <div class="login-box sm:mx-auto sm:w-full sm:max-w-sm">
      <form @submit.prevent="handleSubmit">
        <h2 class="mt-10 text-center text-2xl/9 font-bold tracking-tight text-gray-900">🚀 Sign Up</h2>

        <div class="form-group">
          <label for="email" class="block text-sm/6 font-medium text-gray-900">Email</label>
          <input
            id="email"
            type="email"
            class="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-yellow-500 sm:text-sm/6"
            v-model="email"
            placeholder="Enter email"
          />
        </div>
        <br />
        <div class="form-group">
          <label for="password" class="block text-sm/6 font-medium text-gray-900">Password</label>
          <input
            id="password"
            type="password"
            class="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-yellow-500 sm:text-sm/6"
            v-model="password"
            placeholder="Enter password"
          />
        </div>

        <p class="text-red-600 my-2">{{ msg }}</p>

        <div>
          <p class="mt-10 text-center text-sm/6 text-black">
            Already a member?
            <RouterLink to="/login" class="text-orange-500 dark:text-yellow-500 hover:underline"> Sign in! </RouterLink>
          </p>
        </div>
        <br />
        <div class="justify-center">
          <button
            type="submit"
            class="flex w-full justify-center rounded-md bg-orange-400 px-3 py-2 text-sm/6 font-semibold text-white shadow-xs hover:bg-orange-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-yellow-600"
          >
            Sign Up
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { userPool } from "../services/userpool";

const email = ref("");
const password = ref("");
const msg = ref("");
const router = useRouter();

const handleSignUp = () => {
  msg.value = "";
  return new Promise((resolve, reject) => {
    userPool.signUp(email.value, password.value, [], [], (err, data) => {
      if (err) {
        reject(err);
        console.error(err);
        msg.value = err.message || "Sign up failed.";
        return;
      }
      resolve(data);
      msg.value = "Sign-up successful. Please check your email for the verification code.";
      setTimeout(() => {
        router.push({ path: "/verify-email", state: { email: email.value } });
      }, 3000);
    });
  });
};

const handleSubmit = async () => {
  if (!email.value || !password.value) {
    msg.value = "Both fields are required.";
    return;
  }
  try {
    await handleSignUp();
  } catch (err) {
    if (err instanceof Error) {
      msg.value = err.message;
    }
  }
};
</script>
