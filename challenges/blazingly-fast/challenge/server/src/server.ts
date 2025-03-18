import MESSAGE from "./message.ts";
import Game from "./game.ts";

const GAMES: Record<string, Game> = {};

const server = Bun.serve<{
    player: number;
    gameId: string;
    game: Game;
}>({
    async fetch(req, server) {
        const url = new URL(req.url);

        const gameId = url.searchParams.get("gameId");
        if (gameId === null) return new Response("Game is invalid", { status: 400 }); 

        const name = url.searchParams.get("name")?.substring(0, 8);
        if (name === undefined) return new Response("Name is invalid", { status: 400 }); 

        if (GAMES[gameId] === undefined) GAMES[gameId] = new Game(gameId);
        const game = GAMES[gameId];

        const player = game.join(name);
        if (player == null) return new Response("Game is full", { status: 400 });

        if (server.upgrade(req, {
            data: {
                player,
                gameId,
                game: GAMES[gameId]
            }
        })) return;

        return new Response("WebSocket upgrade error", { status: 400 });
    },
    websocket: {
        async open(ws) {
            ws.subscribe(ws.data.gameId);

            ws.send(JSON.stringify({
                type: "init",
                data: {
                    messages: ws.data.game.getMessages(),
                    players: ws.data.game.getPlayers(),
                    map: ws.data.game.getMap()
                }
            }));

            ws.publish(ws.data.gameId, JSON.stringify({
                type: "players",
                data: {
                    players: ws.data.game.getPlayers()
                }
            }));
        },
        async message(ws, message) {
            const rawMessage = JSON.parse(message.toString());

            const parseMessage = await MESSAGE.safeParseAsync(rawMessage);
            if (parseMessage.error) return;

            switch (parseMessage.data.type) {
            case "message": {
                const data = parseMessage.data.data;
                if (!ws.data.game.message(ws.data.player, data.text)) break;

                const res = JSON.stringify({
                    type: "message",
                    data: {
                        text: ws.data.game.getLastMessage()
                    }
                });

                ws.send(res);
                ws.publish(ws.data.gameId, res);
            } break;

            case "move": {
                const data = parseMessage.data.data;
                if (!ws.data.game.move(ws.data.player, data.direction)) break;

                const res = JSON.stringify({
                    type: "players",
                    data: {
                        players: ws.data.game.getPlayers()
                    }
                });

                ws.send(res);
                ws.publish(ws.data.gameId, res);
            } break;

            case "pickup": {
                let text = null;
                if (ws.data.game.pickup(ws.data.player)) {
                    text = Bun.env.FLAG || "FLAG";
                }

                const res = JSON.stringify({
                    type: "pickup",
                    data: { 
                        map: ws.data.game.getMap(),
                        text
                    }
                });

                ws.send(res);
            } break;

            }
        },
        async close(ws) {
            ws.data.game.leave(ws.data.player);

            if (ws.data.game.getPlayerCount() == 0) {
                GAMES[ws.data.gameId] = undefined;
            } else {
                ws.publish(ws.data.gameId, JSON.stringify({
                    type: "players",
                    data: {
                        players: ws.data.game.getPlayers()
                    }
                }));
            }

            ws.unsubscribe(ws.data.gameId);
        }
    }
});

console.log(`Listening on http://${server.hostname}:${server.port}`);
