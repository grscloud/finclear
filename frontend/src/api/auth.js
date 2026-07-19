import request from './request';

// 登录接口
export const loginApi = (data) => {
    return request.post('/v1/auth/login', data); // 对应你后端的 /auth/login
};

// 退出登录接口
export const logoutApi = () => {
    console.log("loginApi...");
    return request.post('/auth/logout');
};

// 获取当前用户信息接口
export const getUserInfoApi = () => {
    return request.get('/auth/me');
};