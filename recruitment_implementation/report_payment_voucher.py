# -*- coding: utf-8 -*-
"""
Payment Voucher Report for account.payment model
Generates professional payment receipts and vouchers with signatures and approval tracking
"""

from odoo import api, models, fields
from num2words import num2words


class PaymentVoucherReport(models.AbstractModel):
    """Payment Voucher Report Template"""
    _name = 'report.payment_account_enhanced.payment_voucher_template'
    _description = 'Payment Voucher Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get values for the payment voucher report"""
        docs = self.env['account.payment'].browse(docids)
        
        return {
            'doc_ids': docids,
            'doc_model': 'account.payment',
            'docs': docs,
            'get_amount_in_words': self._get_amount_in_words,
        }

    @staticmethod
    def _get_amount_in_words(amount, currency):
        """Convert amount to words for the voucher
        
        Args:
            amount: Numeric amount
            currency: Currency object (account.currency)
            
        Returns:
            String representation of amount in words
        """
        try:
            if not amount or amount == 0:
                return "Zero"
            
            # Handle negative amounts
            is_negative = amount < 0
            amount = abs(amount)
            
            # Get currency code
            currency_name = currency.name if currency else "AED"
            
            # Convert to words
            amount_int = int(amount)
            amount_decimal = round((amount - amount_int) * 100)
            
            # Convert integer part
            words = num2words(amount_int, lang='en')
            words = words.upper()
            
            # Add decimal part
            if amount_decimal > 0:
                decimal_words = num2words(amount_decimal, lang='en')
                words += f" and {decimal_words.upper()} {currency_name} Fils"
            else:
                words += f" {currency_name} only"
            
            # Add negative prefix if needed
            if is_negative:
                words = "NEGATIVE " + words
            
            return words
        except Exception as e:
            return f"Error converting amount: {str(e)}"


class AccountPaymentReport(models.Model):
    """Override account.payment to add report-related fields"""
    _inherit = 'account.payment'

    # Report-related fields
    voucher_number = fields.Char(
        string='Voucher Number',
        readonly=True,
        help='Auto-generated unique voucher number for reports'
    )
    
    remarks = fields.Text(
        string='Remarks',
        help='Additional remarks for the voucher'
    )
    
    qr_code = fields.Binary(
        string='QR Code',
        help='QR code for voucher verification'
    )
    
    reviewer_id = fields.Many2one(
        'res.users',
        string='Reviewed By',
        help='Finance department reviewer'
    )
    
    reviewer_date = fields.Datetime(
        string='Review Date',
        help='Date when the payment was reviewed'
    )
    
    approver_id = fields.Many2one(
        'res.users',
        string='Approved By',
        help='Accounts manager who approved'
    )
    
    approver_date = fields.Datetime(
        string='Approval Date',
        help='Date when the payment was approved'
    )
    
    authorizer_id = fields.Many2one(
        'res.users',
        string='Authorized By',
        help='Authorized officer signature'
    )
    
    authorizer_date = fields.Datetime(
        string='Authorization Date',
        help='Date when the payment was authorized'
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to auto-generate voucher number"""
        for vals in vals_list:
            if not vals.get('voucher_number'):
                # Generate voucher number based on payment name and date
                sequence = self.env['ir.sequence'].next_by_code('account.payment.voucher')
                vals['voucher_number'] = sequence or vals.get('name', 'V-00000')
        
        return super().create(vals_list)

    def action_generate_qr_code(self):
        """Generate QR code for the payment voucher"""
        import qrcode
        from io import BytesIO
        import base64
        
        for payment in self:
            try:
                # Create QR code data from payment reference
                qr_data = f"PAY|{payment.name}|{payment.amount}|{payment.date}"
                
                # Generate QR code
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(qr_data)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Convert to base64
                img_io = BytesIO()
                img.save(img_io, format='PNG')
                img_io.seek(0)
                qr_code_base64 = base64.b64encode(img_io.getvalue())
                
                payment.qr_code = qr_code_base64
            except ImportError:
                # If qrcode library not available, skip
                pass
            except Exception as e:
                # Log error but don't fail
                print(f"Error generating QR code: {str(e)}")

    def button_submit_for_review(self):
        """Submit payment for review"""
        for payment in self:
            payment.reviewer_id = self.env.user
            payment.reviewer_date = fields.Datetime.now()
        return super().button_submit_for_review() if hasattr(super(), 'button_submit_for_review') else True

    def button_review_approve(self):
        """Approve payment after review"""
        for payment in self:
            payment.approver_id = self.env.user
            payment.approver_date = fields.Datetime.now()
        return super().button_review_approve() if hasattr(super(), 'button_review_approve') else True

    def button_authorize(self):
        """Authorize payment"""
        for payment in self:
            payment.authorizer_id = self.env.user
            payment.authorizer_date = fields.Datetime.now()
        return True

    def action_print_voucher(self):
        """Print the payment voucher"""
        # Generate QR code before printing
        self.action_generate_qr_code()
        
        # Return print action
        return self.env.ref('payment_account_enhanced.action_payment_voucher_report').report_action(self)
