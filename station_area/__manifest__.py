# -*- coding: utf-8 -*-
{
    'name': "Satation And Area",

    'summary': """
        Add Station And Area Information""",

    'description': """
        Make Purchase Order Related To Station And Area
        / Make Project Related To Station And Area
        / Every Station And Area Have Manager
    """,

    'author': "Diot",
    'website': "http://www.diot.com.sa",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project_agreement','purchase_requisition'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/project_station_area_groups.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
