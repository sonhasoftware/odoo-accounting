/** @odoo-module */

import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";

const SESSION_CHECK_INTERVAL = 3000;

export const sonhaSessionAliveService = {
    dependencies: ["rpc"],
    start(env, { rpc }) {
        let isChecking = false;

        const checkSession = async () => {
            if (isChecking) {
                return;
            }

            isChecking = true;
            try {
                const result = await rpc("/sonha/session/is_alive", {});
                if (result && result.is_alive === false) {
                    browser.location.href = "/web/session/logout?redirect=/web/login";
                }
            } catch {
                // Ignore transient network/RPC errors; the next interval will check again.
            } finally {
                isChecking = false;
            }
        };

        const intervalId = browser.setInterval(checkSession, SESSION_CHECK_INTERVAL);
        browser.addEventListener("beforeunload", () => browser.clearInterval(intervalId));
    },
};

registry.category("services").add("sonha_session_alive", sonhaSessionAliveService);
