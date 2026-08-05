// src/api/company.js
import request from './request';

// 6. 获取自己公司信息
export const getMyCompany = () => {
  return request.get('/v1/companies/me');
};

// 7. 修改自己公司的基本信息
export const updateMyCompany = (data) => {
  return request.put('/v1/companies/me', data);
};

// 8. [超管权限] 创建一个新的公司租户
export const createCompany = (data) => {
  return request.post('/v1/companies', data);
};

// 9. [超管权限] 全局分页查询所有公司
export const getCompanies = (params) => {
  return request.get('/v1/companies', { params });
};

// 10. [超管权限] 查看指定 UUID 公司详情
export const getCompanyById = (id) => {
  return request.get(`/v1/companies/${id}`);
};

// 11. [超管权限] 逻辑删除某个公司
export const deleteCompany = (id) => {
  return request.delete(`/v1/companies/${id}`);
};

// 12. [超管权限] 修改指定 UUID 公司详情
export const updateCompanyById = (id, data) => {
  return request.put(`/v1/companies/${id}`, data);
};
