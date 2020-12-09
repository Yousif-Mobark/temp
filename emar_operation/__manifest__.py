# -*- coding: utf-8 -*-
{
    'name': "EMAR Operation Module",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm', 'project', 'product', 'stock', 'analytic', 'purchase', 'account', 'sale', 'project_agreement'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/stock_security.xml',
        'views/working_items_views.xml',
        'views/crm_lead_views.xml',
        'views/product_views.xml',
        'views/analytic_account.xml',
        'views/account_bank_statement_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}