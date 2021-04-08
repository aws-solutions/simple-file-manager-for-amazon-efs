import Vue from 'vue'
import App from './App.vue'
import {BootstrapVue, BootstrapVueIcons} from 'bootstrap-vue'

import Amplify, * as AmplifyModules from 'aws-amplify'
import { AmplifyPlugin } from 'aws-amplify-vue'

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

import router from './router.js'


const getRuntimeConfig = async () => {
  const runtimeConfig = await fetch('/runtimeConfig.json');
  return await runtimeConfig.json()
};

getRuntimeConfig().then(function(json) {
  const awsconfig = {
    Auth: {
      region: json.awsRegion,
      userPoolId: json.userPoolId,
      userPoolWebClientId: json.userPoolIdClientId,
      identityPoolId: json.identityPoolId
    },
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
  
  Vue.mixin({
    data() {
      return {
        // Distribute runtime configs into every Vue component
        fileManagerApi: json.fileManagerApiUrl,
        awsRegion: json.awsRegion
      }
    },
  });

  Vue.use(AmplifyPlugin, AmplifyModules)

  Vue.use(BootstrapVue)
  Vue.use(BootstrapVueIcons)
  
  new Vue({
    router,
    render: h => h(App),
    }).$mount('#app')
});
