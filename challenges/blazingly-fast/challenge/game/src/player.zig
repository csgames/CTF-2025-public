const std = @import("std");

pub const Player = extern struct {
    name: [NAME_SIZE]u8 = undefined,
    x: u8,
    y: u8,

    const Self = @This();
    pub const NAME_SIZE = 8;

    pub fn init(name: []const u8, x: u8, y: u8) Self {
        const name_size = @min(name.len, Self.NAME_SIZE);

        var self = Self{ .x = x, .y = y };
        @memcpy(self.name[0..name_size], name[0..name_size]);

        if (name_size < NAME_SIZE) self.name[name_size] = '\x00';

        return self;
    }
};

pub const PlayerLobby = extern struct {
    active: u8 = 0,
    players: [COUNT]Player = undefined,

    const Self = @This();
    pub const COUNT = 8;

    pub fn init() Self {
        return Self{};
    }

    pub fn count(self: *PlayerLobby) u8 {
        var active_bits = self.active;
        var sum: u8 = 0;

        for (0..8) |_| {
            if (active_bits & 1 == 1) sum += 1;
            active_bits >>= 1;
        }

        return sum;
    }

    pub fn add(self: *PlayerLobby, name: []const u8, x: u8, y: u8) !u3 {
        var active_bits = self.active;

        var index: u3 = 0;
        while (true) : (index += 1) {
            if (active_bits & 1 == 0) break;

            if (index >= self.players.len - 1) return error.MaxCapacity;

            active_bits >>= 1;
        }

        const player = &self.players[@intCast(index)];
        self.active ^= @as(u8, 1) << index;

        player.x = x;
        player.y = y;

        const name_size = @min(name.len, Player.NAME_SIZE - 1);
        @memcpy(player.name[0..name_size], name[0..name_size]);
        player.name[name_size] = '\x00';

        return index;
    }

    pub fn remove(self: *PlayerLobby, index: u3) !void {
        const offset = @as(u8, 1) << index;

        const is_active = self.active & offset != 0;
        if (!is_active) return error.Inactive;

        self.active ^= offset;
    }

    pub fn get(self: *const PlayerLobby, index: u3) ?*const Player {
        const offset = @as(u8, 1) << index;

        const is_active = self.active & offset != 0;
        if (!is_active) return null;

        return &self.players[index];
    }

    pub fn get_mut(self: *PlayerLobby, index: u3) ?*Player {
        const offset = @as(u8, 1) << index;

        const is_active = self.active & offset != 0;
        if (!is_active) return null;

        return &self.players[index];
    }
};

test "Add" {
    // Arrange
    var lobby = PlayerLobby.init();
    const name = "TEST";

    // Act
    const index = try lobby.add(name, 1, 2);

    // Assert
    const player = lobby.get(index) orelse return error.NotFound;

    try std.testing.expectEqualSlices(u8, name, player.name[0..name.len]);
    try std.testing.expectEqual(1, player.x);
    try std.testing.expectEqual(2, player.y);
}

test "Max capacity" {
    // Arrange
    var lobby = PlayerLobby.init();
    const name = "TEST";

    // Act
    for (0..lobby.players.len) |_| {
        _ = try lobby.add(name, 0, 0);
    }

    // Assert
    try std.testing.expectError(error.MaxCapacity, lobby.add(name, 0, 0));
}

test "Remove" {
    // Arrange
    var lobby = PlayerLobby.init();
    const name = "TEST";

    // Act
    const first_index = try lobby.add(name, 1, 2);
    try lobby.remove(first_index);

    const second_index = try lobby.add(name, 3, 4);

    // Assert
    try std.testing.expectEqual(1, lobby.count());

    const player = lobby.get(second_index) orelse return error.NotFound;
    try std.testing.expectEqual(0, second_index);
    try std.testing.expectEqual(3, player.x);
    try std.testing.expectEqual(4, player.y);
}
