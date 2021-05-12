<template>
  <div>
    <b-container class="bv-example-row bv-example-row-flex-cols">
        <h1>Filesystem: {{ $route.params.id }}</h1>
        
        <div v-if="processing">
            <b-spinner/>
        </div>
        <div v-else>
        <b-row>
            <b-col align-self="center">
                <b-form @submit="onSubmit">
                        <h3> Create file manager lambda</h3>
                        <b-form-group
                            label="User ID:"
                            description="The numeric POSIX user ID that lambda will use to make file system requests as"
                        >
                            <b-form-input v-model="uid" :state="valid" placeholder="Enter a custom UID or leave default (1000)"></b-form-input>
                        </b-form-group>

                        <b-form-group
                            label="Group ID:"
                            description="The numeric POSIX group ID that lambda will use to make file system requests as"
                        >
                            <b-form-input v-model="gid" :state="valid" placeholder="Enter a custom GID or leave default (1000)"></b-form-input>
                        </b-form-group>

                        <b-form-group
                            label="Path:"
                            description="The file system directory that lambda will use as the root directory"
                        >
                            <b-form-input v-model="path" :state="valid" placeholder="Enter a custom path or leave default (/efs)"></b-form-input>
                        </b-form-group>
                        
                        <b-form-invalid-feedback :state="valid">
                            UID, GID, and Path must not be empty. The path must begin with a forward slash: /
                        </b-form-invalid-feedback>
                        <b-button :disabled='!valid' type="submit">
                            Submit
                        <b-icon icon="Hammer" aria-hidden="true"></b-icon>
                </b-button>
                </b-form>
            </b-col>
            <b-col>
            </b-col>
        </b-row>
        </div>
    </b-container>
  </div>
</template>

<script>
import { API } from 'aws-amplify';

export default {
  name: 'Configure',
  data () {
    return {
        processing: false,
        uid: '1000',
        gid: '1000',
        path: '/efs'
    }
  },
  computed: {
      valid() {
          return this.uid != "" && this.gid != "" && this.path != "" && this.path.charAt(0) == '/'
      }
  },
  methods: {
      async onSubmit(evt) {
        evt.preventDefault();

        if (this.valid) {
            let mountTargetNetinfo = await this.getFilesystemNetinfo()
        
            mountTargetNetinfo['uid'] = this.uid
            mountTargetNetinfo['gid'] = this.gid
            mountTargetNetinfo['path'] = this.path

            this.createManagerLambda(mountTargetNetinfo)
        }
        else {
            alert("Form Validation Error. Check the form input and try again.")
        }
      },
      formatNetinfo (netinfo) {
          let subnets = []
          let securityGroups = []
        
          for (var i=0, n=netinfo.length; i < n; ++i ) {
              let mountTarget = Object.keys(netinfo[i])[0]
              let subnet = netinfo[i][mountTarget]['subnet_id']
              let securityGroup = netinfo[i][mountTarget]['security_groups']

              subnets.push(subnet)
              securityGroups.push.apply(securityGroups, securityGroup)
          }

          let uniqSecurityGroups = [...new Set(securityGroups)]

          if (uniqSecurityGroups.length > 5) {
              uniqSecurityGroups = uniqSecurityGroups.slice(0, 4)
          }
          
          if (subnets.length > 5) {
              subnets = subnets.slice(0, 4)
          }

          let tmpNetinfo = {'subnetIds': subnets, 'securityGroups': uniqSecurityGroups}
          
          return tmpNetinfo
      },
      async getFilesystemNetinfo () {
          try {
              let response = await API.get('fileManagerApi', '/api/filesystems/' + this.$route.params.id + '/netinfo')
              let formattedNetinfo = this.formatNetinfo(response)
              return formattedNetinfo
          }
          catch (error) {
              alert('Unable to retrieve filesystem netinfo, check api logs')
          }
      },
      async createManagerLambda (netinfo) {
          const params = {
              body: {"subnetIds": netinfo.subnetIds, "securityGroups": netinfo.securityGroups, "uid": netinfo.uid, "gid": netinfo.gid, "path": netinfo.path},
              headers: {"Content-Type": "application/json"}
         }
          try {
              this.processing = true
              await API.post('fileManagerApi', '/api/filesystems/' + this.$route.params.id + '/lambda', params)
              this.processing = false
              this.$router.push({ name: "home" })
          }
          catch (error) {
              alert('Unable to create filesystem lambda, check api logs')
              this.processing = false
          }
      }
  }
}


</script>



<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>


</style>
