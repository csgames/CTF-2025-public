Je suis en train de créer un MMORPG ultra-rapide en [Zig](https://ziglang.org/). J'ai seulement implémenté la quête finale: récupérer le flag `~`. Il ne devrait pas encore être possible d'atteindre le flag; il ne sera déverrouillé que lorsque j'aurai implémenté d'autres quêtes. Pour empêcher les joueurs d'accéder au flag, je l'ai entouré de murs `#`.

La semaine dernière, en regardant les journaux, j'ai vu qu'un joueur avait réussi à obtenir le flag...! Je mène une enquête depuis ce temps, mais je n'arrive pas à déterminer exactement comment ça a été fait. Je suis **100%** certain que le problème vient du code [Zig](https://ziglang.org/) (`/game`), et je suis presque sûr qu'il s'agit d'un bug mémoire. J'espère que vous êtes des experts pour trouver ce genre de bugs parce que je ne le suis pas.

Je vous fournis le `source.zip` du serveur de jeu, où vous trouverez le dossier `/game`. Je vous donne aussi le `client.zip` pour vous connecter au jeu. Enfin, je vous donne le `game.wasm` pour que vous n'ayez pas à compiler le code [Zig](https://ziglang.org/).

J'espère que vous pourrez m'aider à sortir de cette impasse... Vous obtiendrez certainement un flag spécial si vous trouvez la solution à ce problème!
