from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="thingspanel-mcp",
    version="0.1.0",
    author="ThingsPanel",
    author_email="contact@thingspanel.cn",
    description="MCP (Model Control Plane) server for ThingsPanel IoT platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ThingsPanel/thingspanel-mcp",
    project_urls={
        "Bug Tracker": "https://github.com/ThingsPanel/thingspanel-mcp/issues",
        "Documentation": "https://docs.thingspanel.cn",
        "Source Code": "https://github.com/ThingsPanel/thingspanel-mcp",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "thingspanel_mcp": ["py.typed"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet of Things",
    ],
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.24.0",
        "python-dotenv>=0.19.0",
    ],
    entry_points={
        "console_scripts": [
            "thingspanel-mcp=thingspanel_mcp.cli:main",
        ],
    },
) 