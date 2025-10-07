/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { menuService } from "@web/webclient/menus/menu_service";  // ✅ Import đúng service
import { rpc } from "@web/core/network/rpc_service";

console.log(">>> sonha_ke_toan: menu_item_patch.js loaded");

patch(menuService, {
    setup() {
        console.log("✅ Patch menuService chạy OK!");
        this._super(...arguments);
    },
});
