<template>
  <div>
  <b-container fluid='true' class="bv-example-row">
    <p> Downloading file: {{filename}}</p>
    <b-progress :value="value" :max="max" class="mb-3"></b-progress>
</b-container>
  </div>
</template>

<script>
import { API } from 'aws-amplify';

export default {
  name: 'download',
  props: ['nav', 'filename'],
  computed: {
    path: function () {
      return this.nav[this.nav.length - 1].to.query.path
    },
    value: function () {
      return ((this.dzchunkindex + 1) / this.totalChunks) * 100
    }
  },
  data () {
    return {
        href: 'data:application/octet-stream;base64,',
        chunkBlobs: [],
        dzchunkindex: null,
        dzchunkbyteoffset: null,
        totalChunks: null,
        max: 95,
        downloadDone: false
    }
  },
  created: function () {
      this.downloadFile()
  },
  methods: {
    async downloadChunk (requestParams) {
          try {
            let response = await API.get('fileManagerApi', '/api/objects/' + this.$route.params.id + '/download', requestParams)
            return response
          }
          catch (error) {
            let formattedResponse = {"type": "danger", "message": "Download did not complete successfully. Check API logs."}
            this.$emit("downloadCompleted", formattedResponse)
          }
      },
    async downloadFile () {
          if (this.dzchunkindex == null && this.dzchunkbyteoffset == null) {
              this.$emit("downloadStarted")
              let requestParams = { 
                  queryStringParameters: {
                    "path": this.path,
                    "filename": this.filename
                  }
              };
              
              let chunk = await this.downloadChunk(requestParams)
              
              
              let offset = chunk.dzchunkbyteoffset
              let chunkIndex = chunk.dzchunkindex

              let chunkData = chunk.chunk_data

              let chunkblob = await (await fetch(this.href + chunkData)).blob();

              this.totalChunks = chunk.dztotalchunkcount
              this.chunkBlobs[chunkIndex] = chunkblob
              
              this.dzchunkindex = chunkIndex
              this.dzchunkbyteoffset = offset
              
              this.downloadFile()
          }
          else {              
              let requestParams = { 
                  queryStringParameters: {
                    "path": this.path,
                    "filename": this.filename,
                    "dzchunkindex": this.dzchunkindex,
                    "dzchunkbyteoffset": this.dzchunkbyteoffset
                  }
              };
              
              
              let chunk = await this.downloadChunk(requestParams)

              let offset = chunk.dzchunkbyteoffset
              let chunkIndex = chunk.dzchunkindex
              console.log(chunkIndex)
              let totalChunks = chunk.dztotalchunkcount

              if (chunkIndex == totalChunks) {
                  this.downloadDone = true
                  
                  let finalBlob = new Blob(this.chunkBlobs)

                  let link = document.createElement('a')
                  
                  link.href = window.URL.createObjectURL(finalBlob)
                  link.download = this.filename
                  
                  link.click()
                  
                  let formattedResponse = {"type": "success", "message": "Download completed successfully!"}
                  this.$emit("downloadCompleted", formattedResponse)
              }
              else {
                  let chunkData = chunk.chunk_data
                  
                  this.dzchunkindex = chunkIndex
                  this.dzchunkbyteoffset = offset

                  let chunkblob = await (await fetch(this.href + chunkData)).blob();

                  this.chunkBlobs[chunkIndex] = chunkblob
                  
                  this.downloadFile()

              }

          }
      }
    }
}


</script>



<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
#navigation {
    padding-left: 2%;
}

#title {
    padding-left: 2%;
}

b-button {
    padding-top: 2%;
}

</style>
