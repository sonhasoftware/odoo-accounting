/** @odoo-module */

import { ListController } from "@web/views/list/list_controller";
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { useService } from "@web/core/utils/hooks";
import { onMounted, onWillUnmount } from "@odoo/owl";

export class KetoanListController extends ListController {

    setup() {
        super.setup();
        this.orm = useService("orm");
        this.notification = useService("notification");

        // 🔥 bind phím tắt
        this._onKeyDown = this._onKeyDown.bind(this);

        onMounted(() => {
            document.addEventListener("keydown", this._onKeyDown);
        });

        onWillUnmount(() => {
            document.removeEventListener("keydown", this._onKeyDown);
        });
    }

    // =========================
    // 🔥 LOGIC DÙNG CHUNG
    // =========================
    async _handleAction() {
        const selectedRecords = this.model.root.selection || [];
        const ids = selectedRecords.map(rec => rec.resId);

        if (!ids.length) {
            this.notification.add(
                "Bạn chưa chọn bản ghi nào",
                { type: "warning" }
            );
            return;
        }

        const action = await this.orm.call(
            "nl.acc.tong.hop",
            "action_receive_ids",
            [ids]
        );

        if (action) {
            this.actionService.doAction(action);
        }
    }

    // =========================
    // 🖱 CLICK CHUỘT
    // =========================
    onTestClick() {
        this._handleAction();
    }

    // =========================
    // ⌨ PHÍM TẮT F2
    // =========================
    _onKeyDown(ev) {
        if (ev.key === "F2") {
            ev.preventDefault();   // ❗ chặn hành vi mặc định
            this._handleAction();
        }
    }
}

registry.category("views").add("button_in_tree", {
    ...listView,
    Controller: KetoanListController,
    buttonTemplate: "button_tong_hop.ListView.Buttons",
});
