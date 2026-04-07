from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agentic-sre-gateway",
    version="1.0.0",
    author="Manik Bodamwad",
    author_email="bodamwadm@gmail.com",
    description="An SRE-Optimized API Gateway for dynamic LLM routing, Redis caching, and Prometheus telemetry.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ManikBodamwad/LLM-Latency-Cost-Router",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "litellm>=1.0.0",
        "redis>=5.0.0",
        "prometheus_client>=0.17.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "agentic-gateway=app.cli:start_gateway",
        ],
    },
)
