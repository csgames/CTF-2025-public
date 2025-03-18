const std = @import("std");

const lib = @import("lib.zig");

pub const Action = struct {
    pub fn join(name: []const u8, lobby: *lib.PlayerLobby, world: *const lib.World) !u3 {
        const spawn = world.spawn() catch return error.OutOfBounds;
        const x = spawn[0];
        const y = spawn[1];

        return lobby.add(name, x, y) catch return error.MaxCapacity;
    }

    pub fn leave(index: u3, lobby: *lib.PlayerLobby) !void {
        lobby.remove(index) catch return error.NotFound;
    }

    pub fn message(player: *const lib.Player, text: []const u8, queue: *lib.MessageQueue) !void {
        var msg_buf: lib.Message = undefined;

        const player_name_len = std.mem.indexOf(u8, &player.name, &.{0}) orelse player.name.len;

        const text_len = @min(text.len, msg_buf.len - (player_name_len + 1));
        const msg = std.fmt.bufPrint(&msg_buf, "{s}:{s}", .{ player.name[0..player_name_len], text[0..text_len] }) catch return error.Invalid;

        queue.add(msg);
    }

    pub fn move(player: *lib.Player, world: *const lib.World, direction: lib.Direction) !void {
        const dx = direction.delta_x();
        const dy = direction.delta_y();

        if (dx == 0 and dy == 0) return error.Nothing;

        const nx = @as(i16, @intCast(player.x)) + dx;
        const ny = @as(i16, @intCast(player.y)) + dy;

        if (ny < 0 or nx < 0 or ny >= world.tiles.len or nx >= world.tiles[0].len) return error.OutOfBounds;

        const x: u8 = @intCast(nx);
        const y: u8 = @intCast(ny);

        if (world.tiles[y][x].isSolid()) return error.Collision;

        player.x = x;
        player.y = y;
    }

    pub fn pickup(player: *const lib.Player, world: *lib.World) !void {
        const tile = &world.tiles[player.y][player.x];

        if (!tile.isPickup()) return error.Nothing;

        tile.* = .empty;
    }
};

test "join" {
    // Arrange
    const name = "TEST";
    var lobby = lib.PlayerLobby.init();
    const world = lib.World.init(0);

    // Act
    const index = try Action.join(name, &lobby, &world);

    // Assert
    const player = lobby.get(index) orelse return error.NotFound;

    try std.testing.expectEqualSlices(u8, name, player.name[0..name.len]);
}

test "message" {
    // Arrange
    const player = lib.Player.init("TEST", 0, 0);

    var queue = lib.MessageQueue.init();
    const text = "MESSAGE";

    const expected = "TEST:MESSAGE";

    // Act
    try Action.message(&player, text, &queue);

    // Assert
    const msg = queue.last() orelse return error.NotFound;

    try std.testing.expectEqualSlices(u8, expected, msg[0..expected.len]);
}

test "move" {
    // Arrange
    var player = lib.Player.init("TEST", 0, 0);

    var world = lib.World.init(0);
    world.tiles[0][0] = .empty;
    world.tiles[0][1] = .empty;

    // Act
    try Action.move(&player, &world, .right);

    // Assert
    try std.testing.expectEqual(1, player.x);
    try std.testing.expectEqual(0, player.y);
}

test "pickup" {
    // Arrange
    var player = lib.Player.init("TEST", 0, 0);

    var world = lib.World.init(0);
    world.tiles[0][0] = .flag;

    // Act + Assert
    try Action.pickup(&player, &world);
}
