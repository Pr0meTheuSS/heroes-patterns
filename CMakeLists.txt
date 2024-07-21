cmake_minimum_required(VERSION 3.22)
project(my_project)

# Отключение проверки версии компилятора
set(CONAN_DISABLE_CHECK_COMPILER ON)

# Включение conanbuildinfo.cmake
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Найти пакет SFML
find_package(SFML 2.5 COMPONENTS system window graphics REQUIRED)

# Собираем все файлы с расширением .cpp в директории src и поддиректориях
file(GLOB_RECURSE SOURCES "src/*.cpp")

# Создание исполняемого файла из всех исходников
add_executable(${PROJECT_NAME} ${SOURCES})

# Линковка с библиотеками SFML и Conan
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS} sfml-system sfml-window sfml-graphics)

