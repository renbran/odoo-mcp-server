# osus_sales_invoicing_dashboard - Issues & Fixes Required

## Critical Issues Found

### 1. **Booking Sale Definition (Line 511-512)**
**Issue**: `total_booked_sales` uses `sum(matching_orders.mapped('sale_value'))`
- `sale_value` is a property/customization field that may not exist on sale.order
- This breaks if the field is not available

**Fix Required**: 
- **Option A (Recommended)**: Use order line item subtotals: `price_unit × qty - discount`
  ```python
  # Calculate from order lines: price_unit * quantity with discounts applied
  order_lines = matching_orders.mapped('order_line')
  rec.total_booked_sales = sum(order_lines.mapped('price_subtotal'))
  ```
  
- **Option B**: Use order total amount_total
  ```python
  rec.total_booked_sales = sum(matching_orders.mapped('amount_total'))
  ```

**YOUR CLARIFICATION NEEDED**: 
- Is "booking_sale" = `price_subtotal` (unit_price × qty in order lines)?
- Or is "booking_sale" = `amount_total` (order total)?
- Or is "booking_sale" = a custom `sale_value` field on sale.order?

---

### 2. **Filter Inconsistencies (Lines 475-509)**

The scorecard metrics don't consistently apply filters:

| Metric | Current Behavior | Issue |
|--------|-----------------|-------|
| `total_booked_sales` | Uses `_get_order_domain()` ✓ | Correct |
| `posted_invoice_count` | Filters invoices by date only | ✗ Ignores order_type, salesperson filters |
| `unpaid_invoice_count` | Filters invoices by date only | ✗ Ignores order_type, salesperson filters |
| `amount_to_collect` | Filters invoices by date only | ✗ Ignores order_type, salesperson filters |

**Fix**: All invoice-based metrics should optionally filter by orders if order filters are set:
```python
# If user filters by order type or salesperson, also limit invoices to those orders
if self.sales_order_type_id or self.sales_order_type_ids.ids or self.agent_partner_id:
    order_ids = self.env['sale.order'].search(order_domain).ids
    invoice_domain.append(('line_ids.sale_line_ids.order_id', 'in', order_ids))
```

---

### 3. **Agent Filter Application (Line 509)**
- `agent_partner_id` is only applied in `_get_order_domain()`
- Invoice metrics don't respect agent filter
- **Fix**: When agent_partner_id is set, filter invoices by orders from that agent

---

### 4. **Sales Order Type Filter (Line 498-499)**
```python
if self.sales_order_type_ids.ids:  # Multi-select
    domain.append(('sale_order_type_id', 'in', self.sales_order_type_ids.ids))
elif self.sales_order_type_id:  # Single select
    domain.append(('sale_order_type_id', '=', self.sales_order_type_id.id))
```
**Issue**: These fields serve same purpose - may confuse users
**Options**:
1. Use only `sales_order_type_ids` (multi-select) - remove single select
2. Make single select override multi-select only if not empty
3. Keep both but document the precedence

---

## Summary of Fixes

### High Priority
1. ✅ **Define "booking_sale"** - is it unit_price, price_subtotal, or amount_total?
2. ✅ **Fix total_booked_sales calculation** - use correct field
3. ✅ **Apply order filters to invoice metrics** - respect user's order type/agent filters

### Medium Priority  
4. Consolidate order_type filters (single + multi-select)
5. Ensure agent filter applies to all metrics

### Low Priority
6. Add logging to debug filter application
7. Document filter precedence clearly

---

## Next Steps

**Please clarify**:
- What does "booking_sale" mean in your system?
- Should it be the unit_price from order lines, the subtotal, or the total order amount?
- Should order type and agent filters apply to invoice metrics too?

Once clarified, I will:
1. Update the dashboard model with correct calculations
2. Deploy fixes to the server
3. Test with real data to verify accuracy
