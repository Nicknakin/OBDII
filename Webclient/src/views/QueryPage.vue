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
            <div>
              <div class="flex rounded">
                <input @focus="showList = true;" v-on:input="filter" type="text" ref="inputQuery" class="bg-gray-50 border-none outline-none text-gray-900 text-sm
                block w-full p-2.5 rounded-l rounded-b-none" placeholder="Query" required>
                <button
                  class="hover:bg-gray-700 outline-none bg-gray-500 text-white font-bold py-2 px-4 rounded-r rounded-b-none"
                  @click="sendQuery">Send</button>
              </div>
              <ul class="bg-gray-300 select-none max-h-48 overflow-auto rounded-b-xl" v-if="showList">
                <li :class="'hover:bg-gray-400 py-1 px-1 ' + (index % 2 ? 'bg-gray-200' : '')"
                  v-for="(pid, index) in Object.entries(filtered_pids)" :key="pid[0]" @click="fillInput">{{
                      pid[0]
                  }}</li>
              </ul>
            </div>
            <div class="py-4">
              <div class="text-white" v-if="diagnostics.length == 0">
                <span>It appears there's no data yet, try making a query!</span>
              </div>
              <div v-if="loading" class="flex justify-center items-center m-auto">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none"
                  viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                  </path>
                </svg>
              </div>
              <div v-if="diagnostics.length > 0">
                <div v-if="!loading" class="grid grid-cols-4 gap-4">
                  <div class="text-center" v-for="diagnostic in diagnostics" :key="diagnostic[0]">
                    <div class="overflow-hidden rounded-xl ">
                      <ul role="list" class="divide-y divide-gray-700 break-words">
                        <li class="bg-gray-500 p-2"> {{ diagnostic.name }} </li>
                        <li class="bg-gray-400 p-1"> {{ diagnostic.value }} </li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<style>
.autocomplete {
  position: relative;
}

.autocomplete-results {
  padding: 0;
  margin: 0;
  border: 1px solid #eeeeee;
  height: 120px;
  min-height: 1em;
  max-height: 6em;
  overflow: auto;
}

.autocomplete-result {
  list-style: none;
  text-align: left;
  padding: 4px 2px;
  cursor: pointer;
}

.autocomplete-result:hover {
  background-color: #4aae9b;
  color: white;
}
</style>


<script setup>
import SideBar from "@/components/SideBar.vue";
</script>

<script>
export default {
  name: "QueryPage",
  data() {
    return {
      filtered_pids: [],
      supported_pids: [],
      diagnostics: [],
      showList: true,
      loading: false,
    };
  },
  created() {
    fetch(`${location.protocol}//${location.host}/api/supported-pids`)
      .then(response => response.json())
      .then(data => {
        this.supported_pids = data.rows.reduce((acc, val) => {
          acc[val.Description] = { service: val.service, pid: val.pid };
          return acc;
        }, {});
        this.filter();
      });
  },
  methods: {
    //Function that is called when query is sent
    sendQuery() {
      this.showList = false;
      this.loading = true;
      if (!this.supported_pids[this.$refs.inputQuery.value]) return;
      const headers = new Headers();
      headers.append('Content-Type', 'application/json');

      fetch(`${location.protocol}//${location.host}/api/manual-query`, {
        body: JSON.stringify(this.supported_pids[this.$refs.inputQuery.value]),
        method: "POST",
        headers,
      })
        .then(response => response.json())
        .then(data => {
          this.diagnostics = data.diagnostics;
          this.loading = false;
        });
    },
    fillInput(el) {
      this.$refs.inputQuery.value = el.target.innerHTML;
    },
    filter() {
      this.filtered_pids = Object.entries(this.supported_pids)
        .filter(val => val[0].toLowerCase().includes(this.$refs.inputQuery.value.toLowerCase()))
        .reduce((acc, val) => {
          acc[val[0]] = val[1];
          return acc;
        }, {});
    },
  },
};
</script>
