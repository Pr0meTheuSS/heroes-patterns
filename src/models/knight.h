#pragma once

#include <cstdint>

#include "unit.h"
#include "unit_state.h"

class Knight : public Unit {
public:
    Knight(UnitState state)
        : Unit(state)
    {
        m_maxPathLength = 3;
    };
    virtual ~Knight() = default;

    uint8_t getMaxPathLength() const override { return m_maxPathLength; };
};
