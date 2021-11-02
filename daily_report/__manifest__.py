# -*- coding: utf-8 -*-
{
    'name': 'Daily Report',
    'author': 'Sindhuja',
    'category': 'Operation/Inventory',
    'summary': 'Daily Production , Outward report',
    'version': '13.0',
    'depends': ['base','account'],
    'data': [
    'security/security.xml',
    'security/ir.model.access.csv',
    'views/views.xml',
    'wizard/daily_report_export.xml',
    ],
    'installable': True,
    'application': False,
}