import request from './request';

// 获取经费列表
export const getExpenses = (params) => {
    return request.get('/v1/expenses/', { params });
};

// 创建经费
export const createExpense = (data) => {
    return request.post('/v1/expenses/', data);
};

// 删除经费 (逻辑删除)
export const deleteExpense = (id) => {
    return request.delete(`/v1/expenses/${id}`);
};

// 状态流转 (提交、审批、驳回、撤销)
export const approveExpense = (id, data) => {
    return request.post(`/v1/expenses/${id}/approve`, data);
};

// 注意：后端给出的代码中缺少 update 的 API，如果需要编辑已保存的草稿，
// 你需要在后端补充 PUT /api/v1/expenses/{id} 接口。
export const updateExpenseById = (id, data) => {
    return request.put(`/v1/expenses/${id}`, data); 
};

// 获取 S3 预签名上传 URL
export const getUploadUrl = (filename) => {
    return request.get('/v1/expenses/upload-url', { params: { filename } });
};