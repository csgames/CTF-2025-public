pub const Tile = enum(u8) {
    empty = ' ',
    wall = '#',
    flag = '~',
    _,

    pub const PLACEABLE = [_]Tile{ .empty, .empty, .empty, .wall };

    const Self = @This();

    pub fn isPickup(self: Self) bool {
        return switch (self) {
            .flag => true,
            else => false,
        };
    }

    pub fn isSolid(self: Self) bool {
        return switch (self) {
            .wall => true,
            else => false,
        };
    }
};
