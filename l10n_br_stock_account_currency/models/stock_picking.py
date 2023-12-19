# Copyright (C) 2014  Renato Lima - Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.onchange("fiscal_operation_id")
    def _onchange_fiscal_operation_id(self):
        # import pudb;pu.db
        result = super()._onchange_fiscal_operation_id()
        for line in self.move_ids_without_package:
            line.write({'fiscal_operation_id': self.fiscal_operation_id.id})
            line._onchange_product_id_fiscal()
        # if self.fiscal_operation_id:
        #     if not self.price_unit:
        #         self._get_product_price()
        #     self._onchange_commercial_quantity()
        #     self.fiscal_operation_line_id = self.fiscal_operation_id.line_definition(
        #         company=self.company_id,
        #         partner=self.partner_id,
        #         product=self.product_id,
        #     )
        #     self._onchange_fiscal_operation_line_id()
        return result
    
    # @api.depends("fiscal_operation_id")
    # def _change_fiscal_operation(self):
    #     import pudb;pu.db
    #     _onchange_fiscal_operation_id
    #     company = self.env.user.company_id
    #     fiscal_operation = self.env.user.company_id.stock_fiscal_operation_id
    #     picking_type_id = self.env.context.get("default_picking_type_id")
    #     if picking_type_id:
    #         picking_type = self.env["stock.picking.type"].browse(picking_type_id)
    #         fiscal_operation = picking_type.fiscal_operation_id or (
    #             company.stock_in_fiscal_operation_id
    #             if picking_type.code == "incoming"
    #             else company.stock_out_fiscal_operation_id
    #         )
    #     return fiscal_operation

    