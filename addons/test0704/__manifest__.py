# -*- coding: utf-8 -*-
{
    'name': "openacademy",

    'summary': """
        軟體的文字說明
    """,

    'description': """
        軟體更長的文字說明
    """,

    'author': "Alltop",
    'website': "http://www.alltop.com",
    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base','sale','report'],

    'data': [
        'views/openacademy.xml',
        'views/partner.xml',
        'views/donate_single.xml',
        'views/donate_order.xml',
        'views/sale_order_view.xml',
        'wizard/wizard_abandon_single.xml',

        # 'report/donate_single_report.xml',
        'report/donate_single_report_print.xml',
        'report/report_donate_single.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}