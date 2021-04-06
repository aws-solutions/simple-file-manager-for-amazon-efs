<template>
  <div>
  <b-container fluid='true' class="bv-example-row">
  <b-row>
    <b-col>
        <h2>Upload</h2>
          <p> Path: {{ path }}</p>
          <div v-if=urlLoaded>
            <vue-dropzone ref="myVueDropzone" id="dropzone" :options="dropzoneOptions" @vdropzone-complete="afterComplete"></vue-dropzone>
          </div>
    </b-col>
  </b-row>
</b-container>
  </div>
</template>

<script>
import vue2Dropzone from 'vue2-dropzone'
import 'vue2-dropzone/dist/vue2Dropzone.min.css'
import Auth from '@aws-amplify/auth';
import { Signer } from '@aws-amplify/core';
//import * as urlLib from 'url';

export default {
  name: 'upload',
  components: {
    vueDropzone: vue2Dropzone
  },
  props: ['nav'],
  computed: {
    path: function () {
      return this.nav[this.nav.length - 1].to.query.path
    },
    dropzoneOptions: function () {
      let options = {
          paramName: 'file',
          url: this.fileManagerApi + '/api/upload/' + this.$route.params.id + '?path=' + this.path,
          chunking: true,
          forceChunking: true,
          method: 'post',
          //timeout: 0,
          maxFilesize: 2048, // megabytes
          chunkSize: 1000000, // bytes
          //parallelChunkUploads: true,
          //retryChunks: true,
          // "Accept": "Application/Octet-Stream", 
          self: this,
          init: function() {
            this.on('sending', async function(file, xhr, formData) {
              xhr.abort()
              let signedParams = await this.options.self.signRequest(this.options.url, formData)
              console.log(signedParams)
              let response = await fetch(signedParams.url, {
                  method: 'POST',
                  mode: 'cors',
                  cache: 'no-cache',
                  headers: signedParams.headers,
                  referrer: 'client',
                  body: signedParams.data
              })
              
              console.log(response)
              // console.log(signedParams)
              // xhr.open("POST", this.options.url)

              // xhr.setRequestHeader('Authorization', signedParams.headers.Authorization)
              // xhr.setRequestHeader('X-Amz-Security-Token', signedParams.headers['X-Amz-Security-Token'])
              // xhr.setRequestHeader('x-amz-date', signedParams.headers['x-amz-date'])
              
              // xhr.send(formData)

            })
          }
        }
        return options
      }
  },
  mounted: function () {
    this.urlLoaded = true
  },
  data () {
    return {
      urlLoaded: false
    }
  },
  methods: {
    afterComplete() {
      this.$emit('uploadCompleted')
    },
    async signRequest(url, data) {
  // const { ...parsedUrl } = urlLib.parse(url, true, true);

  // let formattedUrl = urlLib.format({
  //   ...parsedUrl,
  //   query: { ...parsedUrl.query }
  // });

  // console.log(formattedUrl)

  return Auth.currentCredentials()
    .then(credentials => {
      let cred = Auth.essentialCredentials(credentials);

      return Promise.resolve(cred);
    })
    .then(essentialCredentials => {
      let params = {
        headers: { },
        data: data,
        method: 'POST',
        url: url
      }

      let cred = {
        secret_key: essentialCredentials.secretAccessKey,
        access_key: essentialCredentials.accessKeyId,
        session_token: essentialCredentials.sessionToken
      }

      console.log(params)
      console.log(cred)

      let serviceInfo = {
        region: this.awsRegion, service: 'execute-api'
      }

      console.log(serviceInfo)
      
      let signedReq = Signer.sign(params, cred, serviceInfo);

      return Promise.resolve(signedReq);
    });
}

  }
}


</script>



<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>


</style>