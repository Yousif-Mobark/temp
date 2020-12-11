# -*- coding: utf-8 -*-
{
    'name': "Project Agreement Sales",

    'summary': """
       Project Agreement Sales""",

    'description': """
        keep track of line that deliver to custome , and update Qty and revinue reports 
        track residual Qty , and not delivered line
    """,

    'author': "Diot",
    'website': "http://www.diot.com.sa",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale_management','project_agreement'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/agreement_sale_wiz_view.xml',
        'views/views.xml',
        'views/templates.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}