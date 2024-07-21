#include <iostream>
#include <stdexcept>

#include "SFML/Graphics/ConvexShape.hpp"
#include "SFML/Graphics/Rect.hpp"
#include "SFML/System/Vector2.hpp"
#include "SFML/Window/Mouse.hpp"

#include <SFML/Graphics.hpp>

const int gridWidth = 12;
const int gridHeight = 6;
const int tileSize = 40;
const float windowWidth = 1280;
const float windowHeight = 600;
sf::ConvexShape *hoveredCell;

const auto idleCellColor = sf::Color(150, 150, 150, 128);
const auto hoveredCellColor = sf::Color(200, 200, 200, 128);

std::vector<std::vector<sf::ConvexShape>> fightFieldCells;

void drawPerspectiveView(sf::RenderWindow &window) {
  for (auto column : fightFieldCells) {
    for (auto cell : column) {
      window.draw(cell);
    }
  }
}

sf::ConvexShape *getHoveredCell(sf::Vector2i pos) {
  for (auto &column : fightFieldCells) {
    for (auto &cell : column) {
      if (cell.getLocalBounds().contains(pos.x, pos.y)) {
        return &cell;
      }
    }
  }
  return {};
}

int main() {
  auto effectiveRect = sf::IntRect(0, windowHeight / 2.5, windowWidth,
                                   windowHeight / 2.5 / 8 * 9);
  float width = static_cast<float>(effectiveRect.width) / gridWidth;
  float height = static_cast<float>(effectiveRect.height) /
                 gridHeight; // Эффект перспективы

  for (int i = 0; i < gridWidth; ++i) {
    std::vector<sf::ConvexShape> column;
    for (int j = 0; j < gridHeight; ++j) {
      sf::ConvexShape tile;
      tile.setPointCount(4);

      tile.setPoint(0, sf::Vector2f(effectiveRect.left + i * width,
                                    effectiveRect.top + j * height));
      tile.setPoint(1, sf::Vector2f(effectiveRect.left + (i + 1) * width,
                                    effectiveRect.top + j * height));
      tile.setPoint(2, sf::Vector2f(effectiveRect.left + (i + 1) * width,
                                    effectiveRect.top + (j + 1) * height));
      tile.setPoint(3, sf::Vector2f(effectiveRect.left + i * width,
                                    effectiveRect.top + (j + 1) * height));
      tile.setFillColor(idleCellColor);
      tile.setOutlineColor(sf::Color::Black);
      tile.setOutlineThickness(1);
      column.push_back(tile);
    }
    fightFieldCells.push_back(column);
    column.clear();
  }
  sf::Texture texture;
  if (!texture.loadFromFile("../assets/game_background_3.png")) {
    throw std::runtime_error("texture load error");
  }
  auto textureSize = texture.getSize();
  std::cout << textureSize.x << " " << textureSize.y << std::endl;

  // Создаём окно с заданными размерами
  sf::RenderWindow window(sf::VideoMode(windowWidth, windowHeight),
                          "SFML works!");
  sf::Sprite backgroundSprite;
  backgroundSprite.setTexture(texture);

  // Рассчитываем коэффициенты масштабирования
  float scaleX = windowWidth / textureSize.x;
  float scaleY = windowHeight / textureSize.y;
  backgroundSprite.setScale(scaleX, scaleY);

  while (window.isOpen()) {
    sf::Event event;
    while (window.pollEvent(event)) {
      if (event.type == sf::Event::Closed)
        window.close();
      if (event.type == sf::Event::MouseMoved) {
        auto *cell = getHoveredCell(sf::Mouse::getPosition(window));
        if (!cell) {
          if (hoveredCell) {
            hoveredCell->setFillColor(idleCellColor);
            hoveredCell = {};
          }
        }
        if (cell && cell != hoveredCell) {
          if (hoveredCell) {
            hoveredCell->setFillColor(idleCellColor);
          }
          cell->setFillColor(hoveredCellColor);
          hoveredCell = cell;
        }
      }
    }

    window.clear();
    window.draw(backgroundSprite);
    drawPerspectiveView(window); // Включаем рисование сетки
    window.display();
  }

  return 0;
}
