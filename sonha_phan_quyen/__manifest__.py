# -*- coding: utf-8 -*-
{
    'name': 'Sơn Hà Phân quyền',
    'version': '1.0',
    'summary': 'Module cung cấp thông tin user và phân quyền',
    'author': 'TrungNT2',
    'depends': ['base', 'hr', 'web'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sonha_user_views.xml',
        'views/sonha_phan_quyen_views.xml',
        'views/sonha_phan_quyen_nl_views.xml',
        'views/sonha_xac_nhan_views.xml',
        'views/sonha_bt_them_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sonha_phan_quyen/static/src/js/sonha_user_list_buttons.js',
            'sonha_phan_quyen/static/src/js/session_alive_service.js',
            'sonha_phan_quyen/static/src/xml/sonha_user_list_buttons.xml',
        ],
    },
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
}
