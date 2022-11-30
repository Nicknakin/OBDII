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
              <table class="mx-auto h-full bg-gray-700 table-auto rounded-xl" id="History Table">
                <thead>
                  <tr >
                    <th class="text-neutral-50 font-semibold text-1xl" v-for = "header in fields" :key='header'>{{headers[header]}}</th>
                  </tr>
                </thead>
                <tbody class="bg-gray-300">
                  <tr v-for = "(row, index) in history" :key='row.time'> 
                    <td :class="index%2==1? 'bg-gray-200':'bg-gray-300' + ' px-1'" v-for="field in fields" :key='field'>
                    <div v-if="typeof(row[field]) != 'object' || row[field] == null">{{row[field]}}</div>
                    <div class="text-xs" v-if="typeof(row[field]) == 'object' && row[field]">
                      <table class="table-auto">
                        <thead>
                          <tr>
                            <th class="" v-for="entry in Object.entries(row[field])" :key="entry">
                            <div v-if="entry[1]">{{ entry[0] }}</div>
                          </th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr>
                            <td v-for="entry in Object.entries(row[field])" :key="entry">{{ entry[1] }}</td>
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
        headers: {"endpoint":"Endpoint", "response":"Response", "requestTime":"Request Time", "responseTime":"Response Time"},
        fields: ["endpoint", "response", "requestTime", "responseTime"],
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

