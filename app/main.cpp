#include <SFML/Graphics.hpp>
#include <iostream>
#define WIDTH 200
#define HEIGHT 400
#define FPS 60

using namespace std;
using namespace sf;

int main(int argc, char **argv) {
    RenderWindow window(VideoMode(WIDTH, HEIGHT), "IOF App");

    Clock clock;
    Time last_time;
    while (window.isOpen()) {
        Event event;
        while (window.pollEvent(event)) {
            switch (event.type) {
            case Event::Closed:
                window.close();
                break;
            default:
                break;
            }
        }

        float delta = (long double)(clock.getElapsedTime() - last_time).asSeconds();
        last_time = clock.getElapsedTime();
        cout << delta << '\n';

        if (clock.getElapsedTime().asMilliseconds() > 1000 / FPS) {
            last_time = Time();
            clock.restart();

            window.clear(Color::Black);
            window.display();
        }
    }
}