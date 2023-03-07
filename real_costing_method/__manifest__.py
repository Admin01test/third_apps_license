# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018 Rightechs (<http://www.Rightechs.net/>)
#               <contact@rightechs.net>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Real Costing Method',
    'version': '14.0',
    'author':   "Rightechs Solutions",
    'website': 'http://rightechs.info',
    'category': 'Inventory',
    'description': """Cost Method Real Price""",
    'depends': [
                'base','sale','sale_management', 'purchase', 'product', 'stock', 'stock_account',
                'stock_landed_costs',
                ],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    "qweb":[
    ],
    'demo': [
    ],
    'test': [
    ],
    'css': [],
    "images": ['static/description/Banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'currency': 'USD',
    'price': 200,

}
