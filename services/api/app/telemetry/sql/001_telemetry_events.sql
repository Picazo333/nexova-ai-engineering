-- telemetry_events: hechos inmutables. Una fila por evento aceptado.
-- El mapeo de columnas está en docs/telemetry/telemetry-plan.md, sección 13.
-- No hay UPDATE ni DELETE de aplicación. Los triggers rechazan esas sentencias.

CREATE TABLE IF NOT EXISTS telemetry_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp timestamptz NOT NULL,
    service text NOT NULL,
    event_type text NOT NULL,
    level text NOT NULL DEFAULT 'info',
    value numeric NULL,
    message text NULL,
    tags jsonb NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT telemetry_events_level_check CHECK (level IN ('info', 'warn', 'error')),
    CONSTRAINT telemetry_events_tags_object_check CHECK (jsonb_typeof(tags) = 'object')
);

CREATE INDEX IF NOT EXISTS telemetry_events_timestamp_idx
    ON telemetry_events (timestamp);

CREATE INDEX IF NOT EXISTS telemetry_events_event_type_idx
    ON telemetry_events (event_type);

CREATE INDEX IF NOT EXISTS telemetry_events_tags_gin_idx
    ON telemetry_events USING GIN (tags);

CREATE OR REPLACE FUNCTION telemetry_events_reject_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'telemetry_events es de solo escritura';
END;
$$;

DROP TRIGGER IF EXISTS telemetry_events_no_update ON telemetry_events;
CREATE TRIGGER telemetry_events_no_update
    BEFORE UPDATE ON telemetry_events
    FOR EACH ROW
    EXECUTE PROCEDURE telemetry_events_reject_mutation();

DROP TRIGGER IF EXISTS telemetry_events_no_delete ON telemetry_events;
CREATE TRIGGER telemetry_events_no_delete
    BEFORE DELETE ON telemetry_events
    FOR EACH ROW
    EXECUTE PROCEDURE telemetry_events_reject_mutation();

DROP TRIGGER IF EXISTS telemetry_events_no_truncate ON telemetry_events;
CREATE TRIGGER telemetry_events_no_truncate
    BEFORE TRUNCATE ON telemetry_events
    FOR EACH STATEMENT
    EXECUTE PROCEDURE telemetry_events_reject_mutation();

ALTER TABLE telemetry_events ENABLE ROW LEVEL SECURITY;

COMMENT ON TABLE telemetry_events IS
    'Hechos de telemetría. Solo INSERT. El dueño escribe; no hay política para la clave anónima.';
