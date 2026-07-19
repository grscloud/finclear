import { useConfirm } from 'primevue/useconfirm';

export function useDeleteConfirm() {
    const confirm = useConfirm();

    const confirmDelete = (message, acceptCallback) => {
        confirm.require({
            header: '削除の確認',
            message: message || '本当に削除しますか？',
            icon: 'pi pi-exclamation-triangle',
            acceptLabel: '削除する',
            rejectLabel: 'キャンセル',
            acceptClass: 'p-button-danger',
            accept: acceptCallback
        });
    };

    return { confirmDelete };
}