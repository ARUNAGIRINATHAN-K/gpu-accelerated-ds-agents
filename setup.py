from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gpu-accelerated-ds-agents",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="GPU-accelerated autonomous data science agents using RAPIDS and CUDA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/gpu-accelerated-ds-agents",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "streamlit>=1.29.0",
        "transformers>=4.36.0",
        "torch>=2.1.0",
        "langchain>=0.1.0",
        "pandas>=2.1.0",
        "numpy>=1.24.0",
        "plotly>=5.18.0",
        "pyyaml>=6.0.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.12.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
        ],
    },
)
