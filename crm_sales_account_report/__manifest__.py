# -*- coding: utf-8 -*-
{
    'name': 'Consolidated Report | Biozenic',
    'version': '19.0.1.0.0',
    'category': 'CRM',

    'summary': 'Consolidated report combining CRM Opportunities, Sales Orders, and Customer Invoices',
    'description': """
        Consolidated Report
        =============================================
        This module provides a consolidated report that shows:
        - Opportunities in specific CRM stages (Need to Invoice, Awaiting Payment)
        - Grouped by CRM tags
        - Financial amounts from Sales Orders and Invoices
        - Direct navigation to CRM opportunities
        
        Features:
        ---------
        * Filter opportunities by stage
        * Group by CRM tags
        * View quotation, sales order, and invoice amounts
        * Click-through to opportunity details
        * Advanced filtering by tag, stage, salesperson, and customer
            """,

    'author': 'Waqar Ahmad',
    'license': 'LGPL-3',

    'depends': ['crm', 'sale_management', 'account'],

    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/view.xml',

        'reports/action_report.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
