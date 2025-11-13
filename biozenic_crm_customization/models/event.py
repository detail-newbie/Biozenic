from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

import pytz


class EventEvent(models.Model):
    _inherit = 'event.event'

    event_status = fields.Selection(string="Event Status",
                                    selection=[('un_schedule', 'Unscheduled'), ('schedule', 'Scheduled')],
                                    required=False, default='un_schedule')

    partner_id = fields.Many2one('res.partner', string='Contact', required=True)

    final_count = fields.Char(string="Final Count (2 Week Notice)", required=False)
    total_cost = fields.Float(string="Total Cost", required=False)

    event_date = fields.Date(string="Date", required=False)
    event_time = fields.Datetime(string="Time", required=False)
    event_location = fields.Char(string="Location", required=False)
    event_poc = fields.Char(string="Point of Contact", required=False)
    event_type = fields.Char(string="Event Type", required=False)
    head_count = fields.Char(string="Head Count", required=False)
    biozenic_staff = fields.Char(string="Biozenic Staff", required=False)
    eta_setup = fields.Char(string="ETA Setup", required=False)

    event_materials = fields.Char(string="Materials", required=False)
    plants = fields.Boolean(string="Plants")
    planters_pots = fields.Boolean(string="Planters/Pots")
    soil = fields.Boolean(string="Soil")
    perlite = fields.Boolean(string="Perlite")
    moss = fields.Boolean(string="Moss")
    other_materials = fields.Char(string="Other Required Materials", required=False)

    folding_tables = fields.Boolean(string="Folding Tables")
    floor_covering = fields.Boolean(string="Floor Covering")
    tablecloths = fields.Boolean(string="Tablecloths")
    mini_shovels = fields.Boolean(string="Mini Shovels")
    table_decor = fields.Boolean(string="Table Decor")
    broom_dustpan = fields.Boolean(string="Broom & Dustpan")
    garden_gloves = fields.Boolean(string="Garden Gloves")
    liner_trays = fields.Boolean(string="Plastic Liner Trays for Excess Soil")
    clear_bucket = fields.Boolean(string="Clear Buckets")
    liner = fields.Boolean(string="Liner")
    plant_care = fields.Boolean(string="Plant Care Instructions (Display)")
    business_cards = fields.Boolean(string="Business Cards")

    is_workshop_confirmation = fields.Boolean(string="Workshop Details Confirmation")
    is_qr_printing = fields.Boolean(string="Send Danny QR Code Care Guide for Printing")
    is_workshop_printing = fields.Boolean(string="Send Danny Workshop Flyer for Printing")
    is_guide_client = fields.Boolean(string="Send Care Guide to Client")

    @api.model
    def write(self, vals):
        for rec in self:
            result = super(EventEvent, rec).write(vals)

            if 'stage_id' in vals:
                new_stage = rec.stage_id.name
                if new_stage == 'Scheduled Future Events/Alert Service Team':
                    rec.activity_secure_inventory()
                elif new_stage == 'Billing':
                    rec.activity_invoice_event_customer()
                elif new_stage == '48 Hour Check':
                    rec.activity_48_hours_check()
                    rec.activity_administrative_checklist()

        return result

    def cron_20th_activity(self):
        group = self.env.ref('biozenic_crm_customization.group_activity_on_20th_month', raise_if_not_found=False)
        if not group:
            return

        users = getattr(group, 'users', False) or getattr(group, 'user_ids', False)
        users = users.filtered(lambda u: u.active)
        if not users:
            return

        model_id = self.env['ir.model']._get_id('event.event')
        activity_type_id = self.env.ref('mail.mail_activity_data_todo').id

        sample_event = self.env['event.event'].search([], limit=1)
        if not sample_event:
            return

        notes = [
            "Rotation at the beginning of the month is approaching. Make sure that Oceanridge has the following – Single/Double Orchid, no longer than 8\" planter size.",
            "Rotation at the beginning of the month is approaching. Make sure that Ionis has the following – 5 Bromeliads, 3 × 4\" and 2 × 6\" (check health and color).",
            "Rotation at the beginning of the month is approaching. Make sure that Manatt has the following – Orchid replacement (double orchid, drama, and full).",
            "Rotation at the beginning of the month is approaching. Make sure that Mirador has the following – Single/Double Orchid.",
            "Rotation at the beginning of the month is approaching. Make sure that JP Morgan has the following – Monthly tabletop rotation for front desk, bathrooms, branches.",
            "Rotation at the beginning of the month is approaching. Make sure that ServiceNow has the following – 6 total (Bldg A: 1, Bldg B: 2, Bldg C: 2, Bldg G: 1).",
            "Rotation at the beginning of the month is approaching. Make sure that Sorrento Towers has the following – 1 Orchid rotation.",
            "Rotation at the beginning of the month is approaching. Make sure that Erasca has the following – 1 Double-stemmed Orchid.",
            "Rotation at the beginning of the month is approaching. Make sure that Boundless Bio has the following – Large Double-stemmed Orchid arrangement for reception.",
        ]

        for user in users:
            tz = pytz.timezone(user.tz or 'UTC')
            now_utc = fields.Datetime.now()
            now_local = now_utc.astimezone(tz)

            if now_local.day != 20:
                continue

            for text in notes:
                self.env['mail.activity'].create({
                    'res_model_id': model_id,
                    'res_id': sample_event.id,
                    'activity_type_id': activity_type_id,
                    'summary': 'Monthly Rotation Task',
                    'user_id': user.id,
                    'note': f'<p>{text}</p>',
                    'date_deadline': fields.Date.context_today(self),
                })

    def activity_secure_inventory(self):
        group = self.env.ref('biozenic_crm_customization.group_notify_service_team', raise_if_not_found=False)
        if not group:
            return

        users = getattr(group, 'users', False) or getattr(group, 'user_ids', False)
        activity_type_id = self.env.ref('mail.mail_activity_data_todo').id
        model_id = self.env['ir.model']._get_id('event.event')

        for rec in self:
            for user in users:
                self.env['mail.activity'].create({
                    'res_model_id': model_id,
                    'res_id': rec.id,
                    'activity_type_id': activity_type_id,
                    'summary': 'Secure Inventory',
                    'user_id': user.id,
                    'note': '<p>Notify Service Team of Upcoming Event - Secure Inventory.</p>',
                    'date_deadline': fields.Date.today(),
                })

    def activity_invoice_event_customer(self):
        group = self.env.ref('biozenic_crm_customization.group_customer_invoice_event', raise_if_not_found=False)
        if not group:
            return

        users = getattr(group, 'users', False) or getattr(group, 'user_ids', False)
        activity_type_id = self.env.ref('mail.mail_activity_data_todo').id
        model_id = self.env['ir.model']._get_id('event.event')

        for rec in self:
            for user in users:
                self.env['mail.activity'].create({
                    'res_model_id': model_id,
                    'res_id': rec.id,
                    'user_id': user.id,
                    'activity_type_id': activity_type_id,
                    'summary': 'Invoice Event Customer',
                    'note': f"""
                           <p>Invoice Event Customer. Obtain information from 'Total Cost' Line in Events. Once the invoice is sent, move the Kanban Card to the next stage.</p>
                       """,
                    'date_deadline': fields.Date.today(),
                })

    def activity_48_hours_check(self):
        group = self.env.ref('biozenic_crm_customization.group_48_hours_check', raise_if_not_found=False)
        if not group:
            return

        users = getattr(group, 'users', False) or getattr(group, 'user_ids', False)
        activity_type_id = self.env.ref('mail.mail_activity_data_todo').id
        model_id = self.env['ir.model']._get_id('event.event')

        for rec in self:
            for user in users:
                self.env['mail.activity'].create({
                    'res_model_id': model_id,
                    'res_id': rec.id,
                    'user_id': user.id,
                    'activity_type_id': activity_type_id,
                    'summary': '48 Hours Check',
                    'note': f"""
                           <p>Customer has been invoiced. Event is in 48 Hour Check.</p>
                       """,
                    'date_deadline': fields.Date.today(),
                })

    def activity_administrative_checklist(self):
        group = self.env.ref('biozenic_crm_customization.group_administrative_checklist', raise_if_not_found=False)
        if not group:
            return

        users = getattr(group, 'users', False) or getattr(group, 'user_ids', False)
        activity_type_id = self.env.ref('mail.mail_activity_data_todo').id
        model_id = self.env['ir.model']._get_id('event.event')

        for rec in self:
            for user in users:
                self.env['mail.activity'].create({
                    'res_model_id': model_id,
                    'res_id': rec.id,
                    'user_id': user.id,
                    'activity_type_id': activity_type_id,
                    'summary': 'Administrative Checklist',
                    'note': f"""
                           <p>Event is in 48 Hour Check. Please complete Administrative Checklist.</p>
                       """,
                    'date_deadline': fields.Date.today(),
                })
