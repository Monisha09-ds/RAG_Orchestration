try:
    from langchain_huggingface import HuggingFaceEmbeddings
    print("✅ Successfully imported HuggingFaceEmbeddings")
except ImportError as e:
    print(f"❌ Failed to import: {e}")
