# -*- coding: utf-8 -*-

import base64
import io
from datetime import datetime

import xlsxwriter

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CrmSalesAccountReport(models.Model):
    _name = 'crm.sales.account.report'
    _description = 'CRM Sales Account Consolidated Report'
    _auto = False
    _rec_name = 'opportunity_name'
    _order = 'opportunity_name'

    opportunity_id = fields.Many2one('crm.lead', string='Opportunity', readonly=True)
    opportunity_name = fields.Char(string='Opportunity Name', readonly=True)
    tag_id = fields.Many2one('crm.tag', string='Tag', readonly=True)
    stage_id = fields.Many2one('crm.stage', string='Stage', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    user_id = fields.Many2one('res.users', string='Salesperson', readonly=True)
    quote_amount = fields.Float(string='Quotation Amount', readonly=True)
    so_amount = fields.Float(string='Sales Order Amount', readonly=True)
    invoice_amount = fields.Float(string='Invoice Amount', readonly=True)
    sale_order_id = fields.Many2one('sale.order', string='Sales Order', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW crm_sales_account_report AS (
                SELECT
                    row_number() OVER () AS id,
                    lead.id AS opportunity_id,
                    lead.name AS opportunity_name,
                    tag.id AS tag_id,
                    lead.stage_id AS stage_id,
                    lead.partner_id AS partner_id,
                    lead.user_id AS user_id,
                    lead.company_id AS company_id,
                    so.id AS sale_order_id,
                    COALESCE(so.amount_total, 0) AS quote_amount,
                    CASE 
                        WHEN so.state IN ('sale', 'done') THEN COALESCE(so.amount_total, 0)
                        ELSE 0
                    END AS so_amount,
                    COALESCE(inv_summary.invoice_total, 0) AS invoice_amount
                FROM
                    crm_lead lead
                LEFT JOIN
                    crm_stage stage ON lead.stage_id = stage.id
                LEFT JOIN
                    crm_tag_rel tag_rel ON lead.id = tag_rel.lead_id
                LEFT JOIN
                    crm_tag tag ON tag_rel.tag_id = tag.id
                LEFT JOIN
                    sale_order so ON so.opportunity_id = lead.id
                LEFT JOIN (
                    SELECT
                        so_inner.id AS sale_order_id,
                        SUM(
                            CASE 
                                WHEN inv.state = 'posted' AND inv.move_type = 'out_invoice' 
                                THEN inv.amount_total
                                WHEN inv.state = 'posted' AND inv.move_type = 'out_refund'
                                THEN -inv.amount_total
                                ELSE 0
                            END
                        ) AS invoice_total
                    FROM
                        sale_order so_inner
                    LEFT JOIN
                        sale_order_line_invoice_rel sol_inv_rel ON sol_inv_rel.order_line_id IN (
                            SELECT id FROM sale_order_line WHERE order_id = so_inner.id
                        )
                    LEFT JOIN
                        account_move_line inv_line ON inv_line.id = sol_inv_rel.invoice_line_id
                    LEFT JOIN
                        account_move inv ON inv.id = inv_line.move_id
                    WHERE
                        inv.state = 'posted'
                        AND inv.move_type IN ('out_invoice', 'out_refund')
                    GROUP BY
                        so_inner.id
                ) inv_summary ON inv_summary.sale_order_id = so.id
                WHERE
                    stage.name->>'en_US' IN ('Need to Invoice', 'Awaiting Payment')
                    AND lead.type = 'opportunity'
                    AND lead.active = true
            )
        """)

    def action_open_opportunity(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Opportunity',
            'res_model': 'crm.lead',
            'res_id': self.opportunity_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _get_report_domain(self):
        return []

    def _get_report_lines(self):
        return self.search(self._get_report_domain(), order='opportunity_name')

    def _generate_xlsx_file(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Consolidated Report')

        title_fmt = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D9EAF7',
            'border': 1,
        })
        header_fmt = workbook.add_format({
            'bold': True,
            'bg_color': '#1F4E78',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
        })
        text_fmt = workbook.add_format({
            'border': 1,
            'valign': 'vcenter',
        })
        amount_fmt = workbook.add_format({
            'border': 1,
            'num_format': '#,##0.00',
            'valign': 'vcenter',
        })

        columns = [
            'Tag',
            'Opportunity',
            'Customer',
            'Salesperson',
            'Quotation Amount',
            'Sales Order Amount',
            'Invoice Amount',
            'Stage',
            'Company',
        ]

        row = 0
        worksheet.merge_range(row, 0, row, len(columns) - 1, 'CRM Sales Account Consolidated Report', title_fmt)
        row += 2

        for col, header in enumerate(columns):
            worksheet.write(row, col, header, header_fmt)
        row += 1

        records = self._get_report_lines()

        for rec in records:
            worksheet.write(row, 0, rec.tag_id.display_name or '', text_fmt)
            worksheet.write(row, 1, rec.opportunity_name or '', text_fmt)
            worksheet.write(row, 2, rec.partner_id.display_name or '', text_fmt)
            worksheet.write(row, 3, rec.user_id.display_name or '', text_fmt)
            worksheet.write_number(row, 4, rec.quote_amount or 0.0, amount_fmt)
            worksheet.write_number(row, 5, rec.so_amount or 0.0, amount_fmt)
            worksheet.write_number(row, 6, rec.invoice_amount or 0.0, amount_fmt)
            worksheet.write(row, 7, rec.stage_id.display_name or '', text_fmt)
            worksheet.write(row, 8, rec.company_id.display_name or '', text_fmt)
            row += 1

        worksheet.set_column('A:A', 18)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 25)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:G', 18)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 25)

        workbook.close()
        output.seek(0)

        filename = 'Consolidate Report %s.xlsx' % fields.Date.today()
        file_content = base64.b64encode(output.read())
        output.close()

        return file_content, filename

    @api.model
    def action_download_excel(self):
        file_content, filename = self._generate_xlsx_file()

        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': file_content,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'res_model': self._name,
            'res_id': self[:1].id or 0,
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }

    def _get_consolidate_email_config(self):
        config = self.env['consolidate.config'].search([], order='id desc', limit=1)
        if not config:
            raise UserError(_("Consolidate email configuration not found."))

        if not config.to_email:
            raise UserError(_("Please configure 'To Email' in Consolidate Config."))

        return config

    def _send_report_email(self):
        config = self._get_consolidate_email_config()
        file_content, filename = self._generate_xlsx_file()

        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': file_content,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        mail_values = {
            'subject': config.subject_email or 'CRM Sales Account Consolidated Report',
            'email_from': config.from_email or self.env.company.email or self.env.user.email_formatted,
            'email_to': config.to_email,
            'email_cc': config.cc_email or False,
            'body_html': """
                <div>
                    <p>%s</p>
                </div>
            """ % ((config.body_email or 'Please find attached the weekly CRM consolidated report.').replace('\n',
                                                                                                             '<br/>')),
            'attachment_ids': [(6, 0, [attachment.id])],
        }

        mail = self.env['mail.mail'].create(mail_values)
        mail.send()
        return True

    @api.model
    def cron_send_weekly_consolidated_report(self):
        self.sudo()._send_report_email()


class ConsolidateConfig(models.Model):
    _name = 'consolidate.config'
    _rec_name = 'subject_email'

    subject_email = fields.Char(string="Subject", required=False)
    from_email = fields.Char(string="From", required=False)
    to_email = fields.Char(string="To", required=False)
    cc_email = fields.Char(string="CC", required=False)

    body_email = fields.Text(string="Body", required=False)
    active = fields.Boolean(default=True)
