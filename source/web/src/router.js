import Vue from 'vue'
import VueRouter from 'vue-router'

import Home from '@/routes/Home.vue'
import Configure from '@/routes/Configure.vue'
import Filesystem from '@/routes/Filesystem.vue'
import Login from '@/routes/Login.vue'
import Details from '@/routes/Details.vue'

Vue.use(VueRouter);

const router = new VueRouter({
  base: process.env.BASE_URL,
  mode: 'history',
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login,
      meta: { requiresAuth: false }
    },
    {
      path: '/configure/:id',
      name: 'configure',
      component: Configure,
      meta: { requiresAuth: true }
    },
    {
      path: '/filesystem/:id',
      name: 'filesystem',
      component: Filesystem,
      meta: { requiresAuth: true }
    },
    {
      path: '/',
      name: 'home',
      component: Home,
      meta: { requiresAuth: true }
    },
    {
      path: '/details/:id',
      name: 'details',
      component: Details,
      meta: { requiresAuth: true }
    }
]
})


router.beforeResolve(async (to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    try {
      await Vue.prototype.$Amplify.Auth.currentAuthenticatedUser();
      next();
    } catch (e) {
      console.log(e);
      next({
        path: "/login",
        query: {
          redirect: to.fullPath
        }
      });
    }
  }
  else {
    next();
  }
});

export default router;