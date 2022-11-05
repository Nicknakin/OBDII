import { createRouter, createWebHistory } from "vue-router";
import DashBoard from "../views/DashBoard.vue";
import QueryPage from "../views/QueryPage.vue";
import HistoryPage from "../views/HistoryPage.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "DashBoard",
      component: DashBoard,
    },
    {
      path: "/query",
      name: "Query",
      component: QueryPage,
    },
    {
      path: "/history",
      name: "History",
      component: HistoryPage,
    },
  ],
});

export default router;
