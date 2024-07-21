#pragma once

#include "SFML/Graphics/ConvexShape.hpp"
#include "SFML/Graphics/RenderWindow.hpp"
#include <cstdint>
#include <vector>
class FightFieldGrid {
public:
  FightFieldGrid(uint8_t width, uint8_t height, sf::IntRect effectiveRect)
      : m_width(width), m_height(height) {

    float cellWidth = static_cast<float>(effectiveRect.width) / m_width;
    float cellHeight = static_cast<float>(effectiveRect.height) / m_width;
    for (int i = 0; i < m_width; ++i) {
      std::vector<sf::ConvexShape> column;
      for (int j = 0; j < m_height; ++j) {
        sf::ConvexShape tile;
        tile.setPointCount(4);

        tile.setPoint(0, sf::Vector2f(effectiveRect.left + i * cellWidth,
                                      effectiveRect.top + j * cellHeight));
        tile.setPoint(1, sf::Vector2f(effectiveRect.left + (i + 1) * cellWidth,
                                      effectiveRect.top + j * cellHeight));
        tile.setPoint(2,
                      sf::Vector2f(effectiveRect.left + (i + 1) * cellWidth,
                                   effectiveRect.top + (j + 1) * cellHeight));
        tile.setPoint(3,
                      sf::Vector2f(effectiveRect.left + i * cellWidth,
                                   effectiveRect.top + (j + 1) * cellHeight));
        tile.setFillColor(idleCellColor);
        tile.setOutlineColor(sf::Color::Black);
        tile.setOutlineThickness(1);
        column.push_back(tile);
      }
      fightFieldCells.push_back(column);
      column.clear();
    }
  };
  ~FightFieldGrid() = default;

  void drawPerspectiveView(sf::RenderWindow &window) const {
    for (auto column : fightFieldCells) {
      for (auto cell : column) {
        window.draw(cell);
      }
    }
  }

  void hoverCell(int x, int y) {
    auto *cell = getHoveredCell(x, y);
    if (!cell) {
      if (hoveredCell) {
        hoveredCell->setFillColor(idleCellColor);
      }
      hoveredCell = nullptr;
      return;
    }
    cell->setFillColor(hoveredCellColor);
    if (cell != hoveredCell) {
      if (hoveredCell) {
        hoveredCell->setFillColor(idleCellColor);
      }
      hoveredCell = cell;
    }
  }

private:
  sf::ConvexShape *getHoveredCell(int x, int y) {
    for (auto &column : fightFieldCells) {
      for (auto &cell : column) {
        if (cell.getLocalBounds().contains(x, y)) {
          return &cell;
        }
      }
    }
    return {};
  }

private:
  uint8_t m_width;
  uint8_t m_height;
  sf::ConvexShape *hoveredCell = nullptr;

  const sf::Color idleCellColor = sf::Color(150, 150, 150, 128);
  const sf::Color hoveredCellColor = sf::Color(200, 200, 200, 128);

  std::vector<std::vector<sf::ConvexShape>> fightFieldCells;
};
