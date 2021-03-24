<template>
  <div>
  <b-container fluid='true' class="bv-example-row">
  <!-- <div v-if="downloadDone"> -->
    <!-- <a v-bind:href="href" v-bind:download="filename">Download</a> -->
  <!-- </div> -->
</b-container>
  </div>
</template>

<script>

export default {
  name: 'Download',
  data () {
    return {
        href: 'data:application/octet-stream;base64,',
        chunkBlobs: [],
        filename: 'test_technical_cue.mp4',
        path: '/mnt/efs/test/',
        dzchunkindex: null,
        dzchunkbyteoffset: null,
        base_url: 'https://i076sdxd27.execute-api.us-west-2.amazonaws.com/api/download/fs-b44095b1',
        downloadDone: false
    }
  },
  created: function () {
      this.downloadFile()
  },
  methods: {
    async downloadChunk (url) {
          let response = await fetch(url);
          var body = response.json()
          return body
      },
    async downloadFile () {
          if (this.dzchunkindex == null && this.dzchunkbyteoffset == null) {
              let url = this.base_url + '?path=' + this.path + '&filename=' + this.filename
              let chunk = await this.downloadChunk(url)
              
              let offset = chunk.dzchunkbyteoffset
              let chunkIndex = chunk.dzchunkindex


              let chunkData = chunk.chunk_data

              let chunkblob = await (await fetch(this.href + chunkData)).blob();

              this.chunkBlobs[chunkIndex] = chunkblob
              
              this.dzchunkindex = chunkIndex
              this.dzchunkbyteoffset = offset
              
              this.downloadFile()
          }
          else {
              let url = this.base_url + '?path=' + this.path + '&filename=' + this.filename + '&dzchunkindex=' + this.dzchunkindex + '&dzchunkbyteoffset=' + this.dzchunkbyteoffset
              let chunk = await this.downloadChunk(url)

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

                  console.log('Done')
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
