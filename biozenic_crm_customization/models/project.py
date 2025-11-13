from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.model
    def write(self, vals):
        for rec in self:
            result = super(ProjectProject, rec).write(vals)

            if 'stage_id' in vals:
                new_stage = rec.stage_id.name
                if new_stage == 'Ordering/Manufacturing':
                    rec.activity_double_check_inventory()
                elif new_stage == 'Prep for Installation/All Payments Collected':
                    rec.activity_customer_full_paid()
                    # rec.activity_customer_not_full_paid()

        return result

    def activity_double_check_inventory(self):
        group = self.env.ref('biozenic_crm_customization.group_double_check_inventory', raise_if_not_found=False)
        if not group:
            return

        users = getattr(group, 'users', False) or getattr(group, 'user_ids', False)
        activity_type_id = self.env.ref('mail.mail_activity_data_todo').id
        model_id = self.env['ir.model']._get_id('project.project')

        for rec in self:
            for user in users:
                self.env['mail.activity'].create({
                    'res_model_id': model_id,
                    'res_id': rec.id,
                    'activity_type_id': activity_type_id,
                    'summary': 'Double Check Inventory',
                    'user_id': user.id,
                    'note': '<p>Double Check to see if you have all the inventory you need.</p>',
                    'date_deadline': fields.Date.today(),
                })

    def activity_customer_full_paid(self):
        group = self.env.ref('biozenic_crm_customization.group_customer_full_paid_project', raise_if_not_found=False)
        if not group:
            return

        users = getattr(group, 'users', False) or getattr(group, 'user_ids', False)
        activity_type_id = self.env.ref('mail.mail_activity_data_todo').id
        model_id = self.env['ir.model']._get_id('project.project')

        for rec in self:
            for user in users:
                self.env['mail.activity'].create({
                    'res_model_id': model_id,
                    'res_id': rec.id,
                    'activity_type_id': activity_type_id,
                    'summary': 'Customer Full Paid',
                    'user_id': user.id,
                    'note': '<p>Ensure that the customer has paid in full.</p>',
                    'date_deadline': fields.Date.today(),
                })

    def activity_customer_not_full_paid(self):
        group = self.env.ref('biozenic_crm_customization.group_customer_not_full_paid_project', raise_if_not_found=False)
        if not group:
            return

        users = getattr(group, 'users', False) or getattr(group, 'user_ids', False)
        activity_type_id = self.env.ref('mail.mail_activity_data_todo').id
        model_id = self.env['ir.model']._get_id('project.project')

        for rec in self:
            for user in users:
                self.env['mail.activity'].create({
                    'res_model_id': model_id,
                    'res_id': rec.id,
                    'activity_type_id': activity_type_id,
                    'summary': 'Customer Not Full Paid',
                    'user_id': user.id,
                    'note': '<p>Ensure that the customer has paid in full.</p>',
                    'date_deadline': fields.Date.today(),
                })
