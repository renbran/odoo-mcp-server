-- Add missing columns for deal tracking on sale_order
ALTER TABLE sale_order ADD COLUMN IF NOT EXISTS buyer_name VARCHAR;
ALTER TABLE sale_order ADD COLUMN IF NOT EXISTS project_id INTEGER;
ALTER TABLE sale_order ADD COLUMN IF NOT EXISTS project_name VARCHAR;
ALTER TABLE sale_order ADD COLUMN IF NOT EXISTS unit_sale_value NUMERIC(16,2);
ALTER TABLE sale_order ADD COLUMN IF NOT EXISTS primary_commission_percentage DOUBLE PRECISION;
ALTER TABLE sale_order ADD COLUMN IF NOT EXISTS deal_summary_html TEXT;

-- Add missing columns for deal tracking on account_move
ALTER TABLE account_move ADD COLUMN IF NOT EXISTS buyer_name VARCHAR;
ALTER TABLE account_move ADD COLUMN IF NOT EXISTS project_name VARCHAR;
ALTER TABLE account_move ADD COLUMN IF NOT EXISTS unit_sale_value NUMERIC(16,2);
ALTER TABLE account_move ADD COLUMN IF NOT EXISTS commission_percentage DOUBLE PRECISION;
ALTER TABLE account_move ADD COLUMN IF NOT EXISTS sale_order_deal_reference VARCHAR;
ALTER TABLE account_move ADD COLUMN IF NOT EXISTS sale_order_id INTEGER;

-- Add foreign key constraint for project_id
ALTER TABLE sale_order ADD CONSTRAINT IF NOT EXISTS sale_order_project_id_fk
  FOREIGN KEY (project_id) REFERENCES project_project(id);

-- Add foreign key constraint for sale_order_id on account_move
ALTER TABLE account_move ADD CONSTRAINT IF NOT EXISTS account_move_sale_order_id_fk
  FOREIGN KEY (sale_order_id) REFERENCES sale_order(id);
