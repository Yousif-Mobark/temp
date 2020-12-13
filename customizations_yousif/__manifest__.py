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
        'data/agreement_code_sequence.xml',
        'data/project_code_sequence.xml',
        'views/project_project_views.xml',
        'views/res_partner_form.xml',
        'views/project_agreement_views.xml',
    ],
}
