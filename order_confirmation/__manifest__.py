# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'order confirmation',
    'author': 'Bala',
    'category': 'Operations/Inventory',
    'summary': 'Order Confirmation Report',
    'version': '13.0',
    'depends': ['base'],
    'data': [
    'views/views.xml',
    'security/ir.model.access.csv',
    'security/security.xml',
    ],
    'installable': True,
    'application': True,
}