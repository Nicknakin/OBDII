<template>
  <div>
    <!-- Static sidebar for desktop -->
    <SideBar active='View Database Query History' />
    <!-- This is the dashboard -->
    <div class="flex flex-1 flex-col md:pl-64">
      <main>
        <div class="min-h-screen py-6 h-screen bg-gray-900">
          <div class="mx-auto max-w-7xl px-4 sm:px-6 md:px-8">
            <h1 class="text-2xl font-semibold text-gray-50">History</h1>
          </div>
          <div class="bg-gray-900 mx-auto max-w-7xl px-4 sm:px-6 md:px-8">
            <!-- Replace with your content -->
            <!-- Throw up a little table here -->
            
            <!-- Maybe include some buttons here too to configure the number of elements in the table, or add a pages functionality -->

            <div class="py-4">
              <table class="table-auto border border-white border-collapse" id="History Table">
                <thead>
                  <tr >
                    <th class="border text-neutral-50 " v-for = "header in headers" :key='header'>{{header}}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for = "row in history" :key='row.time'> 
                    <td class="border px-1 text-neutral-50 " v-for="field in headers" :key='field'>
                    <div v-if="typeof(row[field]) != 'object' || row[field] == null">{{row[field]}}</div>
                    <div class="text-xs" v-if="typeof(row[field]) == 'object' && row[field]">
                      <table class="table-auto">
                        <thead>
                          <tr>
                            <th class="border text-neutral-50" v-for="entry in Object.entries(row[field])" :key="entry">{{ entry[0] }}</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr>
                            <td class="border" v-for="entry in Object.entries(row[field])" :key="entry">{{ entry[1] }}</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                    </td>
                  </tr>
                </tbody>
              </table>
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
        //List to generate history elements out of
        history: [],
        headers: ["endpoint", "response", "requestTime", "responseTime"],
        //Object to store search parameters 
        searchSettings: {
          count: 100,
          start: 0,
          //TODO implement some cooler search settings like a filter!
        },
      };
    },
    created(){
      fetch(`${location.protocol}//${location.host}/api/history`)
      .then(response => response.json())
      .then(data => {
        this.history = data.rows;
      });
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

