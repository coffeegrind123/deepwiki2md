from setuptools import setup, find_packages

setup(
    name="deepwiki-to-md",
    version="0.4.0",
    description="A tool to convert deepwiki content to Markdown format using browser automation",
    author="Claude Code",
    author_email="noreply@anthropic.com",
    packages=find_packages(),
    package_data={
        'deepwiki_to_md': ['lang/*.json'],
    },
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "markdownify>=0.11.0",
        "pydoll>=1.0.0",  # For browser automation
    ],
    entry_points={
        'console_scripts': [
            'deepwiki-to-md=deepwiki_to_md.run_scraper:main',
            'deepwiki-chat=deepwiki_to_md.chat:main',
            'deepwiki-create=deepwiki_to_md.create:main',
        ],
    },
    python_requires='>=3.7',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)