<template>
  <div id="app">
    <Parks api_url="https://cheusov.ca/parks/api" />
  </div>
</template>

<script>
import Parks from './components/Parks.vue'
export default {
  name: 'app',
  components: {
    Parks
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>