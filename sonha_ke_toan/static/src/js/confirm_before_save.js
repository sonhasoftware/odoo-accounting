/** @odoo-module **/

import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from "@web/core/utils/patch";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";

console.log("sonha_ke_toan: field_confirm_list_patch loading");

const _origOnCellClicked = ListRenderer.prototype.onCellClicked;

patch(ListRenderer.prototype, {
    async onCellClicked(record, column, ev) {
        const fieldName = column?.name || column?.attrs?.name || column?.field?.name;
        const modelName = this.props?.list?.model?.root?.resModel || this.props?.view?.arch?.attrs?.model;
        console.log("field_confirm: model =", modelName, "field =", fieldName);

        // Lấy danh sách field cần confirm
        let fieldsNeedConfirm = [];
        if (modelName) {
            try {
                fieldsNeedConfirm = await this.getConfirmFields(modelName);
            } catch (error) {
                console.error("field_confirm: Failed to get confirm fields, using fallback", error);
                fieldsNeedConfirm = []
            }
        }

        console.log("field_confirm: fields need confirm =", fieldsNeedConfirm);

        // Kiểm tra nếu là bản ghi mới - KHÔNG confirm
        const isNewRecord = !record.resId || record.isNew;
        if (isNewRecord) {
            console.log("field_confirm: New record detected, skipping confirmation");
            this._pendingConfirmField = null;
            this.cleanupBlurListener();
            return await _origOnCellClicked.call(this, record, column, ev);
        }

        // Nếu field cần confirm, đánh dấu và lưu giá trị gốc
        if (fieldName && fieldsNeedConfirm.includes(fieldName)) {
            console.log("field_confirm: Field requires confirmation:", fieldName);

            // Cleanup listener cũ trước khi tạo mới
            this.cleanupBlurListener();

            // Lưu thông tin field cần confirm
            this._pendingConfirmField = {
                fieldName,
                record,
                column,
                originalValue: record.data[fieldName],
                modelName
            };

            console.log("field_confirm: Original value:", this._pendingConfirmField.originalValue);

            // Thêm event listener để bắt sự kiện blur (khi focus ra ngoài)
            this.setupBlurListener(record, fieldName);

        } else {
            console.log("field_confirm: No confirmation needed for field:", fieldName);
            this._pendingConfirmField = null;
            this.cleanupBlurListener();
        }

        // Gọi lại hàm gốc để cho phép chỉnh sửa
        return await _origOnCellClicked.call(this, record, column, ev);
    },

    setupBlurListener(record, fieldName) {
        // Đợi DOM render xong
        const checkElement = () => {
            // Tìm input element đang được edit
            const activeElement = document.activeElement;
            if (activeElement && (activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA')) {
                console.log("field_confirm: Found active input element:", activeElement);

                // Lưu reference đến element và handlers
                this._currentActiveElement = activeElement;

                // Thêm event listener cho blur
                this._blurHandler = async (e) => {
                    console.log("field_confirm: Input blur detected");

                    // Kiểm tra xem user có click vào nút Discard không
                    const clickedElement = e.relatedTarget;
                    if (clickedElement && clickedElement.classList.contains('o_list_button_discard')) {
                        console.log("field_confirm: User clicked Discard button, skipping confirmation");
                        this._pendingConfirmField = null;
                        this.cleanupBlurListener();
                        return;
                    }

                    const newValue = activeElement.value;
                    await this.handleFieldChange(record, fieldName, newValue);
                };

                // Thêm event listener cho Enter key
                this._keydownHandler = async (e) => {
                    if (e.key === 'Enter') {
                        console.log("field_confirm: Enter key pressed");
                        e.preventDefault(); // Ngăn form submit
                        const newValue = activeElement.value;
                        await this.handleFieldChange(record, fieldName, newValue);
                    }
                };

                activeElement.addEventListener('blur', this._blurHandler);
                activeElement.addEventListener('keydown', this._keydownHandler);

            } else {
                // Thử lại sau nếu chưa tìm thấy element
                setTimeout(checkElement, 10);
            }
        };

        checkElement();
    },

    cleanupBlurListener() {
        // Remove existing event listeners
        if (this._currentActiveElement && this._blurHandler) {
            this._currentActiveElement.removeEventListener('blur', this._blurHandler);
        }
        if (this._currentActiveElement && this._keydownHandler) {
            this._currentActiveElement.removeEventListener('keydown', this._keydownHandler);
        }
        this._blurHandler = null;
        this._keydownHandler = null;
        this._currentActiveElement = null;
    },

    async handleFieldChange(record, fieldName, newValue) {
        // Cleanup listeners trước khi xử lý
        this.cleanupBlurListener();

        if (!this._pendingConfirmField || this._pendingConfirmField.fieldName !== fieldName) {
            return;
        }

        // Kiểm tra lại nếu là bản ghi mới - KHÔNG confirm
        const isNewRecord = !record.resId || record.isNew;
        if (isNewRecord) {
            console.log("field_confirm: New record detected in handleFieldChange, skipping confirmation");
            this._pendingConfirmField = null;
            return;
        }

        const originalValue = this._pendingConfirmField.originalValue;
        console.log("field_confirm: Field change detected - from:", originalValue, "to:", newValue);

        // Nếu giá trị thực sự thay đổi
        if (newValue !== originalValue) {
            console.log("field_confirm: Value changed, showing confirmation...");

            // Sử dụng ConfirmationDialog của Odoo
            const confirmed = await this.showConfirmationDialog(fieldName, originalValue, newValue);

            console.log("field_confirm: Confirm result:", confirmed);

            if (!confirmed) {
                console.log("field_confirm: User cancelled, reverting and clicking discard button...");
                await record.update({ [fieldName]: originalValue });
                this.clickSaveButton();
            } else {
                console.log("field_confirm: User confirmed change, clicking save button...");
                this.clickSaveButton();
            }
        } else {
            console.log("field_confirm: No actual change detected");
        }

        // QUAN TRỌNG: Reset pending confirm field để cho phép click lại
        this._pendingConfirmField = null;
    },

    clickSaveButton() {
        // Tìm nút Save trong list view
        const saveButton = document.querySelector('.o_list_button_save');
        if (saveButton) {
            console.log("field_confirm: Found Save button, clicking...");
            saveButton.click();
        } else {
            console.log("field_confirm: Save button not found");
        }
    },

    async showConfirmationDialog(fieldName, oldValue, newValue) {
        return new Promise((resolve) => {
            const message = _t("Bạn có chắc muốn thay đổi trường này?");

            this.env.services.dialog.add(ConfirmationDialog, {
                title: _t("Xác nhận thay đổi"),
                body: message,
                confirm: () => {
                    console.log("field_confirm: User confirmed change");
                    resolve(true);
                },
                cancel: () => {
                    console.log("field_confirm: User cancelled change");
                    resolve(false);
                },
            });
        });
    },

    async getConfirmFields(modelName) {
        if (!this._fieldsCache) {
            this._fieldsCache = {};
        }

        if (this._fieldsCache[modelName]) {
            console.log("field_confirm: Using cached fields for", modelName);
            return this._fieldsCache[modelName];
        }

        try {
            const fields = await this.env.services.rpc(
                "/field_confirm/get_confirm_fields",
                { model: modelName }
            );
            const result = Array.isArray(fields) ? fields : [];
            this._fieldsCache[modelName] = result;
            console.log("field_confirm: RPC successful, got fields:", result);
            return result;

        } catch (error) {
            delete this._fieldsCache[modelName];
            return [];
        }
    },
});