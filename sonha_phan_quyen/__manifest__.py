# -*- coding: utf-8 -*-
{
    'name': 'Sơn Hà Phân quyền',
    'version': '1.0',
    'summary': 'Module cung cấp thông tin user và phân quyền',
    'author': 'TrungNT2',
    'depends': ['base', 'hr'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sonha_user_views.xml',
        'views/sonha_phan_quyen_views.xml',
    ],
    'installable': True,
    'application': False,
}
