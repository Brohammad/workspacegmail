def check_imports():
    try:
        from langchain_google_genai import GoogleGemini
        print('GG_OK')
    except Exception as e:
        print('GG_ERR', e)

    try:
        from langchain_core.tracers.langchain import LangChainTracer
        print('LCT_OK')
    except Exception as e:
        print('LCT_ERR', e)

    try:
        import langchain_core.prompts.chat as pc
        print('PROMPTS_OK')
    except Exception as e:
        print('PROMPTS_ERR', e)

if __name__ == '__main__':
    check_imports()
