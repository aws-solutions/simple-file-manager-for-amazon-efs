<template>
  <div>
    <div class="row border-top">
      <div class="table-responsive">
        <table class="table table-striped table-hover">
          <thead>
            <tr>
              <th scope="col">Name</th>
              <th scope="col">Managed</th>
              <th scope="col">File System ID</th>
              <th scope="col">Licecycle State</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in filesystems" :key="index">
              <td>
                <p>{{ item.name }}</p>
              </td>
              <td>
                <div v-if="item.managed === true">
                  <a
                    :href="`/details/${item.file_system_id}`"
                    data-bs-toggle="tooltip"
                    data-placement="top"
                    title="Click to unregister file system."
                    >{{ item.managed }}</a
                  >
                </div>
                <div v-else-if="item.managed === 'Deleting'">
                  <a
                    href="/"
                    data-bs-toggle="tooltip"
                    data-placement="top"
                    title="Stack deletion can take several minutes. Click to refresh."
                    >{{ item.managed }}</a
                  >
                </div>
                <div v-else-if="item.managed === 'Creating'">
                  <a
                    href="/"
                    data-bs-toggle="tooltip"
                    data-placement="top"
                    title="Stack creation can take several minutes. Click to refresh."
                    >{{ item.managed }}</a
                  >
                </div>
                <div v-else>
                  <a
                    :href="`/configure/${item.file_system_id}`"
                    data-bs-toggle="tooltip"
                    data-placement="top"
                    title="Click to onboard file system."
                    >{{ item.managed }}</a
                  >
                </div>
              </td>
              <td>
                <div v-if="item.managed === true">
                  <a :href="`/filesystem/${item.file_system_id}`">{{
                    item.file_system_id
                  }}</a>
                </div>
                <div v-else>
                  <p>{{ item.file_system_id }}</p>
                </div>
              </td>
              <td>
                <p>{{ item.lifecycle_state }}</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-if="noFileSystemsFound">
      <p>
        No Amazon EFS file systems found. Please create an EFS filesystem in the
        <a href="https://console.aws.amazon.com/efs/home/file-systems"
          >AWS console</a
        >
      </p>
    </div>
    <div id="moreFilesystemsBtn" v-if="paginationToken != null">
      <button class="btn btn-secondary" @click="listFilesystems()">More</button>
    </div>
  </div>
</template>

<script>
import { API } from "aws-amplify";
import { Tooltip } from "bootstrap";

export default {
  name: "filesystems",
  data() {
    return {
      filesystems: [],
      noFileSystemsFound: false,
      paginationToken: null,
    };
  },
  mounted: function () {
    this.listFilesystems();
  },
  updated: function () {
    var tooltipTriggerList = [].slice.call(
      document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.map((tooltipTriggerEl) => {
      new Tooltip(tooltipTriggerEl);
    });
  },
  methods: {
    async listFilesystems() {
      let apiPath = "";
      if (this.paginationToken == null) {
        apiPath = "/api/filesystems/";
      } else {
        apiPath = "/api/filesystems/?cursor=" + this.paginationToken;
      }

      try {
        let response = await API.get("fileManagerApi", apiPath);
        let filesystems = response.filesystems;
        if (filesystems.length == 0) {
          this.noFileSystemsFound = true;
        } else {
          filesystems.forEach((filesystem) =>
            this.filesystems.push(filesystem)
          );
        }

        if ("paginationToken" in response) {
          this.paginationToken = response.paginationToken;
        } else {
          this.paginationToken = null;
        }
      } catch (error) {
        alert("Unable to list filesystems, check api logs");
        console.log(error);
      }
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
#moreFilesystemsBtn {
  float: right;
}
</style>
