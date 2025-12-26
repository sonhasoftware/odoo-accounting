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

    async _handleAction() {
        const root = this.model.root;

        // DOMAIN & CONTEXT HIỆN TẠI CỦA LIST VIEW
        const domain = root.domain || [];
        const context = root.context || {};

        if (!domain.length) {
            this.notification.add(
                "Không xác định được domain hiện tại",
                { type: "warning" }
            );
            return;
        }

        const action = await this.orm.call(
            "nl.acc.bao.cao",
            "action_exit",
            [domain],
            { context }
        );

        if (action) {
            this.actionService.doAction(action);
        }
    }

    onExitClick() {
        this._handleAction();
    }

    _onKeyDown(ev) {
        if (ev.key === "F2") {
            ev.preventDefault();
            this._handleAction();
        }
    }
}

registry.category("views").add("button_in_tree_bao_cao", {
    ...listView,
    Controller: BaoCaoListController,
    buttonTemplate: "button_bao_cao.ListView.Buttons",
});
