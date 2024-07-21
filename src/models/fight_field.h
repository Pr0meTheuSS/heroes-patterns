#pragma once

#include <cstdint>
#include <vector>

class Cell;

class FightField {
public:
  FightField(uint8_t, uint8_t);
  ~FightField() = default;

  Cell &getCell(int, int);

private:
  uint8_t m_width;
  uint8_t m_height;
  std::vector<std::vector<Cell>> m_field;
};
