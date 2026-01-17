#!/bin/bash
sudo -u postgres psql -d commission_ax << 'EOSQL'
-- Check sale_order columns
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'sale_order' 
  AND column_name IN ('buyer_name', 'project_id', 'project_name', 'unit_sale_value', 'primary_commission_percentage', 'deal_summary_html')
ORDER BY column_name;

-- Check account_move columns
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'account_move' 
  AND column_name IN ('buyer_name', 'project_name', 'unit_sale_value', 'commission_percentage', 'sale_order_deal_reference', 'sale_order_id')
ORDER BY column_name;
EOSQL
