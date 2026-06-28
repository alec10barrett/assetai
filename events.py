class Event(Base):
    __tablename__ = "events"

    id

    property_id

    document_id

    event_type

    title

    description

    occurred_at

    metadata   # JSONB

    created_at
