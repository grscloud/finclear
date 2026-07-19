<script setup>
import { ref, onMounted } from 'vue';
import { useDeleteConfirm } from '@/composables/useDeleteConfirm';

const { confirmDelete } = useDeleteConfirm();

const roles = ref([]);
const allPermissions = ref([]);
const isDialogVisible = ref(false);
const dialogMode = ref('create'); // 'create' | 'view' | 'edit'
const formData = ref({ id: null, name: '', isSystem: false, permissions: [] });

onMounted(() => {
    allPermissions.value = [
        { id: 1, code: 'expense:approve', name: '経費承認' },
        { id: 2, code: 'invoice:create', name: '請求書作成' }
    ];
    roles.value = [
        { id: 1, name: '会社管理者', isSystem: true, permissions: [1, 2] },
        { id: 99, name: '財務専員', isSystem: false, permissions: [1] }
    ];
});

// 新增
const handleCreate = () => {
    dialogMode.value = 'create';
    formData.value = { id: null, name: '', isSystem: false, permissions: [] };
    isDialogVisible.value = true;
};

// 查看详情
const handleView = (role) => {
    dialogMode.value = 'view';
    formData.value = { ...role, permissions: [...role.permissions] };
    isDialogVisible.value = true;
};

// 编辑
const handleEdit = (role) => {
    dialogMode.value = 'edit';
    formData.value = { ...role, permissions: [...role.permissions] };
    isDialogVisible.value = true;
};

const handleDelete = (id) => confirmDelete('このロールを削除しますか？この操作は元に戻せません。', () => console.log('Deleted role:', id));

const saveRole = () => {
    console.log('Saved role:', formData.value);
    isDialogVisible.value = false;
};

const dialogHeader = () => {
    const maps = { 'create': '新規ロール追加', 'view': 'ロール詳細', 'edit': 'ロール編集' };
    return maps[dialogMode.value];
};
</script>

<template>
    <div class="card">
        <div class="font-semibold text-xl mb-4">ロール管理</div>
        <DataTable :value="roles" scrollable scrollHeight="400px">
            <template #header>
                <Button label="ロール追加" icon="pi pi-plus" @click="handleCreate" />
            </template>
            <Column field="name" header="ロール名" />
            <Column field="isSystem" header="タイプ">
                <template #body="slotProps">
                    <Tag :value="slotProps.data.isSystem ? 'システム' : 'カスタム'" :severity="slotProps.data.isSystem ? 'secondary' : 'info'" />
                </template>
            </Column>
            <Column header="操作" :frozen="true" alignFrozen="right" style="width: 200px;">
                <template #body="slotProps">
                    <div class="flex gap-3">
                        <button class="text-gray-500 hover:underline" @click="handleView(slotProps.data)">詳細</button>
                        <button class="text-blue-500 hover:underline" @click="handleEdit(slotProps.data)">編集</button>
                        <button v-if="!slotProps.data.isSystem" class="text-red-500 hover:underline" @click="handleDelete(slotProps.data.id)">削除</button>
                    </div>
                </template>
            </Column>
        </DataTable>

        <ConfirmDialog />

       <Dialog  v-model:visible="isDialogVisible" :header="dialogHeader()" class="responsive-dialog" :style="{ width: '500px' }" :breakpoints="{ '640px': '100vw' }" :modal="true">
            <div class="flex flex-col gap-4 mt-2">
                <div class="flex flex-col gap-2">
                    <label class="font-semibold text-sm">ロール名</label>
                    <InputText 
                        v-model="formData.name" 
                        :disabled="dialogMode === 'view' || formData.isSystem" 
                        placeholder="例：経理担当者" 
                        class="w-full" 
                    />
                </div>
                
                <div class="flex flex-col gap-2">
                    <label class="font-semibold text-sm">権限設定</label>
                    <div class="permissions-container bg-gray-50 p-3 rounded border">
                        <div v-for="perm in allPermissions" :key="perm.id" class="flex items-center mb-2">
                            <Checkbox 
                                v-model="formData.permissions" 
                                :value="perm.id" 
                                :inputId="`perm-${perm.id}`" 
                                :disabled="dialogMode === 'view'"
                            />
                            <label :for="`perm-${perm.id}`" class="ml-2 cursor-pointer">{{ perm.name }}</label>
                        </div>
                    </div>
                </div>
            </div>

            <template #footer>
                <div class="flex justify-end gap-2">
                    <Button label="キャンセル" icon="pi pi-times" text @click="isDialogVisible = false" />
                    <Button v-if="dialogMode !== 'view'" label="保存" icon="pi pi-check" @click="saveRole" />
                </div>
            </template>
        </Dialog>
    </div>
</template>