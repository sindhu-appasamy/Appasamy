from odoo import fields, models, api, _
from odoo import tools

class orderconfirmation(models.Model):
	_name = "orderconfirmation.report"
	_auto = False
	_description = "Order Confirmation report"

	partner_id = fields.Many2one('res.partner',string='Customer',readonly=1)
	company_id = fields.Many2one('res.company',string='Company',readonly=1)
	confirmation_date = fields.Date(string='Date',readonly=1)
	categ_id = fields.Many2one('product.category',string='Product Category',readonly=1)
	source_document = fields.Char(string='Order Number',readonly=1)
	product_id = fields.Many2one('product.product',string='Product Name',readonly=1)
	product_qty = fields.Float(string='Qty',readonly=1)
	state = fields.Char(string='Type',readonly=1)
	reference_id = fields.Char(string='Reference',readonly=1)
	code = fields.Selection(
		[('incoming', 'Purchase'),
		('outgoing', 'Sale'),],
		string='Order Type',readonly=1)

	def _select(self):	
		return """
			SELECT 
				row_number() over(ORDER BY sm.date desc) as id,
    			sm.company_id as company_id,
				sm.date as confirmation_date,
				pt.categ_id as categ_id,
				sm.origin as source_document,
				sm.reference as reference_id,
				sp.partner_id as partner_id,
				sm.product_id as product_id, 
				sm.product_uom_qty as product_qty,
				spt.code as code
		"""

	def _from(self):
		return """
			FROM stock_move as sm
		"""

	def _join(self):
	 	return"""
			LEFT JOIN stock_picking as sp ON (sm.group_id = sp.group_id)
				LEFT JOIN product_product as pp ON (pp.id = sm.product_id)
				LEFT JOIN product_template as pt ON ( pt.id = pp.product_tmpl_id)
				LEFT JOIN sale_order as so ON (so.procurement_group_id = sm.group_id)
				LEFT JOIN purchase_order as po On ( po.group_id = sm.group_id)
				LEFT JOIN stock_picking_type as spt ON ( sm.picking_type_id = spt.id)
		"""

	def _where(self):
		return"""
			WHERE sm.origin_returned_move_id is NULL AND sm.group_id is not NULL 
		"""

	def _group_by(self):
		return """
			GROUP BY 
			sm.reference, sm.origin, sm.company_id, sm.date, pt.categ_id, sp.partner_id, 
			sm.product_id, sm.product_uom_qty, spt.code
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
				




     