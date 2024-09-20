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
        <div class="row">
          <div class="col align-self-center">
            <form @submit="onSubmit" class="needs-validation" novalidate>
              <h3>Create file manager lambda</h3>
              <div class="mb-3">
                <label for="inputUid" class="form-label">User ID:</label>
                <input
                  type="text"
                  class="form-control"
                  id="inputUid"
                  v-model="uid"
                  :class="{ 'is-invalid': !valid, 'is-valid': valid }"
                  placeholder="Enter a custom UID or leave default (1000)"
                />
                <div class="form-text">
                  The numeric POSIX user ID that lambda will use to make file
                  system requests as
                </div>
              </div>

              <div class="mb-3">
                <label for="inputGid" class="form-label">Group ID:</label>
                <input
                  type="text"
                  class="form-control"
                  id="inputGid"
                  v-model="gid"
                  :class="{ 'is-invalid': !valid, 'is-valid': valid }"
                  placeholder="Enter a custom GID or leave default (1000)"
                />
                <div class="form-text">
                  The numeric POSIX group ID that lambda will use to make file
                  system requests as
                </div>
              </div>

              <div class="mb-3">
                <label for="inputPath" class="form-label">Path:</label>
                <input
                  type="text"
                  class="form-control"
                  id="inputPath"
                  v-model="path"
                  :class="{ 'is-invalid': !valid, 'is-valid': valid }"
                  placeholder="Enter a custom path or leave default (/efs)"
                />
                <div class="form-text">
                  The file system directory that lambda will use as the root
                  directory
                </div>
              </div>

              <div class="invalid-feedback" v-if="!valid">
                UID, GID, and Path must not be empty. The path must begin with a
                forward slash: /
              </div>
              <div v-if="!mountTargetNetinfo">
                <div class="spinner-border">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              <div v-else-if="!mountTargetNetinfo.securityGroups.length">
                <div class="alert alert-danger" role="alert">
                  No mount targets available for the filesystem with security
                  group(s) configured for NFS access. See the deployment guide
                  for further details.
                </div>
              </div>
              <div v-else>
                <button
                  :disabled="!valid"
                  type="submit"
                  class="btn btn-secondary"
                >
                  Submit
                  <i class="b-icon bi bi-hammer"></i>
                </button>
              </div>
            </form>
          </div>
          <div class="col"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { API } from "aws-amplify";

export default {
  name: "Configure",
  data() {
    return {
      processing: false,
      uid: "1000",
      gid: "1000",
      path: "/efs",
      mountTargetNetinfo: null,
    };
  },
  computed: {
    valid() {
      return (
        this.uid != "" &&
        this.gid != "" &&
        this.path != "" &&
        this.path.charAt(0) == "/"
      );
    },
  },
  mounted: function () {
    this.getFilesystemNetinfo();
  },
  methods: {
    async onSubmit(evt) {
      evt.preventDefault();

      if (this.valid) {
        let mountTargetNetinfo = this.mountTargetNetinfo;

        mountTargetNetinfo["uid"] = this.uid;
        mountTargetNetinfo["gid"] = this.gid;
        mountTargetNetinfo["path"] = this.path;

        this.createManagerLambda(mountTargetNetinfo);
      } else {
        alert("Form Validation Error. Check the form input and try again.");
      }
    },
    formatNetinfo(netinfo) {
      let subnets = [];
      let securityGroups = [];

      for (var i = 0, n = netinfo.length; i < n; ++i) {
        let mountTarget = Object.keys(netinfo[i])[0];
        let subnet = netinfo[i][mountTarget]["subnet_id"];
        let securityGroup = netinfo[i][mountTarget]["security_groups"];

        subnets.push(subnet);
        securityGroups.push.apply(securityGroups, securityGroup);
      }

      let uniqSecurityGroups = [...new Set(securityGroups)];

      if (uniqSecurityGroups.length > 5) {
        uniqSecurityGroups = uniqSecurityGroups.slice(0, 4);
      }

      if (subnets.length > 5) {
        subnets = subnets.slice(0, 4);
      }

      let tmpNetinfo = {
        subnetIds: subnets,
        securityGroups: uniqSecurityGroups,
      };

      return tmpNetinfo;
    },
    async getFilesystemNetinfo() {
      try {
        let response = await API.get(
          "fileManagerApi",
          "/api/filesystems/" + this.$route.params.id + "/netinfo"
        );
        let formattedNetinfo = this.formatNetinfo(response);
        this.mountTargetNetinfo = formattedNetinfo;
      } catch (error) {
        alert("Unable to retrieve filesystem netinfo, check api logs");
      }
    },
    async createManagerLambda(netinfo) {
      const params = {
        body: {
          subnetIds: netinfo.subnetIds,
          securityGroups: netinfo.securityGroups,
          uid: netinfo.uid,
          gid: netinfo.gid,
          path: netinfo.path,
        },
        headers: { "Content-Type": "application/json" },
      };
      try {
        this.processing = true;
        await API.post(
          "fileManagerApi",
          "/api/filesystems/" + this.$route.params.id + "/lambda",
          params
        );
        this.processing = false;
        this.$router.push({ name: "home" });
      } catch (error) {
        alert("Unable to create filesystem lambda, check api logs");
        this.processing = false;
      }
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped></style>
