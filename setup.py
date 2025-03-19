# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="thingspanel-mcp",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="ThingsPanel MCP服务器，用于通过自然语言与ThingsPanel平台交互",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/thingspanel-mcp",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "mcp>=1.2.0",
        "httpx>=0.23.0",
    ],
    entry_points={
        "console_scripts": [
            "thingspanel-mcp=thingspanel_mcp.main:main",
        ],
    },
)