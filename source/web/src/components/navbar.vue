<template>
  <nav class="navbar navbar-dark bg-info navbar-expand">
    <div class="container-fluid">
      <a class="navbar-brand" href="/">Simple File Manager</a>

      <div class="d-flex ms-auto">
        <amplify-sign-out v-if="signedIn" class="signout"></amplify-sign-out>
      </div>
    </div>
  </nav>
</template>

<script>
import { AmplifyEventBus } from "aws-amplify-vue";
export default {
  name: "navbar",
  data() {
    return {
      signedIn: false,
      username: null,
    };
  },
  async beforeCreate() {
    try {
      let userData = await this.$Amplify.Auth.currentAuthenticatedUser();
      this.username = userData.username;
      this.signedIn = true;
    } catch (err) {
      this.signedIn = false;
    }
    AmplifyEventBus.$on("authState", (info) => {
      this.signedIn = info === "signedIn";
    });
  },
  async mounted() {
    AmplifyEventBus.$on("authState", (info) => {
      this.signedIn = info === "signedOut";
      this.$router.push({ name: "login" });
    });
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.signout {
  padding-top: 11px;
  display: inline-block;
}
</style>
