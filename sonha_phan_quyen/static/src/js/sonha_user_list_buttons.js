/** @odoo-module */

import { ListController } from "@web/views/list/list_controller";
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { useService } from "@web/core/utils/hooks";

export class SonhaUserListController extends ListController {
    setup() {
        super.setup();
        this.actionService = useService("action");
        this.orm = useService("orm");
    }

    async onLockUserLoginsClick() {
        const action = await this.orm.call(
            "res.users",
            "action_lock_user_logins",
            []
        );

        if (action) {
            await this.actionService.doAction(action);
        }
    }

    async onUnlockUserLoginsClick() {
        const action = await this.orm.call(
            "res.users",
            "action_unlock_user_logins",
            []
        );

        if (action) {
            await this.actionService.doAction(action);
        }
    }
}

registry.category("views").add("sonha_user_list_buttons", {
    ...listView,
    Controller: SonhaUserListController,
    buttonTemplate: "sonha_phan_quyen.SonhaUserListView.Buttons",
});
