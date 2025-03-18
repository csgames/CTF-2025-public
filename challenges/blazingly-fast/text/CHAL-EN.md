I'm building a blazingly fast MMORPG in [Zig](https://ziglang.org/). I only implemented the final quest: collect the flag `~`. It shouldn't be possible to get to the flag yet; it will only be unlocked when I implement other quests. To prevent players from accessing the flag, I surrounded the flag with walls `#`.

Last week, I was looking at the logs and saw that a player managed to get the flag...! I've been investigating since then and I can't pinpoint exactly how it was done. I'm **100%** certain that it's in the [Zig](https://ziglang.org/) code (`/game`) and I'm pretty certain it's a memory bug. I hope you're an expert in finding these type of bugs because I'm not.

I'm providing you the `source.zip` of the game server, where you'll find the `/game` folder. I'm also giving you the `client.zip` to connect to the game. Lastly, I'm giving you the `game.wasm` so you don't have to compile the [Zig](https://ziglang.org/) code.

I hope you'll get me unstuck... You'll definitely get a special flag if you figure this one out!
