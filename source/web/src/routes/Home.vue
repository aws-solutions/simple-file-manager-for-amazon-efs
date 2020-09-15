<template>
  <div>
  <b-container fluid='true' class="bv-example-row">
  <b-row>
    <b-col>
      <br>
      <b-card class="ml-3">
        <h2>Filesystems</h2>
        <filesystems/>
      </b-card>
    </b-col>
  </b-row>
</b-container>
  </div>
</template>

<script>
import filesystems from '../components/filesystems.vue'

export default {
  name: 'Home',
  components: {
    filesystems
  },
  data () {
    return {
    }
  }
}


</script>



<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>


</style>
