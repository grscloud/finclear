import axios from 'axios';

const request = axios.create({
    baseURL: '/api', // 替换成你的真实后端地址
    timeout: 10000
});

// 请求拦截器：自动把 Token 放到 Header 里
request.interceptors.request.use(
    config => {
        // 1. 每次发请求前，先去 LocalStorage 里找租户 ID
        const tenantId = localStorage.getItem('x_tenant_id');
        
        // 2. 如果找到了，就塞进 Headers 里！
        if (tenantId) {
            config.headers['X-Tenant-Id'] = tenantId;
            config.headers['Content-Type'] = 'application/json';
        }
        
        // （如果有 Token，也可以顺便在这里塞进去）
        const access_token = localStorage.getItem('access_token');
        if (access_token) {// 关键：统一在这里添加 Header
            config.headers.Authorization = `Bearer ${access_token}`;
        }

        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

// 响应拦截器：统一处理后端报错
request.interceptors.response.use(
    (response) => response.data, // 直接返回后端真实数据，剥离 axios 外壳
    (error) => {
        // 在这里统一处理 401未授权, 500服务器错误 等
        return Promise.reject(error);
    }
);

export default request;