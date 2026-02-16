def try_import(name, import_path):
    try:
        __import__(import_path)
        print(f"{name}: OK")
    except Exception as e:
        print(f"{name}: ERR -> {e}")


tests = [
    ("langchain_google_genai.GoogleGemini", "langchain_google_genai"),
    ("langchain.prompts.chat.ChatPromptTemplate", "langchain.prompts.chat"),
    ("langchain.schema.SystemMessage/HumanMessage", "langchain.schema"),
    ("langchain.callbacks.LangsmithTracer", "langchain.callbacks"),
    ("langchain.tracers.langsmith.LangsmithTracer", "langchain.tracers.langsmith"),
]

for name, path in tests:
    try_import(name, path)

print('\nDone import tests')
