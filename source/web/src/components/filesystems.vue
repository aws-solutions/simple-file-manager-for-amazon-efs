<template>
<div>
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
        <div v-if="noFileSystemsFound">
            <p>No Amazon EFS file systems found. 
                Please create an EFS filesystem in the 
                <a href="https://console.aws.amazon.com/efs/home/file-systems">AWS console</a>
            </p>
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
          noFileSystemsFound: false
      }
  },
  mounted: function () {
      this.listFilesystems()
  },
  methods: {
      async listFilesystems() {
          try {
              let response = await API.get('fileManagerApi', '/api/filesystems/')
              if(response.length == 0){
                  this.noFileSystemsFound = true
              }else{
                  this.filesystems = response
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


</style>