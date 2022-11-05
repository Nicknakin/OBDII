<template>
  <div>
    <!-- Static sidebar for desktop -->
    <SideBar active="Dashboard" />
    <!-- This is the dashboard -->
    <div class="flex flex-1 flex-col md:pl-64">
      <main>
        <div class="py-6">
          <div class="mx-auto max-w-7xl px-4 sm:px-6 md:px-8">
            <h1 class="text-2xl font-semibold text-gray-900">Dashboard</h1>
          </div>
          <div class="mx-auto max-w-7xl px-4 sm:px-6 md:px-8">
            <!-- Replace with your content -->
              <div v-for="diagnostic in diagnostics" :key="diagnostic[0]" class="diagnostic">
                <p> {{ diagnostic[0] }} </p>
                <p> {{ diagnostic[1] }} </p>
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
    name: "DashBoard",
    data() {
      return {
        diagnostics: [],
      };
    },
    created(){
      console.log(`${location.protocol}//${location.host}/api/full-dump`);
      fetch(`${location.protocol}//${location.host}/api/full-dump`)
      .then(response => response.json())
      .then(data => {
        data.diagnostics.forEach(diagnostic => this.diagnostics.push(diagnostic));
        console.log("I got some data!". data);
      });
    }
  };
</script>
