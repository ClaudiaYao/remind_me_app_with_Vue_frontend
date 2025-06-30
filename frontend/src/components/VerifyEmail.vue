<template>
  <div class="login-container flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8">
    <div class="login-box sm:mx-auto sm:w-full sm:max-w-sm">
      <h2 class="mt-10 text-center text-2xl/9 font-bold tracking-tight text-gray-900">Verify Email</h2>
      <form @submit.prevent="handleSubmit">
        <h3>Email Verification</h3>

        <div class="form-group">
          <label for="email" class="block text-sm/6 font-medium text-gray-900">Email</label>
          <input
            type="email"
            :value="email"
            readonly
            placeholder="Email"
            class="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-yellow-500 sm:text-sm/6"
          />
        </div>

        <div class="mb-3">
          <label for="verificationCode" class="block text-sm/6 font-medium text-gray-900">Verification Code</label>
          <input
            type="text"
            v-model="verificationCode"
            placeholder="Verification Code"
            class="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-yellow-500 sm:text-sm/6"
          />
        </div>

        <p class="login-error" v-if="error">{{ error }}</p>

        <div class="buttons-default">
          <button
            type="submit"
            class="flex w-full justify-center rounded-md bg-yellow-600 px-3 py-1.5 text-sm/6 font-semibold text-white shadow-xs hover:bg-yellow-400 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-yellow-600"
          >
            Verify Email
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { CognitoUser } from "amazon-cognito-identity-js";
import { userPool } from "../services/userpool";

const router = useRouter();
const route = useRoute();

const verificationCode = ref("");
const error = ref("");

// Extract email from route state (Vue Router 4 doesn't support passing state like React Router,
// so you usually pass via query or params, or use a global store or localStorage)
// Here, assuming email passed as a query parameter:
const email = (route.query.email as string) || "";

// For debugging
console.log("get email from route.query:", email);

const handleSubmit = async () => {
  error.value = "";

  if (!verificationCode.value) {
    error.value = "Verification code is required.";
    return;
  }

  const cognitoUser = new CognitoUser({
    Username: email,
    Pool: userPool,
  });

  try {
    await new Promise((resolve, reject) => {
      cognitoUser.confirmRegistration(verificationCode.value, true, (err, data) => {
        if (err) {
          reject(err);
          return;
        }
        resolve(data);
      });
    });

    error.value = "Email verified successfully! You can now log in.";

    setTimeout(() => {
      router.push("/login");
    }, 4000);
  } catch (err) {
    error.value = "Error verifying email.";
  }
};
</script>
