<template>
  <div>
    <SideBar active='Send A Custom Query' />
    <div class="flex flex-1 flex-col md:pl-64">
      <main>
        <div class="min-h-screen py-6 h-screen bg-gray-900">
          <div class="mx-auto max-w-7xl px-4 sm:px-6 md:px-8">
            <h1 class="text-2xl font-semibold text-gray-50">Send a Query</h1>
          </div>
          <div class="mx-auto max-w-7xl px-4 sm:px-6 md:px-8">
            <!-- Search bar goes here -->
            <div class="py-4">
            <!-- Response is parsed and populates this region -->
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
    created(){
      //TODO Send get request on /supported-pids endpoint
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
