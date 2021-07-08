<template>
  <div>
  <b-container fluid='true' class="bv-example-row">
  <b-row>
    <b-col>
        <h2>Upload</h2>
          <p> Path: {{ path }}</p>
          <div v-if=urlLoaded>
            <b-form-file
              v-model="fileToUpload"
              :state="Boolean(fileToUpload)"
              placeholder="Choose a file or drop it here..."
              drop-placeholder="Drop file here..."
            ></b-form-file>
            <div v-if="uploading">
              <b-progress :value="value" :max="max" class="mb-3"></b-progress>
            </div>
          </div>
          <div v-if="!uploading">
            <b-button @click="checkIfFileExists()">Upload</b-button>
          </div>
    </b-col>
  </b-row>
</b-container>
  </div>
</template>

<script>
import { API } from 'aws-amplify';

export default {
  name: 'upload',
  props: ['nav', 'files'],
  computed: {
    path: function () {
      return this.nav[this.nav.length - 1].to.query.path
    },
    value: function () {
      return ((this.currentChunk + 1) / this.totalChunks) * 100
    },
    fileNames: function () {
      let fileNames = []
      this.files.forEach(element => fileNames.push(element.Name))
      return fileNames
    }
  },
  mounted: function () {
    this.urlLoaded = true
  },
  data () {
    return {
      urlLoaded: false,
      fileToUpload: null,
      totalChunks: 0,
      currentChunk: 0,
      max: 95,
      uploading: false,
      chunkSize: 1000000 // bytes
    }
  },
  methods: {
    afterComplete(status, message) {
      let formattedResponse = {"type": "", "message": ""}
      if (status == true) {
        formattedResponse.type = "success"
        formattedResponse.message = message
        this.$emit('uploadCompleted', formattedResponse)
      }
      else {
        formattedResponse.type = "danger"
        formattedResponse.message = message
        this.$emit('uploadCompleted', formattedResponse)
      }
    },
    blobToBase64(blob) {
      return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result.split(',').pop());
        reader.readAsDataURL(blob);
      });
    },
    async deleteFile () {
          let requestParams = { 
              queryStringParameters: {  
                path: this.path,
                name: this.fileToUpload.name
            }
          };
          try {
              await API.del('fileManagerApi', '/api/objects/' + this.$route.params.id, requestParams)
          }
          catch (error) {
              console.log(error)
          }
    },
    async uploadChunk(chunkData) {  
      let requestParams = { 
          queryStringParameters: {  
            path: this.path,
            filename: this.fileToUpload.name
          },
          headers: {
            "Content-Type": "application/json"
          },
          body: chunkData
      };
      let response = await API.post('fileManagerApi', '/api/objects/' + this.$route.params.id + '/upload', requestParams)
      let chunkStatus = false;
      if(response.statusCode == 200){
          chunkStatus = true
      }else{
          //Retry request
          response = await API.post('fileManagerApi', '/api/objects/' + this.$route.params.id + '/upload', requestParams)
          if(response.statusCode == 200){
            chunkStatus = true
          }else{
              chunkStatus = false
          }
      }
      return chunkStatus
    },
    checkIfFileExists () {
      if (this.fileNames.indexOf(this.fileToUpload.name) > -1 ) {
        console.log(this.fileToUpload.name, this.fileNames)
        this.afterComplete(false, "File already exists.")
      }
      else {
        this.upload(0, 0)
      }
    },
    // this whole function needs to be cleaned up, notably reduce duplicate code by breaking out into functions - works well for now though
    async upload(chunkIndex, chunkOffset) {
      this.currentChunk = chunkIndex
      // first if block is for the first call to upload, e.g. when the button is clicked
      if (chunkIndex == 0 && chunkOffset == 0) {
        this.$emit('uploadStarted')
        let fileSize = this.fileToUpload.size
        this.totalChunks = Math.ceil(fileSize / this.chunkSize)
        let chunk = this.fileToUpload.slice(0, this.chunkSize + 1)
        let chunkData = {}
        this.uploading = true

        chunkData.dzchunkindex = 0
        chunkData.dztotalfilesize = fileSize
        chunkData.dzchunksize = this.chunkSize
        chunkData.dztotalchunkcount = this.totalChunks
        chunkData.dzchunkbyteoffset = 0
        chunkData.content = await this.blobToBase64(chunk)
        
        let chunkStatus = await this.uploadChunk(chunkData)
        if (!chunkStatus) { //Check if not a 200 response code 
          // Delete partially uploaded file.
          this.deleteFile()
          this.afterComplete(false, "File was unable to be uploaded successfully. Check API logs.")
        }
        else {
          if (this.totalChunks == 1 || this.totalChunks < 1) {
            this.uploading = false
            this.afterComplete(true, "File uploaded successfully!")
          }
          else {
            let nextChunkIndex = 1
            let nextChunkOffset = this.chunkSize + 1
            this.upload(nextChunkIndex, nextChunkOffset)
          }
        }
      }
      // this case is hit recursively from the first call
      else {
        // check to see if the current chunk is equal to total chunks, if so we send the last bytes and return complete
        if (chunkIndex == this.totalChunks - 1) {
          let fileSize = this.fileToUpload.size
          let chunk = this.fileToUpload.slice(chunkOffset)
          let chunkData = {}
        
          chunkData.dzchunkindex = chunkIndex
          chunkData.dztotalfilesize = fileSize
          chunkData.dzchunksize = this.chunkSize
          chunkData.dztotalchunkcount = this.totalChunks
          chunkData.dzchunkbyteoffset = chunkOffset
          chunkData.content = await this.blobToBase64(chunk)
          
          let chunkStatus = await this.uploadChunk(chunkData)
          
          
          if (!chunkStatus) { //Check if not a 200 response code 
            // Delete partially uploaded file.
            this.deleteFile()
            this.afterComplete(false, "File was unable to be uploaded successfully. Check API logs.")
          }
          else {
            this.uploading = false
            this.afterComplete(true, "File uploaded successfully!")
          }
        }
        // in this case there are chunks remaining, so we continue to upload chunks
        else {
          let fileSize = this.fileToUpload.size
          let end = Math.min(chunkOffset + this.chunkSize, fileSize)
          let chunk = this.fileToUpload.slice(chunkOffset, end)
          let chunkData = {}
        
          chunkData.dzchunkindex = chunkIndex
          chunkData.dztotalfilesize = fileSize
          chunkData.dzchunksize = this.chunkSize
          chunkData.dztotalchunkcount = this.totalChunks
          chunkData.dzchunkbyteoffset = chunkOffset
          chunkData.content = await this.blobToBase64(chunk)
          
          let chunkStatus = await this.uploadChunk(chunkData)
          
          if (!chunkStatus) { //Check if not a 200 response code 
            // Delete partially uploaded file.
            this.deleteFile()
            this.afterComplete(false, "File was unable to be uploaded successfully. Check API logs.")
          }
          else {
            let nextChunkIndex = chunkIndex + 1
            let nextChunkOffset = end
            this.upload(nextChunkIndex, nextChunkOffset)
          }
        }
      }
    }
  }
}


</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

button {
  margin-top: 5%;
}

</style>