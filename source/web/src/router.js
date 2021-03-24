import Home from '@/routes/Home.vue'
import Configure from '@/routes/Configure.vue'
//import Upload from '@/routes/Upload.vue'
import Filesystem from '@/routes/Filesystem.vue'
//import Login from '@/routes/Login.vue'

//  mode: 'history',
//base: process.env.BASE_URL,
const routes = [
    {
      path: '/',
      name: 'home',
      component: Home,
      meta: { requiresAuth: false }
    },
    {
      path: '/configure/:id',
      name: 'configure',
      component: Configure,
      meta: { requiresAuth: false }
    },
    {
      path: '/filesystem/:id',
      name: 'filesystem',
      component: Filesystem,
      meta: { requiresAuth: false }
    }
    // {
    //   path: "/",
    //   name: "Login",
    //   component: Login,
    //   meta: { requiresAuth: false },
    // }
]


// router.beforeResolve(async (to, from, next) => {
//   if (to.matched.some(record => record.meta.requiresAuth)) {
//     try {
//       //await Vue.prototype.$Amplify.Auth.currentAuthenticatedUser();
//       next();
//     } catch (e) {
//       console.log(e);
//       next({
//         path: "/",
//         query: {
//           redirect: to.fullPath
//         }
//       });
//     }
//   }
//   else {
//     next();
//   }
// });

export default routes;