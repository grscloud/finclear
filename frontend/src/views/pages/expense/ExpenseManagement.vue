<script setup>
import { ref, onMounted, computed } from 'vue';
import { useDeleteConfirm } from '@/composables/useDeleteConfirm';
import { getExpenses, createExpense, deleteExpense, updateExpenseById, approveExpense, getUploadUrl } from '@/api/expense';

// 👈 1. 引入您的 Auth Store (请根据实际路径修改)
import { useAuthStore } from '@/store/auth'; 

const authStore = useAuthStore();
const { confirmDelete } = useDeleteConfirm();

// ================= 2. 权限（Role）管理逻辑 =================

// 新建权限：包含在对应角色里即可新建 (剔除了 GUEST)
const canCreate = computed(() => {
    return authStore.hasRole(['SUPER_ADMIN', 'COMPANY_ADMIN', 'EMPLOYEE']);
    // 如果您未来想用权限码细粒度控制，可以换成: 
    // return authStore.hasPermission('expense:create');
});

// 编辑/删除/操作权限：超管和公司管理员可管理所有，一般员工只能管理自己的
const canEditOrDelete = (expense) => {
    if (authStore.hasRole('SUPER_ADMIN')) return true; 
    if (authStore.hasRole('COMPANY_ADMIN')) return true; 
    
    const currentUserId = authStore.userInfo?.user_id; 
    if (authStore.hasRole('EMPLOYEE') && expense.user_id === currentUserId) return true; 
    
    return false;
};

// 👈 新增：取下（撤销）权限：仅限本人操作
const canCancel = (expense) => {
    const currentUserId = authStore.userInfo?.user_id;
    // 只有当存在 user_id 且与该记录的创建者一致时才允许取下
    return currentUserId && expense.user_id === currentUserId;
};

// 审批权限：仅超管和公司管理员可审批
const canApprove = () => {
    return authStore.hasRole(['SUPER_ADMIN', 'COMPANY_ADMIN']);
};
// =========================================================


const expenses = ref([]);
const isDialogVisible = ref(false);
const isApprovalDialogVisible = ref(false);
const dialogMode = ref('view'); // 'view' | 'edit' | 'create'

// 审批/状态流转相关
const approvalAction = ref('');
const approvalComment = ref('');
const currentExpenseId = ref(null);

// 字典数据 (用于下拉框)
const categories = [
    { label: '一般経費 (General)', value: 'general' },
    { label: '交通費 (Transportation)', value: 'transportation' }
];

const invoiceTypes = [
    { label: '適格請求書 (Qualified)', value: 'qualified' },
    { label: '適格外 (Non-Qualified)', value: 'non_qualified' }
];

const isUploading = ref(false); // 上传状态指示器

// 表单初始状态
const initialForm = () => ({
    id: null,
    // 👈 3. 新建时默认绑定当前用户的 ID
    user_id: authStore.userInfo?.user_id || null, 
    trans_date: null,
    vendor_name: '',
    total_amount: 0,
    tax_8_amount: 0,
    tax_10_amount: 0,
    category: 'general',
    t_number: '',
    invoice_type: 'qualified',
    deduction_rate: 1.0, 
    purpose: '',
    transport_details: [],
    receipts: []
});

const formData = ref(initialForm());

// 加载经费列表
const loadExpenses = async () => {
    try {
        const res = await getExpenses({ skip: 0, limit: 100 });
        expenses.value = res.data || res || [];
    } catch (error) {
        console.error('获取经费列表失败:', error);
    }
};

onMounted(() => {
    // 如果有获取用户信息的接口，建议在应用初始化时调用，确保页面刷新后 userInfo 存在
    // if (!authStore.userInfo) { authStore.fetchUserInfo(); }
    loadExpenses();
});

// 新建
const handleAddExpense = () => {
    dialogMode.value = 'create';
    formData.value = initialForm();
    isDialogVisible.value = true;
};

// 查看详情
const handleViewExpense = (expense) => {
    dialogMode.value = 'view';
    formData.value = { ...expense, trans_date: new Date(expense.trans_date) };
    isDialogVisible.value = true;
};

