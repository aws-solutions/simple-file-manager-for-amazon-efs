<template>
  <div id="app">
    <navbar />
    <router-view />
  </div>
</template>

<script>
import navbar from "./components/navbar.vue";

export default {
  name: "App",
  components: {
    navbar,
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.navbar.navbar-dark.bg-info.navbar-expand {
  background-color: #232f3e !important;
}

a,
button {
  text-decoration: none !important;
}

a:hover,
button:hover {
  text-decoration: underline !important;
}
</style>
