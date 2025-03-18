const std = @import("std");

pub const Action = @import("action.zig").Action;

pub const Direction = @import("direction.zig").Direction;

pub const Player = @import("player.zig").Player;
pub const PlayerLobby = @import("player.zig").PlayerLobby;

pub const Message = @import("message.zig").Message;
pub const MessageQueue = @import("message.zig").MessageQueue;

pub const Tile = @import("tile.zig").Tile;
pub const World = @import("world.zig").World;

test {
    std.testing.refAllDeclsRecursive(@This());
    std.testing.refAllDeclsRecursive(@import("bindings.zig"));
}
