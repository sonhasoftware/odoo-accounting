/** @odoo-module */

import { ListRenderer } from "@web/views/list/list_renderer";
import { useBus, useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
import { onMounted, onPatched, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

patch(ListRenderer.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this._columnPreferenceCache = new Map();
        this._columnPreferenceLoading = new Set();
        this._columnReorderHandlers = [];
        this._columnWidthPersistTimeout = null;
        this._columnWidthPersistTable = null;
        this._columnWidthPendingWidths = null;
        this._columnWidthPendingStorageKey = null;
        this._columnWidthPendingBaseStorageKey = null;
        this._columnWidthResizeState = null;
        this._columnPreferencePersistTimeouts = new Map();
        this._columnWidthBeforeUnload = () => this._flushPendingColumnWidthPersistence();
        window.addEventListener("beforeunload", this._columnWidthBeforeUnload);
        onMounted(() => this._setupColumnReorder());
        onPatched(() => this._setupColumnReorder());
        onWillUnmount(() => {
            this._cleanupColumnReorderHandlers();
            this._cleanupColumnResizePersistenceHandlers();
        });
    },

    _getColumnStorageViewId() {
        const viewId = this.env.config.viewId;
        return Number.isInteger(viewId) ? viewId : null;
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
        const legacyBaseKey = this._getLegacyColumnWidthBaseStorageKey(table);
        const legacyScreenKey = this._getLegacyColumnWidthStorageKey(table);
        const unknownViewBaseKey = this._getColumnStorageKey("width_cache");
        const unknownViewScreenKey = this._getColumnWidthScreenStorageKey()
            ? `${unknownViewBaseKey}:${this._getColumnWidthScreenStorageKey()}`
            : unknownViewBaseKey;

        return [
            this._getColumnWidthStorageKey(table),
            this._getColumnWidthBaseStorageKey(table),
            unknownViewScreenKey,
            unknownViewBaseKey,
            legacyScreenKey,
            legacyBaseKey,
            this._getLegacyColumnStorageKey("width"),
            ...this._getMatchingColumnWidthStorageKeys(),
        ].filter((key, index, keys) => key && keys.indexOf(key) === index);
    },

    _getMatchingColumnWidthStorageKeys() {
        const resModel = this.props.list?.resModel || "unknown_model";
        const prefixes = [`tree_column_width_cache:${resModel}:`, `tree_column_width:${resModel}:`];
        const matchingKeys = [];
        for (let index = 0; index < localStorage.length; index++) {
            const key = localStorage.key(index);
            if (key && prefixes.some((prefix) => key.startsWith(prefix))) {
                matchingKeys.push(key);
            }
        }
        return matchingKeys;
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
        const cachedValue = this._columnPreferenceCache.get(storageKey);
        if (cachedValue !== undefined) {
            return cachedValue ?? fallbackValue;
        }
        const storedValue = localStorage.getItem(storageKey);
        if (storedValue !== null || storageKey === legacyStorageKey) {
            return storedValue ?? fallbackValue;
        }
        const legacyValue = this._columnPreferenceCache.get(legacyStorageKey);
        if (legacyValue !== undefined) {
            return legacyValue ?? fallbackValue;
        }
        return localStorage.getItem(legacyStorageKey) ?? fallbackValue;
    },

    _loadColumnPreferences(keys, table = null) {
        const missingKeys = keys.filter(
            (key) => key && !this._columnPreferenceCache.has(key) && !this._columnPreferenceLoading.has(key)
        );
        if (!missingKeys.length) {
            return;
        }
        missingKeys.forEach((key) => this._columnPreferenceLoading.add(key));
        this.orm
            .call("tree.view.column.preference", "get_values", [missingKeys])
            .then((values) => {
                Object.entries(values || {}).forEach(([key, value]) => {
                    this._columnPreferenceCache.set(key, value);
                    localStorage.setItem(key, value);
                });
                if (table?.isConnected && Object.keys(values || {}).length) {
                    this._applySavedColumnOrder(table);
                    this._applySavedColumnWidths(table);
                }
            })
            .catch(() => {})
            .finally(() => {
                missingKeys.forEach((key) => this._columnPreferenceLoading.delete(key));
            });
    },

    _persistColumnPreference(key, value) {
        if (!key) {
            return;
        }
        this._columnPreferenceCache.set(key, value);
        localStorage.setItem(key, value);
        if (this._columnPreferencePersistTimeouts.has(key)) {
            clearTimeout(this._columnPreferencePersistTimeouts.get(key));
        }
        this._columnPreferencePersistTimeouts.set(
            key,
            setTimeout(() => {
                this._columnPreferencePersistTimeouts.delete(key);
                this.orm.call("tree.view.column.preference", "set_value", [key, value]).catch(() => {});
            }, 250)
        );
    },

    _getColumnStorageSignature(table) {
        const names = this._getColumnHeaders(table).map((header) => header.dataset.name).filter(Boolean);
        return names.length ? [...names].sort().join("|") : "unknown_view";
    },

    _getColumnHeaderRow(table) {
        return table.querySelector("thead tr");
    },

    _getColumnHeaders(table) {
        return [...table.querySelectorAll("thead > tr:first-child > th")].filter(
            (th) => th.dataset.name && !th.classList.contains("o_list_record_selector")
        );
    },

    _canCustomizeColumns() {
        return Boolean(
            this.env.services.tree_view_column_layout.isAdmin && this._getColumnStorageViewId()
        );
    },

    getActiveColumns(list) {
        return this._sortColumnsBySharedOrder(super.getActiveColumns(list));
    },

    _sortColumnsBySharedOrder(columns) {
        const savedOrder = this._getColumnLayout()?.order || [];
        if (!savedOrder.length) {
            return columns;
        }

        const savedRank = new Map(savedOrder.map((name, index) => [name, index]));
        const indexes = [];
        const orderedColumns = [];
        columns.forEach((column, index) => {
            if (column.type === "field" && savedRank.has(column.name)) {
                indexes.push(index);
                orderedColumns.push(column);
            }
        });
        orderedColumns.sort((left, right) => savedRank.get(left.name) - savedRank.get(right.name));
        if (orderedColumns.length < 2) {
            return columns;
        }

        const result = [...columns];
        indexes.forEach((columnIndex, index) => {
            result[columnIndex] = orderedColumns[index];
        });
        return result;
    },

    _setupColumnCustomization() {
        const table = this.tableRef?.el;
        if (!table || !table.querySelector("thead")) {
            return;
        }

        this._cleanupColumnReorderHandlers({ flushWidths: true });
        this._ensureColumnReorderBaseOrder(table);
        this._loadColumnPreferences([
            this._getColumnReorderStorageKey(table),
            this._getLegacyColumnStorageKey("reorder"),
            ...this._getColumnWidthCacheStorageKeys(table),
        ], table);
        this._applySavedColumnOrder(table);
        this._applySavedColumnWidths(table);
        this._setupColumnWidthPersistence(table);

        for (const header of this._getColumnHeaders(table)) {
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
            const onDragLeave = () => header.classList.remove("o_col_reorder_over");
            const onDrop = (ev) => {
                ev.preventDefault();
                const sourceName = ev.dataTransfer.getData("text/plain");
                const targetName = header.dataset.name;
                this._clearDragIndicators(table);
                this._reorderColumnsByName(sourceName, targetName);
            };

            const listeners = [
                ["dragstart", onDragStart],
                ["dragend", onDragEnd],
                ["dragover", onDragOver],
                ["dragleave", onDragLeave],
                ["drop", onDrop],
            ];
            for (const [eventName, fn] of listeners) {
                header.addEventListener(eventName, fn);
            }
            this._columnReorderHandlers.push({ element: header, listeners });
        }
    },

    _clearDragIndicators(table) {
        table
            .querySelectorAll(".o_col_reorder_over")
            .forEach((el) => el.classList.remove("o_col_reorder_over"));
    },

    _cleanupColumnReorderHandlers() {
        for (const entry of this._columnReorderHandlers) {
            for (const [eventName, fn] of entry.listeners) {
                entry.element.removeEventListener(eventName, fn);
            }
            entry.element.removeAttribute("draggable");
            entry.element.classList.remove("o_col_reorder_draggable");
        }
        this._columnReorderHandlers = [];
    },

    _cleanupColumnResizePersistenceHandlers() {
        for (const [eventName, fn] of this._columnResizePersistenceHandlers) {
            window.removeEventListener(eventName, fn);
        }
        this._columnResizePersistenceHandlers = [];
    },

    onStartResize(ev) {
        if (!this._canCustomizeColumns()) {
            return;
        }

        const header = ev.target.closest("th[data-name]");
        const fieldName = header?.dataset.name;
        super.onStartResize(ev);
        if (!header || !fieldName) {
            return;
        }

        this._cleanupColumnResizePersistenceHandlers();
        const persistWidth = () => {
            this._cleanupColumnResizePersistenceHandlers();
            if (!header.isConnected) {
                return;
            }
            const width = Math.round(header.getBoundingClientRect().width);
            if (width > 0) {
                this.columnLayoutService.saveWidth(
                    this._getColumnStorageViewId(),
                    fieldName,
                    width
                );
            }
        };
        for (const eventName of ["pointerup", "keydown"]) {
            window.addEventListener(eventName, persistWidth);
            this._columnResizePersistenceHandlers.push([eventName, persistWidth]);
        }
    },

    _reorderColumnsByName(sourceName, targetName) {
        if (
            !this._canCustomizeColumns() ||
            !sourceName ||
            !targetName ||
            sourceName === targetName
        ) {
            return;
        }

        const columns = [...this.state.columns];
        const sourceIndex = columns.findIndex(
            (column) => column.type === "field" && column.name === sourceName
        );
        const targetIndex = columns.findIndex(
            (column) => column.type === "field" && column.name === targetName
        );
        if (sourceIndex < 0 || targetIndex < 0 || sourceIndex === targetIndex) {
            return;
        }

        const [sourceColumn] = columns.splice(sourceIndex, 1);
        columns.splice(targetIndex, 0, sourceColumn);
        this.state.columns = columns;
        const order = columns
            .filter((column) => column.type === "field" && column.name)
            .map((column) => column.name);
        this.columnLayoutService.saveOrder(this._getColumnStorageViewId(), order);
    },

    _persistCurrentColumnOrder(table) {
        const storageKey = this._getColumnReorderStorageKey(table);
        const order = this._getColumnHeaders(table).map((header) => header.dataset.name);
        this._persistColumnPreference(storageKey, JSON.stringify(order));
    },

    _applySavedColumnWidths(table) {
        const storageKey = this._getColumnWidthStorageKey(table);
        let savedWidths = {};
        try {
            savedWidths = JSON.parse(
                this._getColumnWidthCacheStorageKeys(table)
                    .map((key) => this._columnPreferenceCache.get(key) || localStorage.getItem(key))
                    .find((value) => value) || "{}"
            );
        } catch {
            savedWidths = {};
        }
        if (!savedWidths || typeof savedWidths !== "object") {
            return;
        }

        let tableWidth = table.getBoundingClientRect().width;
        let widthDelta = 0;
        for (const header of this._getColumnHeaders(table)) {
            const width = widths[header.dataset.name];
            if (!(width > 0)) {
                continue;
            }
            const currentWidth = header.getBoundingClientRect().width;
            widthDelta += width - currentWidth;
            const widthValue = `${width}px`;
            header.style.width = widthValue;
            header.style.maxWidth = widthValue;
        }
        tableWidth += widthDelta;
        if (tableWidth > 0) {
            table.style.width = `${Math.round(tableWidth)}px`;
            table.style.tableLayout = "fixed";
        }
    },

    _onSharedColumnLayoutUpdated({ detail: layout }) {
        if (layout.viewId !== this._getColumnStorageViewId()) {
            return;
        }
        this.keepColumnWidths = false;
        this.columnWidths = null;
        this.state.columns = this.getActiveColumns(this.props.list);
    },

    resetColumnLayout() {
        if (this._canCustomizeColumns()) {
            this.columnLayoutService.reset(this._getColumnStorageViewId());
        }
    },
});
