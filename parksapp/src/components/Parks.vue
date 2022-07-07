<template>
  <div class="container">
    <h3>Parks:</h3>
    <table class="table">
      <thead>
        <tr>
          <th scope="col"></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="weekend in weekends" v-bind:key="weekend.start_date"> 
          <th scope="row">{{weekend.start_date}}<br>{{weekend.end_date}}</th>
          <td>
            <table>
                <tr v-for="park in weekend.parks" v-bind:key="park.name">
                    <td>{{park.name}}</td>
                    <td>
                        <table>
                            <tr v-for="camp in park.campgrounds" v-bind:key="camp.name">
                                <td><a target="_blank" :href="camp.url">{{camp.name}}</a></td>
                                <td><b>{{camp.spots.length}}</b> spot(s) available</td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
          </td>
        </tr>
      </tbody>
    </table> 
  </div> 
</template>


<script>
  import axios from 'axios';  export default {
    name: 'Parks',
    data() {
      return {
        weekends: null,
      }
    },
    mounted() {
        this.apiCall();
        this.intervalFetchData();
    },
    methods: {
        intervalFetchData: function () {
            setInterval(() => {    
                this.apiCall();
            }, 1000 * 60 * 2);    
        },
        apiCall: function() {
            axios
                .get('https://cheusov.ca/parks/api')
                .then(res => {this.weekends = res.data;})
                .catch(error => console.log(error))
        },
    }
}
</script>

<style>
  h3 {
    margin-bottom: 5%;
  }
</style>


