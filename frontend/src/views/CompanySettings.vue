<script setup>
import { ref, reactive } from 'vue';

// 編集モードを管理するフラグ
const isEditing = ref(false);

// 表示用のデータ（初期値）
const companyInfo = reactive({
    name: '株式会社テスト',
    invoiceNumber: 'T1234567890123'
});

// 編集時の入力データを保持する変数（キャンセル時に元の状態を保つため）
const tempInfo = reactive({
    name: '',
    invoiceNumber: ''
});

// 編集モードへの切り替え
const startEdit = () => {
    // 現在のデータを一時変数にコピー
    tempInfo.name = companyInfo.name;
    tempInfo.invoiceNumber = companyInfo.invoiceNumber;
    isEditing.value = true;
};

// 編集のキャンセル
const cancelEdit = () => {
    isEditing.value = false;
};

// 保存処理
const saveData = () => {
    // 編集内容を元のデータに反映
    companyInfo.name = tempInfo.name;
    companyInfo.invoiceNumber = tempInfo.invoiceNumber;
    
    // API等への保存ロジックをここに記述します
    console.log('保存データ:', companyInfo);
    
    // 閲覧モードに戻す
    isEditing.value = false;
};
</script>

<template>
    <Fluid>
        <div class="flex flex-col md:flex-row gap-8">
            <div class="w-full">
                <!-- card は白色背景パネル -->
                <div class="card flex flex-col gap-4">
                    <!-- ヘッダー部分：タイトルと編集ボタン -->
                    <div class="flex justify-between items-center">
                        <div class="font-semibold text-xl">会社情報設定</div>
                        <Button 
                            v-if="!isEditing" 
                            label="編集" 
                            icon="pi pi-pencil" 
                            style="width: auto;" 
                            @click="startEdit" 
                        />
                    </div>
                    
                    <!-- フォーム部分 -->
                    <div class="flex flex-col gap-4 mt-2">
                        <!-- 企業名称 -->
                        <div class="flex flex-col gap-2">
                            <label for="companyName" class="text-surface-500 dark:text-surface-400 font-medium">企業名称</label>
                            <!-- 閲覧モード -->
                            <div v-if="!isEditing" class="text-lg">
                                {{ companyInfo.name }}
                            </div>
                            <!-- 編集モード -->
                            <InputText v-else id="companyName" v-model="tempInfo.name" type="text" />
                        </div>

                        <!-- 適格請求書発行事業者登録番号 -->
                        <div class="flex flex-col gap-2">
                            <label for="invoiceNumber" class="text-surface-500 dark:text-surface-400 font-medium">適格請求書発行事業者登録番号</label>
                            <!-- 閲覧モード -->
                            <div v-if="!isEditing" class="text-lg">
                                {{ companyInfo.invoiceNumber }}
                            </div>
                            <!-- 編集モード -->
                            <InputText v-else id="invoiceNumber" v-model="tempInfo.invoiceNumber" type="text" />
                        </div>
                    </div>

                    <!-- ボタン領域（編集モード時のみ表示） -->
                    <div v-if="isEditing" class="flex justify-end gap-4 mt-4">
                        <Button 
                            label="キャンセル" 
                            icon="pi pi-times" 
                            severity="secondary" 
                            style="width: auto;" 
                            @click="cancelEdit" 
                        />
                        <Button 
                            label="保存" 
                            icon="pi pi-check" 
                            style="width: auto;" 
                            @click="saveData" 
                        />
                    </div>
                </div>
            </div>
        </div>
    </Fluid>
</template>