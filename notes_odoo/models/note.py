# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class CustomNote(models.Model):

    _name = 'custom.note'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Notes"

    def _default_stage_id(self):
        return self.env['custom.note.stage'].search([], limit=1)
    
    name = fields.Text(
        string='Name', 
        copy=True, 
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
    )
    description = fields.Html(
        'Notes Content'
    )
    custom_stage_id = fields.Many2one(
        'custom.note.stage', 
        copy=False,
        default=_default_stage_id,
    )
    custom_tag_ids = fields.Many2many(
        'custom.note.tag', 
        string='Tags'
    )
    custom_user_id = fields.Many2one(
        'res.users',  
        default=lambda self: self.env.user,
        string="User",
    )
    custom_is_public = fields.Boolean(
        string="Share (Internal)",
        help="If set, this notes will be visible to the selected internal followers/users."
    )

    
