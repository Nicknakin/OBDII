<template>
  <div>
    <SideBar active='Send A Custom Query' />
    <div class="flex flex-1 flex-col md:pl-64">
      <main>
        <div class="py-6 h-screen bg-gray-900">
          <div class="mx-auto max-w-7xl px-4 sm:px-6 md:px-8">
            <h1 class="text-2xl font-semibold text-gray-50">Send a Query</h1>
          </div>
          <div class="mx-auto max-w-7xl px-4 sm:px-6 md:px-8">
            <!-- Search bar goes here -->
            <div class="py-4">
              <h1 style= "text=align: center; margin:0"> Get Query Input</h1>
<input type = "text" placeholder=" Enter the search Query"/>
            <!-- Response is parsed and populates this region -->
              <div class="h-96 rounded-lg border-4 border-dashed border-gray-200" />
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import SideBar from "@/components/SideBar.vue";

</script>

<script>
  export default {
    name: "QueryPage",
    data() {
      return {
        supported_pids: [],
        diagnostics: [],
      };
    },
    //GET request using fetch, will continue to update once changes can be tested
    created(){
      //TODO Send get request on /supported-pids endpoint
      //GET request using fetch, will continue to update once changes can be tested
      fetch(/*"Query Page url"*/)
        .then(async response => {
          const data = await response.json();
          //check for error response
          if (!response.ok){
            //get error message from body or defaut to response statusText
            const error = (data && data.message) || response.statusText;
            return Promise.reject(error);
          }

          this.totalVuePackages = data.total;
        })
        .catch(error => {
          this.errorMessage = error;
          console.error("There was an error!", error);
        });
      //TODO then populate supported_pids list
    },
    methods: {
      //Function that is called when query is sent
      sendQuery() {
        //TODO Get input from input box

        //TODO Form request to /manual-query

        //TODO Handle response and populate diagnostics list

      },
    },
  };
</script>
