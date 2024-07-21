from conan import ConanFile
from conan.tools.cmake import cmake_layout


class ExampleRecipe(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain", "cmake"

    def requirements(self):
        self.requires("sfml/2.6.1")

    def layout(self):
        cmake_layout(self)

