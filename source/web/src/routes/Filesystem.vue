<template>
  <div>
    <b-alert
      :variant="alertType"
      dismissible
      fade
      :show="showAlert"
      @dismissed="showAlert=false"
    >
    {{ alertMessage }}
  </b-alert>
  <b-container fluid='true' class="bv-example-row">
  <br>
  <h2 id=title>Filesystem {{ $route.params.id }}</h2>
  <br>
  <b-row>
    <b-col id=navigation>
        <b-card class="mr-3">
            <b-row>
               <b-col cols=7>
                    <h3>Navigation</h3>
                </b-col>
                <b-col>
                </b-col>
                <b-col>
                    <b-button v-b-modal.dir-modal variant="link" class="mb-2 dirBtn">
                        Create directory
                    <b-icon icon="folder-plus" aria-hidden="true"></b-icon>
                    </b-button>
                    <b-modal ref="makedir" hide-footer id="dir-modal">
                        <makedir @dirCreated=refresh v-bind:nav="navObjects"/>
                    </b-modal>
                </b-col>
            </b-row>
            <b-breadcrumb v-on:click="navigateBack" :items="navObjects"></b-breadcrumb>
            <b-table striped hover sort-by="Directory" sort-desc="true" :items="dirs">
                <template v-slot:cell(Directory)="data">
                    <b-button @click='addDirectoryObject(data.value)' variant="link">{{ data.value }}</b-button>
                </template>
            </b-table>
        </b-card>
    </b-col>
    <b-col>
        <b-card class="mr-3">
            <b-row>
                <b-col cols=10>
                    <h3>Files</h3>
                </b-col>
                <b-col align-self="end">
                    <b-button v-b-modal.upload-modal variant="link" class="mb-2 uploadBtn">
                        Upload file
                        <b-icon icon="box-arrow-up" aria-hidden="true"></b-icon>
                    </b-button>
                    <b-modal ref="upload" v-bind:no-close-on-backdrop="active" hide-header hide-footer id="upload-modal">
                        <upload @uploadStarted=operationStart @uploadCompleted=refresh :nav="navObjects" :files="files"/>
                    </b-modal>
                </b-col>
            </b-row>
            <b-table striped hover responsive
            :items="files"
            >
            <template v-slot:cell(Name)="data">
                <b-row>
                    <b-col cols="10">
                        {{data.value}}
                    </b-col>
                    <!-- <b-col cols="1">
                        <b-button variant="outline-warning">
                            <b-icon icon="pencil"></b-icon>
                        </b-button>
                    </b-col>
                    <br> -->
                    <b-col>
                        <b-link @click=deleteFile(data.value)>
                            <b-icon icon="trash" variant="danger"></b-icon>
                        </b-link>
                    </b-col>
                    <b-col>
                        <b-link @click=startDownload(data.value) v-b-modal.download-modal>
                            <b-icon class="downloadIcon" icon="arrow-down" variant="primary"></b-icon>
                        </b-link>
                    </b-col>
                </b-row>
            </template>
            </b-table>
            <b-modal ref="download" v-bind:no-close-on-backdrop="active" hide-header hide-footer id="download-modal">
                <download @downloadStarted=operationStart @downloadCompleted=refresh :nav="navObjects" :filename="filename"/>
            </b-modal>
        </b-card>
    </b-col>
  </b-row>
</b-container>
  </div>
</template>

<script>
import { API } from 'aws-amplify';
import download from '../components/download.vue'
import upload from '../components/upload.vue'
import makedir from '../components/makedir.vue'

export default {
  name: 'Filesystem',
  components: {
      upload,
      makedir,
      download
  },
  data () {
    return {
        active: false,
        editEnabled: false,
        filename: null,
        files: [],
        dirs: [],
        navObjects: [
            {
                text: '/mnt/efs',
                to: {name: 'filesystem', query: {'path': '/mnt/efs'}},
                active: true
            }
        ],
        showAlert: false,
        alertMessage: null,
        alertType: null
    }
  },
  mounted: function () {
      this.retrieveObjects()
  },
  methods: {
      operationStart () {
          this.active = true
      },
      refresh (response) {
          this.dirs = []
          this.files = []
          this.retrieveObjects()
          this.$refs['download'].hide()
          this.$refs['upload'].hide()
          this.$refs['makedir'].hide()
          this.active = false
          this.alertMessage = response.message
          this.alertType = response.type
          this.showAlert = true
      },
      navigateBack () {
          if (this.navObjects.length > 1) {
              this.navObjects.pop()
              this.navObjects[this.navObjects.length - 1].active = true
              this.dirs = []
              this.files = []
              this.retrieveObjects()
          }
      },
      listObjects (objects) {
          let files = objects.files
          this.files = []
          for (var file = 0, fileLen = files.length; file < fileLen; file++) {
            let tmp_item = {"Name": files[file]}
            this.files.push(tmp_item)
          }
          // todo: need to fix this typo in the api response 
          let directories = objects.directiories
          this.directories = []
          for (var dir = 0, dirLen = directories.length; dir < dirLen; dir++) {
            let tmp_item = {"Directory": directories[dir]}
            this.dirs.push(tmp_item)
        }
      },
      startDownload (filename) {
          this.filename = filename
      },
      async deleteFile (name) {
          let requestParams = { 
              queryStringParameters: {  
                path: this.navObjects[this.navObjects.length - 1].to.query.path,
                name: name
            }
          };
          let formattedResponse = {"type": "", "message": ""}
          try {
              let response = await API.del('fileManagerApi', '/api/objects/' + this.$route.params.id, requestParams)
              if (response.statusCode != 200) {
                formattedResponse.type = "danger"
                formattedResponse.message = "File was unable to be deleted successfully. Check API logs."
              }
              else {
                 formattedResponse.type = "success"
                 formattedResponse.message = "File deleted successfully!"
              }
          }
          catch (error) {
            formattedResponse.type = "danger"
            formattedResponse.message = "File was unable to be deleted successfully. Check API logs."
          }
          this.refresh(formattedResponse)
        },
      addDirectoryObject (directory) {
          this.navObjects[this.navObjects.length - 1].active = false
          let existingPath = this.navObjects[this.navObjects.length - 1].to.query.path
          let newPath = existingPath + '/' + directory
          console.log(newPath)
          let newDirObject = {'text': directory, 'to': {name: 'filesystem', query: {'path': newPath}}, active: true}
          this.navObjects.push(newDirObject)
          this.dirs = []
          this.files = []
          this.retrieveObjects()
      },

      async retrieveObjects () {
          //let activeDirectory = this.objects[this.objects - 1]
          //console.log(path)
          let requestParams = { 
              queryStringParameters: {  
                path: this.navObjects[this.navObjects.length - 1].to.query.path
            }
          };
          try {
              let response = await API.get('fileManagerApi', '/api/objects/' + this.$route.params.id, requestParams)
              this.listObjects(response)
          }
          catch (error) {
              let formattedResponse = {"type": "danger", "message": "Unable to list filesystem objects. Check API logs."}
              this.refresh(formattedResponse)
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

.downloadIcon {
    color:#FF9900!important;
}

.uploadBtn {
    color:#FF9900!important;
}

.dirBtn {
    color:#FF9900!important;
}
</style>