// 编辑
const handleEditExpense = (expense) => {
    dialogMode.value = 'edit';
    formData.value = { ...expense, trans_date: new Date(expense.trans_date) };
    isDialogVisible.value = true;
};

// 删除
const handleDeleteExpense = (id) => {
    confirmDelete(`経費申請ID「${id}」を削除しますか？`, async () => {
        try {
            await deleteExpense(id);
            await loadExpenses();
        } catch (error) {
            console.error(`删除失败:`, error);
        }
    });
};

// 保存新建或编辑
const saveExpense = async () => {
    try {
        const payload = { ...formData.value };
        if (payload.trans_date) {
            payload.trans_date = new Date(payload.trans_date).toISOString();
        }
        
        if (payload.category !== 'transportation') {
            payload.transport_details = [];
        }

        if (dialogMode.value === 'create') {
            await createExpense(payload);
        } else if (dialogMode.value === 'edit') {
            await updateExpenseById(payload.id, payload);
        }
        
        isDialogVisible.value = false;
        await loadExpenses();
    } catch (error) {
        console.error('保存失败:', error);
    }
};

// ================= 交通费明细操作 =================
const addTransportDetail = () => {
    formData.value.transport_details.push({
        seq_num: formData.value.transport_details.length + 1,
        origin: '',
        destination: '',
        amount: 0,
        is_round_trip: false,
        input_method: 'manual'
    });
};

const removeTransportDetail = (index) => {
    formData.value.transport_details.splice(index, 1);
    formData.value.transport_details.forEach((item, i) => {
        item.seq_num = i + 1;
    });
};

// ================= 审批工作流 =================
const openApprovalDialog = (expenseId, action) => {
    currentExpenseId.value = expenseId;
    approvalAction.value = action;
    approvalComment.value = '';
    
    if (['submit', 'cancel'].includes(action)) {
        submitApproval();
    } else {
        isApprovalDialogVisible.value = true;
    }
};

const submitApproval = async () => {
    try {
        const payload = {
            action: approvalAction.value,
            comment: approvalComment.value || null
        };
        await approveExpense(currentExpenseId.value, payload);
        isApprovalDialogVisible.value = false;
        await loadExpenses(); 
    } catch (error) {
        console.error('状态操作失败:', error);
    }
};

// 弹窗标题
const dialogHeader = computed(() => {
    const maps = { 'create': '新規経費申請', 'edit': '経費申請編集', 'view': '経費詳細' };
    return maps[dialogMode.value];
});

// 审批操作名称映射
const actionName = computed(() => {
    const maps = { 'approve': '承認', 'reject': '却下' };
    return maps[approvalAction.value] || '';
});

// 状态 Badge 颜色映射
const getStatusSeverity = (status) => {
    const maps = {
        'draft': 'secondary',
        'pending': 'warning',
        'approved': 'success',
        'rejected': 'danger',
        'canceled': 'info'
    };
    return maps[status] || 'info';
};

// ================= S3 直传逻辑 =================
const onCustomUpload = async (event) => {
    const file = event.files[0];
    if (!file) return;

    isUploading.value = true;
    try {
        const res = await getUploadUrl(file.name);
        const { upload_url, s3_key } = res.data || res;

        const uploadResponse = await fetch(upload_url, {
            method: 'PUT',
            body: file,
            headers: {
                'Content-Type': file.type 
            }
        });

        if (!uploadResponse.ok) {
            throw new Error('S3へのアップロードに失敗しました');
        }

        formData.value.receipts.push({
            original_filename: file.name,
            mime_type: file.type,
            file_size: file.size,
            s3_key: s3_key
        });
    } catch (error) {
        console.error('アップロード失敗:', error);
    } finally {
        isUploading.value = false;
    }
};

const removeReceipt = (index) => {
    formData.value.receipts.splice(index, 1);
};
</script>

