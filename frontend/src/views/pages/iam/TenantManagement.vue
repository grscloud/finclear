<script setup>
import { ref, onMounted } from 'vue';
import { useDeleteConfirm } from '@/composables/useDeleteConfirm';
// 假设你已经按照前面的建议将 API 封装在 @/api/company 中
import { getCompanies, createCompany, deleteCompany, updateCompanyById } from '@/api/company';
// 之前引入的 request 也可以去掉了，因为不再需要直接调用它
// 引入基础 request 实例以调用封装外可能存在的超管更新接口
//import request from '@/api/request'; 

const { confirmDelete } = useDeleteConfirm();

const tenants = ref([]);
const isDialogVisible = ref(false);
const dialogMode = ref('view'); // 'view' | 'edit' | 'create'

// 字段对齐后端: name(公司名), invoice_number(税号)
const formData = ref({ id: null, name: '', invoice_number: '' });

// 1. 加载租户列表 (GET /api/v1/companies)
const loadTenants = async () => {
    try {
        const res = await getCompanies({ page: 1, limit: 100 });
        // 根据后端实际返回结构调整，假设为 res.data.items 或 res.data
        tenants.value = res.data.items || res.data || [];
    } catch (error) {
        console.error('获取テナント列表失败:', error);
    }
};

// 页面加载时获取数据
onMounted(() => {
    loadTenants();
});

// 新建
const handleAddTenant = () => {
    dialogMode.value = 'create';
    formData.value = { id: null, name: '', invoice_number: '' };
    isDialogVisible.value = true;
};

// 查看详情
const handleViewTenant = (tenant) => {
    dialogMode.value = 'view';
    formData.value = { ...tenant };
    isDialogVisible.value = true;
};

// 编辑
const handleEditTenant = (tenant) => {
    dialogMode.value = 'edit';
    formData.value = { ...tenant };
    isDialogVisible.value = true;
};

// 删除 (DELETE /api/v1/companies/{id})
const handleDeleteTenant = (id) => {
    confirmDelete(`テナントID「${id}」を削除しますか？\n全ての関連データが完全に消去されます。`, async () => {
        try {
            await deleteCompany(id);
            console.log(`Deleted tenant: ${id}`);
            // 删除成功后刷新列表
            await loadTenants();
        } catch (error) {
            console.error(`删除テナント ${id} 失败:`, error);
        }
    });
};

// 保存新建或编辑 (POST or PUT)
const saveTenant = async () => {
    try {
        const payload = {
            name: formData.value.name,
            invoice_number: formData.value.invoice_number
        };

        if (dialogMode.value === 'create') {
            await createCompany(payload);
            console.log('Created tenant:', payload);
        } else if (dialogMode.value === 'edit') {
            // ❌ 之前这里直接写了 request.put(`/api/v1/companies/${formData.value.id}`, payload);
            // ✅ 现在替换为调用封装好的 API
            await updateCompanyById(formData.value.id, payload);
            console.log('Updated tenant:', payload);
        }
        
        isDialogVisible.value = false;
        // 保存成功后刷新列表
        await loadTenants();
    } catch (error) {
        console.error('保存テナント失败:', error);
    }
};

// 计算弹窗标题
const dialogHeader = () => {
    const maps = { 'create': '新規テナント追加', 'edit': 'テナント情報編集', 'view': 'テナント詳細' };
    return maps[dialogMode.value];
};
</script>

<template>
    <div class="card">
        <div class="font-semibold text-xl mb-4">テナント管理</div>
        
        <DataTable :value="tenants" scrollable scrollHeight="400px" tableStyle="min-width: 50rem">
            <template #header>
                <div class="flex justify-start mb-2">
                    <Button label="テナント追加" icon="pi pi-plus" @click="handleAddTenant" />
                </div>
            </template>

            <Column field="id" header="テナントID" style="min-width: 120px"></Column>
            <!-- 字段名更新为后端对应的 name -->
            <Column field="name" header="会社名" style="min-width: 200px"></Column>
            <!-- 假设后端返回的创建时间字段为 created_at -->
            <Column field="created_at" header="作成時間" style="min-width: 150px">
                <template #body="slotProps">
                    {{ slotProps.data.created_at || '-' }}
                </template>
            </Column>
            
            <Column header="操作" style="min-width: 150px" :frozen="true" alignFrozen="right">
                <template #body="slotProps">
                    <div class="flex items-center gap-3">
                        <button @click="handleViewTenant(slotProps.data)" class="text-gray-500 hover:underline cursor-pointer bg-transparent border-none p-0">詳細</button>
                        <button @click="handleEditTenant(slotProps.data)" class="text-blue-500 hover:underline cursor-pointer bg-transparent border-none p-0">編集</button>
                        <button @click="handleDeleteTenant(slotProps.data.id)" class="text-red-500 hover:underline cursor-pointer bg-transparent border-none p-0">削除</button>
                    </div>
                </template>
            </Column>
        </DataTable>

        <ConfirmDialog />

       <Dialog v-model:visible="isDialogVisible" :header="dialogHeader()" class="responsive-dialog" :style="{ width: '500px' }" :breakpoints="{ '640px': '100vw' }" :modal="true">
            <div class="flex flex-col gap-4 mt-2">
                <div class="p-4 bg-gray-50 border border-gray-200 rounded">
                    <h3 class="text-sm font-bold text-gray-600 mb-3 border-b pb-2">企業情報</h3>
                    <div class="flex flex-col gap-2">
                        <label for="companyName" class="font-semibold text-sm">会社名</label>
                        <InputText 
                            id="companyName" 
                            v-model="formData.name" 
                            :disabled="dialogMode === 'view'"
                            placeholder="例：株式会社テスト" 
                            class="w-full" 
                        />
                    </div>
                </div>

                <div class="p-4 bg-gray-50 border border-gray-200 rounded">
                    <!-- 标题和字段更新为税务/发票信息，匹配 invoice_number -->
                    <h3 class="text-sm font-bold text-gray-600 mb-3 border-b pb-2">登録情報</h3>
                    <div class="flex flex-col gap-2">
                        <label for="invoiceNumber" class="font-semibold text-sm">インボイス登録番号 (Tax ID)</label>
                        <InputText 
                            id="invoiceNumber" 
                            v-model="formData.invoice_number" 
                            :disabled="dialogMode === 'view'"
                            placeholder="例：T1234567890123" 
                            class="w-full" 
                        />
                    </div>
                </div>
            </div>

            <template #footer>
                <div class="flex justify-end gap-2">
                    <Button label="キャンセル" icon="pi pi-times" text @click="isDialogVisible = false" />
                    <!-- 查看模式下隐藏保存按钮 -->
                    <Button v-if="dialogMode !== 'view'" label="保存" icon="pi pi-check" @click="saveTenant" />
                </div>
            </template>
        </Dialog>
    </div>
</template>