# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.constrains('move_type', 'journal_id')
    def _check_journal_type(self):
        for record in self:
            journal_type = record.journal_id.type

            if record.is_sale_document() and journal_type != 'sale' or record.is_purchase_document() and journal_type != 'purchase':
                return
                #raise ValidationError(_("The chosen journal has a type that is not compatible with your invoice type. Sales operations should go to 'sale' journals, and purchase operations to 'purchase' ones."))