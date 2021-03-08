<template>
  <div>
  <b-container fluid='true' class="bv-example-row">
  <br>
  <h2 id=title>Filesystem {{ $route.params.id }}</h2>
  <br>
  <b-row>
    <b-col id=navigation>
        <b-card class="mr-3">
            <b-row>
               <b-col align-self="start">
                    <h3>Navigation</h3>
                </b-col>
                <b-col>
                </b-col>
                <b-col align-self="end">
                    <b-button v-b-modal.dir-modal variant="outline-info" class="mb-2">
                        Create directory
                    <b-icon icon="folder-plus" aria-hidden="true"></b-icon>
                    </b-button>
                    <b-modal id="dir-modal">
                        <makedir @dirCreated=refresh v-bind:nav="navObjects"/>
                    </b-modal>
                </b-col>
            </b-row>
            <b-breadcrumb v-on:click="navigateBack" :items="navObjects"></b-breadcrumb>
            <b-table striped hover :items="dirs">
                <template v-slot:cell(Directory)="data">
                    <b-button @click='addDirectoryObject(data.value)' variant="link">{{ data.value }}</b-button>
                </template>
            </b-table>
        </b-card>
    </b-col>
    <b-col>
        <b-card class="mr-3">
            <b-row>
                <b-col cols="5">
                    <h3>Files</h3>
                </b-col>
                <b-col>
                    <b-form-checkbox v-model="editEnabled" name="editEnableButton" switch>
                        Delete Mode
                    </b-form-checkbox>
                </b-col>
                <b-col cols="4">
                    <b-button v-b-modal.file-modal variant="outline-info" class="mb-2">
                        Upload file
                        <b-icon icon="box-arrow-up" aria-hidden="true"></b-icon>
                    </b-button>
                    <b-modal id="file-modal">
                        <upload @uploadCompleted=refresh v-bind:nav="navObjects"/>
                    </b-modal>
                </b-col>
            </b-row>
            <b-table striped hover responsive
            :items="files"
            >
            <template v-slot:cell(Name)="data">
                <b-row>
                    <b-col cols="9">
                        {{data.value}}
                    </b-col>
                    <div v-if="editEnabled">
                    <!-- <b-col cols="1">
                        <b-button variant="outline-warning">
                            <b-icon icon="pencil"></b-icon>
                        </b-button>
                    </b-col>
                    <br> -->
                    <b-col cols="1">
                        <b-button @click=deleteFile(data.value) variant="outline-danger">
                            <b-icon icon="trash"></b-icon>
                        </b-button>
                    </b-col>
                    </div>
                </b-row>
            </template>
            </b-table>
        </b-card>
    </b-col>
  </b-row>
</b-container>
  </div>
</template>

<script>
import { API } from 'aws-amplify';
import upload from '../components/upload.vue'
import makedir from '../components/makedir.vue'

export default {
  name: 'Filesystem',
  components: {
      upload,
      makedir
  },
  data () {
    return {
        editEnabled: false,
        files: [],
        dirs: [],
        navObjects: [
            {
                text: '/mnt/efs',
                to: {name: 'filesystem', query: {'path': '/mnt/efs'}},
                active: true
            }
        ]
    }
  },
  mounted: function () {
      console.log(this.$route.params)
      this.retrieveObjects()
  },
  methods: {
      refresh () {
          this.dirs = []
          this.files = []
          this.retrieveObjects()
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
      async deleteFile (name) {
          let requestParams = { 
              queryStringParameters: {  
                path: this.navObjects[this.navObjects.length - 1].to.query.path,
                name: name
            }
          };
          try {
              let response = await API.del('fileManagerApi', '/api/objects/' + this.$route.params.id, requestParams)
              console.log(response)
              alert(JSON.stringify(response))
              this.refresh()
          }
          catch (error) {
              alert('Unable to delete file, check api logs')
              console.log(error)
          }
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
              alert('Unable to list filesystem objects, check api logs')
              console.log(error)
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
