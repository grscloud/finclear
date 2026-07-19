// src/api/user.js
import request from './request';

// 1. 邀请新用户
export const inviteUser = (data) => {
  return request.post('/v1/tenant/users/invite', data);
};

// 2. 重置密码
export const resetPassword = (data) => {
  return request.post('/v1/auth/reset-password', data);
};

// 3. 登录验证
export const login = (data) => {
  return request.post('/v1/auth/login', data);
};

// 4. 获取租户用户列表
export const getTenantUsers = (params) => {
  return request.get('/v1/tenant/users', { params });
};

// 5. 移除租户成员
export const removeUser = (userId) => {
  return request.delete(`/v1/tenant/users/${userId}`);
};

// 【新增】6. 修改用户信息（匹配后端的 PUT 路由）
export const updateUser = (userId, data) => {
  return request.put(`/v1/tenant/users/${userId}`, data);
};