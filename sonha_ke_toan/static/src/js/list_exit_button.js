/** @odoo-module */

import { ListController } from "@web/views/list/list_controller";
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { useService } from "@web/core/utils/hooks";
import { onMounted, onWillUnmount } from "@odoo/owl";

export class BaoCaoListController extends ListController {

    setup() {
        super.setup();
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.actionService = useService("action");

        this._onKeyDown = this._onKeyDown.bind(this);

        onMounted(() => {
            document.addEventListener("keydown", this._onKeyDown);
        });

        onWillUnmount(() => {
            document.removeEventListener("keydown", this._onKeyDown);
        });
    }

    async onDetailClick() {
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
            "nl.acc.bao.cao",
            "action_exit",
            [ids]
        );

        if (action) {
            this.actionService.doAction(action);
        }
    }

    async onSearchClick() {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: 'Tìm kiếm',
            res_model: "popup.tim.kiem",
            views: [[false, "form"]],
            target: "new",
        });
    }

    async onThoatClick() {
        return this.actionService.doAction({
            type: "ir.actions.act_window",
            name: 'Báo cáo',
            res_model: "popup.bao.cao",
            views: [[false, "form"]],
            target: "new",
        });
    }

    _onKeyDown(ev) {
        if (ev.key === "F2") {
            ev.preventDefault();
            this.onExitClick();
        }
    }
}

registry.category("views").add("button_in_tree_bao_cao", {
    ...listView,
    Controller: BaoCaoListController,
    buttonTemplate: "button_bao_cao.ListView.Buttons",
});
