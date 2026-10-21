CREATE TABLE regions (region_id integer PRIMARY KEY, name text NOT NULL UNIQUE);
CREATE TABLE customers (customer_id integer PRIMARY KEY, name text NOT NULL, region_id integer NOT NULL REFERENCES regions, segment text NOT NULL, created_at date NOT NULL);
CREATE TABLE categories (category_id integer PRIMARY KEY, name text NOT NULL UNIQUE);
CREATE TABLE products (product_id integer PRIMARY KEY, name text NOT NULL, category_id integer NOT NULL REFERENCES categories, unit_price numeric(12,2) NOT NULL CHECK(unit_price >= 0), active boolean NOT NULL);
CREATE TABLE sales_reps (rep_id integer PRIMARY KEY, name text NOT NULL, region_id integer NOT NULL REFERENCES regions, hired_at date NOT NULL);
CREATE TABLE orders (order_id integer PRIMARY KEY, customer_id integer NOT NULL REFERENCES customers, rep_id integer NOT NULL REFERENCES sales_reps, order_date date NOT NULL, status text NOT NULL CHECK(status IN ('OPEN','INVOICED','CANCELLED')), freight numeric(12,2) NOT NULL CHECK(freight >= 0));
CREATE TABLE order_items (order_item_id integer PRIMARY KEY, order_id integer NOT NULL REFERENCES orders, product_id integer NOT NULL REFERENCES products, quantity integer NOT NULL CHECK(quantity > 0), unit_price numeric(12,2) NOT NULL CHECK(unit_price >= 0), discount_pct numeric(5,4) NOT NULL CHECK(discount_pct BETWEEN 0 AND 1));
CREATE TABLE sales_targets (target_id integer PRIMARY KEY, rep_id integer NOT NULL REFERENCES sales_reps, month_start date NOT NULL, target_amount numeric(12,2) NOT NULL, UNIQUE(rep_id, month_start));
CREATE INDEX orders_date_idx ON orders(order_date); CREATE INDEX items_order_idx ON order_items(order_id);
