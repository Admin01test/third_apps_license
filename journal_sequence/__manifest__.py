# -*- coding: utf-8 -*-
{
    'name': 'Journal Sequence',
    'version': '14.0.1.3',
    'author': 'Grupo Nahuiik',
    'website': 'http://gruponahuiik.com',
    'description': """
                    Add sequence configuration for journal in odoo 14.
                    
                    Below are search tags.
                    custom journal sequence, odoo 14 journal sequence, account journal sequence, account journal sequence odoo 14.
                    
    """,
    'summary': """
                    Add sequence configuration for journal in odoo 14 same like previous odoo version.
    """,
    'depends': [
        'account',
    ],
    'data': [
        'views/account_journal_view.xml',
        'views/account_move_view.xml',
    ],
    "images": ['static/description/1.jpg'],

    'installable': True,
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 19.99
}
