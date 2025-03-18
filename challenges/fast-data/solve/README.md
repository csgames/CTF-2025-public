# Fast-Data

NOTE: The intended solution doesn't work, but someone still broke the challenge and got the flag.

The intended solve was an reflected XSS in the data query on the "Try it" page. To bypass CSP, it was needed to exploit the vulnerable domain https://*.github.io/FastDataStaticFile/ by hosting your payload on github pages, but that doesn't work. After that, you would poison your payload with querying `?s=&s=PAYLOAD`, which would poison the cache and give your payload to the admin.

The unintended solve is by doing cache deception instead. Shoutout to `Monopoly` for finding it. You can create a payload that is `<img src='http://CHALLENGE/api/admin'>`, and poison it into the cache with the same query `?s=&s=PAYLOAD`. After that, the admin would fetch the api call and put the flag into the cache, which can be access by any user after that.

----

NOTE: La solution prévu ne fonctionne pas, mais quelqu'un quand-même brisé le challenge et a eu le flag.

La façon prévu commence par un reflected XSS dans les data queries sur la page "Try it". Le payload se fait renvoyer dans un call API. Cependant, une règle CSP empêche le payload de s'exécuter. Il faut donc exploiter le domaine vulnérable https://*.github.io/FastDataStaticFile/, qui est en fait un Github Pages sur un repo s'appelant FastDataStaticFile. En hébergeant le payload, il pourra être exécuté.

Pour que le payload s'exécute sur le compte de l'admin, il faut empoisonner la cache. Le serveur de cache est configuré pour prendre la première apparition du paramètre s comme cache-key, tandis que le serveur utilise le deuxième. En mettant donc `?s=&s=PAYLOAD`, le payload sera mis en cache pour le paramètre vide que l'admin visite.

La façon non prévu est en fesant du cache deception. Shoutout à `Monopoly` pour la solution. Il est possible de créer un payload qui ressemble à `<img src='http://CHALLENGE/api/admin'>`, et empoisonner la cache avec la même query `?s=&s=PAYLOAD`. Après cela, l'admin fait un appel à l'API et met le flag en cache, qui peut par la suite est accessible à tous les users.