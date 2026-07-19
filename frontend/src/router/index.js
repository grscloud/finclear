import AppLayout from '@/layout/AppLayout.vue';
import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
    history: createWebHistory(),
    routes: [
        // 1. 将原本的 /auth/login 移到最前面，并把 path 改为 '/'
        {
            path: '/',
            name: 'login',
            component: () => import('@/views/pages/auth/Login.vue')
        },
        
        // 2. 原来的 AppLayout 布局框架
        {
            path: '/app', // 给框架一个不冲突的父路径（你也可以叫它其他名字）
            component: AppLayout,
            children: [
                // 注意：由于 path 以 '/' 开头，它们是绝对路径。
                // 这样依然能完美匹配你在 AppMenu.vue 里配置的路径。
                {
                    path: '/dashboard', // 从 '/' 改为了 '/dashboard'
                    name: 'dashboard',
                    component: () => import('@/views/Dashboard.vue'),
                    meta: { 
                        title: 'ダッシュボード',
                        // icon: 'el-icon-money',
                        // 四种角色都能看到这个菜单
                        roles: ['SUPER_ADMIN', 'COMPANY_ADMIN', 'EMPLOYEE', 'GUEST'] 
                    }
                },
                {
                    path: '/pages/iam/UserManagement',
                    name: 'usermanagement',
                    component: () => import('@/views/pages/iam/UserManagement.vue'),
                    meta: { 
                        title: 'ユーザー管理',
                        // icon: 'el-icon-money',
                        // 四种角色都能看到这个菜单
                        roles: ['SUPER_ADMIN', 'COMPANY_ADMIN', 'GUEST'] 
                    }
                },
                {
                    path: '/pages/iam/RoleManagement',
                    name: 'RoleManagement',
                    component: () => import('@/views/pages/iam/RoleManagement.vue'),
                    meta: { 
                        title: 'ロール管理',
                        // icon: 'el-icon-money',
                        // 四种角色都能看到这个菜单
                        roles: ['SUPER_ADMIN'] 
                    }
                },
                {
                    path: '/pages/iam/TenantManagement',
                    name: 'TenantManagement',
                    component: () => import('@/views/pages/iam/TenantManagement.vue'),
                    meta: { 
                        title: 'テナント管理',
                        // icon: 'el-icon-office-building',
                        // 只有超管和公司管理员能看到
                        roles: ['SUPER_ADMIN'] 
                    }
                },
                {
                    path: '/company-settings',
                    name: 'company-settings',
                    component: () => import('@/views/CompanySettings.vue'),
                    meta: { 
                        title: '会社信息',
                        // icon: 'el-icon-office-building',
                        // 只有超管和公司管理员能看到
                        roles: ['SUPER_ADMIN', 'COMPANY_ADMIN'] 
                    }
                },
                {
                    path: '/pages/expense/ExpenseManagement',
                    name: 'ExpenseManagement',
                    component: () => import('@/views/pages/expense/ExpenseManagement.vue'),
                    meta: { 
                        title: '経費管理',
                        // icon: 'el-icon-money',
                        // 四种角色都能看到这个菜单
                        roles: ['SUPER_ADMIN', 'COMPANY_ADMIN', 'EMPLOYEE', 'GUEST'] 
                    }
                },
                {
                    path: '/pages/client/ClientManagement',
                    name: 'ClientManagement',
                    component: () => import('@/views/pages/client/ClientManagement.vue'),
                    meta: { 
                        title: '顧客管理',
                        // icon: 'el-icon-money',
                        // 四种角色都能看到这个菜单
                        roles: ['SUPER_ADMIN', 'COMPANY_ADMIN', 'GUEST'] 
                    }
                },
                {
                    path: '/pages/client/InvoiceManagement',
                    name: 'InvoiceManagement',
                    component: () => import('@/views/pages/client/InvoiceManagement.vue'),
                    meta: { 
                        title: '請求書管理',
                        // icon: 'el-icon-money',
                        // 三种角色都能看到这个菜单
                        roles: ['SUPER_ADMIN', 'COMPANY_ADMIN', 'GUEST'] 
                    }
                },
                {
                    path: '/pages/client/ProductManagement',
                    name: 'ProductManagement',
                    component: () => import('@/views/pages/client/ProductManagement.vue'),
                    meta: { 
                        title: '商品管理',
                        // icon: 'el-icon-money',
                        // 三种角色都能看到这个菜单
                        roles: ['SUPER_ADMIN', 'COMPANY_ADMIN', 'GUEST'] 
                    }
                }
            ]
        }
    ]
});

export default router;