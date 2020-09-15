<template>
  <div>
  <b-container fluid='true' class="bv-example-row">
  <b-row>
    <b-col>
           <b-form @submit="onSubmit" inline>
                        <h4> Directory Name: </h4>
                        <b-input
                            id="inline-form-input-mounttarget"
                            class="mb-2 mr-sm-2 mb-sm-0"
                            placeholder="enter a directory name"
                            v-model="form.dirName"
                        ></b-input>
                        <br>
                        <br>
                        <b-button type="submit">
                            Submit
                        <b-icon icon="Hammer" aria-hidden="true"></b-icon>
                </b-button>
                </b-form>
    </b-col>
  </b-row>
</b-container>
  </div>
</template>

<script>
import { API } from 'aws-amplify';

export default {
  name: 'upload',
  props: ['nav'],
  computed: {
    path: function () {
      return this.nav[this.nav.length - 1].to.query.path
    }
  },
  mounted: function () {
    this.urlLoaded = true
  },
  data () {
    return {
      urlLoaded: false,
      form: {
        dirName: ''
      }
    }
  },
  methods: {
    async createDirectory (name, path) {
          const params = {

              queryStringParameters: {
                path: path,
                name: name
              }
         }
          try {
              let response = await API.post('fileManagerApi', '/api/objects/' + this.$route.params.id + '/dir', params)
              alert(JSON.stringify(response))
          }
          catch (error) {
              alert('Unable to create directory, check api logs')
              console.log(error)
          }
      },
    onSubmit(evt) {
        evt.preventDefault()
        this.createDirectory(this.form.dirName, this.path)
      }
  }
}


</script>



<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>


</style>
