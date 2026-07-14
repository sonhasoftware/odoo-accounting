/** @odoo-module **/

import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { onMounted, onWillUnmount, onPatched } from "@odoo/owl";

const WIDTH_SAVE_DELAY = 500;
const MIN_COLUMN_WIDTH = 30;

function debounce(fn, delay) {
    let timer;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

function getFieldName(th) {
    return th?.dataset?.name || th?.dataset?.field || th?.getAttribute("name") || null;
}

function getColumnWidth(th) {
    const width = Math.round(th.getBoundingClientRect().width || th.offsetWidth || 0);
    return width >= MIN_COLUMN_WIDTH ? width : 0;
}

patch(ListRenderer.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this._sonhaColumnWidths = {};
        this._sonhaColumnWidthObserver = null;
        this._sonhaColumnWidthSaving = false;
        this._sonhaSaveColumnWidthsDebounced = debounce(() => this._sonhaSaveColumnWidths(), WIDTH_SAVE_DELAY);

        onMounted(async () => {
            await this._sonhaLoadColumnWidths();
            this._sonhaApplyColumnWidths();
            this._sonhaStartColumnWidthObserver();
        });

        onPatched(() => {
            this._sonhaApplyColumnWidths();
            this._sonhaStartColumnWidthObserver();
        });

        onWillUnmount(() => {
            if (this._sonhaColumnWidthObserver) {
                this._sonhaColumnWidthObserver.disconnect();
                this._sonhaColumnWidthObserver = null;
            }
        });
    },

    _sonhaGetModelName() {
        return this.props?.list?.resModel || this.props?.list?.model?.root?.resModel || this.props?.view?.arch?.attrs?.model || null;
    },

    _sonhaGetViewKey() {
        return String(this.props?.archInfo?.xmlDoc?.getAttribute?.("js_class") || this.props?.archInfo?.viewId || "default");
    },

    async _sonhaLoadColumnWidths() {
        const modelName = this._sonhaGetModelName();
        if (!modelName) {
            return;
        }
        try {
            this._sonhaColumnWidths = await this.orm.call(
                "sonha.list.column.width",
                "get_widths",
                [modelName, this._sonhaGetViewKey()]
            ) || {};
        } catch (error) {
            console.warn("sonha_ke_toan: cannot load list column widths", error);
            this._sonhaColumnWidths = {};
        }
    },

    _sonhaApplyColumnWidths() {
        const table = this.el?.querySelector?.("table.o_list_table");
        if (!table || !this._sonhaColumnWidths) {
            return;
        }
        const headers = table.querySelectorAll("thead th");
        headers.forEach((th, index) => {
            const fieldName = getFieldName(th);
            const width = fieldName ? parseInt(this._sonhaColumnWidths[fieldName], 10) : 0;
            if (!width) {
                return;
            }
            const pxWidth = `${width}px`;
            th.style.width = pxWidth;
            th.style.minWidth = pxWidth;
            table.querySelectorAll(`tbody tr td:nth-child(${index + 1})`).forEach((td) => {
                td.style.width = pxWidth;
                td.style.minWidth = pxWidth;
            });
        });
    },

    _sonhaStartColumnWidthObserver() {
        const table = this.el?.querySelector?.("table.o_list_table");
        const thead = table?.querySelector?.("thead");
        if (!thead) {
            return;
        }
        if (this._sonhaColumnWidthObserver) {
            this._sonhaColumnWidthObserver.disconnect();
        }
        this._sonhaColumnWidthObserver = new MutationObserver(() => {
            if (!this._sonhaColumnWidthSaving) {
                this._sonhaSaveColumnWidthsDebounced();
            }
        });
        this._sonhaColumnWidthObserver.observe(thead, {
            attributes: true,
            subtree: true,
            attributeFilter: ["style", "class"],
        });
    },

    async _sonhaSaveColumnWidths() {
        const modelName = this._sonhaGetModelName();
        const table = this.el?.querySelector?.("table.o_list_table");
        if (!modelName || !table) {
            return;
        }
        const widths = {};
        table.querySelectorAll("thead th").forEach((th) => {
            const fieldName = getFieldName(th);
            const width = getColumnWidth(th);
            if (fieldName && width) {
                widths[fieldName] = width;
            }
        });
        if (!Object.keys(widths).length) {
            return;
        }
        this._sonhaColumnWidths = { ...this._sonhaColumnWidths, ...widths };
        this._sonhaColumnWidthSaving = true;
        try {
            await this.orm.call(
                "sonha.list.column.width",
                "save_widths",
                [modelName, this._sonhaGetViewKey(), widths]
            );
        } catch (error) {
            console.warn("sonha_ke_toan: cannot save list column widths", error);
        } finally {
            this._sonhaColumnWidthSaving = false;
        }
    },
});
