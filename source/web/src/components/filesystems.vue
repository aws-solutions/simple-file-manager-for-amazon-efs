<template>
<div>
    <b-table striped hover :items="filesystems">
        <template v-slot:cell(file_system_id)="data">
            <div v-if=data.item.managed>
                <a :href="`/filesystem/${data.value}`">{{ data.value }}</a>
            </div>
            <div v-else>
                <p>{{data.value}}</p>
            </div>
        </template>
        <template v-slot:cell(managed)="data">
            <div v-if=data.value>
                <p>{{data.value}}</p>
            </div>
            <div v-else>
                <a :href="`/configure/${data.item.file_system_id}`">{{ data.value }}</a>
            </div>
        </template>
        <template v-slot:cell(file_systems)>
            <div>
                <p>No Amazon EFS file systems found. 
                   Please create an EFS filesystem in the 
                   <a href="https://console.aws.amazon.com/efs/home/file-systems">AWS console</a>
                </p>
            </div>
        </template>
    </b-table>
</div>
</template>

<script>
import { API } from 'aws-amplify';

export default {
  name: 'filesystems',
  data() {
      return {
          filesystems: []
      }
  },
  mounted: function () {
      this.listFilesystems()
  },
  methods: {
      async listFilesystems() {
          try {
              let response = await API.get('fileManagerApi', '/api/filesystems/')
              this.filesystems = response
          }
          catch (error) {
              //alert('Unable to list filesystems, check api logs')
              console.log(error)
              this.filesystems = [{"file_systems": "True"}]
          }
      }
  }
}


</script>



<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>


</style>