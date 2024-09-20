<template>
  <div>
    <div
      v-if="showAlert"
      :class="[
        'alert',
        `alert-${alertType}`,
        'alert-dismissible',
        'fade',
        { show: showAlert },
      ]"
      role="alert"
    >
      {{ alertMessage }}
      <button
        type="button"
        class="btn-close"
        aria-label="Close"
        @click="showAlert = false"
      ></button>
    </div>
    <div class="container-fluid d-flex flex-column ps-3 pe-3 bv-example-row">
      <br />
      <h2 id="title">Filesystem {{ $route.params.id }}</h2>
      <br />
      <div class="row">
        <div class="col" id="navigation">
          <div class="card mr-3 p-3 ml-3">
            <div class="row">
              <div class="col-7">
                <h3>Navigation</h3>
              </div>
              <div class="col"></div>
              <div class="col">
                <button
                  type="button"
                  class="btn btn-link mb-2 dirBtn"
                  data-bs-toggle="modal"
                  data-bs-target="#create-dir"
                >
                  Create directory
                  <i class="bi bi-folder-plus"></i>
                </button>
                <div class="modal fade" id="create-dir">
                  <div class="modal-dialog">
                    <div class="modal-content">
                      <div class="modal-header">
                        <h5 class="modal-title" id="dirModalLabel">
                          Create Directory
                        </h5>
                        <button
                          type="button"
                          id="closeCreateDirModal"
                          class="btn-close"
                          data-bs-dismiss="modal"
                          aria-label="Close"
                        ></button>
                      </div>
                      <div class="modal-body">
                        <!-- Your component or content goes here -->
                        <makedir
                          @dirCreated="refresh"
                          v-bind:nav="navObjects"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="row">
              <nav aria-label="breadcrumb">
                <ol
                  class="breadcrumb p-2"
                  style="background-color: #e9ecef; border-radius: 0.25rem"
                >
                  <li
                    v-for="(item, index) in navObjects"
                    :key="index"
                    class="breadcrumb-item"
                    :class="{ active: index === navObjects.length - 1 }"
                  >
                    <!-- Make only non-active items clickable -->
                    <a
                      v-if="index !== navObjects.length - 1"
                      href="#"
                      @click.prevent="navigateBack(item)"
                    >
                      {{ item.text }}
                    </a>
                    <!-- Active item, no link -->
                    <span v-else>{{ item.text }}</span>
                  </li>
                </ol>
              </nav>
            </div>
            <table class="table table-striped table-hover">
              <thead>
                <tr>
                  <th class="border-top">Directory</th>
                </tr>
              </thead>
              <tbody>
                <!-- Dynamically generate rows for each directory -->
                <tr v-for="(item, index) in dirs" :key="index">
                  <td>
                    <button
                      @click="addDirectoryObject(item.Directory)"
                      class="btn btn-link"
                    >
                      {{ item.Directory }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="col" id="files">
          <div class="card mr-3 p-3">
            <div class="row">
              <!-- Title Section -->
              <div class="col-10">
                <h3>Files</h3>
              </div>

              <!-- Upload Button Section -->
              <div class="col align-self-end">
                <button
                  type="button"
                  class="btn btn-link mb-2 uploadBtn"
                  data-bs-toggle="modal"
                  data-bs-target="#upload-modal"
                >
                  Upload file
                  <i class="bi bi-box-arrow-up" aria-hidden="true"></i>
                </button>

                <!-- Upload Modal -->
                <div class="modal fade" id="upload-modal" aria-hidden="true">
                  <div class="modal-dialog">
                    <div class="modal-content">
                      <div class="modal-header">
                        <h5 class="modal-title" id="uploadModalLabel">
                          Upload File
                        </h5>
                        <button
                          type="button"
                          id="closeUploadModal"
                          class="btn-close"
                          data-bs-dismiss="modal"
                          aria-label="Close"
                        ></button>
                      </div>
                      <div class="modal-body">
                        <upload
                          @uploadStarted="operationStart"
                          @uploadCompleted="refresh"
                          :nav="navObjects"
                          :files="files"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Files Table -->
            <div class="table-responsive">
              <table class="table table-striped table-hover">
                <thead>
                  <tr>
                    <th scope="col">Name</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(file, index) in files" :key="index">
                    <td>
                      <div class="row">
                        <div class="col-10">
                          {{ file.Name }}
                        </div>
                        <!-- Delete Button -->
                        <div class="col">
                          <a
                            href="#"
                            @click="deleteFile(file.Name)"
                            class="text-danger"
                          >
                            <i class="bi bi-trash"></i>
                          </a>
                        </div>
                        <!-- Download Button -->
                        <div class="col">
                          <a
                            href="#"
                            @click="startDownload(file.Name)"
                            data-bs-toggle="modal"
                            data-bs-target="#download-modal"
                            class="text-primary"
                          >
                            <i class="bi bi-arrow-down downloadIcon"></i>
                          </a>
                        </div>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Download Modal -->
            <div
              class="modal fade"
              id="download-modal"
              tabindex="-1"
              aria-hidden="true"
            >
              <div class="modal-dialog">
                <div class="modal-content">
                  <div class="modal-header" style="display: none">
                    <button
                      type="button"
                      style="display: none"
                      id="closeDownloadModal"
                      class="btn-close"
                      data-bs-dismiss="modal"
                      aria-label="Close"
                    ></button>
                  </div>
                  <!-- Modal body -->
                  <div class="modal-body">
                    <download
                      ref="downloadModal"
                      @downloadStarted="operationStart"
                      @downloadCompleted="refresh"
                      :nav="navObjects"
                      :filename="filename"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { API } from "aws-amplify";
import download from "../components/download.vue";
import upload from "../components/upload.vue";
import makedir from "../components/makedir.vue";
// eslint-disable-next-line no-unused-vars
import { Modal } from "bootstrap";

export default {
  name: "Filesystem",
  components: {
    upload,
    makedir,
    download,
  },
  data() {
    return {
      active: false,
      editEnabled: false,
      filename: null,
      files: [],
      dirs: [],
      navObjects: [
        {
          text: "/mnt/efs",
          to: { name: "filesystem", query: { path: "/mnt/efs" } },
          active: true,
        },
      ],
      showAlert: false,
      alertMessage: null,
      alertType: null,
    };
  },
  mounted: function () {
    this.retrieveObjects();
  },
  methods: {
    operationStart() {
      this.active = true;
    },
    refresh(response) {
      this.dirs = [];
      this.files = [];
      this.retrieveObjects();
      document.getElementById("closeCreateDirModal").click();
      document.getElementById("closeUploadModal").click();
      document.getElementById("closeDownloadModal").click();
      this.active = false;
      this.alertMessage = response.message;
      this.alertType = response.type;
      this.showAlert = true;
    },
    navigateBack() {
      if (this.navObjects.length > 1) {
        this.navObjects.pop();
        this.navObjects[this.navObjects.length - 1].active = true;
        this.dirs = [];
        this.files = [];
        this.retrieveObjects();
      }
    },
    listObjects(objects) {
      let files = objects.files;
      this.files = [];
      for (var file = 0, fileLen = files.length; file < fileLen; file++) {
        let tmp_item = { Name: files[file] };
        this.files.push(tmp_item);
      }
      // todo: need to fix this typo in the api response
      let directories = objects.directiories;
      this.directories = [];
      for (var dir = 0, dirLen = directories.length; dir < dirLen; dir++) {
        let tmp_item = { Directory: directories[dir] };
        this.dirs.push(tmp_item);
      }
    },
    startDownload(filename) {
      this.filename = filename;
      this.$refs.downloadModal.downloadFile(filename);
      this.$refs.downloadModal.resetModal();
    },
    async deleteFile(name) {
      let requestParams = {
        queryStringParameters: {
          path: this.navObjects[this.navObjects.length - 1].to.query.path,
          name: name,
        },
      };
      let formattedResponse = { type: "", message: "" };
      try {
        let response = await API.del(
          "fileManagerApi",
          "/api/objects/" + this.$route.params.id,
          requestParams
        );
        if (response.statusCode != 200) {
          formattedResponse.type = "danger";
          formattedResponse.message =
            "File was unable to be deleted successfully. Check API logs.";
        } else {
          formattedResponse.type = "success";
          formattedResponse.message = "File deleted successfully!";
        }
      } catch (error) {
        formattedResponse.type = "danger";
        formattedResponse.message =
          "File was unable to be deleted successfully. Check API logs.";
      }
      this.refresh(formattedResponse);
    },
    addDirectoryObject(directory) {
      this.navObjects[this.navObjects.length - 1].active = false;
      let existingPath =
        this.navObjects[this.navObjects.length - 1].to.query.path;
      let newPath = existingPath + "/" + directory;
      console.log(newPath);
      let newDirObject = {
        text: directory,
        to: { name: "filesystem", query: { path: newPath } },
        active: true,
      };
      this.navObjects.push(newDirObject);
      this.dirs = [];
      this.files = [];
      this.retrieveObjects();
    },

    async retrieveObjects() {
      //let activeDirectory = this.objects[this.objects - 1]
      //console.log(path)
      let requestParams = {
        queryStringParameters: {
          path: this.navObjects[this.navObjects.length - 1].to.query.path,
        },
      };
      try {
        let response = await API.get(
          "fileManagerApi",
          "/api/objects/" + this.$route.params.id,
          requestParams
        );
        this.listObjects(response);
      } catch (error) {
        let formattedResponse = {
          type: "danger",
          message: "Unable to list filesystem objects. Check API logs.",
        };
        this.refresh(formattedResponse);
      }
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
#navigation,
#files {
  padding-left: 1.5%;
  padding-right: 1.5%;
  padding-bottom: 2%;
}

#title {
  padding-left: 2%;
}

button {
  padding-top: 2%;
}

.downloadIcon {
  color: #ff9900 !important;
}

.uploadBtn {
  color: #ff9900 !important;
}

.dirBtn {
  color: #ff9900 !important;
}
</style>
