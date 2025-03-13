from setuptools import setup, find_packages

setup(
    name="llm_hub",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "chainlit>=0.7.700",
        "langchain>=0.0.300",
        "anthropic>=0.8.0",
        "openai>=1.6.0",
        "mistralai>=0.0.7",
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.0.0",
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "pypdf>=3.17.0",
        "pillow>=10.1.0",
        "pandas>=2.1.2",
        "numpy>=1.26.0",
    ],
)