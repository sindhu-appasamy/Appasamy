from odoo import fields, models, api, _
from odoo import tools

class Field(models.Model):
	_name = "category.report"
	_auto = False
	_description = "Category report"

	partner_id = fields.Many2one('res.partner',string='Customer')
	state_id = fields.Many2one('res.country.state',string='State')
	#division_id = fields.Many2one('res.partner.division',string='Division')
	#branch_id = fields.Many2one('res.partner.branch',string='Branch')
	invoice_ids = fields.Many2one('account.move',string='Invoices', readonly=True, copy=False)
	name_id = fields.Char(string='Invoice Number')
	inv_date = fields.Date(string='Invoice Date')
	product_id = fields.Text(string='Product Name')
	product_category_id = fields.Many2one('product.category',string='Order Category')
	inv_total = fields.Float(string='Invoice Total')
	payment_ids = fields.Char(string='Payment Reference')
	payment_amount =fields.Float(string='Payment Received')
	payment_date = fields.Date(string='Payment Date')
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
	
	def _select(self):	
		select_str = """
			SELECT 
				row_number() over(ORDER BY acc.name) as id,
				acc.invoice_date as inv_date,
				payrel.invoice_id as invoice_ids,
				acc.name as name_id,
				acc.x_product_category_id as product_category_id,
				acc.partner_id as partner_id,
				res.state_id as state_id,
				ipc.product_id as product_id,
				acc.amount_total as inv_total,
				pay.name as payment_ids,
				pay.payment_date as payment_date,
				pay.amount as payment_amount,
				aml.company_id as company_id
			"""
		return select_str

	def _from(self):
		from_str = """
		FROM 
			account_payment as pay
			left join account_invoice_payment_rel as payrel ON (payrel.payment_id = pay.id)
			left join account_move as acc ON (payrel.invoice_id = acc.id)
			left join account_move_line as aml ON (aml.move_id = acc.id) 
			left join res_partner as res ON (res.id = acc.partner_id) 
			left join inv_product_concat as ipc ON (ipc.inv_id = acc.id)
		"""
		return from_str

	def _where(self):
		return"""Where acc.type = 'out_invoice' And acc.state = 'posted'"""

	def _group_by(self):
		group_by_str = """
		GROUP BY 
			payrel.invoice_id, acc.name,acc.invoice_date, acc.partner_id, res.state_id, acc.amount_total,
			acc.amount_residual, pay.payment_date, pay.amount, aml.move_id, ipc.product_id, aml.company_id,
			acc.x_product_category_id, pay.name
		"""
		return group_by_str

	def init(self):
		tools.drop_view_if_exists(self._cr, self._table)
		self._cr.execute("""
			CREATE OR REPLACE VIEW inv_product_concat As (
			SELECT
			row_number() over(ORDER BY move_id) as id,
 			move_id as inv_id,
			array_to_string(array_agg(distinct "name"),' , ') AS product_id
			FROM account_move_line
			where tax_line_id is null and product_id is not null
			GROUP BY move_id
			)""")

		self.env.cr.execute("""
			CREATE OR REPLACE VIEW %s As(
			%s
			%s
			%s
			%s
			)"""% (self._table, self._select(), self._from(), self._where(), self._group_by()))

	