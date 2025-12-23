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

        this.lastFocusedCell = null;

        this.onKeyDown = this.onKeyDown.bind(this);
    }

    mounted() {
        super.mounted();

        // ✅ BẮT CLICK CHUỘT (QUAN TRỌNG)
        this.el.addEventListener("mousedown", (ev) => {
            const cell = ev.target.closest("td[data-name]");
            if (!cell) return;
            this._storeCell(cell);
        }, true);

        // ✅ BẮT TAB / ENTER
        this.el.addEventListener("focusin", (ev) => {
            const cell = ev.target.closest("td[data-name]");
            if (!cell) return;
            this._storeCell(cell);
        }, true);

        // ✅ BẮT PHÍM F9
        window.addEventListener("keydown", this.onKeyDown, true);
    }

    willUnmount() {
        super.willUnmount();
        window.removeEventListener("keydown", this.onKeyDown, true);
    }

    _storeCell(cell) {
        const tr = cell.closest("tr");
        if (!tr || !tr.dataset.id) return;

        this.lastFocusedCell = {
            recordId: parseInt(tr.dataset.id),
            fieldName: cell.dataset.name,
            value: cell.innerText?.trim(), // ⚠️ td KHÔNG có value
        };

        console.log("Focused cell:", this.lastFocusedCell);
    }

    onKeyDown(ev) {
        if (ev.key === "F2") {
            console.log("aaaaaaaaaaaaaaa")
            ev.preventDefault();
            ev.stopPropagation();
            this.onClickF9();
        }
    }

    async onClickF9() {
    const selection = this.model.root.selection;

    if (!selection || !selection.length) {
        this.notification.add(
            "Bạn chưa đứng ở ô nào",
            { type: "warning" }
        );
        return;
    }

    const record = selection[0];

    // field đang active
    const fieldName = this.model.root.activeField;

    if (!fieldName) {
        this.notification.add(
            "Không xác định được field đang đứng",
            { type: "warning" }
        );
        return;
    }

    const value = record.data[fieldName];

    await this.orm.call(
        "popup.change.field",
        "open_from_list",
        [],
        {
            context: {
                default_record_id: record.resId,
                default_field_name: fieldName,
                default_value: value,
            },
        }
    );
}
}

// ✅ ĐĂNG KÝ VIEW
registry.category("views").add("button_click_f9", {
    ...listView,
    Controller: FocusListController,
    buttonTemplate: "button_tong_hop.ListView.Buttons",
});
