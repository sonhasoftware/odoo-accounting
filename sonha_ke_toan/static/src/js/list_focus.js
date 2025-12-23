/** @odoo-module */

import { ListController } from "@web/views/list/list_controller";
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { useService } from "@web/core/utils/hooks";

export class FocusListController extends ListController {

    setup() {
        super.setup();

        this.orm = useService("orm");
        this.notification = useService("notification");

        this.focusedCell = null;

        // ⭐ QUAN TRỌNG: bind handler
        this.onClickF9 = this.onClickF9.bind(this);
    }

    mounted() {
        super.mounted();

        this.el.addEventListener("focusin", (ev) => {
            const cell = ev.target.closest("td[data-name]");
            if (!cell) return;

            const recordId = cell.closest("tr")?.dataset?.id;
            const fieldName = cell.dataset.name;
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
            this.notification.add(
                "Bạn chưa đứng ở ô nào",
                { type: "warning" }
            );
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
