# -*- coding: utf-8 -*-
{
    'name': "Project Emergency",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "DIOT",
    'website': "http://diot.com.sa",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['station_area','product','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/project_emerg_groups.xml',
        'data/data.xml',
        'wizard/project_emergency_invoice.xml',
	    'data/ir_sequence_data.xml',
        'views/project_emergency_view.xml',
        'views/emergency_config.xml',
        'views/emergency_line_view.xml',
        'views/account_invoice_view.xml',
    ],

}
