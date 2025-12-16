/** @odoo-module **/

/*
  Safe version:
  - Chỉ init khi DOM ready
  - Kiểm tra target nodes trước khi observe
  - Không gọi observe với null
  - Throttle nhẹ khi re-sync để tránh chạy quá nhiều lần
*/

function debounce(fn, delay) {
    let t;
    return function() {
        clearTimeout(t);
        const args = arguments;
        t = setTimeout(() => fn.apply(this, args), delay);
    };
}

function findOne2manyTable() {
    // tìm table one2many rõ ràng đã gán class parent-one2many
    return document.querySelector('.parent-one2many table.o_list_table') ||
           document.querySelector('table.o_list_table');
}

function getVisibleChildFields(table) {
    if (!table) return [];
    const visible = [];
    const ths = table.querySelectorAll('thead th');
    ths.forEach(th => {
        // Odoo thường set data-name hoặc data-field
        const fname = (th.dataset && (th.dataset.name || th.dataset.field)) || null;
        // kiểm tra visible: style.display != 'none' và offsetParent != null
        const isVisible = (th.style.display !== 'none') && (th.offsetParent !== null);
        if (fname && isVisible) visible.push(fname);
        else if (!fname && isVisible) {
            // fallback lấy text (cần map nếu label khác tên field)
            const txt = (th.textContent || '').trim();
            if (txt) visible.push(txt);
        }
    });
    return visible;
}

function syncParentFieldsVisibilityOnce() {
    const table = findOne2manyTable();
    const parentGroups = document.querySelectorAll('.parent-fields');

    if (!table || !parentGroups || parentGroups.length === 0) return;

    const visibleFields = getVisibleChildFields(table);

    parentGroups.forEach(group => {
        // tìm tất cả label + field inputs bên trong group
        // giả sử label[for="FIELD"] và field có attribute name="FIELD"
        const labels = group.querySelectorAll('label[for]');
        labels.forEach(lbl => {
            const fname = lbl.getAttribute('for');
            if (!fname) return;
            const fieldEl = group.querySelector(`[name="${fname}"]`) || group.querySelector(`[data-field="${fname}"]`);
            const container = fieldEl ? fieldEl.closest('.form-row') || fieldEl.parentElement : lbl.parentElement;
            if (!container) return;

            if (visibleFields.includes(fname)) {
                // ẩn parent container nếu child đang visible
                container.dataset._hiddenBySync = '1';
                container.style.display = 'none';
            } else {
                // chỉ khôi phục nếu trước đó script đã ẩn nó
                if (container.dataset._hiddenBySync === '1') {
                    container.style.removeProperty('display');
                    delete container.dataset._hiddenBySync;
                }
            }
        });

        // Ngoài label, kiểm tra trực tiếp các element có attribute name
        group.querySelectorAll('[name]').forEach(el => {
            const fname = el.getAttribute('name');
            if (!fname) return;
            // nếu đã xử lý thông qua label, skip để tránh double work
            const lbl = group.querySelector(`label[for="${fname}"]`);
            if (lbl) return;
            const container = el.closest('.form-row') || el.parentElement;
            if (!container) return;
            if (visibleFields.includes(fname)) {
                container.dataset._hiddenBySync = '1';
                container.style.display = 'none';
            } else {
                if (container.dataset._hiddenBySync === '1') {
                    container.style.removeProperty('display');
                    delete container.dataset._hiddenBySync;
                }
            }
        });
    });
}

const syncDebounced = debounce(syncParentFieldsVisibilityOnce, 80);

function initObservers() {
    const body = document.body;
    if (!(body && body.nodeType === 1)) {
        // nếu DOM chưa có, đợi DOMContentLoaded
        return;
    }

    // Initial run (có thể table chưa render ngay lập tức)
    setTimeout(syncDebounced, 80);

    // Observe the whole form area (body) but chỉ nếu body hợp lệ
    const mainObserver = new MutationObserver((mutations) => {
        // mỗi lần có thay đổi lớn, debounce sync
        syncDebounced();
    });

    // Lưu ý: only observe if body is a Node
    try {
        mainObserver.observe(body, { childList: true, subtree: true, attributes: true });
    } catch (err) {
        // fallback: không crash
        console.warn('auto_toggle_parent_fields: observer not started', err);
    }

    // Additionally observe the specific table's thead for attribute changes (th hide/show)
    const table = findOne2manyTable();
    if (table) {
        const thead = table.querySelector('thead');
        if (thead) {
            try {
                new MutationObserver(syncDebounced).observe(thead, { attributes: true, subtree: true, attributeFilter: ['style', 'class'] });
            } catch (e) { /* ignore */ }
        }
        const tbody = table.querySelector('tbody');
        if (tbody) {
            try {
                new MutationObserver(syncDebounced).observe(tbody, { childList: true, subtree: true });
            } catch (e) { /* ignore */ }
        }
    }
}

// Start when DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initObservers();
    });
} else {
    // already ready
    initObservers();
}
