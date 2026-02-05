from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="linkbrain",
    version="0.1.0",
    author="Satyam Tomar",
    author_email="satyamtomar41015@gmail.com",
    description="AI-powered ESP32 control framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/satyam-tomar/linkbrain",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Home Automation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "bleak>=0.20.0",  # Bluetooth support
    ],
    extras_require={
        "ai": [
            "anthropic>=0.7.0",  # Claude support
            "google-generativeai>=0.3.0",  # Gemini support
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
)