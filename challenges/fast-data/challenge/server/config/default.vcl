vcl 4.0;

import std;

backend default {
    .host = "127.0.0.1";
    .port = "8888";
}

sub vcl_recv {
    if (req.url ~ "\?s=") {
        # Parse the value from the query string
        set req.http.S-And-After = regsub(req.url, "^.*?(\?s=|&s=)[^a-zA-z0-9&]*", "");
        set req.http.to-use = regsub(req.http.S-And-After, "&.*", "");

        return (hash);
    }

    set req.http.to-use = req.url;
    return (hash);
}

sub vcl_hash {
    hash_data(req.http.to-use);
    return (lookup);
}

sub vcl_backend_response {
    # Use the custom cache key for storing cached responses
    if (beresp.status == 200) {
        set beresp.grace = 15s; # Keep in cache for 15 sec
        set beresp.ttl = 15s;   # Time to live
    }
}

sub vcl_deliver {
    if (obj.hits > 0) {
        set resp.http.X-Cache = "HIT";
    } else {
        set resp.http.X-Cache = "MISS";
    }

    set resp.http.X-Cache-Hits = obj.hits;
}
