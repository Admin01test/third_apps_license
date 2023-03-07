# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    'name': 'PDF Viewer',
    "summary": "PDF, PDF Viewer, PDF Preview, PDF Report",
    "category": "Extra Tools",
    
    "website": "https://www.open-inside.com",
    "author": "Openinside",
    "version": "14.0.1.1.4",
    "license": "OPL-1",
    "price" : 29.99,    
    "currency": 'EUR',
    'depends': [
        'web',
    ],    
    'data': [
        'view/assets_backend.xml'
    ],
    'images': [
            'static/description/cover.png'
        ],
    'qweb': [
        'static/src/xml/templates.xml'
        ],
    'installable': True,
    'odoo-apps' : True,
    'auto_install': True  
}
