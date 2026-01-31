import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import PlantList from '../views/PlantList.vue'
import PlantDetail from '../views/PlantDetail.vue'
import EventForm from '../views/EventForm.vue'
import TaskList from '../views/TaskList.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/plants',
    name: 'PlantList',
    component: PlantList
  },
  {
    path: '/plants/:id',
    name: 'PlantDetail',
    component: PlantDetail
  },
  {
    path: '/events/new',
    name: 'EventForm',
    component: EventForm
  },
  {
    path: '/tasks',
    name: 'TaskList',
    component: TaskList
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
