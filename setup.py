import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wechy",
    version="2.0.0",
    author="netss",
    description="wechy — Web Check Your site. AI-Agentic TUI for web diagnostics, DNS, SSL, security & more.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/netssv/enhanced-web-audit-script",
    packages=setuptools.find_packages(exclude=["tests*", "modules*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
        "Topic :: System :: Networking",
        "Topic :: Security",
    ],
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.31.0",
        "dnspython>=2.4.0",
        "python-whois>=0.8.0",
        "pyopenssl>=23.0.0",
        "textual>=0.40.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "ai": [
            "google-generativeai>=0.3.0",
            "openai>=1.0.0",
        ],
        "streamlit": [
            "streamlit>=1.28.0",
            "plotly>=5.15.0",
            "pandas>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "wechy=tui_app_run:main",
        ],
    },
)
