import { loginApi } from '@/api/auth'; // 假设你有一个获取当前用户信息的接口
import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useRouter } from 'vue-router';


export const useAuthStore = defineStore('auth', () => {
    // === State (状态) ===
    const token = ref(localStorage.getItem('token') || '');
    const userInfo = ref(null);
    
    // 新增：角色与权限状态
    const role = ref(localStorage.getItem('role_code') || null);         // 例如: 'SUPER_ADMIN', 'COMPANY_ADMIN', 'EMPLOYEE', 'GUEST'
    const permissions = ref([]);    // 例如: ['expense:create', 'expense:read', 'expense:delete']
    
    const router = useRouter();

    // === Getters / Helpers (辅助方法) ===
    
    // 判断是否拥有某些角色 (用于路由守卫和菜单显示)
    const hasRole = (allowedRoles) => {
        if (!role.value) return false;
        if (Array.isArray(allowedRoles)) {
            return allowedRoles.includes(role.value);
        }
        return allowedRoles === role.value;
    };

    // 判断是否拥有特定权限 (用于按钮级别控制，Guest 没有增删改)
    const hasPermission = (permissionCode) => {
        // 超级管理员直接放行所有权限
        if (role.value === 'SUPER_ADMIN') return true; 
        return permissions.value.includes(permissionCode);
    };

    // 登录动作
    const login = async (username, password) => {
        try {
            // 1. 调用 API 层
            const res = await loginApi({ username, password });
            
            // 2. 把 company_id 存到浏览器的 LocalStorage 中
            if (res.company_id) {
                localStorage.setItem('x_tenant_id', res.company_id);
            }
            
            // 3. 保存 Token
            if (res.token) {
                localStorage.setItem('token', res.token);
                token.value = res.token;
            }
            
            // 【新增】4. 保存角色信息，否则 AppMenu 里的 hasRole 永远是 false
            if (res.role_code) {
                role.value = res.role_code;
                localStorage.setItem('role_code', res.role_code); // 建议存入本地，防止刷新页面后丢失
            }
            // 【新增】5. 保存token信息
            if (res.access_token) {
                localStorage.setItem('access_token', res.access_token); // 建议存入本地，防止刷新页面后丢失
            }
            // 保存其他用户信息（可选）
            if (res.user_id) {
                userInfo.value = res;
                localStorage.setItem('user_id', res.user_id); // 建议存入本地，防止刷新页面后丢失
            }
            
            return res;
        } catch (error) {
            console.error('Login failed:', error);
            throw error; 
        }
    };

    // 登出动作
    const logout = () => {
        // 1. 清除本地状态
        userInfo.value = null; 
        role.value = null;
        permissions.value = [];
        token.value = ''; 
        
        // 2. 清除 localStorage 数据 (注意把租户 ID 也清理掉)
        localStorage.removeItem('token');
        localStorage.removeItem('x_tenant_id');
        localStorage.removeItem('role_code');
        localStorage.removeItem('user_id');
        localStorage.removeItem('access_token');
        
        // 3. 跳转回登录页
        // 使用 router.push 代替 window.location.href 体验更平滑 (不会重载整个页面)
        router.push('/'); 
    };

    // 必须将所有供外部使用的变量和方法 return 出来
    return { 
        token, 
        userInfo, 
        role, 
        permissions, 
        hasRole, 
        hasPermission, 
        // fetchUserInfo, 
        login, 
        logout 
    };
});