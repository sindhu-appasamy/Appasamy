# -*- coding: utf-8 -*-

{
    'name': 'Daily Report',
    'author': 'Sindhuja',
    'category': 'Operation/Inventory',
    'summary': 'Daily Production , Outward report',
    'version': '13.0',
    'depends': ['base','account','grn_report','sale_fields'],
    'data': [
    'security/security.xml',
    'security/ir.model.access.csv',
    'views/views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}