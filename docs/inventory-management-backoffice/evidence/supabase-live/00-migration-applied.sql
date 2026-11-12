-- 021 inventario: DDL generado desde los modelos SQLModel de 106083a (dialecto postgresql) + semilla de app/inventory/seed.py
CREATE TABLE asset (
	id SERIAL NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	sku VARCHAR(64) NOT NULL, 
	category VARCHAR(32) NOT NULL, 
	office VARCHAR(32) NOT NULL, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_asset_office ON asset (office);
CREATE UNIQUE INDEX ix_asset_sku ON asset (sku);
CREATE TABLE assetentry (
	id SERIAL NOT NULL, 
	asset_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	supplier VARCHAR(200) NOT NULL, 
	office VARCHAR(32) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	user_uuid VARCHAR(64) NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_assetentry_quantity_positive CHECK (quantity > 0), 
	FOREIGN KEY(asset_id) REFERENCES asset (id)
);
CREATE INDEX ix_assetentry_asset_id ON assetentry (asset_id);
CREATE INDEX ix_assetentry_user_uuid ON assetentry (user_uuid);
CREATE TABLE assetexit (
	id SERIAL NOT NULL, 
	asset_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	exit_type VARCHAR(32) NOT NULL, 
	assigned_to VARCHAR(200), 
	office VARCHAR(32) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	user_uuid VARCHAR(64) NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_assetexit_quantity_positive CHECK (quantity > 0), 
	FOREIGN KEY(asset_id) REFERENCES asset (id)
);
CREATE INDEX ix_assetexit_asset_id ON assetexit (asset_id);
CREATE INDEX ix_assetexit_user_uuid ON assetexit (user_uuid);
INSERT INTO asset (name, sku, category, office) VALUES ('Laptop 14" Business', 'NXV-IT-001', 'hardware', 'Valencia');
INSERT INTO asset (name, sku, category, office) VALUES ('Laptop 14" Business', 'NXV-IT-002', 'hardware', 'Miami');
INSERT INTO asset (name, sku, category, office) VALUES ('Ergonomic mouse', 'NXV-PER-001', 'peripherals', 'Valencia');
INSERT INTO asset (name, sku, category, office) VALUES ('USB-C Hub', 'NXV-PER-002', 'peripherals', 'Miami');
INSERT INTO asset (name, sku, category, office) VALUES ('A4 paper ream', 'NXV-OFF-001', 'office_supplies', 'Valencia');
INSERT INTO asset (name, sku, category, office) VALUES ('Leadership training workbook', 'NXV-TRN-001', 'training_materials', 'Valencia');
INSERT INTO assetentry (asset_id, quantity, supplier, office, created_at, user_uuid) SELECT id, 10, 'TechDistrib Valencia S.L.', 'Valencia', TIMESTAMPTZ '2026-03-02 09:00:00+00', '00000000-0000-4000-8000-000000000201' FROM asset WHERE sku = 'NXV-IT-001';
INSERT INTO assetentry (asset_id, quantity, supplier, office, created_at, user_uuid) SELECT id, 5, 'TechDistrib Valencia S.L.', 'Valencia', TIMESTAMPTZ '2026-03-02 09:01:00+00', '00000000-0000-4000-8000-000000000201' FROM asset WHERE sku = 'NXV-IT-001';
INSERT INTO assetentry (asset_id, quantity, supplier, office, created_at, user_uuid) SELECT id, 8, 'Office Depot Miami', 'Miami', TIMESTAMPTZ '2026-03-02 09:02:00+00', '00000000-0000-4000-8000-000000000201' FROM asset WHERE sku = 'NXV-IT-002';
INSERT INTO assetentry (asset_id, quantity, supplier, office, created_at, user_uuid) SELECT id, 20, 'TechDistrib Valencia S.L.', 'Valencia', TIMESTAMPTZ '2026-03-02 09:03:00+00', '00000000-0000-4000-8000-000000000201' FROM asset WHERE sku = 'NXV-PER-001';
INSERT INTO assetentry (asset_id, quantity, supplier, office, created_at, user_uuid) SELECT id, 30, 'TechDistrib Valencia S.L.', 'Valencia', TIMESTAMPTZ '2026-03-02 09:04:00+00', '00000000-0000-4000-8000-000000000201' FROM asset WHERE sku = 'NXV-OFF-001';
INSERT INTO assetentry (asset_id, quantity, supplier, office, created_at, user_uuid) SELECT id, 15, 'TechDistrib Valencia S.L.', 'Valencia', TIMESTAMPTZ '2026-03-02 09:05:00+00', '00000000-0000-4000-8000-000000000201' FROM asset WHERE sku = 'NXV-TRN-001';
INSERT INTO assetexit (asset_id, quantity, exit_type, assigned_to, office, created_at, user_uuid) SELECT id, 3, 'allocation', 'NXV-EMP-1042', 'Valencia', TIMESTAMPTZ '2026-03-02 09:06:00+00', '00000000-0000-4000-8000-000000000201' FROM asset WHERE sku = 'NXV-IT-001';
INSERT INTO assetexit (asset_id, quantity, exit_type, assigned_to, office, created_at, user_uuid) SELECT id, 2, 'allocation', 'NXV-EMP-2201', 'Miami', TIMESTAMPTZ '2026-03-02 09:07:00+00', '00000000-0000-4000-8000-000000000201' FROM asset WHERE sku = 'NXV-IT-002';
INSERT INTO assetexit (asset_id, quantity, exit_type, assigned_to, office, created_at, user_uuid) SELECT id, 12, 'consumption', NULL, 'Valencia', TIMESTAMPTZ '2026-03-02 09:08:00+00', '00000000-0000-4000-8000-000000000201' FROM asset WHERE sku = 'NXV-OFF-001';
ALTER TABLE asset ENABLE ROW LEVEL SECURITY;
ALTER TABLE assetentry ENABLE ROW LEVEL SECURITY;
ALTER TABLE assetexit ENABLE ROW LEVEL SECURITY;
