import { createApp } from "vue";
import { createPinia } from "pinia";
import router from "./router";
import App from "./App.vue";
import "./assets/style.css";
import "./assets/icons.css";

const app = createApp(App);

app.config.errorHandler = (err, instance, info) => {
  console.warn("Vue Error Handler:", err?.toString?.()?.slice(0, 200), info);
};

app.use(createPinia());
app.use(router);

document.documentElement.dir = "rtl";
document.documentElement.lang = "ar";

app.mount("#app");
