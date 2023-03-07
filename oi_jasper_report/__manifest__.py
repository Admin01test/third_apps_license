# -*- coding: utf-8 -*-
# Copyright 2018 Openinside co. W.L.L.
{
    "name": "Jasper Report Integration",
    "summary": "Jasper Report Server Integration, Jasper Report, Jasper Integration, Jasper Connector, Jasper View",
    "version": "14.0.1.1.11",
    'category': 'Extra Tools',
    "website": "https://www.open-inside.com",
	"description": """
		execute report in jasper report server from odoo		 
    """,
    "author": "Openinside",
    "license": "OPL-1",
    "price" : 50,
    "currency": 'EUR',
    "installable": True,
    "depends": [
        'web', 'oi_action_file', 'oi_pdf_viewer'
    ],
    "data": [
        'views/action.xml',
        'views/res_config_settings.xml',
        'views/jasper_report.xml',
        'views/jasper_report_run.xml',        
        'views/menu.xml',
        'security/ir.model.access.csv'
    ],
    'qweb' : [
        
    ],
    'external_dependencies' : {
        
    },    
    'installable': True,
    'auto_install': False,    
    'odoo-apps' : True,
    'images':[
        'static/description/cover.png'
    ],        
}

