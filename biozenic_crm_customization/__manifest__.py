# -*- coding: utf-8 -*-

{
    'name': 'Biozenic Customization',
    'category': 'Tools',

    'version': '1.0',

    'depends': ['base', 'mail', 'crm', 'project', 'event', 'website_event'],

    "data": [
        'data/data.xml',
        'security/security.xml',
        'views/crm_lead.xml',
        'views/event.xml',
    ],

    'installable': True,
    'auto_install': False,
    "license": "LGPL-3",
}
