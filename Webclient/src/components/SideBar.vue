<template>
    <!-- Static sidebar for desktop -->
    <div class="md:fixed md:inset-y-0 md:flex md:flex-col">
      <!-- Sidebar component, swap this element with another sidebar if you like -->
      <div class="flex flex-grow flex-col bg-gray-700 pt-5">
        <div class="flex flex-shrink-0 items-center px-4">
          <img class="h-16 w-auto m-auto" src="@/assets/Debuggy-logos_white.png" alt="Debuggy" />
        </div>
        <div class="mt-5 flex flex-1 flex-col">
          <nav class="flex-1 space-y-1 px-2 pb-4">
            <router-link v-for="item in navigation" :key="item.name" :to="item.href" 
            :class="[item.current ? 'bg-gray-800 text-white' : 'text-gray-100 hover:bg-gray-600', 'group flex items-center px-2 py-2 text-sm font-medium rounded-md']">
              <component :is="item.icon" class="mr-3 h-6 w-6 flex-shrink-0 text-gray-300" aria-hidden="true" />
              {{ item.name }}
            </router-link>
          </nav>
        </div>
      </div>
    </div>
</template>

<script setup>
import { CodeIcon, DatabaseIcon, HomeIcon } from "@heroicons/vue/outline";

const navigation = [
  { name: "Dashboard", href: "/", icon: HomeIcon, current: false },
  { name: "Send A Custom Query", href: "/query", icon: CodeIcon, current: false },
  { name: "View Database Query History", href: "/history?count=100&start=1", icon: DatabaseIcon, current: false },
]
</script>

<script>
export default {
  name:"SideBar",
  props: {
    active: {
        type: String,
        required: true,
    },
  },
  created() {
    for(let i = 0; i < this.navigation.length; i++){
        if(this.navigation[i].name === this.active){
            this.navigation[i].current = true;
            break;
        }
    }
  },
}
</script>
