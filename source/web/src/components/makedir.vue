<template>
  <div>
    <div class="container-fluid bv-example-row">
      <div class="row">
        <div class="col">
          <form @submit="onSubmit" class="row g-3">
            <!-- Bootstrap 5 Input Group -->
            <div class="col-auto">
              <input
                type="text"
                id="inline-form-input-mounttarget"
                class="form-control mb-2"
                placeholder="Enter a directory name"
                v-model="form.dirName"
              />
            </div>

            <!-- Submit Button -->
            <div class="col-auto">
              <button type="submit" class="btn btn-secondary mb-2">
                Submit
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { API } from "aws-amplify";

export default {
  name: "makedir",
  props: ["nav"],
  computed: {
    path: function () {
      return this.nav[this.nav.length - 1].to.query.path;
    },
  },
  mounted: function () {
    this.urlLoaded = true;
  },
  data() {
    return {
      urlLoaded: false,
      form: {
        dirName: "",
      },
    };
  },
  methods: {
    async createDirectory(name, path) {
      let dir_data = { path: path, name: name };
      const params = {
        body: dir_data,
        headers: {
          "Content-Type": "application/json",
        },
      };
      let formattedResponse = { type: "", message: "" };
      try {
        let response = await API.post(
          "fileManagerApi",
          "/api/objects/" + this.$route.params.id + "/dir",
          params
        );
        if (response.statusCode != 200) {
          formattedResponse.type = "danger";
          formattedResponse.message =
            "Could not create directory. Check API logs. ";
        } else {
          formattedResponse.type = "success";
          formattedResponse.message = "Directory created!";
        }
      } catch (error) {
        formattedResponse.type = "danger";
        formattedResponse.message =
          "Could not create directory. Check API logs. ";
      }
      this.$emit("dirCreated", formattedResponse);
    },
    onSubmit(evt) {
      evt.preventDefault();
      this.createDirectory(this.form.dirName, this.path);
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped></style>
