// src/router/index.ts
import { createRouter, createWebHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";

import Home from "@/pages/Home.vue";
import Identify from "@/pages/Identify.vue";
import Upload from "@/pages/Upload.vue";
import TrainModel from "@/pages/Train.vue";
import SignUpComponent from "@/components/Signup.vue";
import VerifyEmail from "@/components/VerifyEmail.vue";
import PasswordResetComponent from "@/components/PasswordReset.vue";
import Login from "@/components/Login.vue";
import MyProfile from "@/components/MyProfile.vue";
import RemindeeDetails from "@/pages/RemindeeDetails.vue";
import Instruction from "@/pages/Instruction.vue";
import RootLayout from "@/layouts/RootLayout.vue";

// const routes: Array<RouteRecordRaw> = [
//   {
//     path: "/",
//     component: RootLayout,
//     children: [
//       { path: "", name: "Home", component: Home }, // index route
//       { path: "identify", name: "Identify", component: Identify },
//       { path: "upload", name: "Upload", component: Upload },
//       { path: "train", name: "TrainModel", component: TrainModel },
//       { path: "register", name: "SignUp", component: SignUpComponent },
//       { path: "verify-email", name: "VerifyEmail", component: VerifyEmail },
//       { path: "reset-password", name: "PasswordReset", component: PasswordResetComponent },
//       { path: "login", name: "Login", component: Login },
//       { path: "profile", name: "MyProfile", component: MyProfile },
//       { path: "remindee-details", name: "RemindeeDetails", component: RemindeeDetails },
//       { path: "instruction", name: "Instruction", component: Instruction },
//     ],
//   },
// ];
const routes = [
  { path: "/", name: "", component: Home }, // index route
  { path: "/identify", name: "Identify", component: Identify },
  { path: "/upload", name: "Upload", component: Upload },
  { path: "/train", name: "TrainModel", component: TrainModel },
  { path: "/register", name: "SignUp", component: SignUpComponent },
  { path: "/verify-email", name: "VerifyEmail", component: VerifyEmail },
  { path: "/reset-password", name: "PasswordReset", component: PasswordResetComponent },
  { path: "/login", name: "Login", component: Login },
  { path: "/profile", name: "MyProfile", component: MyProfile },
  { path: "/remindee-details", name: "RemindeeDetails", component: RemindeeDetails },
  { path: "/instruction", name: "Instruction", component: Instruction },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
