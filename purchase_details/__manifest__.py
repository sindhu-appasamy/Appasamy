# -*- coding: utf-8 -*-
{
    'name': 'purchase_order_details',
    'author': 'Sindhuja',
    'category': 'Operations/Purchase',
    'summary': 'Purchase Order Details',
    'version': '13.0',
    'depends': ['base','purchase'],
    'data': [
    'security/security.xml',
    'security/ir.model.access.csv',
    'views/views.xml',
    ],
    'installable': True,
    'application': True,
}
