// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import Vue from 'vue'
import { createApp } from 'vue'
import App from './App.vue'

import Amplify, * as AmplifyModules from 'aws-amplify'
import { AmplifyPlugin } from 'aws-amplify-vue'

import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import 'bootstrap-icons/font/bootstrap-icons.css';
import 'bootstrap/dist/css/bootstrap.css'

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
  
  const app = createApp({router, ...App})
  app.mount('#app');
});
