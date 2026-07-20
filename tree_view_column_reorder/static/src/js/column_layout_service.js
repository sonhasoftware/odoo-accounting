/** @odoo-module */

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";
import { EventBus } from "@odoo/owl";

const MODEL = "tree.view.column.layout";
const NOTIFICATION_TYPE = "tree_view_column_layout/updated";

function normalizeLayout(layout) {
    if (!layout || !Number.isInteger(layout.viewId)) {
        return null;
    }
    return {
        viewId: layout.viewId,
        resModel: layout.resModel || "",
        order: Array.isArray(layout.order) ? layout.order : [],
        widths:
            layout.widths && typeof layout.widths === "object" && !Array.isArray(layout.widths)
                ? layout.widths
                : {},
        revision: Number.isInteger(layout.revision) ? layout.revision : 0,
    };
}

export const columnLayoutService = {
    dependencies: ["bus_service", "notification", "orm", "user"],

    start(env, { bus_service: busService, notification, orm, user }) {
        const eventBus = new EventBus();
        const layouts = new Map();
        let saveQueue = Promise.resolve();

        for (const layout of Object.values(session.tree_view_column_layouts || {})) {
            const normalized = normalizeLayout(layout);
            if (normalized) {
                layouts.set(normalized.viewId, normalized);
            }
        }

        const applyLayout = (layout) => {
            const normalized = normalizeLayout(layout);
            if (!normalized) {
                return null;
            }
            const current = layouts.get(normalized.viewId);
            if (current && current.revision >= normalized.revision) {
                return current;
            }
            layouts.set(normalized.viewId, normalized);
            eventBus.trigger("updated", normalized);
            return normalized;
        };

        const enqueueSave = (viewId, values) => {
            if (!user.isAdmin || !Number.isInteger(viewId)) {
                return Promise.resolve(null);
            }
            const execute = async () => {
                try {
                    const layout = await orm.call(MODEL, "save_layout", [viewId], values);
                    return applyLayout(layout);
                } catch (error) {
                    notification.add(_t("Could not save the shared column layout."), {
                        type: "danger",
                    });
                    return null;
                }
            };
            saveQueue = saveQueue.then(execute, execute);
            return saveQueue;
        };

        busService.subscribe(NOTIFICATION_TYPE, applyLayout);
        busService.start();

        return {
            bus: eventBus,
            isAdmin: user.isAdmin,
            get(viewId) {
                return Number.isInteger(viewId) ? layouts.get(viewId) || null : null;
            },
            saveOrder(viewId, order) {
                return enqueueSave(viewId, { column_order: order });
            },
            saveWidth(viewId, fieldName, width) {
                return enqueueSave(viewId, { width_updates: { [fieldName]: width } });
            },
            reset(viewId) {
                return enqueueSave(viewId, { reset: true });
            },
        };
    },
};

registry.category("services").add("tree_view_column_layout", columnLayoutService);
