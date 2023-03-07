# -*- coding: utf-8 -*-
{
    'name': "Odoo Gantt View Base",

    'summary': """
        Gantt Native Web view,Gantt Native Exchange for Project,gantt chart widget view,Gantt Native Report for Project,Gantt Native view for Leave,
        Gantt MRP,Project Gantt Native Web View,Project Gantt Native Web View,Base for Gantt view,Gantt View Time Off
        """,

    'description': """
        odoo gantt view
        base for odoo gantt view
        odoo 14 gantt view base
        odoo gantt view base in 14
        Odoo Gantt Base
    """,
    'author': "Ksolves India Ltd.",
    'license': 'OPL-1',
    'currency': 'EUR',
    'price': 190.0,
    'website': "https://store.ksolves.com",
    'maintainer': 'Ksolves India Ltd.',
    'category': 'Tools',
    'version': '14.0.1.0.3',
    'support': 'sales@ksolves.com',
    'depends': ['base', 'base_setup'],
    'images': [
        "static/description/blk_frd.jpg",
    ],
    'data': [
        'views/ks_gantt_view_assets.xml',
        'views/ks_res_config_settings_view.xml',
        'data/week_days_data.xml',
        'security/ir.model.access.csv',
    ],

    'qweb': [
        'static/src/xml/ks_gantt_view.xml',
        'static/src/xml/ks_recommend_color_picker.xml',
    ],
}
