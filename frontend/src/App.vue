<template>
  <div class="min-h-screen flex flex-col">
    <!-- Desktop Navigation -->
    <nav class="bg-white shadow-sm border-b border-gray-200 hidden md:block">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex">
            <div class="flex-shrink-0 flex items-center">
              <h1 class="text-2xl font-bold text-primary-600">🌱 Garden Tracker</h1>
            </div>
            <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
              <router-link
                to="/"
                class="nav-link"
                active-class="border-primary-500 text-gray-900"
              >
                Dashboard
              </router-link>
              <router-link
                to="/plants"
                class="nav-link"
                active-class="border-primary-500 text-gray-900"
              >
                Pflanzen
              </router-link>
              <router-link
                to="/tasks"
                class="nav-link"
                active-class="border-primary-500 text-gray-900"
              >
                Aufgaben
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="flex-1 pb-20 md:pb-0">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <router-view />
      </div>
    </main>

    <!-- Mobile Bottom Navigation -->
    <nav class="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg z-50">
      <div class="flex justify-around items-center h-16">
        <router-link
          to="/"
          class="mobile-nav-link"
          active-class="text-primary-600"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          <span class="text-xs mt-1">Dashboard</span>
        </router-link>

        <router-link
          to="/plants"
          class="mobile-nav-link"
          active-class="text-primary-600"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
          </svg>
          <span class="text-xs mt-1">Pflanzen</span>
        </router-link>

        <router-link
          to="/events/new"
          class="mobile-nav-link-fab"
        >
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
        </router-link>

        <router-link
          to="/tasks"
          class="mobile-nav-link"
          active-class="text-primary-600"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
          <span class="text-xs mt-1">Aufgaben</span>
        </router-link>
      </div>
    </nav>
  </div>
</template>

<script setup>
// Navigation component
</script>

<style scoped>
.nav-link {
  @apply inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:border-gray-300 hover:text-gray-700 transition-colors;
}

.mobile-nav-link {
  @apply flex flex-col items-center justify-center flex-1 text-gray-500 hover:text-primary-600 transition-colors;
}

.mobile-nav-link-fab {
  @apply flex items-center justify-center w-14 h-14 bg-primary-600 text-white rounded-full shadow-lg hover:bg-primary-700 transition-all transform hover:scale-110 -mt-8;
}
</style>
