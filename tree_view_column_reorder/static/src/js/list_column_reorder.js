/** @odoo-module */

import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from "@web/core/utils/patch";
import { onMounted, onPatched, onWillUnmount } from "@odoo/owl";

patch(ListRenderer.prototype, {
    setup() {
        super.setup();
        this._columnReorderHandlers = [];
        this._columnWidthPersistTimeout = null;
        this._columnWidthPersistTable = null;
        this._columnWidthPendingWidths = null;
        this._columnWidthPendingStorageKey = null;
        this._columnWidthPendingBaseStorageKey = null;
        this._columnWidthResizeState = null;
        this._columnWidthBeforeUnload = () => this._flushPendingColumnWidthPersistence();
        window.addEventListener("beforeunload", this._columnWidthBeforeUnload);
        onMounted(() => this._setupColumnReorder());
        onPatched(() => this._setupColumnReorder());
        onWillUnmount(() => {
            this._cleanupColumnReorderHandlers({ flushWidths: true });
            window.removeEventListener("beforeunload", this._columnWidthBeforeUnload);
        });
    },

    _getColumnStorageKey(type, table = null) {
        const resModel = this.props.list?.resModel || "unknown_model";
        const viewId = this.props.archInfo?.viewId || this.props.list?.viewId;
        if (viewId) {
            return `tree_column_${type}:${resModel}:${viewId}`;
        }

        const columnSignature = table ? this._getColumnStorageSignature(table) : "unknown_view";
        return `tree_column_${type}:${resModel}:${columnSignature}`;
    },

    _getColumnReorderStorageKey(table = null) {
        return this._getColumnStorageKey("reorder", table);
    },

    _getColumnWidthBaseStorageKey(table = null) {
        return this._getColumnStorageKey("width_cache", table);
    },

    _getColumnWidthStorageKey(table = null) {
        const baseKey = this._getColumnWidthBaseStorageKey(table);
        const screenKey = this._getColumnWidthScreenStorageKey();
        return screenKey ? `${baseKey}:${screenKey}` : baseKey;
    },

    _getLegacyColumnWidthBaseStorageKey(table = null) {
        return this._getColumnStorageKey("width", table);
    },

    _getLegacyColumnWidthStorageKey(table = null) {
        const baseKey = this._getLegacyColumnWidthBaseStorageKey(table);
        const screenKey = this._getColumnWidthScreenStorageKey();
        return screenKey ? `${baseKey}:${screenKey}` : baseKey;
    },

    _getColumnWidthCacheStorageKeys(table = null) {
        return [
            this._getColumnWidthStorageKey(table),
            this._getColumnWidthBaseStorageKey(table),
            this._getLegacyColumnWidthStorageKey(table),
            this._getLegacyColumnWidthBaseStorageKey(table),
            this._getLegacyColumnStorageKey("width"),
        ].filter((key, index, keys) => key && keys.indexOf(key) === index);
    },

    _getColumnWidthScreenStorageKey() {
        const hashParams = new URLSearchParams(window.location.hash.replace(/^#/, ""));
        const actionId = this.env?.config?.actionId || hashParams.get("action");
        const menuId = this.env?.config?.menuId || hashParams.get("menu_id");
        const viewType = this.env?.config?.viewType || hashParams.get("view_type") || "list";
        const parts = [
            actionId ? `action=${actionId}` : "",
            menuId ? `menu=${menuId}` : "",
            viewType ? `view=${viewType}` : "",
        ].filter(Boolean);

        return parts.length ? parts.join("|") : "";
    },

    _getLegacyColumnStorageKey(type) {
        const resModel = this.props.list?.resModel || "unknown_model";
        return `tree_column_${type}:${resModel}:unknown_view`;
    },

    _getStoredColumnValue(storageKey, legacyStorageKey, fallbackValue) {
        const storedValue = localStorage.getItem(storageKey);
        if (storedValue !== null || storageKey === legacyStorageKey) {
            return storedValue ?? fallbackValue;
        }
        return localStorage.getItem(legacyStorageKey) ?? fallbackValue;
    },

    _getColumnStorageSignature(table) {
        const names = this._getColumnHeaders(table).map((header) => header.dataset.name).filter(Boolean);
        return names.length ? [...names].sort().join("|") : "unknown_view";
    },

    _getColumnHeaderRow(table) {
        return table.querySelector("thead tr");
    },

    _getColumnHeaders(table) {
        const headerRow = this._getColumnHeaderRow(table);
        if (!headerRow) {
            return [];
        }
        return [...headerRow.children].filter(
            (th) => th.dataset.name && !th.classList.contains("o_list_record_selector")
        );
    },

    _setupColumnReorder() {
        const table = this.tableRef?.el || this.el?.querySelector("table.o_list_table");
        if (!table || !table.querySelector("thead")) {
            return;
        }

        this._cleanupColumnReorderHandlers({ flushWidths: true });
        this._ensureColumnReorderBaseOrder(table);
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

    _cleanupColumnReorderHandlers({ flushWidths = false } = {}) {
        if (flushWidths) {
            this._flushPendingColumnWidthPersistence();
        }
        if (this._columnWidthResizeObserver) {
            this._columnWidthResizeObserver.disconnect();
            this._columnWidthResizeObserver = null;
        }
        for (const entry of this._columnReorderHandlers) {
            for (const [eventName, fn, options] of entry.listeners) {
                entry.element.removeEventListener(eventName, fn, options);
            }
        }
        this._columnReorderHandlers = [];
    },

    _flushPendingColumnWidthPersistence() {
        if (this._columnWidthPersistTimeout) {
            clearTimeout(this._columnWidthPersistTimeout);
            this._columnWidthPersistTimeout = null;
        }

        const resizeState = this._columnWidthResizeState;
        if (
            resizeState?.table &&
            this._isTableUsableForWidthPersistence(resizeState.table) &&
            this._hasColumnWidthChanged(resizeState.table, resizeState.widths)
        ) {
            this._persistCurrentColumnWidths(resizeState.table);
        }
        this._columnWidthResizeState = null;

        if (this._columnWidthPendingWidths) {
            this._persistColumnWidths(
                this._columnWidthPendingWidths,
                null,
                this._columnWidthPendingStorageKey,
                this._columnWidthPendingBaseStorageKey
            );
        }
        this._columnWidthPersistTable = null;
        this._columnWidthPendingWidths = null;
        this._columnWidthPendingStorageKey = null;
        this._columnWidthPendingBaseStorageKey = null;
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
            const widths = this._getCurrentColumnWidths(table);
            const storageKey = this._getColumnWidthStorageKey(table);
            const baseStorageKey = this._getColumnWidthBaseStorageKey(table);
            this._persistColumnWidths(widths, table, storageKey, baseStorageKey);
            this._columnWidthPersistTable = table;
            this._columnWidthPendingWidths = widths;
            this._columnWidthPendingStorageKey = storageKey;
            this._columnWidthPendingBaseStorageKey = baseStorageKey;
            this._columnWidthPersistTimeout = setTimeout(() => {
                this._flushPendingColumnWidthPersistence();
            }, 100);
        };

        if (this._columnWidthResizeObserver) {
            this._columnWidthResizeObserver.disconnect();
        }
        if (window.ResizeObserver) {
            this._columnWidthResizeObserver = new ResizeObserver(() => persistWidths());
        }
        headers.forEach((header) => {
            this._columnWidthResizeObserver?.observe(header);

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
                    document.removeEventListener("pointerup", onResizeEnd, true);
                    document.removeEventListener("pointercancel", onResizeEnd, true);

                    const resizeState = this._columnWidthResizeState;
                    [0, 100, 300].forEach((delay) => {
                        setTimeout(() => {
                            if (!resizeState?.table || !this._isTableUsableForWidthPersistence(resizeState.table)) {
                                return;
                            }
                            if (this._hasColumnWidthChanged(resizeState.table, resizeState.widths)) {
                                persistWidths();
                            }
                            if (this._columnWidthResizeState === resizeState) {
                                this._columnWidthResizeState = null;
                            }
                        }, delay);
                    });
                };

                document.addEventListener("mouseup", onResizeEnd, true);
                document.addEventListener("touchend", onResizeEnd, true);
                document.addEventListener("touchcancel", onResizeEnd, true);
                document.addEventListener("pointerup", onResizeEnd, true);
                document.addEventListener("pointercancel", onResizeEnd, true);
            };

            const onAutoResize = (ev) => {
                if (this._isColumnResizeEvent(ev, header)) {
                    persistWidths();
                }
            };

            header.addEventListener("mousedown", onResizeStart, true);
            header.addEventListener("touchstart", onResizeStart, true);
            header.addEventListener("pointerdown", onResizeStart, true);
            header.addEventListener("dblclick", onAutoResize, true);
            this._columnReorderHandlers.push({
                element: header,
                listeners: [
                    ["mousedown", onResizeStart, true],
                    ["touchstart", onResizeStart, true],
                    ["pointerdown", onResizeStart, true],
                    ["dblclick", onAutoResize, true],
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

    _isTableUsableForWidthPersistence(table) {
        return Boolean(table?.isConnected && table.offsetParent !== null);
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

    _ensureColumnReorderBaseOrder(table) {
        const currentOrder = [...(this._getColumnHeaderRow(table)?.children || [])].map(
            (header, index) => header.dataset.name || `__column_${index}`
        );
        const currentNamedColumns = currentOrder.filter((name) => !name.startsWith("__column_"));
        const baseNamedColumns = (this._columnReorderBaseOrder || []).filter((name) => !name.startsWith("__column_"));
        const hasSameColumns =
            currentNamedColumns.length === baseNamedColumns.length &&
            currentNamedColumns.every((name) => baseNamedColumns.includes(name));

        if (!hasSameColumns) {
            this._columnReorderBaseOrder = currentOrder;
        }
    },

    _getBaseColumnOrder(table) {
        return this._columnReorderBaseOrder || [...(this._getColumnHeaderRow(table)?.children || [])].map(
            (header, index) => header.dataset.name || `__column_${index}`
        );
    },

    _getDesiredColumnOrder(table, savedOrder) {
        const baseOrder = this._getBaseColumnOrder(table);
        const savedNames = new Set(savedOrder);
        const orderedNames = savedOrder.filter((name) => baseOrder.includes(name));
        const remainingColumns = baseOrder.filter((name) => !savedNames.has(name));
        return [...remainingColumns.filter((name) => name.startsWith("__column_")), ...orderedNames, ...remainingColumns.filter((name) => !name.startsWith("__column_"))];
    },

    _reorderCells(row, currentOrder, desiredOrder) {
        const cellsByName = new Map();
        [...row.children].forEach((cell, index) => {
            const name = currentOrder[index];
            if (name && !cellsByName.has(name)) {
                cellsByName.set(name, cell);
            }
        });

        desiredOrder.forEach((name) => {
            const cell = cellsByName.get(name);
            if (cell) {
                row.appendChild(cell);
            }
        });
        row.dataset.columnReorderOrder = JSON.stringify(desiredOrder);
    },

    _applySavedColumnOrder(table) {
        const storageKey = this._getColumnReorderStorageKey(table);
        let savedOrder = [];
        try {
            savedOrder = JSON.parse(
                this._getStoredColumnValue(storageKey, this._getLegacyColumnStorageKey("reorder"), "[]")
            );
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

        const desiredOrder = this._getDesiredColumnOrder(table, savedOrder);
        const headerRows = table.querySelectorAll("thead tr");
        headerRows.forEach((row) => {
            const currentOrder = [...row.children].map((cell, index) => cell.dataset.name || `__column_${index}`);
            this._reorderCells(row, currentOrder, desiredOrder);
        });

        const colgroupCols = table.querySelectorAll("colgroup col");
        if (colgroupCols.length) {
            const currentOrder = [...colgroupCols].map((col, index) => col.dataset.columnReorderName || `__column_${index}`);
            colgroupCols.forEach((col, index) => {
                col.dataset.columnReorderName = currentOrder[index];
            });
            this._reorderCells(colgroupCols[0].parentElement, currentOrder, desiredOrder);
        }

        table.querySelectorAll("tbody tr, tfoot tr").forEach((row) => {
            let currentOrder = null;
            try {
                currentOrder = JSON.parse(row.dataset.columnReorderOrder || "null");
            } catch {
                currentOrder = null;
            }
            if (!currentOrder || currentOrder.length !== row.children.length) {
                currentOrder = this._getBaseColumnOrder(table);
            }
            this._reorderCells(row, currentOrder, desiredOrder);
        });
    },

    _moveColumnByName(table, sourceName, targetName, persist = true) {
        if (!sourceName || !targetName || sourceName === targetName) {
            return;
        }

        const headerRow = this._getColumnHeaderRow(table);
        const headers = headerRow ? [...headerRow.children] : [];
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

        const currentOrder = [...(this._getColumnHeaderRow(table)?.children || [])].map(
            (header, index) => header.dataset.name || `__column_${index}`
        );
        table.querySelectorAll("tr").forEach((row) => {
            row.dataset.columnReorderOrder = JSON.stringify(currentOrder);
        });

        if (persist) {
            this._persistCurrentColumnOrder(table);
        }
    },

    _persistCurrentColumnOrder(table) {
        const storageKey = this._getColumnReorderStorageKey(table);
        const order = this._getColumnHeaders(table).map((header) => header.dataset.name);
        localStorage.setItem(storageKey, JSON.stringify(order));
    },

    _applySavedColumnWidths(table) {
        const storageKey = this._getColumnWidthStorageKey(table);
        let savedWidths = {};
        try {
            savedWidths = JSON.parse(
                this._getColumnWidthCacheStorageKeys(table)
                    .map((key) => localStorage.getItem(key))
                    .find((value) => value) || "{}"
            );
        } catch {
            savedWidths = {};
        }
        if (!savedWidths || typeof savedWidths !== "object") {
            return;
        }

        const headers = this._getColumnHeaders(table);
        headers.forEach((header) => {
            const index = [...header.parentElement.children].indexOf(header);
            const name = header.dataset.name;
            const width = name ? savedWidths[name] : null;
            if (!width) {
                return;
            }
            const widthValue = `${width}px`;
            const col = table.querySelector(`colgroup col:nth-child(${index + 1})`);
            if (col) {
                this._setColumnWidthStyle(col, widthValue);
            }
            table.querySelectorAll("tr").forEach((row) => {
                const cell = row.children[index];
                if (cell) {
                    this._setColumnWidthStyle(cell, widthValue);
                }
            });
        });
    },

    _setColumnWidthStyle(element, widthValue) {
        element.style.setProperty("width", widthValue, "important");
        element.style.setProperty("min-width", widthValue, "important");
    },

    _persistCurrentColumnWidths(table) {
        this._persistColumnWidths(this._getCurrentColumnWidths(table), table);
    },

    _persistColumnWidths(widths, table = null, storageKey = null, baseStorageKey = null) {
        storageKey = storageKey || this._getColumnWidthStorageKey(table);
        baseStorageKey = baseStorageKey || (table ? this._getColumnWidthBaseStorageKey(table) : storageKey);
        const validWidths = {};
        Object.entries(widths || {}).forEach(([name, width]) => {
            if (name && width > 0) {
                validWidths[name] = width;
            }
        });
        if (!Object.keys(validWidths).length) {
            return;
        }

        let savedWidths = {};
        try {
            savedWidths = JSON.parse(localStorage.getItem(storageKey) || "{}");
        } catch {
            savedWidths = {};
        }
        const nextWidths = JSON.stringify({ ...savedWidths, ...validWidths });
        localStorage.setItem(storageKey, nextWidths);

        if (baseStorageKey !== storageKey) {
            let savedBaseWidths = {};
            try {
                savedBaseWidths = JSON.parse(localStorage.getItem(baseStorageKey) || "{}");
            } catch {
                savedBaseWidths = {};
            }
            localStorage.setItem(baseStorageKey, JSON.stringify({ ...savedBaseWidths, ...validWidths }));
        }
    },
});
