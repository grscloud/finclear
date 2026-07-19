<script setup>
import { ref, onMounted } from 'vue';
import { useDeleteConfirm } from '@/composables/useDeleteConfirm';
// 【修改】引入 updateUser API
import { inviteUser, getTenantUsers, removeUser, updateUser } from '@/api/user';
import { getCompanies } from '@/api/company';

const { confirmDelete } = useDeleteConfirm();

// API的规范：role_id 的映射
const roleOptions = ref([
    { label: '会社管理者', value: 2 }, 
    { label: '一般社員', value: 3 }
]);

const getRoleLabel = (roleId) => {
    const role = roleOptions.value.find(r => r.value === roleId);
    return role ? role.label : '不明';
};

// 响应式数据
const users = ref([]);
const companyOptions = ref([]); 
const isDialogVisible = ref(false);
const dialogMode = ref('create'); // 'create' | 'view' | 'edit'

// 表单数据
const formData = ref({
    user_id: '',
    username: '',
    password: '',
    full_name: '',
    email: '',
    role_id: 3,
    company_id: null 
});

// 获取真实的租户用户列表
const fetchUsers = async () => {
    try {
        const res = await getTenantUsers({ page: 1, limit: 100 });
        const responseData = res.data || res;
        users.value = responseData.items || []; 
    } catch (error) {
        console.error('获取用户列表失败:', error);
    }
};

// 获取公司列表的方法
const fetchCompanies = async () => {
    try {
        const res = await getCompanies();
        const responseData = res.data || res;
        let rawCompanies = [];
        
        if (Array.isArray(responseData)) {
            rawCompanies = responseData;
        } else if (responseData && Array.isArray(responseData.items)) {
            rawCompanies = responseData.items;
        } else if (responseData && Array.isArray(responseData.data)) {
            rawCompanies = responseData.data;
        } else {
            rawCompanies = [];
            console.warn('获取到的公司数据格式不正确，已自动降级为空数组：', responseData);
        }

        // 【核心修复点】数据归一化
        // 强制确保列表中的每个公司对象都有 company_id 属性（不管后端返回的是 id 还是 company_id）
        companyOptions.value = rawCompanies.map(item => ({
            ...item,
            company_id: item.company_id || item.id // 优先取 company_id，没有则取 id 兜底
        }));

    } catch (error) {
        console.error('获取公司列表失败:', error);
        companyOptions.value = []; 
    }
};

// 页面加载时获取数据
onMounted(() => {
    fetchUsers();
    fetchCompanies(); 
});

// 新增（打开弹窗）
const handleAdd = () => {
    dialogMode.value = 'create';
    formData.value = { user_id: '', username: '', password: '', full_name: '', email: '', role_id: 3, company_id: null };
    isDialogVisible.value = true;
};

// 查看
const handleView = (user) => {
    dialogMode.value = 'view';
    formData.value = { 
        ...user, 
        role_id: user.role?.role_id || 3,
        // 【核心修复点】多渠道兼容读取公司ID，防止初始化或回显时匹配失败
        company_id: user.company_id || user.company?.company_id || user.company?.id || null, 
        password: '' 
    };
    isDialogVisible.value = true;
};

// 编辑
const handleEdit = (user) => {
    dialogMode.value = 'edit';
    formData.value = { 
        ...user, 
        user_id: user.user_id, // 确保 user_id 存在并绑定
        role_id: user.role?.role_id || 3,
        // 【核心修复点】多渠道兼容读取公司ID，防止初始化或回显时匹配失败
        company_id: user.company_id || user.company?.company_id || user.company?.id || null, 
        password: '' 
    };
    isDialogVisible.value = true;
};

// 调用真实删除 API
const handleDelete = (userId) => {
    confirmDelete('このユーザーを削除しますか？', async () => {
        try {
            await removeUser(userId);
            console.log('删除成功:', userId);
            await fetchUsers(); 
        } catch (error) {
            console.error('删除失败:', error);
        }
    });
};

// 提交表单（支持新建与修改）
const saveUser = async () => {
    try {
        if (dialogMode.value === 'create') {
            const payload = {
                username: formData.value.username,
                password: formData.value.password,
                full_name: formData.value.full_name,
                email: formData.value.email,
                role_id: formData.value.role_id,
                company_id: formData.value.company_id 
            };
            
            await inviteUser(payload);
            console.log('用户邀请成功');
            
            isDialogVisible.value = false;
            await fetchUsers(); 
            
        } else if (dialogMode.value === 'edit') {
            const userId = formData.value.user_id;
            if (!userId) {
                console.error('编辑用户失败：未获取到有效的用户ID');
                return;
            }

            // 构建匹配后端 schemas.UpdateUserReq 的请求体
            const payload = {
                company_id: formData.value.company_id, // 传回原公司的 company_id 保持不变
                username: formData.value.username,
                full_name: formData.value.full_name,
                email: formData.value.email,
                role_id: formData.value.role_id,
                status: formData.value.status || 'active'
            };

            await updateUser(userId, payload);
            console.log('用户信息修改成功');

            isDialogVisible.value = false;
            await fetchUsers(); // 刷新列表
        }
    } catch (error) {
        console.error('保存用户失败:', error);
    }
};

