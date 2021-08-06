# -*- coding: utf-8 -*-
{
    'name': 'Report-Category',
    'author': 'Sindhuja',
    'category': 'Accounting',
    'summary': 'Categorywise Report',
    'version': '13.0',
    'depends': ['base','account','product','contacts'],
    'data': [
    'views/views.xml',
    'security/ir.model.access.csv',
    'security/security.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

