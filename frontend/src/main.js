import { createApp } from "vue";
import { createPinia } from "pinia";
import router from "./router";
import App from "./App.vue";
import "./assets/style.css";

const app = createApp(App);

app.use(createPinia());
app.use(router);

document.documentElement.dir = "rtl";
document.documentElement.lang = "ar";

app.mount("#app");
