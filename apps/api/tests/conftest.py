import os

os.environ.setdefault("ATLAS_LLM_PROVIDER", "fake")
os.environ.setdefault("ATLAS_ALLOW_FAKE_FOR_TESTS", "true")
os.environ.setdefault("ATLAS_DATA_DIR", "./data/test")

