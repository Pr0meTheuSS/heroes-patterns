#include <stdexcept>

#include <SFML/Graphics.hpp>
#include <SFML/Graphics/Rect.hpp>
#include <SFML/System/Vector2.hpp>
#include <SFML/Window/Mouse.hpp>

#include "fight_field_grid.h"

const int gridWidth = 12;
const int gridHeight = 6;

const int tileSize = 40;
const float windowWidth = 1280;
const float windowHeight = 600;

int main()
{
    auto effectiveRect = sf::IntRect(0, windowHeight / 2.5, windowWidth,
        windowHeight / 2.5 / 8 * 9);

    FightFieldGrid fightFieldGrid(12, 6, effectiveRect);

    sf::Texture texture;
    if (!texture.loadFromFile("../assets/game_background_3.png")) {
        throw std::runtime_error("texture load error");
    }
    auto textureSize = texture.getSize();
    sf::Sprite backgroundSprite;
    backgroundSprite.setTexture(texture);

    // Рассчитываем коэффициенты масштабирования
    float scaleX = windowWidth / textureSize.x;
    float scaleY = windowHeight / textureSize.y;
    backgroundSprite.setScale(scaleX, scaleY);

    // Создаём окно с заданными размерами
    sf::RenderWindow window(sf::VideoMode(windowWidth, windowHeight),
        "SFML works!");

    sf::Texture knightTexture;
    if (!knightTexture.loadFromFile("../assets/knight_idle_sprite_0.png")) {
        throw std::runtime_error("texture load error");
    }
    auto knightTextureSize = knightTexture.getSize();
    sf::Sprite knightSprite;
    knightSprite.setTexture(knightTexture);
    knightSprite.setPosition(effectiveRect.left, effectiveRect.top);

    while (window.isOpen()) {
        sf::Event event;
        while (window.pollEvent(event)) {
            if (event.type == sf::Event::Closed)
                window.close();
            if (event.type == sf::Event::MouseMoved) {
                auto relativePosition = sf::Mouse::getPosition(window);
                fightFieldGrid.hoverCell(relativePosition.x, relativePosition.y);
            }
        }

        window.clear();
        window.draw(backgroundSprite);
        window.draw(knightSprite);
        fightFieldGrid.drawPerspectiveView(window);
        window.display();
    }

    return 0;
}
