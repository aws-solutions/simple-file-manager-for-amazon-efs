<template>
<div>
    <b-row>
    <b-table striped hover :items="filesystems">
        <template v-slot:cell(file_system_id)="data">
            <div v-if="data.item.managed === true">
                <a :href="`/filesystem/${data.value}`">{{ data.value }}</a>
            </div>
            <div v-else>
                <p>{{data.value}}</p>
            </div>
        </template>
        <template v-slot:cell(managed)="data">
            <div v-if="data.value === true">
                <a :href="`/details/${data.item.file_system_id}`" v-b-tooltip.hover title="Click to unregister file system.">{{ data.value }}</a>
            </div>
            <div v-else-if="data.value === 'Deleting'">
                <b-link href="/" v-b-tooltip.hover title="Stack deletion can take several minutes. Click to refresh.">{{data.value}}</b-link>
            </div>
            <div v-else-if="data.value === 'Creating'">
                <b-link href="/" v-b-tooltip.hover title="Stack creation can take several minutes. Click to refresh.">{{data.value}}</b-link>
            </div>
            <div v-else>
                <a :href="`/configure/${data.item.file_system_id}`" v-b-tooltip.hover title="Click to onboard file system.">{{ data.value }}</a>
            </div>
        </template>
    </b-table>
    </b-row>
    <div v-if="noFileSystemsFound">
        <p>No Amazon EFS file systems found. 
            Please create an EFS filesystem in the 
            <a href="https://console.aws.amazon.com/efs/home/file-systems">AWS console</a>
        </p>
    </div>
    <div id="moreFilesystemsBtn" v-if="paginationToken != null">
            <b-button @click=listFilesystems()>More</b-button>
    </div>
</div>
</template>

<script>
import { API } from 'aws-amplify';

export default {
  name: 'filesystems',
  data() {
      return {
          filesystems: [], 
          noFileSystemsFound: false,
          paginationToken: null
      }
  },
  mounted: function () {
      this.listFilesystems()
  },
  methods: {
      async getFileSystemData(apiPath) {
        let response = await API.get('fileManagerApi', apiPath)
        return response
      },
      async listFilesystems() {
        let apiPath = ''
        if (this.paginationToken == null) {
            apiPath = '/api/filesystems/'
        }    
        else {
            apiPath = '/api/filesystems/?cursor=' + this.paginationToken
        }

        try {
            let filesystemData = await this.getFileSystemData(apiPath)
            let filesystems = filesystemData.filesystems
            if (filesystems.length == 0) {
                this.noFileSystemsFound = true
            }
            else {
                filesystems.forEach(filesystem => this.filesystems.push(filesystem))
            }
            
            if ("paginationToken" in filesystemData) {
                this.paginationToken = filesystemData.paginationToken
            }
            else {
                this.paginationToken = null
            }
          }
          
          catch (error) {
              alert('Unable to list filesystems, check api logs')
              console.log(error)
          }
      }
  }
}


</script>



<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

#moreFilesystemsBtn {
    float: right;

}

</style>