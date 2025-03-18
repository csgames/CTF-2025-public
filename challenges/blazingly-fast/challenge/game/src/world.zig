const std = @import("std");

const Tile = @import("tile.zig").Tile;

pub const World = extern struct {
    tiles: WorldTiles,

    const Self = @This();
    const WorldTiles = [DIMENSION][DIMENSION]Tile;

    pub const DIMENSION = 16;

    pub fn init(seed: u64) Self {
        var tiles: WorldTiles = undefined;
        Self.generate(seed, &tiles);

        return Self{ .tiles = tiles };
    }

    pub fn spawn(self: *const World) ![2]u8 {
        var y = self.tiles.len - 1;
        while (true) : (y -= 1) {
            const row = &self.tiles[y];

            var x = row.len - 1;
            while (true) : (x -= 1) {
                const tile = &row[x];

                if (tile.* == .empty) return .{ @intCast(x), @intCast(y) };
            }

            if (y == 0) break;
        }

        return error.NoEmpty;
    }

    pub fn generate(seed: u64, tiles: *WorldTiles) void {
        var prng = std.rand.DefaultPrng.init(seed);

        for (tiles) |*row| {
            for (row) |*tile| {
                tile.* = Tile.PLACEABLE[@intCast(prng.next() % Tile.PLACEABLE.len)];
            }
        }

        const flag_coord = prng.next();
        const flag_y: usize = @intCast((flag_coord & 0xFF) % tiles.len);
        const flag_x: usize = @intCast(((flag_coord >> 8) & 0xFF) % tiles[0].len);

        if (flag_y > 0) tiles[flag_y - 1][flag_x] = .wall;
        if (flag_y < tiles.len - 1) tiles[flag_y + 1][flag_x] = .wall;

        if (flag_x > 0) tiles[flag_y][flag_x - 1] = .wall;
        if (flag_x < tiles[0].len - 1) tiles[flag_y][flag_x + 1] = .wall;

        tiles[flag_y][flag_x] = .flag;
    }
};

test "World generation" {
    // Arrange + Act + Assert
    _ = World.init(0);
}
