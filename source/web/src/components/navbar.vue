<template>
  <div>
    <b-navbar type="dark" variant="info">
        <b-navbar-nav>
            <b-navbar-brand class='name' to='/'>Simple File Manager</b-navbar-brand>
        </b-navbar-nav>
        <b-navbar-nav class="ml-auto">
          <amplify-sign-out class="signout" v-if="signedIn"></amplify-sign-out>
        </b-navbar-nav>
    </b-navbar>
  </div>
</template>

<script>
import { AmplifyEventBus } from "aws-amplify-vue";
export default {
  name: 'navbar',
  data() {
    return {
      signedIn: false,
      username: null
    }
  },
  async beforeCreate() {
    try {
      let userData = await this.$Amplify.Auth.currentAuthenticatedUser();
      this.username = userData.username
      this.signedIn = true;
    } catch (err) {
      this.signedIn = false;
    }
    AmplifyEventBus.$on("authState", info => {
      this.signedIn = info === "signedIn";
    });
  },
  async mounted() {
    AmplifyEventBus.$on("authState", info => {
      this.signedIn = info === "signedOut";
      this.$router.push({name: 'login'})
    });
  }
}
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.signout {
  padding-top: 11px;
  display: inline-block;
}
</style>