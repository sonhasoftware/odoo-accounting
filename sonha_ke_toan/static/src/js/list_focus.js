/** @odoo-module */

import { ListController } from "@web/views/list/list_controller";
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { useService } from "@web/core/utils/hooks";

export class FocusListController extends ListController {

    setup() {
        super.setup();
        this.orm = useService("orm");

        this.focusedCell = null;
    }

    mounted() {
        super.mounted();

        // Lắng nghe focus vào cell
        this.el.addEventListener("focusin", (ev) => {
            const cell = ev.target.closest("td[data-name]");
            if (!cell) return;

            const fieldName = cell.dataset.name;
            const recordId = cell.closest("tr")?.dataset?.id;
            const value = ev.target.value;

            this.focusedCell = {
                recordId: parseInt(recordId),
                fieldName,
                value,
            };
        });
    }

    async onClickF9() {
        if (!this.focusedCell) {
            this.notification.add("Bạn chưa đứng ở ô nào", { type: "warning" });
            return;
        }

        await this.orm.call(
            "popup.change.field",
            "open_from_list",
            [],
            {
                context: {
                    default_record_id: this.focusedCell.recordId,
                    default_field_name: this.focusedCell.fieldName,
                    default_value: this.focusedCell.value,
                }
            }
        );
    }
}

registry.category("views").add("button_click_f9", {
    ...listView,
    Controller: FocusListController,
});
