import setuptools

setuptools.setup (
    name = "fakessl",
    version = "0.0.1",
    packages = setuptools.find_packages (),
    ext_modules = [
        setuptools.Extension (
            "fakessl",
            ["src/fakessl.c"]
        )
    ]
)