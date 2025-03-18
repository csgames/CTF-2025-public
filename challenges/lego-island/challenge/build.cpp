#include "lib/interleaf.h"

#include <iostream>

#ifndef FLAG
#define FLAG "FLAG"
#endif

const char FLAG_BUFFER[64] = FLAG;
const std::vector<std::string> MESSAGE {
    "Whoops!",
    "You",
    "Have",
    "To",
    "Put",
    "The",
    "CD",
    "In",
    "Your",
    "Computer",
    "To",
    "Find",
    "The",
    "Flag!"
};

int main(int argc, const char **argv) {
    si::Interleaf il;
    il.Read(argv[1]);

    size_t id = 3;
    size_t fi = 0;

    for (auto segment : MESSAGE) {
        auto obj = new si::Object();

        obj->type_ = si::MxOb::Type::Object;
        obj->name_ = segment;
        obj->id_ = id++;
        obj->location_ = si::Vector3(FLAG_BUFFER[fi++], 0, FLAG_BUFFER[fi++]);
        obj->up_ = si::Vector3(0, 1, 0);

        il.AppendChild(obj);
    }

    il.Write(argv[2]);

    return 0;
}
