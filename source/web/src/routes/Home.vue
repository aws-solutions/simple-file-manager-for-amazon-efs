<template>
  <div>
    <div class="container-fluid bv-example-row">
      <div class="row">
        <div class="col">
          <br />
          <div class="card ml-3 p-3">
            <h2>Filesystems</h2>
            <filesystems />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import filesystems from "../components/filesystems.vue";

export default {
  name: "Home",
  components: {
    filesystems,
  },
  data() {
    return {};
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped></style>
