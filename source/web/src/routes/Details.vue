<template>
  <div>
    <div class="container bv-example-row bv-example-row-flex-cols">
      <h1>Filesystem: {{ $route.params.id }}</h1>
      <div v-if="processing">
        <div class="spinner-border">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <div v-else>
        <p>Remove Simple File Manager Resources?</p>
        <button class="btn btn-danger" @click="deleteFileManager">
          Delete
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { API } from "aws-amplify";

export default {
  name: "Details",
  data() {
    return {
      processing: false,
    };
  },
  methods: {
    async deleteFileManager() {
      try {
        this.processing = true;
        await API.del(
          "fileManagerApi",
          "/api/filesystems/" + this.$route.params.id + "/lambda"
        );
        this.processing = false;
        this.$router.push({ name: "home" });
      } catch (error) {
        alert("Unable to delete filesystem manager resources, check api logs");
        this.processing = false;
      }
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped></style>
