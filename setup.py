import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="enhanced-web-audit-script",
    version="2.0.0",
    author="netss",
    author_name="netss",
    description="An AI-Agentic Web Audit Tool with autonomous skills and Streamlit interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/netssv/enhanced-web-audit-script",
    packages=setuptools.find_packages(exclude=["tests*", "modules*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "streamlit>=1.28.0",
        "requests>=2.31.0",
        "dnspython>=2.4.0",
        "python-whois>=0.8.0",
        "plotly>=5.15.0",
        "pandas>=2.0.0",
        "pyopenssl>=23.0.0",
        "google-generativeai>=0.3.0",
        "openai>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "web-audit=demo_audit:main",
        ],
    },
)
