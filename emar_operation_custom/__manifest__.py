# -*- coding: utf-8 -*-
{
    'name': "Project Customizations",

    'author': "Yousif Mobark",
    'category': 'project',
    'version': '11.0.0.1',
    'depends': ['emar_operation'],
    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizards/generate_assigned_doc_inter.xml',
        'wizards/generate_assigned_doc_sub.xml',
        'data/agreement_code_sequence.xml',
        'data/project_code_sequence.xml',
        'views/project_project_views.xml',
        'views/res_partner_views.xml',
        'views/account_invoice_views.xml',
        'views/product_product_views.xml',
        'views/purchase_order_views.xml',
        'views/stock_picking_views.xml',
        'views/project_agreement_views.xml',
        'views/assigned_document_int_views.xml',
        'views/assigned_document_sub_views.xml',
        'views/assigned_line_views.xml',
        'views/contracting_menu_items.xml',
        'views/project_task_views.xml',
    ],
}
