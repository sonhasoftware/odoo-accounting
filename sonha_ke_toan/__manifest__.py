# -*- coding: utf-8 -*-
{
    'name': 'Sơn Hà Kế toán',
    'version': '1.0',
    'summary': 'Module Kế Toán',
    'author': 'TrungNT2',
    'depends': ['base'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/acc_tai_khoan_views.xml',
        'views/acc_kho_views.xml',
        'views/acc_bo_phan_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sonha_ke_toan/static/src/js/field_confirm_list_patch.js',
        ],
    },
    'installable': True,
    'application': False,
}
