# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Service Checlist',
    'price': 9.0,
    'version': '3.1.1',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': 'Allows your users to create and manage notes.',
    'description': """
This apps allow you to create and manage service checklist.

    """,
    'author': "Biozenic.",
    'website': "www.biozenic.com",
    'support': 'hello@biozenic.com',
    'category': 'Sales/Sales',
    'depends' : ['mail'],
    'data': [
        'security/custom_notes_security.xml',
        'security/ir.model.access.csv',
        'report/note_custom_report_template.xml',
        'report/note_custom_report.xml',
        'views/custom_note_views.xml',
        'views/custom_note_stage_view.xml',
        'views/custom_note_tag_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
