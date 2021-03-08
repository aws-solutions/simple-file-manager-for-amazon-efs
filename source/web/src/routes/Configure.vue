<template>
  <div>
    <b-container class="bv-example-row bv-example-row-flex-cols">
        <h1>Filesystem: {{ $route.params.id }}</h1>
        <b-row>
            <b-col>
                <br>
                <br>
                <br>
                <br>
                <h3> Mount Target Network Information</h3>
                <p>{{netinfo}}</p>
            </b-col>
            <b-col align-self="center">
                <b-form @submit="onSubmit">
                        <h3> Create file manager lambda</h3>
                        <p> Select a mount point to attach to:</p>
                        <b-form-select v-model="selected" :options="options"></b-form-select>
                        <br>
                        <br>
                        <b-button type="submit">
                            Submit
                        <b-icon icon="Hammer" aria-hidden="true"></b-icon>
                </b-button>
                </b-form>
            </b-col>
            <b-col>
            </b-col>
        </b-row>
    </b-container>
  </div>
</template>

<script>
import { API } from 'aws-amplify';

export default {
  name: 'Configure',
  data () {
    return {
        netinfo: null,
        form: {
            mountTarget: null
        },
        selected: null
    }
  },
  created: function () {
      this.getFilesystemNetinfo()
  },
  computed: {
      options: function () {
          let mountTargetNames = Object.keys(this.netinfo)
          return mountTargetNames
      }
  },
  methods: {
      onSubmit(evt) {
        evt.preventDefault()
        let mountTarget = this.selected
        let mountTargetNetinfo = this.netinfo[mountTarget]
        this.createManagerLambda(mountTargetNetinfo)
      },
      formatNetinfo (netinfo) {
          let tmpNetinfo = {}
          for (var i=0, n=netinfo.length; i < n; ++i ) {
              let netinfoKeys = Object.keys(netinfo[i])
              let mountTargetName = netinfoKeys[0]
              tmpNetinfo[mountTargetName] = netinfo[i][mountTargetName]
              
          }
          return tmpNetinfo
      },
      async getFilesystemNetinfo () {
          try {
              let response = await API.get('fileManagerApi', '/api/filesystems/' + this.$route.params.id + '/netinfo')
              let formattedNetinfo = this.formatNetinfo(response)
              this.netinfo = formattedNetinfo
          }
          catch (error) {
              alert('Unable to retrieve filesystem netinfo, check api logs')
              console.log(error)
          }
      },
      async createManagerLambda (netinfo) {
          const params = {
              body: {"subnetId": netinfo.subnet_id, "securityGroups": netinfo.security_groups},
              headers: {"Content-Type": "application/json"}
         }
          try {
              let response = await API.post('fileManagerApi', '/api/filesystems/' + this.$route.params.id + '/lambda', params)
              console.log(response)
          }
          catch (error) {
              alert('Unable to create filesystem lambda, check api logs')
              console.log(error)
          }
      }
  }
}


</script>



<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>


</style>
