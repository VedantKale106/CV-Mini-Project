# setup.py
from setuptools import setup, find_packages

setup(
    name="smart-surveillance-system",
    version="1.0.0",
    description="AI-powered surveillance system with face recognition and intruder alerts",
    author="Your Name",
    author_email="your.email@gmail.com",
    packages=find_packages(),
    install_requires=[
        "opencv-python>=4.8.0",
        "face-recognition>=1.3.0",
        "numpy>=1.24.0",
        "playsound>=1.3.0",
        "Pillow>=10.0.0",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "surveillance=surveillance:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Security",
        "Topic :: Multimedia :: Video :: Capture",
    ],
)
