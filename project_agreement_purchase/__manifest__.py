# -*- coding: utf-8 -*-
{
    'name': "Project Agreement Purchase Management",

    'summary': """
        Manage Agreement Purchase (QTY , Cost , Invoices)""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Diot",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['project_agreement','station_area','purchase_requisition'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/agreement_purchase_security_rule.xml',
        'views/views.xml',
        'views/templates.xml',
        'wizard/project_agreement_tender.xml',
        'views/agreemnt_line_views.xml',
        'views/purchase_view.xml',
        'report/purchase_order_contract.xml',
        'report/purchase_reports_contract.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}