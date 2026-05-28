DISCUSSION_PROMPT = """Answer the user compactly. Do not expose backend artifacts, map patches, or raw JSON. Mark uncertainty clearly. Use no tables unless requested."""

EXTRACTION_PROMPT = """Extract cognitive residue from the turn. Preserve uncertainty. Do not infer user beliefs, learning, acceptance, or psychology without explicit confirmation."""

MAP_PATCH_PROMPT = """Create an append-only map patch. Do not destructively rewrite maps. Source-backed status requires explicit source ids."""

