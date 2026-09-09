from setuptools import setup, find_packages

setup(
    name="explainable-hybrid-ai-cancer",
    version="1.0.0",
    author="Your Name",
    description="Explainable Hybrid AI for Cancer Diagnosis",
    packages=find_packages(),
    install_requires=[
        'torch>=1.12.0',
        'torchvision>=0.13.0',
        'numpy>=1.21.0',
        'scikit-learn>=1.0.0',
        'Pillow>=9.0.0',
        'opencv-python>=4.5.0',
        'matplotlib>=3.4.0',
        'seaborn>=0.11.0',
        'shap>=0.41.0',
        'lime>=0.2.0.1',
        'fastapi>=0.85.0',
        'uvicorn>=0.18.0',
        'tqdm>=4.64.0',
        'pyyaml>=6.0'
    ],
    python_requires='>=3.8',
)
