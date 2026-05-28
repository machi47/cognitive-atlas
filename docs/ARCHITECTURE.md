# Architecture

The app separates three planes:

- Conversation plane: compact user-facing replies with bounded context.
- Infrastructure plane: routing, research detection, extraction, patch validation, event persistence.
- State/rendering plane: sessions, atlas tree, source cards, map impact, inspector, exports.

Pipeline:

```text
turn intake -> session association -> topic routing -> research detection -> optional source broker
-> conversational reply -> post-turn extraction -> map patch builder -> validator -> writer
-> events/FTS/UI projections/exports
```

The conversational agent does not receive the whole atlas. `ContextBroker` gives each role a bounded packet.

The atlas is a map forest rather than one giant graph so unrelated sessions can remain independent while still contributing bridges and shared maps. Map patches are append-only; writers add/update materialized tables without destructive regeneration.
