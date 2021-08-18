# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo import tools

class Field(models.Model):
    _name = "purchase.detail"
    _auto = False
    _description = "Purchase Details"

    partner_id = fields.Many2one('res.partner',string='Vendor',readonly=1)
    company_id = fields.Many2one('res.company', string='Company',readonly=1)
    name = fields.Char(string='Purchase Order',readonly=1)
    state = fields.Selection(
        [('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),],
        string='Status',readonly=1)
    order_date = fields.Date(string='Order Date')
    amount_untaxed = fields.Float(string='Untaxed Amount',readonly=1)
    amount_tax = fields.Float(string='Tax Amount',readonly=1)
    bill_qty = fields.Float(string='Billed Qty',readonly=1)
    grn_qty = fields.Float(string='Received Qty',readonly=1)
    unbilled_qty = fields.Float(string="Unbilled Qty",readonly=1)

    def _select(self):  
        return """
            SELECT
                row_number() over(ORDER BY po.name DESC) as id,
                po.company_id as company_id,
                po.partner_id as partner_id,
                po.date_order as order_date,
                po.name as name,
                po.state as state,
                po.amount_untaxed as amount_untaxed,
                po.amount_tax as amount_tax,
                SUM(COALESCE(pol.qty_invoiced,0)) as bill_qty,
                SUM(COALESCE(pol.qty_received,0)) as grn_qty,
                SUM(COALESCE(pol.qty_received,0)) - SUM(COALESCE(pol.qty_invoiced,0)) as unbilled_qty
        """

    def _from(self):
        return """
            FROM purchase_order as po
        """

    def _join(self):
        return """
            LEFT JOIN purchase_order_line as pol ON po.id = pol.order_id
        """

    def _where(self):
        return"""
            WHERE
            po.state != 'cancel'
        """

    def _group_by(self):
        return """
            GROUP BY
            po.company_id, po.partner_id, po.date_order, po.name, po.state, po.amount_untaxed, po.amount_tax
        """

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s As(
            %s
            %s
            %s
            %s
            %s
        )
        """% (self._table, self._select(), self._from(), self._join(), self._where(), self._group_by())
        )