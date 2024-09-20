<template>
  <div>
    <div class="container h-100">
      <div class="row h-100 justify-content-center align-items-center">
        <div class="col-md-6 text-center">
          <amplify-authenticator
            :authConfig="{ signInConfig: { isSignUpDisplayed: false } }"
          />
        </div>
      </div>
    </div>
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
    AmplifyEventBus.$on("authState", (eventInfo) => {
      if (eventInfo === "signedIn") {
        this.$router.push({ name: "home" });
      } else if (eventInfo === "signedOut") {
        this.$router.push({ name: "login" });
      }
    });
  },
  created() {
    this.getLoginStatus();
  },
  methods: {
    getLoginStatus() {
      this.$Amplify.Auth.currentSession().then((data) => {
        this.session = data;
        if (this.session == null) {
          console.log("user must login");
        } else {
          this.$router.push({ name: "home" });
        }
      });
    },
  },
};
</script>

<style scoped></style>
