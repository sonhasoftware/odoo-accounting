/** @odoo-module */

import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from "@web/core/utils/patch";
import { onMounted, onPatched } from "@odoo/owl";

patch(ListRenderer.prototype, {
    setup() {
        super.setup();
        this._columnReorderHandlers = [];
        this._columnWidthPersistTimeout = null;
        this._columnWidthResizeState = null;
        onMounted(() => this._setupColumnReorder());
        onPatched(() => this._setupColumnReorder());
    },

    _getColumnReorderStorageKey() {
        const resModel = this.props.list?.resModel || "unknown_model";
        const viewId = this.props.archInfo?.viewId || this.props.list?.viewId || "unknown_view";
        return `tree_column_reorder:${resModel}:${viewId}`;
    },

    _getColumnWidthStorageKey() {
        const resModel = this.props.list?.resModel || "unknown_model";
        const viewId = this.props.archInfo?.viewId || this.props.list?.viewId || "unknown_view";
        return `tree_column_width:${resModel}:${viewId}`;
    },

    _getColumnHeaders(table) {
        return [...table.querySelectorAll("thead th")].filter(
            (th) => th.dataset.name && !th.classList.contains("o_list_record_selector")
        );
    },

    _setupColumnReorder() {
        const table = this.tableRef?.el || this.el?.querySelector("table.o_list_table");
        if (!table || !table.querySelector("thead")) {
            return;
        }

        this._cleanupColumnReorderHandlers();
        this._applySavedColumnOrder(table);
        this._applySavedColumnWidths(table);
        this._setupColumnWidthPersistence(table);

        const headers = this._getColumnHeaders(table);
        headers.forEach((header) => {
            header.setAttribute("draggable", "true");
            header.classList.add("o_col_reorder_draggable");

            const onDragStart = (ev) => {
                ev.dataTransfer.effectAllowed = "move";
                ev.dataTransfer.setData("text/plain", header.dataset.name || "");
                header.classList.add("o_col_reorder_dragging");
            };

            const onDragEnd = () => {
                header.classList.remove("o_col_reorder_dragging");
                this._clearDragIndicators(table);
            };

            const onDragOver = (ev) => {
                ev.preventDefault();
                header.classList.add("o_col_reorder_over");
            };

            const onDragLeave = () => {
                header.classList.remove("o_col_reorder_over");
            };

            const onDrop = (ev) => {
                ev.preventDefault();
                const sourceName = ev.dataTransfer.getData("text/plain");
                const targetName = header.dataset.name;
                header.classList.remove("o_col_reorder_over");
                this._moveColumnByName(table, sourceName, targetName);
            };

            header.addEventListener("dragstart", onDragStart);
            header.addEventListener("dragend", onDragEnd);
            header.addEventListener("dragover", onDragOver);
            header.addEventListener("dragleave", onDragLeave);
            header.addEventListener("drop", onDrop);

            this._columnReorderHandlers.push({
                element: header,
                listeners: [
                    ["dragstart", onDragStart],
                    ["dragend", onDragEnd],
                    ["dragover", onDragOver],
                    ["dragleave", onDragLeave],
                    ["drop", onDrop],
                ],
            });
        });
    },

    _clearDragIndicators(table) {
        table.querySelectorAll(".o_col_reorder_over").forEach((el) => el.classList.remove("o_col_reorder_over"));
    },

    _cleanupColumnReorderHandlers() {
        if (this._columnWidthPersistTimeout) {
            clearTimeout(this._columnWidthPersistTimeout);
            this._columnWidthPersistTimeout = null;
        }
        for (const entry of this._columnReorderHandlers) {
            for (const [eventName, fn] of entry.listeners) {
                entry.element.removeEventListener(eventName, fn);
            }
        }
        this._columnReorderHandlers = [];
    },

    _setupColumnWidthPersistence(table) {
        const headers = this._getColumnHeaders(table);
        if (!headers.length) {
            return;
        }

        const persistWidths = () => {
            if (this._columnWidthPersistTimeout) {
                clearTimeout(this._columnWidthPersistTimeout);
            }
            this._columnWidthPersistTimeout = setTimeout(() => {
                this._persistCurrentColumnWidths(table);
                this._columnWidthPersistTimeout = null;
            }, 50);
        };

        headers.forEach((header) => {
            const onResizeStart = (ev) => {
                if (!this._isColumnResizeEvent(ev, header)) {
                    return;
                }

                this._columnWidthResizeState = {
                    table,
                    widths: this._getCurrentColumnWidths(table),
                };

                const onResizeEnd = () => {
                    document.removeEventListener("mouseup", onResizeEnd, true);
                    document.removeEventListener("touchend", onResizeEnd, true);
                    document.removeEventListener("touchcancel", onResizeEnd, true);

                    const resizeState = this._columnWidthResizeState;
                    this._columnWidthResizeState = null;
                    if (resizeState?.table && this._hasColumnWidthChanged(resizeState.table, resizeState.widths)) {
                        persistWidths();
                    }
                };

                document.addEventListener("mouseup", onResizeEnd, true);
                document.addEventListener("touchend", onResizeEnd, true);
                document.addEventListener("touchcancel", onResizeEnd, true);
            };

            const onAutoResize = (ev) => {
                if (this._isColumnResizeEvent(ev, header)) {
                    persistWidths();
                }
            };

            header.addEventListener("mousedown", onResizeStart);
            header.addEventListener("touchstart", onResizeStart);
            header.addEventListener("dblclick", onAutoResize);
            this._columnReorderHandlers.push({
                element: header,
                listeners: [
                    ["mousedown", onResizeStart],
                    ["touchstart", onResizeStart],
                    ["dblclick", onAutoResize],
                ],
            });
        });

    },

    _isColumnResizeEvent(ev, header) {
        const resizeHandle = ev.target?.closest?.(".o_resize, .o_column_resize, .o_list_column_resize");
        if (resizeHandle && header.contains(resizeHandle)) {
            return true;
        }

        const pointer = ev.touches?.[0] || ev;
        if (typeof pointer.clientX !== "number") {
            return false;
        }

        const rect = header.getBoundingClientRect();
        const resizeHotZone = 8;
        return Math.abs(pointer.clientX - rect.right) <= resizeHotZone;
    },

    _getCurrentColumnWidths(table) {
        const widths = {};
        this._getColumnHeaders(table).forEach((header) => {
            const name = header.dataset.name;
            if (!name) {
                return;
            }
            widths[name] = Math.round(header.getBoundingClientRect().width);
        });
        return widths;
    },

    _hasColumnWidthChanged(table, previousWidths) {
        const currentWidths = this._getCurrentColumnWidths(table);
        return Object.entries(currentWidths).some(([name, width]) => Math.abs(width - (previousWidths[name] || 0)) > 1);
    },

    _applySavedColumnOrder(table) {
        const storageKey = this._getColumnReorderStorageKey();
        let savedOrder = [];
        try {
            savedOrder = JSON.parse(localStorage.getItem(storageKey) || "[]");
        } catch {
            savedOrder = [];
        }

        if (!savedOrder.length) {
            return;
        }

        const headers = this._getColumnHeaders(table);
        const availableNames = headers.map((h) => h.dataset.name);
        const isCompatible = savedOrder.every((name) => availableNames.includes(name));
        if (!isCompatible) {
            return;
        }

        for (let index = 0; index < savedOrder.length; index++) {
            const targetName = savedOrder[index];
            const currentHeaders = this._getColumnHeaders(table);
            const sourceName = currentHeaders[index]?.dataset.name;
            if (sourceName && sourceName !== targetName) {
                this._moveColumnByName(table, targetName, sourceName, false);
            }
        }
    },

    _moveColumnByName(table, sourceName, targetName, persist = true) {
        if (!sourceName || !targetName || sourceName === targetName) {
            return;
        }

        const headers = [...table.querySelectorAll("thead th")];
        const sourceIndex = headers.findIndex((th) => th.dataset.name === sourceName);
        const targetIndex = headers.findIndex((th) => th.dataset.name === targetName);

        if (sourceIndex < 0 || targetIndex < 0 || sourceIndex === targetIndex) {
            return;
        }

        table.querySelectorAll("tr").forEach((row) => {
            const cells = [...row.children];
            const sourceCell = cells[sourceIndex];
            const targetCell = cells[targetIndex];
            if (!sourceCell || !targetCell || sourceCell === targetCell) {
                return;
            }

            if (sourceIndex < targetIndex) {
                targetCell.after(sourceCell);
            } else {
                targetCell.before(sourceCell);
            }
        });

        if (persist) {
            this._persistCurrentColumnOrder(table);
        }
    },

    _persistCurrentColumnOrder(table) {
        const storageKey = this._getColumnReorderStorageKey();
        const order = this._getColumnHeaders(table).map((header) => header.dataset.name);
        localStorage.setItem(storageKey, JSON.stringify(order));
    },

    _applySavedColumnWidths(table) {
        const storageKey = this._getColumnWidthStorageKey();
        let savedWidths = {};
        try {
            savedWidths = JSON.parse(localStorage.getItem(storageKey) || "{}");
        } catch {
            savedWidths = {};
        }
        if (!savedWidths || typeof savedWidths !== "object") {
            return;
        }

        const headers = [...table.querySelectorAll("thead th")];
        headers.forEach((header, index) => {
            const name = header.dataset.name;
            const width = name ? savedWidths[name] : null;
            if (!width) {
                return;
            }
            const widthValue = `${width}px`;
            table.querySelectorAll("tr").forEach((row) => {
                const cell = row.children[index];
                if (cell) {
                    cell.style.width = widthValue;
                    cell.style.minWidth = widthValue;
                }
            });
        });
    },

    _persistCurrentColumnWidths(table) {
        const storageKey = this._getColumnWidthStorageKey();
        const widths = {};
        this._getColumnHeaders(table).forEach((header) => {
            const name = header.dataset.name;
            if (!name) {
                return;
            }
            const width = Math.round(header.getBoundingClientRect().width);
            if (width > 0) {
                widths[name] = width;
            }
        });
        localStorage.setItem(storageKey, JSON.stringify(widths));
    },
});
