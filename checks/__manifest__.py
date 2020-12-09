# -*- coding: utf-8 -*-
{
    'name': "Checks",

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
    'depends': ['base', 'account', 'account_invoicing','payment', 'account_payment_customization', 'emar_operation'],

    # always loaded
    'data': [
        'data/account_data.xml',
        'wizards/returned_wizard_view.xml',
        'wizards/rejected_wizard_view.xml',
        'wizards/handed_to_collect_nr_wizard_view.xml',
        'wizards/cancellation_nr_wizard_view.xml',
        'wizards/in_bank_nr_wizard_view.xml',
        'wizards/collected_cash_nr_wizard_view.xml',
        'wizards/cancellation_nr_wizard_view.xml',
        'wizards/returned_nr_wizard_view.xml',
        'wizards/bank_deposited_nr_wizard_view.xml',
        'wizards/rejected_nr_wizard_view.xml',
        'wizards/stop_check_request_nr_wizard_view.xml',
        'wizards/return_from_bank_nr_wizard_view.xml',
        'wizards/handed_to_partner_nr_wizard_view.xml',
        'views/account_views.xml',
        'views/account_payment_views.xml',
        'views/checks_views.xml',
        'views/partner_views.xml',

    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}