/** @odoo-module **/

import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from "@web/core/utils/patch";
import { Dialog } from "@web/core/dialog/dialog";

console.log("sonha_ke_toan: field_confirm_list_patch loading");

const _origOnCellClicked = ListRenderer.prototype.onCellClicked;

patch(ListRenderer.prototype, {
    getCellClass(record, column) {
        let res = super.getCellClass(record, column);
        if (column.type === "integer" || column.type === "float") {
            res += " col-number";
        }
        if (column.type === "char" || column.type === "text") {
            res += " col-text";
        }
        if (column.type === "boolean") {
            res += " col-checkbox";
        }
        return res;
    },
});

//patch(ListRenderer.prototype, {
//    async onCellClicked(record, column, ev) {
//        try {
//            const fieldName = column?.name || column?.attrs?.name || column?.field?.name;
//            const modelName = this.props?.list?.model?.root?.resModel || this.props?.view?.arch?.attrs?.model;
//            console.log("field_confirm: model =", modelName, "field =", fieldName);
//
//            // Lấy danh sách field cần confirm (cache lại để không gọi nhiều lần)
//            if (!this._fieldsNeedConfirm) {
//                this._fieldsNeedConfirm = [];
//                if (modelName) {
//                    try {
//                        this._fieldsNeedConfirm = await this.env.services.rpc(
//                            "/field_confirm/get_fields",
//                            { model: modelName }
//                        );
//                        console.log("field_confirm: fieldsNeedConfirm =", this._fieldsNeedConfirm);
//                    } catch (e) {
//                        console.error("field_confirm: RPC lỗi", e);
//                        this._fieldsNeedConfirm = [];
//                    }
//                }
//            }
//
//            // Nếu field nằm trong danh sách confirm thì show popup
//            if (fieldName && Array.isArray(this._fieldsNeedConfirm) && this._fieldsNeedConfirm.includes(fieldName)) {
//                const confirmed = await new Promise((resolve) => {
//                    if (this.env?.services?.dialog?.add) {
//                        this.env.services.dialog.add(Dialog, {
//                            title: "Xác nhận bac",
//                            body: "Bạn có chắc muốn sửa trường <b>${fieldName}</b> không?",
//                            buttons: [
//                                { text: "Hủy", close: true, click: () => resolve(false) },
//                                { text: "Đồng ý", close: true, primary: true, click: () => resolve(true) },
//                            ],
//                        });
//                    } else {
//                        resolve(window.confirm(`Bạn có chắc muốn sửa trường "${fieldName}" không?`));
//                    }
//                });
//                if (!confirmed) {
//                    return; // Người dùng hủy thì dừng luôn
//                }
//            }
//        } catch (err) {
//            console.error("field_confirm: unexpected error", err);
//        }
//
//        // Gọi lại hàm gốc thay vì this._super
//        return await _origOnCellClicked.call(this, record, column, ev);
//    },
//});
