# -*- coding: utf-8 -*-
{
    'name': "Stock Internal Transit Valuation",
    'name_vi_VN': "Định Giá Chuyển Tiếp Kho",
    
    'old_technical_name': "to_transit_loc_accounts",
    
    'summary': """Automatically create accounting entries when validating stock move between internal and transit locations.""",
    'summary_vi_VN': """Tự động tạo bút toán kế toán khi thực hiện dịch chuyển kho giữa các địa điểm kiểu nội bộ và chuyển tiếp (theo 2 chiều)
        """,

    'description': """
What it does
============
* Unhide stock valuation account fields on the location form with usage = transit (transit location).
* This provides more control on stock input/output valuation during accounting journal entries creation.
* Automatically create accounting entries when validating stock move between internal and transit locations.
* Create stock valuation layer for changing stock valuation of products.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Ứng dụng này làm gì
===================
* Bỏ ẩn các trường tài khoản định giá tồn kho trên biểu mẫu địa điểm với usage = transit (địa điểm chuyển tiếp).
* Điều này cung cấp thêm quyền kiểm soát đối với định giá nhập / xuất tồn kho trong quá trình tạo bút toán kế toán. 
* Tự động tạo bút toán kế toán khi thực hiện dịch chuyển kho giữa các địa điểm kiểu nội bộ và chuyển tiếp (theo 2 chiều)
* Tạo các bản ghi stock valuation layer để thể hiện việc thay đổi giá trị hàng hóa trong kho

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
   'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock_account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_account_view.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
