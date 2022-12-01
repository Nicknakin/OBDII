<template>
  <div>
    <!-- Static sidebar for desktop -->
    <SideBar active='View Database Query History' />
    <!-- This is the dashboard -->
    <div class="bg-gray-900 flex flex-1 flex-col md:pl-64">
      <main class="w-full">
        <div class="min-h-screen py-6 h-screen bg-gray-900">
          <div class="mx-auto max-w-7xl px-4 sm:px-6 md:px-8">
            <h1 class="text-2xl font-semibold text-gray-50">History</h1>
          </div>
          <div class="bg-gray-900 w-full mx-auto max-w-7xl px-4 sm:px-6 md:px-8">
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
                    <td :class="(index%2==1? 'bg-gray-200':'bg-gray-300') + ' px-1'" v-for="field in fields" :key='field'>
                    <div v-if="typeof(row[field]) != 'object' || row[field] == null">{{row[field]}}</div>
                    <div class="text-xs" v-if="typeof(row[field]) == 'object' && row[field]">
                      <JsonModal :data="row[field]"/>
                      <div class="cursor-pointer bg-gray-700 hover:bg-gray-500 text-white font-bold m-2 py-1 px-1 rounded" @click="openModal">View More</div>
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

<style>
  html {
    --tw-bg-opacity: 1;
    background-color: rgb(17 24 39 / var(--tw-bg-opacity)) !important;
  }
</style>

<script setup>
import SideBar from "@/components/SideBar.vue";
import JsonModal from "@/components/JsonModal.vue";

</script>

<script>
  export default {
    name: "HistoryPage",
    data() {
      return {
        //List to generate history elements out of
        history: [],
        headers: {"endpoint":"Endpoint", "response":"Response", "requestTime":"Request Time", "responseTime":"Response Time"},
        fields: ["endpoint", "response", "requestTime", "responseTime"],
        //Object to store search parameters 
        searchSettings: {
          count: this.$route.query.count ?? 100,
          start: this.$route.query.start ?? 0,
        },
      };
    },
    created(){
      let headers = new Headers();
      headers.append("Content-Type", "application/json");
      fetch(`${location.protocol}//${location.host}/api/history`, {
        body: JSON.stringify(this.searchSettings),
        method: "POST",
        headers,
      })
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
      openModal(el) {
        el.target.parentElement.children[0].__vueParentComponent.ctx.toggleModal();
      }
    },
  };
</script>

