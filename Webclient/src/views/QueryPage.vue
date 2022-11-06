<template>
  <div>
    <!-- Static sidebar for desktop -->
    <SideBar active='Send A Custom Query' />
    <!-- This is the dashboard -->
    <div class="flex flex-1 flex-col md:pl-64">
      <main>
        <div class="py-6 h-screen bg-gray-900">
          <div class="mx-auto max-w-7xl px-4 sm:px-6 md:px-8">
            <h1 class="text-2xl font-semibold text-gray-50">Send a Query</h1>
          </div>
          <div class="mx-auto max-w-7xl px-4 sm:px-6 md:px-8">
            <!-- Replace with your content -->
            <div class="py-4">
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
