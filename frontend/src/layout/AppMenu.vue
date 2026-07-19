<script setup>
import { ref, computed } from 'vue';
import AppMenuItem from './AppMenuItem.vue';
import { useAuthStore } from '@/store/auth';

const authStore = useAuthStore();

// 在你原有的模型中，直接加入 roles 字段来控制权限
const model = ref([
    {
        label: '経費管理',
        path: '/pages/expense',
        items: [
            {
                label: '経費管理',
                icon: 'pi pi-fw pi-check-square',
                to: '/pages/expense/ExpenseManagement',
                roles: ['SUPER_ADMIN', 'COMPANY_ADMIN', 'EMPLOYEE', 'GUEST']
            }
        ]
    },
    {
        label: '見積・請求書管理',
        path: '/pages/client',
        items: [
            {
                label: '顧客管理',
                icon: 'pi pi-fw pi-check-square',
                to: '/pages/client/ClientManagement',
                roles: ['SUPER_ADMIN', 'COMPANY_ADMIN', 'GUEST']
            },
            {
                label: '見積書管理',
                icon: 'pi pi-fw pi-check-square',
                to: '/pages/client/InvoiceManagement',
                roles: ['SUPER_ADMIN', 'COMPANY_ADMIN', 'GUEST']
            },
            {
                label: '商品・サービス管理',
                icon: 'pi pi-fw pi-check-square',
                to: '/pages/client/ProductManagement',
                roles: ['SUPER_ADMIN', 'COMPANY_ADMIN', 'GUEST']
            }
        ]
    },
    {
        label: '権限管理',
        path: '/iam',
        items: [
            {
                label: 'ユーザー管理',
                icon: 'pi pi-fw pi-check-square',
                to: '/pages/iam/UserManagement',
                roles: ['SUPER_ADMIN', 'COMPANY_ADMIN', 'GUEST'] 
            },
            {
                label: 'テナント管理',
                icon: 'pi pi-fw pi-check-square',
                to: '/pages/iam/TenantManagement',
                // 只有超管能看
                roles: ['SUPER_ADMIN']
            }
        ]
    }
]);

// 【核心逻辑】根据当前用户的角色过滤菜单
const filteredModel = computed(() => {
    return model.value.map(menuGroup => {
        // 浅拷贝一下分类对象，避免直接修改原数据
        const group = { ...menuGroup };
        
        if (group.items) {
            // 过滤该分类下的子菜单
            group.items = group.items.filter(item => {
                if (item.roles) {
                    return authStore.hasRole(item.roles);
                }
                return true; // 如果没有配置 roles，默认显示
            });
        }
        return group;
    })
    // 过滤掉空的分类：如果某个分类下的子菜单都被权限挡住了，那么这个分类标题（如"権限管理"）也不应该显示
    .filter(group => group.items && group.items.length > 0); 
});
</script>

<template>
    <ul class="layout-menu">
        <!-- 注意这里：把循环的 model 换成了我们计算好的 filteredModel -->
        <template v-for="(item, i) in filteredModel" :key="item">
            <app-menu-item v-if="!item.separator" :item="item" :index="i"></app-menu-item>
            <li v-if="item.separator" class="menu-separator"></li>
        </template>
    </ul>
</template>

<style lang="scss" scoped></style>