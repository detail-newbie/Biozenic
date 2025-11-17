from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    secondary_contact_id = fields.Many2one('res.partner', string='Secondary Contact')
    job_site = fields.Char(string="Job Site", required=False)
    add_on_notes = fields.Text(string="Add-on Notes", required=False)

    sqr_ft = fields.Integer(string="Square Ft", required=False)
    other = fields.Char(string="Other", required=False)
    service_time = fields.Datetime(string="Time of Service", required=False)
    replacement_cost = fields.Float(string="Est. Cost of Replacements", required=False)
    additional_notes = fields.Text(string="Additional Notes", required=False)

    no_total_plants = fields.Integer(string="Total Number Plants", required=False)
    no_large_plans = fields.Integer(string="Number of Large Plants", required=False)
    no_medium_plants = fields.Integer(string="Number of Medium Plants", required=False)
    no_small_plant = fields.Integer(string="Number of Small Plants", required=False)
    no_tabletops = fields.Integer(string="Number of Tabletops", required=False)
    no_changes = fields.Integer(string="Number of Changes", required=False)

    @api.model
    def write(self, vals):
        for rec in self:
            result = super(CRMLead, rec).write(vals)

            if 'stage_id' in vals:
                new_stage = rec.stage_id.name
                if new_stage == 'Proposal Negotiations':
                    rec.activity_create_proposal()
                    rec.activity_secure_inventory()
                elif new_stage == 'Need to Invoice':
                    rec.activity_invoice_customer()
                elif new_stage == 'Won - Billed In Full':
                    rec.activity_customer_full_paid()

        return result

    def activity_create_proposal(self):
        group = self.env.ref('biozenic_crm_customization.group_create_proposal', raise_if_not_found=False)
        if not group:
            return

        users = getattr(group, 'users', False) or getattr(group, 'user_ids', False)
        activity_type_id = self.env.ref('mail.mail_activity_data_todo').id
        model_id = self.env['ir.model']._get_id('crm.lead')

        for rec in self:
            for user in users:
                self.env['mail.activity'].create({
                    'res_model_id': model_id,
                    'res_id': rec.id,
                    'activity_type_id': activity_type_id,
                    'summary': 'Create Proposal',
                    'user_id': user.id,
                    'note': '<p>Create Proposal.</p>',
                    'date_deadline': fields.Date.today(),
                })

    def activity_secure_inventory(self):
        group = self.env.ref('biozenic_crm_customization.group_secure_inventory', raise_if_not_found=False)
        if not group:
            return

        users = getattr(group, 'users', False) or getattr(group, 'user_ids', False)
        activity_type_id = self.env.ref('mail.mail_activity_data_todo').id
        model_id = self.env['ir.model']._get_id('crm.lead')

        for rec in self:
            for user in users:
                self.env['mail.activity'].create({
                    'res_model_id': model_id,
                    'res_id': rec.id,
                    'activity_type_id': activity_type_id,
                    'summary': 'Secure Inventory',
                    'user_id': user.id,
                    'note': '<p>Secure Inventory.</p>',
                    'date_deadline': fields.Date.today(),
                })

    def activity_invoice_customer(self):
        group = self.env.ref('biozenic_crm_customization.group_invoice_customer', raise_if_not_found=False)
        if not group:
            return

        users = getattr(group, 'users', False) or getattr(group, 'user_ids', False)
        activity_type_id = self.env.ref('mail.mail_activity_data_todo').id
        model_id = self.env['ir.model']._get_id('crm.lead')

        for rec in self:
            for user in users:
                self.env['mail.activity'].create({
                    'res_model_id': model_id,
                    'res_id': rec.id,
                    'activity_type_id': activity_type_id,
                    'summary': 'Invoice Customer',
                    'user_id': user.id,
                    'note': '<p>Invoice Customer.</p>',
                    'date_deadline': fields.Date.today(),
                })

    def activity_customer_full_paid(self):
        group = self.env.ref('biozenic_crm_customization.group_customer_full_paid', raise_if_not_found=False)
        if not group:
            return

        users = getattr(group, 'users', False) or getattr(group, 'user_ids', False)
        activity_type_id = self.env.ref('mail.mail_activity_data_todo').id
        model_id = self.env['ir.model']._get_id('crm.lead')

        for rec in self:
            for user in users:
                self.env['mail.activity'].create({
                    'res_model_id': model_id,
                    'res_id': rec.id,
                    'activity_type_id': activity_type_id,
                    'summary': 'Customer Full Paid',
                    'user_id': user.id,
                    'note': '<p>Customer Full Paid.</p>',
                    'date_deadline': fields.Date.today(),
                })
