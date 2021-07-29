# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Report-Category',
    'author': 'Sindhuja',
    'category': 'Accounting',
    'summary': 'Category Report',
    'version': '13.0',
    'depends': ['base','account'],
    'data': [
    'views/views.xml',
    'security/ir.model.access.csv',
    'security/security.xml',
    ],
    'installable': True,
    'application': True,
}
