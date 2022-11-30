<template>
  <div>
    <!-- Static sidebar for desktop -->
    <SideBar active="Dashboard" />

    <!-- This is the dashboard -->
    <div class="flex flex-1 flex-col md:pl-64">
      <main>
        <div class="min-h-screen py-6 bg-gray-900" >
          <div class="mx-auto max-w-7xl px-4 sm:px-6 md:px-8">
            <h1 class="text-2xl font-semibold text-neutral-50 ">Dashboard</h1>
          </div>
          <div class="mx-auto max-w-7xl px-4 sm:px-6 md:px-8">
            <!-- This is where we display the diagnostics -->
              <div class="grid grid-cols-4 gap-4">
                <div class="text-center" v-for="diagnostic in diagnostics" :key="diagnostic[0]">
                  <div class="overflow-hidden rounded-xl ">
                    <ul role="list" class="divide-y divide-gray-700 break-words">
                      <li class="bg-gray-500 p-2"> {{ diagnostic.name}} </li>
                      <li class="bg-gray-400 p-1" > {{ diagnostic.value}} </li>
                    </ul>
                  </div>
                </div>
              </div>
            <!-- /End of the diagnostics divs -->
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
    name: "DashBoard",
    data() {
      return {
        diagnostics: [],
      };
    },
    created(){
      //TODO This is working fine, but maybe throw it in to a set interval or something fancy so that the page updates.
      // You could have a refresh button or refactor it to use a websocket connection
      console.log(`${location.protocol}//${location.host}/api/full-dump`);
      fetch(`${location.protocol}//${location.host}/api/full-dump`)
      .then(response => response.json())
      .then(data => {
        this.diagnostics = data.diagnostics;
      });
    }
  };
</script>
