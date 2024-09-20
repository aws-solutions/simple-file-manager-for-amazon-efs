<template>
  <div>
    <div class="container-fluid bv-example-row">
      <div class="row">
        <p>Downloading file: {{ filename }}</p>
        <div class="progress p-0">
          <div
            class="progress-bar"
            style="width: 50%"
            role="progressbar"
            :aria-valuenow="50"
            aria-valuemin="0"
            :aria-valuemax="max"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { API } from "aws-amplify";

export default {
  name: "download",
  props: ["nav", "filename"],
  computed: {
    path: function () {
      return this.nav[this.nav.length - 1].to.query.path;
    },
  },
  data() {
    return {
      href: "data:application/octet-stream;base64,",
      chunkBlobs: [],
      dzchunkindex: null,
      dzchunkbyteoffset: null,
      totalChunks: null,
      max: 95,
      downloadDone: false,
    };
  },
  created: function () {},
  methods: {
    resetModal() {
      this.href = "data:application/octet-stream;base64,";
      this.chunkBlob = [];
      this.dzchunkindex = null;
      this.dzchunkbyteoffset = null;
      this.totalChunks = null;
      this.max = 95;
      this.downloadDone = false;
      var bar = document.querySelector(".progress-bar");
      bar.setAttribute("aria-valuenow", 0);
      bar.style.width = 0 + "%";
    },
    async downloadChunk(requestParams) {
      console.log(requestParams);
      try {
        let response = await API.get(
          "fileManagerApi",
          "/api/objects/" + this.$route.params.id + "/download",
          requestParams
        );
        var progressValue = ((this.dzchunkindex + 1) / this.totalChunks) * 100;
        var bar = document.querySelector(".progress-bar");
        bar.setAttribute("aria-valuenow", progressValue);
        bar.style.width = progressValue + "%";
        return response;
      } catch (error) {
        let formattedResponse = {
          type: "danger",
          message: "Download did not complete successfully. Check API logs.",
        };
        this.$emit("downloadCompleted", formattedResponse);
      }
    },
    async downloadFile(filename) {
      if (this.dzchunkindex == null && this.dzchunkbyteoffset == null) {
        this.$emit("downloadStarted");
        let requestParams = {
          queryStringParameters: {
            path: this.path,
            filename: filename,
          },
        };

        let chunk = await this.downloadChunk(requestParams);

        let offset = chunk.dzchunkbyteoffset;
        let chunkIndex = chunk.dzchunkindex;

        let chunkData = chunk.chunk_data;
        let chunkblob = await (await fetch(this.href + chunkData)).blob();

        this.totalChunks = chunk.dztotalchunkcount;
        this.chunkBlobs[chunkIndex] = chunkblob;

        this.dzchunkindex = chunkIndex;
        this.dzchunkbyteoffset = offset;

        this.downloadFile(filename);
      } else {
        let requestParams = {
          queryStringParameters: {
            path: this.path,
            filename: filename,
            dzchunkindex: this.dzchunkindex,
            dzchunkbyteoffset: this.dzchunkbyteoffset,
          },
        };

        let chunk = await this.downloadChunk(requestParams);

        let offset = chunk.dzchunkbyteoffset;
        let chunkIndex = chunk.dzchunkindex;
        console.log(chunkIndex);
        let totalChunks = chunk.dztotalchunkcount;

        if (chunkIndex == totalChunks) {
          this.downloadDone = true;

          let finalBlob = new Blob(this.chunkBlobs);

          let link = document.createElement("a");

          link.href = window.URL.createObjectURL(finalBlob);
          link.download = filename;

          link.click();

          let formattedResponse = {
            type: "success",
            message: "Download completed successfully!",
          };
          this.$emit("downloadCompleted", formattedResponse);
          this.resetModal();
        } else {
          let chunkData = chunk.chunk_data;

          this.dzchunkindex = chunkIndex;
          this.dzchunkbyteoffset = offset;

          let chunkblob = await (await fetch(this.href + chunkData)).blob();

          this.chunkBlobs[chunkIndex] = chunkblob;

          this.downloadFile(filename);
        }
      }
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
#navigation {
  padding-left: 2%;
}

#title {
  padding-left: 2%;
}

button {
  padding-top: 2%;
}
</style>
