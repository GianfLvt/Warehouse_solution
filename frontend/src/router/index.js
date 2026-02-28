import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { guest: true }
  },
  {
    path: '/',
    component: () => import('@/components/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'Dashboard', component: () => import('@/views/DashboardView.vue') },
      { path: 'products', name: 'Products', component: () => import('@/views/ProductsView.vue'), meta: { roles: ['admin', 'responsabile', 'magazziniere'] } },
      { path: 'products/new', name: 'ProductCreate', component: () => import('@/views/ProductFormView.vue'), meta: { roles: ['admin', 'responsabile', 'magazziniere'] } },
      { path: 'products/:id/edit', name: 'ProductEdit', component: () => import('@/views/ProductFormView.vue'), meta: { roles: ['admin', 'responsabile', 'magazziniere'] } },
      { path: 'stock-movements', name: 'StockMovements', component: () => import('@/views/StockMovementsView.vue'), meta: { roles: ['admin', 'responsabile', 'magazziniere'] } },
      { path: 'customers', name: 'Customers', component: () => import('@/views/CustomersView.vue'), meta: { roles: ['admin', 'responsabile', 'commerciale'] } },
      { path: 'customers/new', name: 'CustomerCreate', component: () => import('@/views/CustomerFormView.vue'), meta: { roles: ['admin', 'responsabile', 'commerciale'] } },
      { path: 'customers/:id/edit', name: 'CustomerEdit', component: () => import('@/views/CustomerFormView.vue'), meta: { roles: ['admin', 'responsabile', 'commerciale'] } },
      { path: 'orders', name: 'Orders', component: () => import('@/views/OrdersView.vue'), meta: { roles: ['admin', 'responsabile', 'commerciale', 'magazziniere'] } },
      { path: 'orders/new', name: 'OrderCreate', component: () => import('@/views/OrderFormView.vue'), meta: { roles: ['admin', 'responsabile', 'commerciale'] } },
      { path: 'orders/:id', name: 'OrderDetail', component: () => import('@/views/OrderDetailView.vue'), meta: { roles: ['admin', 'responsabile', 'commerciale', 'magazziniere'] } },
      { path: 'supplier-orders', name: 'SupplierOrders', component: () => import('@/views/SupplierOrdersView.vue'), meta: { roles: ['admin', 'responsabile', 'magazziniere'] } },
      { path: 'supplier-orders/new', name: 'SupplierOrderCreate', component: () => import('@/views/SupplierOrderFormView.vue'), meta: { roles: ['admin', 'responsabile', 'magazziniere'] } },
      { path: 'quotes', name: 'Quotes', component: () => import('@/views/QuotesView.vue'), meta: { roles: ['admin', 'responsabile', 'commerciale'] } },
      { path: 'quotes/new', name: 'QuoteCreate', component: () => import('@/views/QuoteFormView.vue'), meta: { roles: ['admin', 'responsabile', 'commerciale'] } },
      // --- WMS 4.0 routes ---
      { path: 'warehouses', name: 'Warehouses', component: () => import('@/views/WarehousesView.vue'), meta: { roles: ['admin', 'responsabile', 'magazziniere'] } },
      { path: 'lots', name: 'Lots', component: () => import('@/views/LotsView.vue'), meta: { roles: ['admin', 'responsabile', 'magazziniere'] } },
      { path: 'asn', name: 'ASN', component: () => import('@/views/ASNView.vue'), meta: { roles: ['admin', 'responsabile', 'magazziniere'] } },
      { path: 'asn/new', name: 'ASNCreate', component: () => import('@/views/ASNFormView.vue'), meta: { roles: ['admin', 'responsabile', 'magazziniere'] } },
      { path: 'asn/:id/edit', name: 'ASNEdit', component: () => import('@/views/ASNFormView.vue'), meta: { roles: ['admin', 'responsabile', 'magazziniere'] } },
      { path: 'picking', name: 'Picking', component: () => import('@/views/PickingView.vue'), meta: { roles: ['admin', 'responsabile', 'magazziniere', 'operatore'] } },
      { path: 'shipments', name: 'Shipments', component: () => import('@/views/ShipmentsView.vue'), meta: { roles: ['admin', 'responsabile', 'magazziniere'] } },
      { path: 'iot', name: 'IoT', component: () => import('@/views/IoTDashboardView.vue'), meta: { roles: ['admin', 'responsabile'] } },
      { path: 'inventory', name: 'Inventory', component: () => import('@/views/InventoryCountView.vue'), meta: { roles: ['admin', 'responsabile', 'magazziniere'] } },
      { path: 'ai', name: 'AIInsights', component: () => import('@/views/AIInsightsView.vue'), meta: { roles: ['admin', 'responsabile'] } },
      { path: 'integrations', name: 'Integrations', component: () => import('@/views/IntegrationsView.vue'), meta: { roles: ['admin'] } },
      { path: 'users', name: 'Users', component: () => import('@/views/UsersView.vue'), meta: { roles: ['admin'] } },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.token) return '/login'
  if (to.meta.guest && auth.token) return '/'
  if (to.meta.roles && !to.meta.roles.includes(auth.user?.role)) return '/'
})

export default router
