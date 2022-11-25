<template>
  <div>
    <!-- Static sidebar for desktop -->
    <SideBar active='View Database Query History' />
    <!-- This is the dashboard -->
    <div class="flex flex-1 flex-col md:pl-64">
      <main>
        <div class="py-6 h-screen bg-gray-900">
          <div class="mx-auto max-w-7xl px-4 sm:px-6 md:px-8">
            <h1 class="text-2xl font-semibold text-gray-50">History</h1>
          </div>
          <div class="mx-auto max-w-7xl px-4 sm:px-6 md:px-8">
            <!-- Replace with your content -->
            <!-- Throw up a little table here -->
            <!-- Maybe include some buttons here too to configure the number of elements in the table, or add a pages functionality -->
            <div class="py-4">
              <!-- Generate elements of the table using the history list -->
              <div class="h-96 rounded-lg border-4 border-dashed border-gray-200" />
            </div>
            <!-- /End replace -->
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
        //List to generate history elements out of
        history: [],
        //Object to store search parameters 
        searchSettings: {
          count: 100,
          start: 0,
          //TODO implement some cooler search settings like a filter!
        },
      };
    },
    created(){
      //TODO Send get request on /history endpoint
      //TODO then populate history list
    },
    methods: {
      //Function that is called when query is sent
      sendQuery() {
        //TODO Get the search settings (ie count and start position)

        //TODO Form request to /history

        //TODO Handle response and populate history list

      },
    },
  };
</script>

