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
          url: 'https://i076sdxd27.execute-api.us-west-2.amazonaws.com/api/upload/' + this.$route.params.id + '?path=' + this.path,
          chunking: true,
          forceChunking: true,
          method: 'post',
          //timeout: 0,
          maxFilesize: 2048, // megabytes
          chunkSize: test_download.py, // bytes
          //parallelChunkUploads: true,
          //retryChunks: true,
          // "Accept": "Application/Octet-Stream", 
          //"Content-Type": "Application/Octet-Stream", '
          headers: {'Cache-Control': null, 'X-Requested-With': null}
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
    }
  }
}


</script>



<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>


</style>
