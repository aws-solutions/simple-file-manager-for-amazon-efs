import Vue from 'vue'
import App from './App.vue'
import {BootstrapVue, BootstrapVueIcons} from 'bootstrap-vue'
import VueRouter from 'vue-router';

import Amplify from 'aws-amplify'
//import { AmplifyPlugin } from "aws-amplify-vue";

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

import routes from './router.js'


const getRuntimeConfig = async () => {
  const runtimeConfig = await fetch('/runtimeConfig.json');
  return await runtimeConfig.json()
};

getRuntimeConfig().then(function(json) {
  const awsconfig = {
    // Auth: {
    //   region: json.AWS_REGION,
    //   userPoolId: json.USER_POOL_ID,
    //   userPoolWebClientId: json.USER_POOL_CLIENT_ID,
    //   identityPoolId: json.IDENTITY_POOL_ID
    // },
    API: {
      endpoints: [
        {
          name: "fileManagerApi",
          endpoint: json.fileManagerApiUrl,
          region: json.awsRegion
        }
      ]
    }
  };
  Vue.config.productionTip = false
  Amplify.configure(awsconfig);
  
  // Vue.mixin({
  //   data() {
  //     return {
  //       // Distribute runtime configs into every Vue component
  //       fileManagerApi: json.fileManagerApiUrl,
  //       awsRegion: json.awsRegion
  //     }
  //   },
  // });
  Vue.use(BootstrapVue)
  Vue.use(BootstrapVueIcons)
  Vue.use(VueRouter);

  const router = new VueRouter({routes, mode: 'history'});
  
  new Vue({
    router,
    render: h => h(App),
    }).$mount('#app')
});
