# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo import tools

class dailyreport(models.Model):
	_name = "daily.report"
	_auto = False
	_description = "Daily report"

	reference = fields.Char(string='Reference',readonly=1)
	date = fields.Date(string='Date',readonly=1)
	date_of_transfer = fields.Date(string='Date of Transfer', readonly=1)
	picking_type_id = fields.Many2one('stock.picking.type', string="Operation Type", readonly=1)
	location_id = fields.Many2one('stock.location',string="Source Location",readonly=1)
	location_dest_id = fields.Many2one('stock.location',string="Destination Location",readonly=1)
	product_id = fields.Many2one('product.product',string='Product Name',readonly=1)
	categ_id = fields.Many2one('product.category',string='Product Category',readonly=1)
	inward_qty = fields.Float(string='Inward',readonly=1)
	today_inward = fields.Float(string='Todays Inward',readonly=1)
	production_qty = fields.Float(string='Production',readonly=1)
	today_production = fields.Float(string='Todays Production',readonly=1)
	outward_qty = fields.Float(string='Outward',readonly=1)
	today_outward = fields.Float(string='Todays Outward',readonly=1)
	return_qty = fields.Float(string='Return',readonly=1)
	today_return = fields.Float(string='Todays Return',readonly=1)
	pending_qty = fields.Float(string='Pending',readonly=1)
	company_id = fields.Many2one('res.company',string='Company',readonly=1)
	state = fields.Selection([
		('draft', 'Draft'),
		('waiting', 'Waiting Another Move'),
		('confirmed', 'Waiting Availability'),
		('partially_available', 'Partially Available'),
		('assigned', 'Avaiable'),
		('done', 'Done'),
		],string="Status")

	def _select(self):	
		return """
			SELECT
				row_number() over(ORDER BY date desc) as id,
				date,
				date_of_transfer,
				picking_type_id,
				origin_returned_move_id, 
				reference,
				location_id,
				location_dest_id,
				product_id,
				categ_id,
				main.production_qty,
				main.today_production,
				main.inward_qty,
				main.today_inward,
				main.outward_qty,
				main.today_outward,
				main.return_qty,
				main.today_return,
				main.pending_qty,
				state,
				company_id
			"""

	def _from(self):
		return """
			FROM
			(
			SELECT
				sm.date as date,
				sm.date as date_of_transfer,
				sm.picking_type_id,
				sm.origin_returned_move_id, 
				sm.reference,
				sm.location_id,
				sm.location_dest_id,
				sm.product_id,
				pt.categ_id,
				CASE
				WHEN sm.origin_returned_move_id IS Null AND source_loc.usage = 'production' AND dest_loc.usage = 'internal'
				THEN sm.product_uom_qty
				ELSE 0
				END AS production_qty,
				CASE
				WHEN sm.origin_returned_move_id IS Null AND source_loc.usage = 'production' AND dest_loc.usage = 'internal' AND CAST(sm.date as Date) = CAST(NOW() AS Date)
				THEN sm.product_uom_qty
				ELSE 0
				END AS today_production,
				CASE
				WHEN sm.origin_returned_move_id IS Null AND source_loc.usage != 'internal' AND dest_loc.usage = 'internal'
				THEN sm.product_uom_qty
				ELSE 0
				END AS inward_qty,
				CASE
				WHEN sm.origin_returned_move_id IS Null AND source_loc.usage != 'internal' AND dest_loc.usage = 'internal' AND CAST(sm.date as Date) = CAST(NOW() AS Date)
				THEN sm.product_uom_qty
				ELSE 0
				END AS today_inward,
				CASE
				WHEN dest_loc.usage != 'internal' AND source_loc.usage = 'internal'
				THEN sm.product_uom_qty
				ELSE 0
				END AS outward_qty,
				CASE
				WHEN dest_loc.usage != 'internal' AND source_loc.usage = 'internal' AND CAST(sm.date as Date) = CAST(NOW() AS Date)
				THEN sm.product_uom_qty
				ELSE 0
				END AS today_outward,
				CASE
				WHEN sm.origin_returned_move_id IS NOT NULL AND sale_line_id IS NOT NULL AND dest_loc.usage != 'supplier'
				THEN sm.product_uom_qty 
				ELSE 0
				END AS return_qty,
				CASE
				WHEN sm.origin_returned_move_id IS NOT NULL AND sale_line_id IS NOT NULL AND dest_loc.usage != 'supplier' AND CAST(sm.date as Date) = CAST(NOW() AS Date)
				THEN sm.product_uom_qty 
				ELSE 0
				END AS today_return,
				0 as pending_qty,
				sm.state,
				sm.company_id
			FROM stock_move AS sm
				LEFT JOIN product_product AS pp ON (pp.id = sm.product_id)
				LEFT JOIN product_template AS pt ON (pt.id = pp.product_tmpl_id)
				LEFT JOIN stock_location as source_loc ON (sm.location_id = source_loc.id)
				LEFT JOIN stock_location as dest_loc ON (sm.location_dest_id = dest_loc.id)
			WHERE
				sm.state = 'done'
				AND (dest_loc.usage != 'internal' OR source_loc.usage != 'internal')
			UNION ALL
			SELECT
				Cast(NOW() as date),
				sm.date as date_of_transfer,
				sm.picking_type_id,
				sm.origin_returned_move_id, 
				sm.reference,
				sm.location_id,
				sm.location_dest_id,
				sm.product_id,
				pt.categ_id,
				0 AS production_qty,
				0 AS today_production,
				0 AS inward_qty,
				0 AS today_inward,
				0 AS outward_qty,
				0 AS today_outward,
				0 AS return_qty,
				0 AS today_return,
				sm.product_uom_qty AS pending_qty,
				sm.state,
				sm.company_id
			FROM stock_move AS sm
				LEFT JOIN product_product AS pp ON (pp.id = sm.product_id)
				LEFT JOIN product_template AS pt ON (pt.id = pp.product_tmpl_id)
				LEFT JOIN stock_location as source_loc ON (sm.location_id = source_loc.id)
				LEFT JOIN stock_location as dest_loc ON (sm.location_dest_id = dest_loc.id)
			WHERE
				sm.state NOT IN ('done', 'cancel') AND sm.sale_line_id IS NOT NULL 
				AND dest_loc.usage != 'internal' AND source_loc.usage = 'internal'
			
			) AS MAIN
		"""
	def init(self):
		tools.drop_view_if_exists(self._cr, self._table)
		self.env.cr.execute("""
			CREATE OR REPLACE VIEW %s As(
			%s
			%s
		)
		"""% (self._table, self._select(), self._from())
		)
