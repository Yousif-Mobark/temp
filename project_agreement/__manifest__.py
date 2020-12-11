# -*- coding: utf-8 -*-
{
    'name': "Project Agreement",

    'summary': """
        Project Agreement Module""",

    'description': """
        Project Agreement Module
    """,

    'author': "E.Mudathir",
    'website': "http://www.diot.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'project',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['project','purchase' ,'account_invoicing', 'account_budget','hr_user_group'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/agreement_security_rule.xml',
        'security/ir.model.access.csv',
        'views/agreement_view.xml',
        'views/templates.xml',
        'views/agreement_budget.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
