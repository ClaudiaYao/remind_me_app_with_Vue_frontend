// main.ts

import "./assets/styles/Authentication.css";
// import "./assets/styles/Navbar.css";
import "./assets/styles/Index.css";
import "./assets/styles/App.css";

import { createPinia } from "pinia";
import { createApp } from "vue";
import App from "./App.vue";
import router from "@/router/index";

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.mount("#app");
