pub const Direction = enum(u8) {
    up = 0,
    down = 1,
    left = 2,
    right = 3,
    _,

    const Self = @This();

    pub fn delta_x(self: Self) i2 {
        return switch (self) {
            .left => -1,
            .right => 1,
            else => 0,
        };
    }

    pub fn delta_y(self: Self) i2 {
        return switch (self) {
            .up => -1,
            .down => 1,
            else => 0,
        };
    }
};
