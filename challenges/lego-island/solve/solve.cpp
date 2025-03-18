#include "lib/interleaf.h"

#include <iostream>
#include <sstream>

int main(int argc, const char **argv) {
    si::Interleaf il;
    il.Read(argv[1]);

    std::string expected(argv[2]);

    size_t i = 0;
    std::stringstream ss;
    for (auto child : il.GetChildren()) {
        if (i++ == 0) continue;

        auto obj = static_cast<si::Object *>(child);

        if (obj->location_.z == 0) break;
        ss << (char)obj->location_.z;

        if (obj->location_.x == 0) break;
        ss << (char)obj->location_.x;
    }

    auto actual = ss.str();
    if (actual != expected) {
        std::cerr << "FAIL: " << actual << std::endl;

        return 1;
    }

    return 0;
}