<template>
    <div class="card">
        <div class="font-semibold text-xl mb-4">経費管理</div>
        
        <!-- 列表 -->
        <DataTable :value="expenses" scrollable scrollHeight="500px" tableStyle="min-width: 60rem">
            <template #header>
                <div class="flex justify-start mb-2">
                    <!-- 👈 使用 canCreate 控制新建按钮可见性 -->
                    <Button v-if="canCreate" label="新規申請" icon="pi pi-plus" @click="handleAddExpense" />
                </div>
            </template>

            <Column field="trans_date" header="発生日" style="min-width: 120px">
                <template #body="{ data }">
                    {{ new Date(data.trans_date).toLocaleDateString() }}
                </template>
            </Column>
            <Column field="vendor_name" header="支払先" style="min-width: 150px"></Column>
            <Column field="category" header="カテゴリ" style="min-width: 120px">
                <template #body="{ data }">
                    {{ data.category === 'transportation' ? '交通費' : '一般経費' }}
                </template>
            </Column>
            <Column field="total_amount" header="金額" style="min-width: 120px">
                <template #body="{ data }">
                    ¥{{ data.total_amount.toLocaleString() }}
                </template>
            </Column>
            <Column field="status" header="ステータス" style="min-width: 120px">
                <template #body="{ data }">
                    <Tag :severity="getStatusSeverity(data.status)" :value="data.status.toUpperCase()" />
                </template>
            </Column>
            
            <Column header="操作" style="min-width: 250px" :frozen="true" alignFrozen="right">
                <template #body="{ data }">
                    <div class="flex items-center gap-3 text-sm">
                        <!-- 所有角色都能查看详细 -->
                        <button @click="handleViewExpense(data)" class="text-gray-500 hover:underline cursor-pointer bg-transparent border-none p-0">詳細</button>
                        
                        <!-- 👈 仅在允许编辑该条数据时，显示 编辑/提交/删除 -->
                        <template v-if="['draft', 'rejected'].includes(data.status) && canEditOrDelete(data)">
                            <button @click="handleEditExpense(data)" class="text-blue-500 hover:underline cursor-pointer bg-transparent border-none p-0">編集</button>
                            <button @click="openApprovalDialog(data.id, 'submit')" class="text-green-500 hover:underline cursor-pointer bg-transparent border-none p-0">提出</button>
                            <button @click="handleDeleteExpense(data.id)" class="text-red-500 hover:underline cursor-pointer bg-transparent border-none p-0">削除</button>
                        </template>

                        <!-- 👈 仅当前用户是超管或公司管理员时，显示 审批/驳回 -->
                        <template v-if="data.status === 'pending' && canApprove()">
                            <button @click="openApprovalDialog(data.id, 'approve')" class="text-green-600 hover:underline cursor-pointer bg-transparent border-none p-0 font-bold">承認</button>
                            <button @click="openApprovalDialog(data.id, 'reject')" class="text-orange-500 hover:underline cursor-pointer bg-transparent border-none p-0">却下</button>
                        </template>
                        
                        <!-- 👈 修改后: 撤销操作：只有本人才能取下自己的申请 -->
                        <template v-if="data.status === 'pending' && canCancel(data)">
                            <button @click="openApprovalDialog(data.id, 'cancel')" class="text-gray-500 hover:underline cursor-pointer bg-transparent border-none p-0">取下</button>
                        </template>
                    </div>
                </template>
            </Column>
        </DataTable>

        <ConfirmDialog />

        <!-- 经费编辑/详情弹窗 -->
        <Dialog v-model:visible="isDialogVisible" :header="dialogHeader" class="responsive-dialog" :style="{ width: '700px' }" :modal="true">
            <div class="flex flex-col gap-4 mt-2">
                <!-- 基础信息 (省略修改，保持原样) -->
                <div class="p-4 bg-gray-50 border border-gray-200 rounded grid grid-cols-2 gap-4">
                    <div class="flex flex-col gap-2 col-span-2 md:col-span-1">
                        <label class="font-semibold text-sm">発生日 (Date)*</label>
                        <Calendar v-model="formData.trans_date" :disabled="dialogMode === 'view'" dateFormat="yy/mm/dd" />
                    </div>
                    
                    <div class="flex flex-col gap-2 col-span-2 md:col-span-1">
                        <label class="font-semibold text-sm">カテゴリ (Category)*</label>
                        <Dropdown v-model="formData.category" :options="categories" optionLabel="label" optionValue="value" :disabled="dialogMode === 'view'" />
                    </div>

                    <div class="flex flex-col gap-2 col-span-2">
                        <label class="font-semibold text-sm">支払先 (Vendor Name)*</label>
                        <InputText v-model="formData.vendor_name" :disabled="dialogMode === 'view'" placeholder="例：JR東日本 / Amazon" />
                    </div>

                    <div class="flex flex-col gap-2 col-span-2 md:col-span-1">
                        <label class="font-semibold text-sm">合計金額 (Total Amount)*</label>
                        <InputNumber v-model="formData.total_amount" mode="currency" currency="JPY" locale="ja-JP" :disabled="dialogMode === 'view'" />
                    </div>
                </div>

                <!-- 電帳法/发票相关信息 (如果是一般经费用) -->
                <div v-if="formData.category === 'general'" class="p-4 bg-gray-50 border border-gray-200 rounded grid grid-cols-2 gap-4">
                    <h3 class="text-sm font-bold text-gray-600 col-span-2 mb-1 border-b pb-1">適格請求書・税情報</h3>
                    
                    <div class="flex flex-col gap-2 col-span-2 md:col-span-1">
                        <label class="font-semibold text-sm">請求書区分</label>
                        <Dropdown v-model="formData.invoice_type" :options="invoiceTypes" optionLabel="label" optionValue="value" :disabled="dialogMode === 'view'" />
                    </div>

                    <div class="flex flex-col gap-2 col-span-2 md:col-span-1">
                        <label class="font-semibold text-sm">登録番号 (T-Number)</label>
                        <InputText v-model="formData.t_number" :disabled="dialogMode === 'view'" placeholder="例：T1234567890123" />
                    </div>

                    <div class="flex flex-col gap-2 col-span-2 md:col-span-1">
                        <label class="font-semibold text-sm">8%対象額</label>
                        <InputNumber v-model="formData.tax_8_amount" mode="currency" currency="JPY" locale="ja-JP" :disabled="dialogMode === 'view'" />
                    </div>

                    <div class="flex flex-col gap-2 col-span-2 md:col-span-1">
                        <label class="font-semibold text-sm">10%対象額</label>
                        <InputNumber v-model="formData.tax_10_amount" mode="currency" currency="JPY" locale="ja-JP" :disabled="dialogMode === 'view'" />
                    </div>
                </div>

                <!-- 交通费明细 -->
                <div v-if="formData.category === 'transportation'" class="p-4 bg-white border border-blue-200 rounded">
                    <div class="flex justify-between items-center mb-3 border-b pb-2">
                        <h3 class="text-sm font-bold text-blue-600">交通費明細</h3>
                        <Button v-if="dialogMode !== 'view'" label="経路追加" icon="pi pi-plus" size="small" text @click="addTransportDetail" />
                    </div>

                    <div v-if="formData.transport_details.length === 0" class="text-sm text-gray-400 py-2">明細がありません</div>

                    <div v-for="(detail, index) in formData.transport_details" :key="index" class="flex flex-wrap gap-2 items-end mb-3 p-2 bg-gray-50 rounded">
                        <div class="flex flex-col gap-1 w-24">
                            <label class="text-xs">出発 (Origin)</label>
                            <InputText v-model="detail.origin" :disabled="dialogMode === 'view'" size="small" />
                        </div>
                        <div class="flex flex-col gap-1 w-24">
                            <label class="text-xs">到着 (Dest)</label>
                            <InputText v-model="detail.destination" :disabled="dialogMode === 'view'" size="small" />
                        </div>
                        <div class="flex flex-col gap-1 w-24">
                            <label class="text-xs">金額</label>
                            <InputNumber v-model="detail.amount" :disabled="dialogMode === 'view'" size="small" />
                        </div>
                        <div class="flex flex-col gap-1">
                            <label class="text-xs text-center">往復</label>
                            <Checkbox v-model="detail.is_round_trip" :binary="true" :disabled="dialogMode === 'view'" class="mt-2 ml-2" />
                        </div>
                        <Button v-if="dialogMode !== 'view'" icon="pi pi-trash" severity="danger" text @click="removeTransportDetail(index)" class="ml-auto" />
                    </div>
                </div>

                <!-- 添付書類 (Receipts) -->
                <div class="p-4 bg-gray-50 border border-gray-200 rounded flex flex-col gap-3">
                    <h3 class="text-sm font-bold text-gray-600 border-b pb-2">添付書類 (Receipts)</h3>
                    
                    <div v-if="dialogMode !== 'view'" class="flex items-center gap-3">
                        <FileUpload 
                            mode="basic" 
                            chooseLabel="ファイルを選択 (領収書等)" 
                            class="p-button-outlined p-button-sm"
                            :auto="true" 
                            customUpload 
                            @uploader="onCustomUpload" 
                            :disabled="isUploading"
                        />
                        <span v-if="isUploading" class="text-sm text-blue-500 flex items-center gap-1">
                            <i class="pi pi-spin pi-spinner"></i> アップロード中...
                        </span>
                    </div>

                    <div class="flex flex-col gap-2 max-h-40 overflow-y-auto">
                        <div 
                            v-for="(file, index) in formData.receipts" 
                            :key="index" 
                            class="flex items-center justify-between bg-white p-2 border border-gray-200 rounded text-sm"
                        >
                            <div class="flex items-center gap-2 truncate pr-2">
                                <i class="pi pi-file text-gray-400"></i>
                                <span class="font-medium truncate" :title="file.original_filename">
                                    {{ file.original_filename }}
                                </span>
                                <span class="text-xs text-gray-400 flex-shrink-0">
                                    ({{ (file.file_size / 1024).toFixed(1) }} KB)
                                </span>
                            </div>
                            
                            <Button 
                                v-if="dialogMode !== 'view'" 
                                icon="pi pi-trash" 
                                severity="danger" 
                                text 
                                rounded 
                                size="small" 
                                class="p-0 h-8 w-8"
                                @click="removeReceipt(index)" 
                            />
                        </div>
                        
                        <div v-if="formData.receipts.length === 0" class="text-sm text-gray-400 text-center py-2">
                            添付ファイルはありません。
                        </div>
                    </div>
                </div>

                <div class="flex flex-col gap-2">
                    <label class="font-semibold text-sm">目的/備考 (Purpose)</label>
                    <Textarea v-model="formData.purpose" rows="3" :disabled="dialogMode === 'view'" placeholder="出張の目的などを入力" />
                </div>
            </div>

            <template #footer>
                <div class="flex justify-end gap-2 mt-4">
                    <Button label="閉じる" icon="pi pi-times" text @click="isDialogVisible = false" />
                    <!-- 只在编辑或新建模式下显示保存按钮 -->
                    <Button v-if="dialogMode !== 'view'" label="保存 (Draft)" icon="pi pi-save" @click="saveExpense" />
                </div>
            </template>
        </Dialog>

        <!-- 审批备注弹窗 -->
        <Dialog v-model:visible="isApprovalDialogVisible" :header="actionName + '処理'" :style="{ width: '400px' }" :modal="true">
            <div class="flex flex-col gap-3 pt-4">
                <label class="text-sm font-semibold">コメント (必須ではない)</label>
                <Textarea v-model="approvalComment" rows="4" placeholder="承認/却下の理由を入力してください..." class="w-full" />
            </div>
            <template #footer>
                <Button label="キャンセル" text @click="isApprovalDialogVisible = false" />
                <Button :label="actionName" :severity="approvalAction === 'reject' ? 'danger' : 'success'" @click="submitApproval" />
            </template>
        </Dialog>
    </div>
</template>