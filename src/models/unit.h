#pragma once

#include <cstdint>

#include "unit_state.h"

class Unit {
public:
    Unit(UnitState& state)
        : m_state(state) {};
    virtual ~Unit() = default;
    virtual uint8_t getMaxPathLength() const = 0;

protected:
    uint8_t m_maxPathLength;
    UnitState& m_state;
};
