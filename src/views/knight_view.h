#pragma once

#include "../models/knight.h"

#include "SFML/Graphics/Sprite.hpp"

class KnightView {
public:
    // TODO: change sprite to class AnimationSrites for changing sprite by
    // model-state.
    KnightView(Knight& model, sf::Sprite& sprite)
        : m_knight(model) {};

    virtual ~KnightView() = default;

private:
    Knight& m_knight;
};