const dialogHeader = () => {
    const maps = { 'create': 'ユーザー招待', 'view': 'ユーザー詳細', 'edit': 'ユーザー編集' };
    return maps[dialogMode.value];
};
</script>

<template>
    <div class="card">
        <div class="font-semibold text-xl mb-4">ユーザー管理</div>
        <DataTable :value="users" scrollable scrollHeight="400px" tableStyle="min-width: 50rem">
            <template #header>
                <Button label="ユーザー招待" icon="pi pi-plus" @click="handleAdd" />
            </template>
            <Column field="username" header="ユーザーID" />
            <Column field="full_name" header="氏名" />
            <Column field="email" header="メール" />
            <Column header="所属会社">
                <template #body="slotProps">
                    {{ slotProps.data.company?.name || 'システム管理者 (未所属)' }}
                </template>
            </Column>
            <Column header="ロール">
                <template #body="slotProps">
                    {{ slotProps.data.role?.name || getRoleLabel(slotProps.data.role?.role_id) }}
                </template>
            </Column>
            <Column header="操作" :frozen="true" alignFrozen="right" style="width: 200px;">
                <template #body="slotProps">
                    <div class="flex gap-3">
                        <button class="text-gray-500 hover:underline" @click="handleView(slotProps.data)">詳細</button>
                        <button class="text-blue-500 hover:underline" @click="handleEdit(slotProps.data)">編集</button>
                        <button class="text-red-500 hover:underline" @click="handleDelete(slotProps.data.user_id)">削除</button>
                    </div>
                </template>
            </Column>
        </DataTable>

        <ConfirmDialog />

        <Dialog v-model:visible="isDialogVisible" :header="dialogHeader()" class="responsive-dialog" :style="{ width: '500px' }" :breakpoints="{ '640px': '100vw' }" :modal="true">
            <div class="flex flex-col gap-4">
                <div class="flex flex-col gap-2">
                    <label class="font-semibold text-sm">ユーザーID</label>
                    <InputText v-model="formData.username" :disabled="dialogMode === 'view' || dialogMode === 'edit'" class="w-full" />
                </div>
                
                <div class="flex flex-col gap-2">
                    <label class="font-semibold text-sm">氏名</label>
                    <InputText v-model="formData.full_name" :disabled="dialogMode === 'view'" class="w-full" />
                </div>

                <div class="flex flex-col gap-2">
                    <label class="font-semibold text-sm">メールアドレス</label>
                    <InputText v-model="formData.email" :disabled="dialogMode === 'view'" class="w-full" />
                </div>

                <!-- 仅在新建(邀请)时显示密码 -->
                <div v-if="dialogMode === 'create'" class="flex flex-col gap-2">
                    <label class="font-semibold text-sm">初期パスワード</label>
                    <InputText type="password" v-model="formData.password" class="w-full" />
                </div>

                <!-- 所属会社的下拉框 -->
                <div class="flex flex-col gap-2">
                    <label class="font-semibold text-sm">所属会社</label>
                    <Dropdown 
                        v-model="formData.company_id" 
                        :options="companyOptions" 
                        optionLabel="name" 
                        optionValue="company_id" 
                        placeholder="所属会社を選択してください"
                        :disabled="dialogMode === 'view' || dialogMode === 'edit'" 
                        class="w-full" 
                        filter
                        showClear
                    />
                </div>

                <div class="flex flex-col gap-2">
                    <label class="font-semibold text-sm">ロール</label>
                    <Dropdown v-model="formData.role_id" :options="roleOptions" optionLabel="label" optionValue="value" :disabled="dialogMode === 'view'" class="w-full" />
                </div>
            </div>

            <template #footer>
                <div class="flex justify-end gap-2">
                    <Button label="キャンセル" icon="pi pi-times" text @click="isDialogVisible = false" />
                    <Button v-if="dialogMode !== 'view'" label="保存" icon="pi pi-check" @click="saveUser" />
                </div>
            </template>
        </Dialog>
    </div>
</template>