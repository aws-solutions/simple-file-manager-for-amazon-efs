<template>
  <div>
    <b-container fluid>
        <b-row align-h="center">
            <b-col md="auto">
                <amplify-authenticator :authConfig="{ signInConfig: { isSignUpDisplayed: false } }" />
            </b-col>
        </b-row>
    </b-container>
  </div>
</template>

<script>

import { AmplifyEventBus } from "aws-amplify-vue";
export default {
  name: "Login",
  data() {
    return {};
  },
  mounted() {
    AmplifyEventBus.$on("authState", eventInfo => {
      if (eventInfo === "signedIn") {
        this.$router.push({ name: "home" });
      } else if (eventInfo === "signedOut") {
        this.$router.push({ name: "login" });
      }
    });
  },
  created() {
    this.getLoginStatus()
  },
  methods: {
    getLoginStatus () {
      this.$Amplify.Auth.currentSession().then(data => {
        this.session = data;
        if (this.session == null) {
          console.log('user must login')
        } else {
          this.$router.push({name: "home"})
        }
      })
    }
  }
};
</script>

<style scoped>
</style>